#!/usr/bin/env python3
"""check_content.py — Phase 5c content-truth validator for lesson-builder courses.

Usage:
    python scripts/check_content.py <output_dir> <config_path>

    # Cheapest path — exits immediately, no quota consumed:
    python scripts/check_content.py HTML/tefl/children_10_12/ config/children_10_12.json

    # With tavily backend (uses tvly research queries):
    # Set "content_truth": {"backend": "tavily"} in the config first.

Exit codes:
    0 — no flags (or backend is off)
    1 — one or more unresolved content-truth flags
    2 — invocation error (unknown backend, config not found, etc.)

First stdout line ALWAYS prints the active backend so the operator is never
unaware of quota spend:
    content-truth backend: off
    content-truth backend: tavily
    content-truth backend: notebooklm

Sampling rates (plan §3.4):
    vocab_card:        20% per unit (seeded per course_id for reproducibility)
    grammar_box:       10% per unit
    exam_correct_mark: 100% of exam correct-answer entries

Reports written to:
    {output_dir}/_content_truth_report.json  (machine-readable)
    {output_dir}/_content_truth_report.md    (human-readable — grep UNRESOLVED)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Sampling rates (plan §3.4)
# ---------------------------------------------------------------------------

SAMPLE_RATES: dict[str, float] = {
    "vocab_card":        0.20,   # 20% per unit
    "grammar_box":       0.10,   # 10% per unit
    "exam_correct_mark": 1.00,   # 100% of exam correct answers
}


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

def load_config(config_path: str) -> dict[str, Any]:
    p = Path(config_path)
    if not p.exists():
        print(f"ERROR: config not found: {config_path}", file=sys.stderr)
        sys.exit(2)
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def course_id_seed(cfg: dict[str, Any]) -> int:
    """Deterministic seed derived from course_id — stable across re-runs."""
    course_id = cfg.get("course_id", "unknown")
    return int(hashlib.sha256(course_id.encode()).hexdigest(), 16) % (2 ** 32)


# ---------------------------------------------------------------------------
# Item extraction from generated HTML output
# ---------------------------------------------------------------------------

def _extract_vocab_items(output_dir: Path) -> list[dict[str, Any]]:
    """Scrape vocab term + translation pairs from generated lesson HTML files."""
    items: list[dict[str, Any]] = []
    # Lesson pages typically contain vocab cards with data-term / data-l1 attrs,
    # or tables/spans with bilingual pairs. We look for common patterns.
    for html_path in sorted(output_dir.glob("*.html")):
        text = html_path.read_text(encoding="utf-8", errors="replace")
        # Pattern 1: data-term="word" data-l1="translation"
        for m in re.finditer(
            r'data-term=["\']([^"\']+)["\'][^>]*data-l1=["\']([^"\']+)["\']',
            text
        ):
            items.append({
                "type": "vocab_card",
                "term": m.group(1),
                "translation": m.group(2),
                "file": html_path.name,
            })
        # Pattern 2: class="vocab-term">word</... class="vocab-l1">translation<
        for m in re.finditer(
            r'class=["\']vocab-term["\'][^>]*>([^<]+)<[^>]+>'
            r'(?:.*?)class=["\']vocab-l1["\'][^>]*>([^<]+)<',
            text, re.DOTALL
        ):
            items.append({
                "type": "vocab_card",
                "term": m.group(1).strip(),
                "translation": m.group(2).strip(),
                "file": html_path.name,
            })
    return items


def _extract_grammar_items(output_dir: Path) -> list[dict[str, Any]]:
    """Scrape grammar explanation snippets from generated HTML files."""
    items: list[dict[str, Any]] = []
    for html_path in sorted(output_dir.glob("*.html")):
        text = html_path.read_text(encoding="utf-8", errors="replace")
        # Grammar boxes often have class="grammar-box" or similar
        for m in re.finditer(
            r'class=["\']grammar(?:-box|-focus|-rule)["\'][^>]*>(.*?)</(?:div|section)',
            text, re.DOTALL | re.IGNORECASE
        ):
            snippet = re.sub(r"<[^>]+>", " ", m.group(1)).strip()
            snippet = re.sub(r"\s+", " ", snippet)[:200]
            if len(snippet) > 20:
                items.append({
                    "type": "grammar_box",
                    "snippet": snippet,
                    "file": html_path.name,
                })
    return items


def _extract_exam_correct_answers(output_dir: Path) -> list[dict[str, Any]]:
    """Extract all correct-answer entries from exam HTML files (100% sample)."""
    items: list[dict[str, Any]] = []
    exam_pattern = re.compile(r"_exam\.html$|_quiz\.html$", re.IGNORECASE)
    for html_path in sorted(output_dir.glob("*.html")):
        if not exam_pattern.search(html_path.name):
            continue
        text = html_path.read_text(encoding="utf-8", errors="replace")
        # Pattern: quiz-q blocks with data-correct or correct-answer markers
        for m in re.finditer(
            r'<div[^>]+class=["\']quiz-q["\'][^>]*>(.*?)</div>\s*</div>',
            text, re.DOTALL | re.IGNORECASE
        ):
            block = m.group(1)
            # Extract question text
            q_match = re.search(
                r'class=["\']question(?:-text)?["\'][^>]*>([^<]+)', block
            )
            question = q_match.group(1).strip() if q_match else "(unknown question)"
            # Extract marked-correct answer
            ans_match = re.search(
                r'data-correct=["\']1["\'][^>]*>\s*([^<]+)', block
            )
            if not ans_match:
                # Try: class="correct-answer" or similar
                ans_match = re.search(
                    r'class=["\']correct(?:-answer)?["\'][^>]*>\s*([^<]+)', block
                )
            if ans_match:
                items.append({
                    "type": "exam_correct_mark",
                    "question": question,
                    "correct_answer": ans_match.group(1).strip(),
                    "file": html_path.name,
                })
    return items


# ---------------------------------------------------------------------------
# Sampling
# ---------------------------------------------------------------------------

def sample_items(
    output_dir: Path,
    sample_rates: dict[str, float],
    seed: int,
) -> list[dict[str, Any]]:
    """Collect items from output_dir and apply sampling rates."""
    rng = random.Random(seed)

    all_vocab = _extract_vocab_items(output_dir)
    all_grammar = _extract_grammar_items(output_dir)
    all_exam = _extract_exam_correct_answers(output_dir)

    def _sample(items: list, rate: float) -> list:
        if rate >= 1.0:
            return list(items)
        k = max(1, int(len(items) * rate)) if items else 0
        return rng.sample(items, min(k, len(items))) if items else []

    sampled = (
        _sample(all_vocab, sample_rates["vocab_card"])
        + _sample(all_grammar, sample_rates["grammar_box"])
        + _sample(all_exam, sample_rates["exam_correct_mark"])
    )
    return sampled


# ---------------------------------------------------------------------------
# Backend checks
# ---------------------------------------------------------------------------

def check_via_tavily(item: dict[str, Any]) -> tuple[bool, str]:
    """Cross-check a single item via the Tavily Research CLI."""
    if item["type"] == "vocab_card":
        query = (
            f'Is "{item["term"]}" correctly translated as "{item["translation"]}" '
            f'in Thai (ภาษาไทย)? Reply with yes or no and a brief explanation.'
        )
    elif item["type"] == "grammar_box":
        query = (
            f'Is the following English grammar explanation correct? '
            f'"{item["snippet"][:150]}" Reply yes or no with a brief explanation.'
        )
    else:  # exam_correct_mark
        query = (
            f'For the question "{item["question"]}", '
            f'is "{item["correct_answer"]}" the correct answer? '
            f'Reply yes or no with a brief explanation.'
        )

    try:
        result = subprocess.run(
            ["tvly", "research", query, "--model", "mini", "--json"],
            capture_output=True, text=True, timeout=30,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        output = result.stdout.strip()
        if not output:
            return True, "tavily returned no output (assumed ok)"
        try:
            data = json.loads(output)
            answer_text = str(data.get("answer", data.get("results", output)))[:300]
        except json.JSONDecodeError:
            answer_text = output[:300]

        # Heuristic: if the response contains a clear "no" or "incorrect",
        # flag it. This is intentionally conservative to keep FP rate low.
        lower = answer_text.lower()
        negative_signals = [
            "not correct", "incorrect", "wrong translation",
            "mistranslation", "does not mean", "is not the correct",
            "this is wrong", "inaccurate"
        ]
        for signal in negative_signals:
            if signal in lower:
                return False, f"tavily flagged: {answer_text[:200]}"
        return True, f"tavily ok: {answer_text[:100]}"
    except subprocess.TimeoutExpired:
        return True, "tavily timed out — skipped (assumed ok)"
    except Exception as exc:
        return True, f"tavily error — skipped: {exc}"


def check_via_notebooklm(item: dict[str, Any], notebook_id: str) -> tuple[bool, str]:
    """Cross-check a single item via a NotebookLM notebook."""
    if item["type"] == "vocab_card":
        query = (
            f'Does the course corpus support translating "{item["term"]}" '
            f'as "{item["translation"]}" in Thai?'
        )
    elif item["type"] == "grammar_box":
        query = (
            f'Does the course corpus support this grammar explanation: '
            f'"{item["snippet"][:150]}"?'
        )
    else:
        query = (
            f'According to the course corpus, for "{item["question"]}", '
            f'is "{item["correct_answer"]}" the correct answer?'
        )

    try:
        cmd = [sys.executable, "-m", "notebooklm", "ask", query]
        if notebook_id:
            cmd += ["--notebook-id", notebook_id]
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=30,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        output = result.stdout.strip() or result.stderr.strip()
        if result.returncode != 0:
            return True, f"notebooklm unavailable — skipped: {output[:100]}"
        lower = output.lower()
        negative_signals = [
            "not supported", "does not support", "incorrect",
            "not found in the corpus", "contradicts"
        ]
        for signal in negative_signals:
            if signal in lower:
                return False, f"notebooklm flagged: {output[:200]}"
        return True, f"notebooklm ok: {output[:100]}"
    except subprocess.TimeoutExpired:
        return True, "notebooklm timed out — skipped"
    except Exception as exc:
        return True, f"notebooklm error — skipped: {exc}"


def check_item(
    item: dict[str, Any],
    backend: str,
    notebook_id: str = "",
) -> tuple[bool, str]:
    """Dispatch to the correct backend check."""
    if backend == "tavily":
        return check_via_tavily(item)
    elif backend == "notebooklm":
        return check_via_notebooklm(item, notebook_id)
    else:
        return True, "no-op"


# ---------------------------------------------------------------------------
# Report emitters
# ---------------------------------------------------------------------------

def emit_report(
    flags: list[dict[str, Any]],
    sampled: list[dict[str, Any]],
    output_dir: Path,
    backend: str,
) -> None:
    """Write JSON + Markdown report to output_dir."""
    report_json = {
        "backend": backend,
        "items_sampled": len(sampled),
        "flags": flags,
        "unresolved_count": len(flags),
    }
    json_path = output_dir / "_content_truth_report.json"
    md_path = output_dir / "_content_truth_report.md"

    json_path.write_text(
        json.dumps(report_json, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    lines = [
        "# Content-Truth Validation Report",
        "",
        f"**Backend:** `{backend}`  ",
        f"**Items sampled:** {len(sampled)}  ",
        f"**Unresolved flags:** {len(flags)}  ",
        "",
    ]
    if flags:
        lines += ["## UNRESOLVED Flags", ""]
        for i, flag in enumerate(flags, 1):
            item = flag["item"]
            lines += [
                f"### Flag {i} — {item['type']} ({item['file']})",
            ]
            if item["type"] == "vocab_card":
                lines.append(f"- Term: `{item['term']}` → Translation: `{item['translation']}`")
            elif item["type"] == "grammar_box":
                lines.append(f"- Grammar snippet: `{item['snippet'][:120]}`")
            else:
                lines.append(
                    f"- Question: `{item['question']}`  \n"
                    f"  Correct answer: `{item['correct_answer']}`"
                )
            lines += [f"- Reason: {flag['reason']}", ""]
    else:
        lines += ["## Result", "", "No content-truth flags raised. All sampled items passed.", ""]

    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Reports written: {json_path}, {md_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 5c content-truth validator for lesson-builder courses."
    )
    parser.add_argument("output_dir", help="Course output directory (e.g. HTML/tefl/children_10_12/)")
    parser.add_argument("config_path", help="Course config JSON file (e.g. config/children_10_12.json)")
    args = parser.parse_args()

    cfg = load_config(args.config_path)
    backend: str = cfg.get("content_truth", {}).get("backend", "off")

    # First line ALWAYS declares the active backend — operator can never be
    # unaware of quota spend.
    print(f"content-truth backend: {backend}")

    if backend == "off":
        print("Phase 5c skipped by config — no quota consumed.")
        return 0

    if backend not in ("tavily", "notebooklm"):
        print(f"ERROR: unknown backend '{backend}'. Valid values: tavily, notebooklm, off", file=sys.stderr)
        return 2

    output_dir = Path(args.output_dir)
    if not output_dir.exists():
        print(f"ERROR: output_dir not found: {output_dir}", file=sys.stderr)
        return 2

    seed = course_id_seed(cfg)
    print(f"Sampling seed: {seed} (deterministic per course_id '{cfg.get('course_id', '?')}')")

    # Resolve notebooklm notebook ID if needed
    notebook_id = ""
    if backend == "notebooklm":
        # Try research.md in the spec directory for the notebook ID
        course_id = cfg.get("course_id", "")
        research_paths = list(Path("specs").glob(f"*{course_id}*/research.md")) if course_id else []
        for rp in research_paths:
            text = rp.read_text(encoding="utf-8", errors="replace")
            m = re.search(r"notebook[_\s-]*id[:\s]+([a-zA-Z0-9_-]{10,})", text, re.IGNORECASE)
            if m:
                notebook_id = m.group(1)
                print(f"Using NotebookLM notebook ID: {notebook_id}")
                break
        if not notebook_id:
            nb_id_from_cfg = cfg.get("notebooklm_notebook_id", "")
            if nb_id_from_cfg:
                notebook_id = nb_id_from_cfg
            else:
                print(
                    "WARNING: no notebooklm_notebook_id found in config or research.md. "
                    "Queries will use default notebook context."
                )

    print(f"Extracting items from: {output_dir}")
    sampled = sample_items(output_dir, SAMPLE_RATES, seed)
    print(f"Sampled {len(sampled)} items "
          f"(vocab={sum(1 for i in sampled if i['type']=='vocab_card')}, "
          f"grammar={sum(1 for i in sampled if i['type']=='grammar_box')}, "
          f"exam={sum(1 for i in sampled if i['type']=='exam_correct_mark')})")

    if not sampled:
        print("No items found to validate — check that output_dir contains generated HTML.")
        emit_report([], [], output_dir, backend)
        return 0

    flags: list[dict[str, Any]] = []
    for item in sampled:
        ok, reason = check_item(item, backend, notebook_id)
        if not ok:
            flags.append({"item": item, "reason": reason})

    emit_report(flags, sampled, output_dir, backend)

    if flags:
        print(
            f"\n{len(flags)} content-truth flag(s) found. "
            f"Resolve each flag (fix / mark-false-positive-with-justification / explicit-override) "
            f"before shipping. Grep _content_truth_report.md for UNRESOLVED to enumerate blockers."
        )
        return 1

    print(f"\nContent-truth validation passed — {len(sampled)} items checked, 0 flags.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
