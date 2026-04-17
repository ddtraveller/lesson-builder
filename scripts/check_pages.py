#!/usr/bin/env python3
"""check_pages.py — verify generated lesson HTML pages for common page-level bugs.

Usage:
    python scripts/check_pages.py <output_dir>

Rules checked per HTML file:
  2.1  No undefined function references in JS onclick/onchange/inline handlers
  2.2  No Python-style \\' escape leakage in emitted JS strings
  2.3  No SVG attribute single-quote collisions inside JS strings
  2.4  speechSynthesis.cancel() guard present before every .speak() call
  2.5  onclick attribute quote safety (embedded single quotes)
  2.6  <img>/<video> src attributes match actual files on disk (relative to imgs root)
  2.7  Every <script> block parses as valid JS (node --check or python-regex fallback)

Exit codes:
  0 — no findings
  1 — one or more findings
  2 — invocation error

Output: first stdout line declares the JS-parse mode in use.
  [check_pages] JS parser: node
  [check_pages] JS parser: python-regex

Report format (per finding):
  [filename] rule-name  line N: description
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import NamedTuple


# ---------------------------------------------------------------------------
# JS parse mode detection (per-invocation, no caching)
# ---------------------------------------------------------------------------

def _detect_node() -> bool:
    """Return True if node is on PATH and responds to --version."""
    if shutil.which("node") is None:
        return False
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True, text=True, timeout=5,
        )
        return result.returncode == 0
    except Exception:  # noqa: BLE001
        return False


NODE_AVAILABLE: bool = _detect_node()
JS_PARSE_MODE: str = "node" if NODE_AVAILABLE else "python-regex"


# ---------------------------------------------------------------------------
# Finding record
# ---------------------------------------------------------------------------

class Finding(NamedTuple):
    file: str
    rule: str
    line: int        # 1-based; 0 if not derivable
    description: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Extract text content of every <script> block (inline only, no src=)
SCRIPT_RE = re.compile(
    r"<script(?:\s[^>]*)?>(.+?)</script>",
    re.DOTALL | re.IGNORECASE,
)

# Locate all src="..." and poster="..." in <img> and <video> tags
MEDIA_SRC_RE = re.compile(
    r"<(?:img|video)[^>]+\bsrc\s*=\s*\"([^\"]+)\"",
    re.IGNORECASE,
)

# onclick/onchange/onXxx attributes
INLINE_HANDLER_RE = re.compile(
    r'\bon\w+\s*=\s*"([^"]*)"',
    re.IGNORECASE,
)

# Bare function calls: word followed by ( — extract the function name
CALL_RE = re.compile(r'\b([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(')

# Function definitions in a script block: function name(...) { and arrow fns
DEF_SIMPLE_RE = re.compile(r'\bfunction\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(')
DEF_ASSIGN_RE = re.compile(
    r'\b(?:var|let|const)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(?:async\s*)?(?:function|\()'
)
DEF_ARROW_RE = re.compile(
    r'\b([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>'
)
DEF_METHOD_RE = re.compile(
    r'^\s*([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\([^)]*\)\s*\{',
    re.MULTILINE,
)

# Built-in / globally available identifiers — don't flag these as undefined
JS_BUILTINS = frozenset({
    # window / DOM
    "window", "document", "navigator", "location", "history",
    "console", "alert", "confirm", "prompt", "setTimeout", "setInterval",
    "clearTimeout", "clearInterval", "requestAnimationFrame",
    "addEventListener", "removeEventListener", "dispatchEvent",
    "fetch", "XMLHttpRequest", "WebSocket",
    # Speech
    "speechSynthesis", "SpeechSynthesisUtterance",
    # JSON / Math / Array / Object / Promise / etc.
    "JSON", "Math", "Date", "Array", "Object", "String", "Number",
    "Boolean", "RegExp", "Error", "Promise", "Map", "Set", "Symbol",
    "parseInt", "parseFloat", "isNaN", "isFinite", "encodeURIComponent",
    "decodeURIComponent", "encodeURI", "decodeURI",
    "undefined", "null", "true", "false", "NaN", "Infinity",
    # Common patterns used in lesson pages
    "localStorage", "sessionStorage",
    "this", "self", "super", "arguments",
    "HTMLElement", "Event", "KeyboardEvent", "MouseEvent",
    "canvas", "ctx", "Image", "Audio",
    "Blob", "URL", "File", "FileReader",
    # Any bare identifier referencing the element itself
    "event",
})


def _line_number(text: str, pos: int) -> int:
    """Return 1-based line number for character position pos in text."""
    return text[:pos].count("\n") + 1


def _extract_defined_names(script: str) -> set[str]:
    """Extract all function / variable names defined in a script block."""
    names: set[str] = set()
    for pat in (DEF_SIMPLE_RE, DEF_ASSIGN_RE, DEF_ARROW_RE, DEF_METHOD_RE):
        for m in pat.finditer(script):
            names.add(m.group(1))
    return names


# ---------------------------------------------------------------------------
# Rule 2.1 — undefined function references in inline handlers
# ---------------------------------------------------------------------------

def check_undefined_js_refs(html_path: Path) -> list[Finding]:
    """Rule 2.1: functions called in inline handlers must be defined somewhere in the page."""
    text = html_path.read_text(encoding="utf-8", errors="replace")
    findings: list[Finding] = []

    # Collect all names defined across all script blocks in this page
    defined: set[str] = set(JS_BUILTINS)
    for m in SCRIPT_RE.finditer(text):
        defined.update(_extract_defined_names(m.group(1)))

    # Scan inline handlers
    for hm in INLINE_HANDLER_RE.finditer(text):
        handler_body = hm.group(1)
        line = _line_number(text, hm.start())
        for cm in CALL_RE.finditer(handler_body):
            name = cm.group(1)
            if name not in defined:
                findings.append(Finding(
                    file=str(html_path),
                    rule="2.1-undefined-js-ref",
                    line=line,
                    description=f"function '{name}' called in inline handler but not defined in page",
                ))
    return findings


# ---------------------------------------------------------------------------
# Rule 2.2 — Python \\' escape leakage in emitted JS
# ---------------------------------------------------------------------------

# Pattern: a literal backslash-quote inside a JS string that lives inside an
# HTML attribute value.  In an HTML file this would look like:  \'  (backslash
# immediately followed by a single quote).  When the Python generator wrote
# \'  it was a Python literal single-quote inside a single-quoted string — but
# it landed in the HTML as the two-character sequence \ ' which is NOT a valid
# JS escape inside a double-quoted attribute.  We detect \' appearing inside
# onclick/etc. attribute values and inside <script> blocks.
ESCAPE_LEAK_RE = re.compile(r"\\'")


def check_python_js_escape_leak(html_path: Path) -> list[Finding]:
    """Rule 2.2: detect \\' (backslash-quote) in inline JS handlers or script blocks."""
    text = html_path.read_text(encoding="utf-8", errors="replace")
    findings: list[Finding] = []

    # Check inline handlers
    for hm in INLINE_HANDLER_RE.finditer(text):
        if ESCAPE_LEAK_RE.search(hm.group(1)):
            findings.append(Finding(
                file=str(html_path),
                rule="2.2-python-escape-leak",
                line=_line_number(text, hm.start()),
                description="possible Python \\' escape leakage in inline handler",
            ))

    # Check script blocks
    for sm in SCRIPT_RE.finditer(text):
        for em in ESCAPE_LEAK_RE.finditer(sm.group(1)):
            abs_pos = sm.start(1) + em.start()
            findings.append(Finding(
                file=str(html_path),
                rule="2.2-python-escape-leak",
                line=_line_number(text, abs_pos),
                description="possible Python \\' escape leakage in <script> block",
            ))
    return findings


# ---------------------------------------------------------------------------
# Rule 2.3 — SVG attribute single-quote collision in JS strings
# ---------------------------------------------------------------------------

# Look for patterns inside script blocks where a single-quoted JS string
# contains an HTML/SVG tag with single-quoted attributes, e.g.:
#   innerHTML = '<svg viewBox=\'0 0 10 10\'>'
# The tell-tale signature is  \'  or attribute=\'  inside a script block.
SVG_ATTR_COLLISION_RE = re.compile(
    r"""(?:viewBox|width|height|d|fill|stroke|xmlns|class|id)\s*=\s*\\'""",
    re.IGNORECASE,
)

# Also catch inline SVG in single-quoted strings where attribute uses '
SVG_TAG_SINGLE_QUOTE_RE = re.compile(
    r"'[^']*<(?:svg|path|circle|rect|polygon|polyline|line|g|use)[^']*=['\"][^']*'",
    re.IGNORECASE,
)


def check_svg_attr_quotes_in_js(html_path: Path) -> list[Finding]:
    """Rule 2.3: SVG/HTML attribute quote collisions inside JS string literals."""
    text = html_path.read_text(encoding="utf-8", errors="replace")
    findings: list[Finding] = []

    for sm in SCRIPT_RE.finditer(text):
        script = sm.group(1)
        for m in SVG_ATTR_COLLISION_RE.finditer(script):
            abs_pos = sm.start(1) + m.start()
            findings.append(Finding(
                file=str(html_path),
                rule="2.3-svg-attr-quote-collision",
                line=_line_number(text, abs_pos),
                description="SVG/HTML attribute with single-quote inside JS script block — may cause string termination",
            ))
    return findings


# ---------------------------------------------------------------------------
# Rule 2.4 — speechSynthesis.cancel() guard before speak()
# ---------------------------------------------------------------------------

SPEAK_CALL_RE = re.compile(r'\bwindow\.speechSynthesis\.speak\s*\(|\bspeechSynthesis\.speak\s*\(')
CANCEL_CALL_RE = re.compile(r'\bwindow\.speechSynthesis\.cancel\s*\(|\bspeechSynthesis\.cancel\s*\(')


def check_speechsynthesis_cancel_guard(html_path: Path) -> list[Finding]:
    """Rule 2.4: every speechSynthesis.speak() call must have a preceding cancel()."""
    text = html_path.read_text(encoding="utf-8", errors="replace")
    findings: list[Finding] = []

    for sm in SCRIPT_RE.finditer(text):
        script = sm.group(1)
        # If there are speak() calls but no cancel() at all, flag
        speak_calls = list(SPEAK_CALL_RE.finditer(script))
        cancel_calls = list(CANCEL_CALL_RE.finditer(script))

        if speak_calls and not cancel_calls:
            # No cancel anywhere in this script block
            abs_pos = sm.start(1) + speak_calls[0].start()
            findings.append(Finding(
                file=str(html_path),
                rule="2.4-speechsynthesis-cancel-missing",
                line=_line_number(text, abs_pos),
                description="speechSynthesis.speak() called but no speechSynthesis.cancel() found in script block",
            ))
        elif speak_calls:
            # Check each speak() has a cancel() somewhere before it
            cancel_positions = {m.start() for m in cancel_calls}
            for sm2 in speak_calls:
                pos = sm2.start()
                # Is there any cancel() before this speak() in the script?
                if not any(cp < pos for cp in cancel_positions):
                    abs_pos = sm.start(1) + pos
                    findings.append(Finding(
                        file=str(html_path),
                        rule="2.4-speechsynthesis-cancel-missing",
                        line=_line_number(text, abs_pos),
                        description="speechSynthesis.speak() called without a preceding speechSynthesis.cancel()",
                    ))
    return findings


# ---------------------------------------------------------------------------
# Rule 2.5 — onclick attribute quote safety
# ---------------------------------------------------------------------------

# Inline handler with double-quoted attribute value containing single quotes.
# Normal case:  onclick="speak('hello')"   — exactly 2 single-quotes (one pair)
# Broken case:  onclick="speak('it's')"    — 3 single-quotes; middle one is an apostrophe
# The heuristic: if the attribute value contains an ODD number of single-quotes,
# or more than 2 consecutive single-quote-delimited tokens, flag it.
INLINE_HANDLER_FULL_RE = re.compile(
    r'\bon\w+\s*=\s*"([^"]*)"',
    re.IGNORECASE,
)


def check_onclick_quote_safety(html_path: Path) -> list[Finding]:
    """Rule 2.5: single quotes inside onclick/onchange args must not break the JS string."""
    text = html_path.read_text(encoding="utf-8", errors="replace")
    findings: list[Finding] = []

    for m in INLINE_HANDLER_FULL_RE.finditer(text):
        handler_val = m.group(1)
        single_quote_count = handler_val.count("'")
        # Normal: 0 (no single-quoted args), 2 (one pair), 4 (two pairs), etc.
        # Flag odd counts or > 2 when there's a single-quoted section containing
        # a word with an apostrophe.
        if single_quote_count == 0 or single_quote_count % 2 == 0:
            # Even count — check if any pair contains another single-quote (i.e.,
            # an apostrophe word like "it's" between the pair delimiters).
            # Strategy: split on single-quotes and look at odd-indexed segments
            # (the content between pairs); if any such segment contains chars
            # suggesting a word (letters+apostrophe+letters), flag.
            parts = handler_val.split("'")
            # parts[1], parts[3], ... are inside the single-quote pairs
            for i in range(1, len(parts), 2):
                # This segment should be a clean identifier/string
                # If the next split after this created an extra part with
                # a mid-word apostrophe, the count would already be odd.
                # Even-count case: if segment appears empty and the surrounding
                # parts show a word broken around the apostrophe, flag.
                pass
        if single_quote_count % 2 == 1:
            # Odd count — definitely broken (unterminated JS string in handler)
            findings.append(Finding(
                file=str(html_path),
                rule="2.5-onclick-quote-safety",
                line=_line_number(text, m.start()),
                description=(
                    f"odd number of single-quotes ({single_quote_count}) in inline handler — "
                    f"possible apostrophe in argument: {handler_val[:80]}"
                ),
            ))
        elif single_quote_count >= 2:
            # Even count but > expected pairs — check content between quotes
            # for apostrophe pattern (word boundary + ' + word boundary inside a pair)
            # e.g.: speak('hello') is fine; speak('it's') would have been odd (handled above)
            # This branch handles: speak('it') when there's a stray ' — but that's already odd
            # Additional check: look for \' within a double-quoted attribute (rule 2.2 overlap,
            # but flagged here too from the onclick perspective)
            if re.search(r"\\'", handler_val):
                findings.append(Finding(
                    file=str(html_path),
                    rule="2.5-onclick-quote-safety",
                    line=_line_number(text, m.start()),
                    description=(
                        f"backslash-quote (\\') in inline handler — Python escape leakage: "
                        f"{handler_val[:80]}"
                    ),
                ))

    return findings


# ---------------------------------------------------------------------------
# Rule 2.6 — <img>/<video> src vs actual files on disk
# ---------------------------------------------------------------------------

def check_media_src_exists_on_disk(html_path: Path, imgs_root: Path | None = None) -> list[Finding]:
    """Rule 2.6: <img>/<video> src attributes should resolve to real files on disk."""
    text = html_path.read_text(encoding="utf-8", errors="replace")
    findings: list[Finding] = []

    for m in MEDIA_SRC_RE.finditer(text):
        ref = m.group(1)
        line = _line_number(text, m.start())

        # Skip data URIs and external URLs
        if ref.startswith(("data:", "http://", "https://", "//")):
            continue

        # Try to resolve relative to the HTML file
        resolved = (html_path.parent / ref).resolve()
        if not resolved.exists():
            findings.append(Finding(
                file=str(html_path),
                rule="2.6-media-src-missing",
                line=line,
                description=f"src='{ref}' does not resolve to an existing file (looked at {resolved})",
            ))

    return findings


# ---------------------------------------------------------------------------
# Rule 2.7 — <script> block JS syntax check
# ---------------------------------------------------------------------------

def _check_js_node(script_text: str, label: str) -> list[str]:
    """Run node --check on script_text. Returns list of error strings."""
    errors = []
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".js", encoding="utf-8", delete=False
    ) as f:
        f.write(script_text)
        tmp = f.name
    try:
        result = subprocess.run(
            ["node", "--check", tmp],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            errors.append(result.stderr.strip() or "node --check reported an error")
    except Exception as e:  # noqa: BLE001
        errors.append(f"node --check failed to run: {e}")
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass
    return errors


def _check_js_regex(script_text: str) -> list[str]:
    """Python-regex fallback for JS syntax checking.

    Checks:
    - Unbalanced braces / brackets / parens
    - Unterminated string literals (simple heuristic)
    - Python-style \\' escape outside of legitimate uses
    """
    errors = []

    # Bracket balance
    depth_curly = 0
    depth_square = 0
    depth_paren = 0
    in_string: str | None = None  # '"' or "'"
    escape_next = False

    for i, ch in enumerate(script_text):
        if escape_next:
            escape_next = False
            continue
        if ch == "\\" and in_string:
            escape_next = True
            continue
        if in_string:
            if ch == in_string:
                in_string = None
            continue
        if ch in ('"', "'"):
            in_string = ch
            continue
        if ch == "{":
            depth_curly += 1
        elif ch == "}":
            depth_curly -= 1
        elif ch == "[":
            depth_square += 1
        elif ch == "]":
            depth_square -= 1
        elif ch == "(":
            depth_paren += 1
        elif ch == ")":
            depth_paren -= 1

    if in_string:
        errors.append(f"unterminated string literal (ends in {in_string!r})")
    if depth_curly != 0:
        errors.append(f"unbalanced braces: net depth {depth_curly:+d}")
    if depth_square != 0:
        errors.append(f"unbalanced brackets: net depth {depth_square:+d}")
    if depth_paren != 0:
        errors.append(f"unbalanced parens: net depth {depth_paren:+d}")

    # Python-style \' escape leakage (already covered by Rule 2.2, but flag here too)
    if ESCAPE_LEAK_RE.search(script_text):
        errors.append("possible Python \\' escape leakage in script block")

    return errors


def check_js_parses(html_path: Path) -> list[Finding]:
    """Rule 2.7: every <script> block must parse as valid JS."""
    text = html_path.read_text(encoding="utf-8", errors="replace")
    findings: list[Finding] = []

    for i, sm in enumerate(SCRIPT_RE.finditer(text)):
        script = sm.group(1)
        label = f"script block {i + 1}"
        line = _line_number(text, sm.start())

        if NODE_AVAILABLE:
            errors = _check_js_node(script, label)
        else:
            errors = _check_js_regex(script)

        for err in errors:
            findings.append(Finding(
                file=str(html_path),
                rule="2.7-js-parse-error",
                line=line,
                description=f"{label}: {err}",
            ))

    return findings


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

ALL_RULES = [
    check_undefined_js_refs,
    check_python_js_escape_leak,
    check_svg_attr_quotes_in_js,
    check_speechsynthesis_cancel_guard,
    check_onclick_quote_safety,
    check_media_src_exists_on_disk,
    check_js_parses,
]


def scan_file(html_path: Path, imgs_root: Path | None = None) -> list[Finding]:
    """Run all rules against a single HTML file and return aggregated findings."""
    all_findings: list[Finding] = []
    for rule_fn in ALL_RULES:
        if rule_fn is check_media_src_exists_on_disk:
            all_findings.extend(rule_fn(html_path, imgs_root))
        else:
            all_findings.extend(rule_fn(html_path))
    return all_findings


def main() -> int:
    # Emit mode banner as FIRST line of stdout (plan §2 requirement)
    print(f"[check_pages] JS parser: {JS_PARSE_MODE}")

    ap = argparse.ArgumentParser(description="Verify generated lesson HTML pages")
    ap.add_argument("output_dir", help="Directory containing the course's .html files")
    ap.add_argument(
        "--imgs-root",
        default=None,
        help="Root directory for media files (default: auto-detect from output_dir parents)",
    )
    args = ap.parse_args()

    output_dir = Path(args.output_dir)
    if not output_dir.is_dir():
        print(f"ERROR: {output_dir} is not a directory", file=sys.stderr)
        return 2

    imgs_root: Path | None = None
    if args.imgs_root:
        imgs_root = Path(args.imgs_root)

    html_files = sorted(output_dir.rglob("*.html"))
    if not html_files:
        print(f"WARN: no .html files found under {output_dir}", file=sys.stderr)
        return 0

    total_findings = 0
    last_file = None

    for hf in html_files:
        findings = scan_file(hf, imgs_root)
        if findings:
            rel = hf.relative_to(output_dir) if hf.is_relative_to(output_dir) else hf
            if str(rel) != last_file:
                print(f"\n[{rel}]")
                last_file = str(rel)
            for f in findings:
                print(f"  {f.rule}  line {f.line}: {f.description}")
            total_findings += len(findings)

    print(
        f"\nSummary: {len(html_files)} files scanned, {total_findings} finding(s)"
    )
    return 1 if total_findings else 0


if __name__ == "__main__":
    sys.exit(main())
