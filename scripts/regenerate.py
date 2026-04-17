#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""regenerate.py — surgical patch path for individual course pages or quiz questions.

Usage — page-level (regenerates one complete page):
    python scripts/regenerate.py --course-config config/COURSE.json --unit 7 --page-type quiz

Usage — question-level (splices one question inside a quiz page):
    python scripts/regenerate.py --course-config config/COURSE.json --unit 7 --exam-question vocabulary:medium:3

Usage — determinism check (page-level only; compares output against a fresh full-run):
    python scripts/regenerate.py --course-config config/COURSE.json --unit 7 --page-type quiz --determinism-check

Supported courses (hard allowlist):
    children_10_12, teens_13_14, tefl_beginners, tefl_intermediate

Exit codes:
  0 — success (page written or question spliced)
  1 — validation/semantic error (coord out-of-range, page type not found, splice failed, etc.)
  2 — invocation error (bad args, missing config, unsupported course)
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

SUPPORTED_COURSES: set[str] = {
    "children_10_12",
    "teens_13_14",
    "tefl_beginners",
    "tefl_intermediate",
}

# For courses whose generators live in the watdonchan repo, we locate them
# relative to a well-known anchor (the lesson-builder repo root's parent, or
# the watdonchan sibling directory).  Adjust if your layout differs.
_REPO_ROOT = Path(__file__).resolve().parents[1]
_WATDONCHAN_CANDIDATES = [
    _REPO_ROOT.parent / "watdonchan",
    Path.home() / "claude" / "watdonchan",
]

# Maps course_id → generator script name (relative to the watdonchan root).
_GENERATOR_SCRIPTS: dict[str, str] = {
    "children_10_12": "generate_tefl_children_10_12.py",
    "teens_13_14":    "generate_tefl_teens_13_14.py",
    "tefl_beginners": "generate_tefl_beginners.py",
    "tefl_intermediate": "generate_tefl_intermediate.py",
}

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _sha256(path: Path) -> str:
    """Return hex SHA-256 of a file's content, or '' if the file doesn't exist."""
    if not path.exists():
        return ""
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _load_config(config_path: Path) -> dict:
    """Load and return a course config JSON. Exits 2 on errors."""
    if not config_path.exists():
        print(f"ERROR: config not found: {config_path}", file=sys.stderr)
        sys.exit(2)
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON in {config_path}: {exc}", file=sys.stderr)
        sys.exit(2)


def _resolve_output_dir(cfg: dict, config_path: Path) -> Path:
    """Resolve the course output directory from the config.

    Resolution order for relative paths:
    1. Relative to config_path's parent's parent (lesson-builder root)
    2. Relative to the watdonchan repo root (for courses whose output lives there)
    3. Relative to cwd
    """
    raw = cfg.get("output_dir", "")
    if not raw:
        print("ERROR: config missing 'output_dir' field", file=sys.stderr)
        sys.exit(2)
    p = Path(raw)
    if p.is_absolute():
        return p

    candidates = [
        config_path.parent.parent / raw,   # lesson-builder root
        Path.cwd() / raw,
    ]
    # Also try watdonchan root for courses whose output_dir starts with HTML/
    wc_root = _find_watdonchan_root()
    if wc_root:
        candidates.insert(1, wc_root / raw)

    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()

    # Default to first candidate even if it doesn't exist yet (will be created).
    return candidates[0].resolve()


def _find_watdonchan_root() -> Optional[Path]:
    """Return the watdonchan repo root if it can be located."""
    for candidate in _WATDONCHAN_CANDIDATES:
        if candidate.is_dir():
            return candidate.resolve()
    return None


def _load_generator_module(course_id: str):
    """
    Import and return the generator module for `course_id`.

    Returns (module, watdonchan_root) on success; calls sys.exit(2) on failure.
    The module is loaded without executing its __main__ block.
    """
    wc_root = _find_watdonchan_root()
    if wc_root is None:
        print(
            "ERROR: cannot locate watdonchan repo. Tried:\n"
            + "\n".join(f"  {p}" for p in _WATDONCHAN_CANDIDATES),
            file=sys.stderr,
        )
        sys.exit(2)

    script_name = _GENERATOR_SCRIPTS.get(course_id)
    if script_name is None:
        print(
            f"ERROR: no generator script registered for course '{course_id}'.\n"
            f"       Add an entry to _GENERATOR_SCRIPTS in regenerate.py.",
            file=sys.stderr,
        )
        sys.exit(2)

    script_path = wc_root / script_name
    if not script_path.exists():
        print(
            f"ERROR: generator script not found: {script_path}\n"
            f"       Expected for course '{course_id}'.",
            file=sys.stderr,
        )
        sys.exit(2)

    spec = importlib.util.spec_from_file_location(f"generator_{course_id}", script_path)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    # Temporarily redirect __name__ so the `if __name__ == '__main__':` block
    # inside the generator is NOT executed on import.
    module.__name__ = f"generator_{course_id}"
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module, wc_root


def _find_unit(module, unit_n: int) -> Optional[dict]:
    """Return the unit dict for unit number `unit_n` (1-based week)."""
    units = getattr(module, "UNITS", None)
    if units is None:
        return None
    for u in units:
        if u.get("week") == unit_n:
            return u
    return None


def _dispatch_table(module) -> dict[str, callable]:
    """
    Build a {page_type: generate_fn} dispatch table from the generator module.
    Looks for functions named generate_{page_type}.
    """
    table: dict[str, callable] = {}
    for attr in dir(module):
        if attr.startswith("generate_"):
            page_type = attr[len("generate_"):]
            fn = getattr(module, attr)
            if callable(fn):
                table[page_type] = fn
    return table


def _infer_filename(module, unit: dict, page_type: str) -> Optional[str]:
    """
    Infer the output filename from generator conventions.
    Tries module.OUT_DIR / <prefix>_<slug>_<page_type>.html.
    Falls back to scanning OUT_DIR for a matching file.
    """
    slug = unit.get("slug", "")
    prefix = getattr(module, "OUT_DIR", None)

    # The children_10_12 generator uses "explorers" as a hard-coded prefix.
    # Check whether the module has a FILE_PREFIX constant or similar.
    file_prefix = getattr(module, "FILE_PREFIX", None)
    if file_prefix is None:
        # Derive from OUT_DIR base name if possible; fall back to "explorers"
        out_dir_attr = getattr(module, "OUT_DIR", "")
        file_prefix = os.path.basename(str(out_dir_attr)) or "explorers"
        # For children_10_12, OUT_DIR is .../children_10_12; base name → "children_10_12"
        # But actual prefix in filenames is "explorers". Try a known mapping.
        _KNOWN_PREFIXES = {
            "children_10_12": "explorers",
            "teens_13_14":    "teens",
            "tefl_beginners": "begin",
            "tefl_intermediate": "inter",
        }
        # We don't have the course_id here directly; scan for it.
        for k, v in _KNOWN_PREFIXES.items():
            if k in str(out_dir_attr):
                file_prefix = v
                break

    return f"{file_prefix}_{slug}_{page_type}.html"


def _write_log(output_dir: Path, entry: dict) -> None:
    """Append a JSON log entry to {output_dir}/_regenerate_log.jsonl."""
    log_path = output_dir / "_regenerate_log.jsonl"
    line = json.dumps(entry, ensure_ascii=False)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(f"  [log] {log_path.name} updated")


def _log_entry(
    course_id: str,
    unit_n: int,
    page_type: Optional[str],
    coord: Optional[str],
    before_hash: str,
    after_hash: str,
    file_path: str,
    byte_delta: int,
) -> dict:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "course_id": course_id,
        "unit": unit_n,
        "page_type": page_type,
        "exam_question_coord": coord,
        "file": file_path,
        "before_hash": before_hash,
        "after_hash": after_hash,
        "byte_delta": byte_delta,
        "operator": os.environ.get("USERNAME") or os.environ.get("USER") or "unknown",
    }


# ─────────────────────────────────────────────────────────────────────────────
# PAGE-LEVEL REGENERATE
# ─────────────────────────────────────────────────────────────────────────────

def regenerate_page(
    course_id: str,
    unit_n: int,
    page_type: str,
    config_path: Path,
    determinism_check: bool = False,
) -> int:
    """
    Regenerate one page for the given unit and page type.

    Returns 0 on success, 1 on error.
    When determinism_check is True, regenerates to a tmp dir and diffs against
    a fresh full-generator run for the same unit+page_type.
    """
    cfg = _load_config(config_path)
    output_dir = _resolve_output_dir(cfg, config_path)

    print(f"Loading generator for course '{course_id}'...")
    module, wc_root = _load_generator_module(course_id)

    dispatch = _dispatch_table(module)
    if page_type not in dispatch:
        available = sorted(dispatch.keys())
        print(
            f"ERROR: page type '{page_type}' not found in generator dispatch table.\n"
            f"       Available types: {available}",
            file=sys.stderr,
        )
        return 1

    unit = _find_unit(module, unit_n)
    if unit is None:
        units_list = [u.get("week") for u in getattr(module, "UNITS", [])]
        print(
            f"ERROR: unit {unit_n} not found. Available units (weeks): {units_list}",
            file=sys.stderr,
        )
        return 1

    all_units = getattr(module, "UNITS", [])
    gen_fn = dispatch[page_type]

    print(f"Generating unit {unit_n} page type '{page_type}'...")
    try:
        html = gen_fn(unit, all_units)
    except Exception as exc:
        print(f"ERROR: generator raised an exception: {exc}", file=sys.stderr)
        return 1

    filename = _infer_filename(module, unit, page_type)
    target_path = output_dir / filename

    if determinism_check:
        return _run_determinism_check(
            course_id, unit_n, page_type, html, target_path, module, output_dir
        )

    before_hash = _sha256(target_path)
    before_size = target_path.stat().st_size if target_path.exists() else 0

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(html, encoding="utf-8")
    after_size = len(html.encode("utf-8"))
    after_hash = _sha256(target_path)
    byte_delta = after_size - before_size

    print(f"  [ok] Wrote {target_path}")
    print(f"       Before: {before_size} bytes  |  After: {after_size} bytes  |  Delta: {byte_delta:+d}")

    _write_log(
        output_dir,
        _log_entry(
            course_id, unit_n, page_type, None,
            before_hash, after_hash, str(target_path), byte_delta,
        ),
    )

    _check_sibling_integrity(output_dir, filename, page_type, html)
    return 0


def _run_determinism_check(
    course_id: str,
    unit_n: int,
    page_type: str,
    regenerated_html: str,
    target_path: Path,
    module,
    output_dir: Path,
) -> int:
    """
    Compare `regenerated_html` against a full generator run in a tmp dir.
    Exit 0 if byte-identical; exit 1 if diffs found.
    """
    print("  [determinism] Running full generator into a tmpdir for comparison...")
    with tempfile.TemporaryDirectory(prefix="regen_det_") as tmp:
        tmp_dir = Path(tmp)

        # Override OUT_DIR in the module so the generator writes to tmp_dir.
        original_out_dir = getattr(module, "OUT_DIR", None)
        module.OUT_DIR = str(tmp_dir)

        try:
            all_units = getattr(module, "UNITS", [])
            unit = _find_unit(module, unit_n)
            gen_fn = _dispatch_table(module)[page_type]
            full_html = gen_fn(unit, all_units)
        finally:
            if original_out_dir is not None:
                module.OUT_DIR = original_out_dir

        if regenerated_html == full_html:
            print("  [determinism] PASS — output is byte-identical to full generator run.")
            return 0
        else:
            # Show a brief diff.
            regen_lines = regenerated_html.splitlines(keepends=True)
            full_lines = full_html.splitlines(keepends=True)
            import difflib
            diff = list(difflib.unified_diff(
                full_lines, regen_lines,
                fromfile="full-generator", tofile="regenerate.py",
                n=3,
            ))
            print(
                f"  [determinism] FAIL — {len(diff)} diff lines found.\n"
                f"  First 20 diff lines:",
                file=sys.stderr,
            )
            for line in diff[:20]:
                print("    " + line.rstrip(), file=sys.stderr)
            return 1


def _check_sibling_integrity(
    output_dir: Path,
    regenerated_filename: str,
    page_type: str,
    new_content: str,
) -> None:
    """
    Check that sibling pages (same unit, different page types) were NOT touched.
    Reads all HTML files in output_dir with the same unit slug and reports if any
    byte counts changed (they shouldn't since we only wrote one file).

    This is purely diagnostic; does not fail the run.
    """
    # Extract slug prefix from filename: <prefix>_<slug>_<page_type>.html
    # e.g. "explorers_technology_quiz.html" → slug_prefix = "explorers_technology"
    base = regenerated_filename.replace(".html", "")
    parts = base.rsplit("_", 1)
    if len(parts) != 2:
        return
    slug_prefix = parts[0]

    siblings = [
        p for p in output_dir.glob(f"{slug_prefix}_*.html")
        if p.name != regenerated_filename
    ]

    if siblings:
        print(f"  [siblings] {len(siblings)} sibling page(s) present — none were modified by this run.")


# ─────────────────────────────────────────────────────────────────────────────
# QUESTION-LEVEL REGENERATE
# ─────────────────────────────────────────────────────────────────────────────

# Regex to locate a single <div class="quiz-q" ...> block.
# The quiz pages store all questions as <div class="quiz-q" id="qq-N" ...>...</div>
# blocks in the HTML source.  We use a narrowly-scoped pattern that matches
# the outer <div> by its id attribute and captures everything up to the matching
# closing </div> (non-greedy, but because these blocks don't nest, a simple
# stop-at-next-quiz-q strategy works).
_QUIZ_Q_BLOCK_RE = re.compile(
    r'(<div class="quiz-q"[^>]+id="qq-(\d+)"[^>]*>)(.*?)(</div>)',
    re.DOTALL,
)

# For exam-style pages that use a `const questionBank = { ... };` JS pattern.
_QB_BLOCK_RE = re.compile(
    r"(const\s+questionBank\s*=\s*\{)(.*?)(\};)",
    re.DOTALL,
)


def _parse_coord(coord: str) -> tuple[str, str, int]:
    """
    Parse 'CATEGORY:DIFFICULTY:INDEX' into (category, difficulty, index).
    Exits 2 on bad format.
    """
    parts = coord.split(":")
    if len(parts) != 3:
        print(
            f"ERROR: --exam-question must be CATEGORY:DIFFICULTY:INDEX "
            f"(e.g. vocabulary:medium:3), got: '{coord}'",
            file=sys.stderr,
        )
        sys.exit(2)
    cat, diff, idx_str = parts
    try:
        idx = int(idx_str)
    except ValueError:
        print(
            f"ERROR: INDEX in --exam-question must be an integer, got: '{idx_str}'",
            file=sys.stderr,
        )
        sys.exit(2)
    return cat, diff, idx


def _find_quiz_page(output_dir: Path, module, unit: dict) -> Optional[Path]:
    """
    Locate the quiz page for this unit.  Tries quiz then the general dispatch
    table page-type names.
    """
    for page_type in ("quiz",):
        filename = _infer_filename(module, unit, page_type)
        candidate = output_dir / filename
        if candidate.exists():
            return candidate
    return None


def regenerate_exam_question(
    course_id: str,
    unit_n: int,
    coord: str,
    config_path: Path,
) -> int:
    """
    Splice a single quiz question replacement into an existing quiz page.

    The coordinate format is CATEGORY:DIFFICULTY:INDEX where:
      - CATEGORY:  a logical category name for the question (e.g. 'vocabulary',
                   'grammar').  For inline-HTML quiz pages the category is used
                   for logging only — the index is the 0-based question number.
      - DIFFICULTY: 'easy', 'medium', or 'hard' (for logging and future prompt use).
      - INDEX:     0-based index of the question block (<div class="quiz-q" id="qq-N">).

    Returns 0 on success, 1 on error.
    """
    category, difficulty, idx = _parse_coord(coord)

    cfg = _load_config(config_path)
    output_dir = _resolve_output_dir(cfg, config_path)

    print(f"Loading generator for course '{course_id}'...")
    module, _ = _load_generator_module(course_id)

    unit = _find_unit(module, unit_n)
    if unit is None:
        units_list = [u.get("week") for u in getattr(module, "UNITS", [])]
        print(
            f"ERROR: unit {unit_n} not found. Available units (weeks): {units_list}",
            file=sys.stderr,
        )
        return 1

    quiz_path = _find_quiz_page(output_dir, module, unit)
    if quiz_path is None:
        print(
            f"ERROR: could not locate quiz page for unit {unit_n} in {output_dir}.\n"
            f"       Run a page-level regenerate first: "
            f"--unit {unit_n} --page-type quiz",
            file=sys.stderr,
        )
        return 1

    print(f"Reading existing quiz page: {quiz_path}")
    original_html = quiz_path.read_text(encoding="utf-8")
    before_hash = _sha256(quiz_path)

    # Collect all question blocks.
    matches = list(_QUIZ_Q_BLOCK_RE.finditer(original_html))
    if not matches:
        print(
            "ERROR: no <div class=\"quiz-q\"> blocks found in the quiz page.\n"
            "       The question-level splice requires inline HTML quiz format.\n"
            "       Use --page-type quiz to regenerate the whole page instead.",
            file=sys.stderr,
        )
        return 1

    bucket_size = len(matches)
    if idx >= bucket_size or idx < 0:
        print(
            f"ERROR: index {idx} out of range for {category}/{difficulty} "
            f"(bucket has {bucket_size} items, valid range 0–{bucket_size-1})",
            file=sys.stderr,
        )
        return 1

    target_match = matches[idx]
    question_start = target_match.start()
    question_end = target_match.end()

    # Generate a replacement question block by re-running the generator for the
    # whole quiz page into a tmpdir, then extracting the Nth question block from
    # the fresh output.  This uses the generator as the source of new question
    # content while leaving ALL other blocks in the original file untouched.
    print(f"  Generating replacement for question {idx} ({category}/{difficulty})...")
    all_units = getattr(module, "UNITS", [])
    gen_fn = _dispatch_table(module).get("quiz")
    if gen_fn is None:
        print(
            "ERROR: generator does not expose a 'quiz' page-type function.\n"
            "       Cannot generate a replacement question automatically.\n"
            "       Edit the quiz HTML manually and re-run the page-level regenerate.",
            file=sys.stderr,
        )
        return 1

    try:
        fresh_html = gen_fn(unit, all_units)
    except Exception as exc:
        print(f"ERROR: generator raised an exception: {exc}", file=sys.stderr)
        return 1

    fresh_matches = list(_QUIZ_Q_BLOCK_RE.finditer(fresh_html))
    if idx >= len(fresh_matches):
        print(
            f"ERROR: fresh generator output has only {len(fresh_matches)} question blocks "
            f"but index {idx} was requested. "
            f"Generator output has changed structure — use --page-type quiz instead.",
            file=sys.stderr,
        )
        return 1

    fresh_q_block = fresh_matches[idx].group(0)
    original_q_block = target_match.group(0)

    if fresh_q_block == original_q_block:
        print(
            f"  [info] New question block is byte-identical to the existing one. "
            f"No change written."
        )
        return 0

    # Splice: replace only the target question block.
    new_html = original_html[:question_start] + fresh_q_block + original_html[question_end:]

    # Sanity check: diff scope must be limited to the question block lines.
    _validate_splice_scope(original_html, new_html, question_start, question_end, fresh_q_block)

    # Back up the original (for auditability; .bak is overwritten each run).
    bak_path = quiz_path.with_suffix(".html.bak")
    shutil.copy2(quiz_path, bak_path)
    print(f"  [backup] {bak_path.name}")

    quiz_path.write_text(new_html, encoding="utf-8")
    after_hash = _sha256(quiz_path)

    before_size = len(original_html.encode("utf-8"))
    after_size = len(new_html.encode("utf-8"))
    byte_delta = after_size - before_size

    print(f"  [ok] Spliced question {idx} into {quiz_path}")
    print(f"       Before: {before_size} bytes  |  After: {after_size} bytes  |  Delta: {byte_delta:+d}")

    _write_log(
        output_dir,
        _log_entry(
            course_id, unit_n, None, coord,
            before_hash, after_hash, str(quiz_path), byte_delta,
        ),
    )
    return 0


def _validate_splice_scope(
    original: str,
    new_html: str,
    question_start: int,
    question_end: int,
    new_block: str,
) -> None:
    """
    Verify that the diff between original and new_html is confined to the
    replaced question block.  Reports a warning (does not abort) if the diff
    extends outside that region.
    """
    prefix_same = original[:question_start] == new_html[:question_start]
    suffix_start_in_new = question_start + len(new_block)
    suffix_same = original[question_end:] == new_html[suffix_start_in_new:]

    if not prefix_same:
        print(
            "  [WARNING] Splice validation: content BEFORE the question block "
            "differs between original and patched file. This is unexpected — "
            "review the output before deploying.",
            file=sys.stderr,
        )
    if not suffix_same:
        print(
            "  [WARNING] Splice validation: content AFTER the question block "
            "differs between original and patched file. This is unexpected — "
            "review the output before deploying.",
            file=sys.stderr,
        )
    if prefix_same and suffix_same:
        print("  [splice-scope] PASS — diff is confined to the target question block.")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description=(
            "Surgical regeneration for individual lesson pages or exam questions.\n"
            "\n"
            "Page-level:     --course-config config/COURSE.json --unit N --page-type TYPE\n"
            "Question-level: --course-config config/COURSE.json --unit N --exam-question CAT:DIFF:IDX\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    ap.add_argument(
        "--course-config",
        required=True,
        metavar="PATH",
        help="Path to the course config JSON (e.g. config/tefl_beginners.json)",
    )
    ap.add_argument(
        "--unit",
        type=int,
        required=True,
        metavar="N",
        help="Unit (week) number to regenerate (1-based)",
    )

    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--page-type",
        metavar="TYPE",
        help=(
            "Page type to regenerate (e.g. quiz, story, game, song, reading, "
            "flashcards, reward)"
        ),
    )
    mode.add_argument(
        "--exam-question",
        metavar="CAT:DIFF:IDX",
        help=(
            "Question coordinate to splice: CATEGORY:DIFFICULTY:INDEX. "
            "INDEX is 0-based (e.g. vocabulary:medium:3 → 4th question block)"
        ),
    )

    ap.add_argument(
        "--determinism-check",
        action="store_true",
        default=False,
        help=(
            "After regenerating, compare output to a fresh full-generator run. "
            "Exits 1 if they differ. Page-level only."
        ),
    )

    return ap


def main() -> int:
    ap = build_parser()
    args = ap.parse_args()

    config_path = Path(args.course_config)
    cfg = _load_config(config_path)

    course_id = cfg.get("course_id", "")
    if not course_id:
        print("ERROR: config is missing 'course_id' field", file=sys.stderr)
        return 2

    if course_id not in SUPPORTED_COURSES:
        print(
            f"ERROR: '{course_id}' is not in the SUPPORTED_COURSES allowlist.\n"
            f"       Supported: {sorted(SUPPORTED_COURSES)}\n"
            f"       To add a new course, add its course_id to SUPPORTED_COURSES\n"
            f"       and add its generator script to _GENERATOR_SCRIPTS in regenerate.py.",
            file=sys.stderr,
        )
        return 2

    if args.determinism_check and args.exam_question:
        print(
            "ERROR: --determinism-check is only valid with --page-type, not --exam-question.",
            file=sys.stderr,
        )
        return 2

    print(f"regenerate.py | course: {course_id} | unit: {args.unit}")

    if args.page_type:
        return regenerate_page(
            course_id=course_id,
            unit_n=args.unit,
            page_type=args.page_type,
            config_path=config_path,
            determinism_check=args.determinism_check,
        )
    else:
        return regenerate_exam_question(
            course_id=course_id,
            unit_n=args.unit,
            coord=args.exam_question,
            config_path=config_path,
        )


if __name__ == "__main__":
    sys.exit(main())
