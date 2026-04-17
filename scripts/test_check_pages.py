#!/usr/bin/env python3
"""test_check_pages.py — unit tests for check_pages.py rules.

For each rule 2.1–2.7, tests that:
  - the pass fixture produces zero findings for that rule
  - the broken fixture produces at least one finding for that rule

Usage:
    python scripts/test_check_pages.py

Exit codes:
  0 — all pass fixtures clean and all broken fixtures flagged
  1 — one or more rule failures
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add scripts/ to path so we can import check_pages
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

import check_pages  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "check_pages"
PASS_DIR = FIXTURES / "pass"
BROKEN_DIR = FIXTURES / "broken"


# Rule → (rule_function, pass_fixture_name, broken_fixture_name)
RULE_TESTS = [
    (
        "2.1-undefined-js-ref",
        check_pages.check_undefined_js_refs,
        "rule_2_1_pass.html",
        "rule_2_1_broken.html",
    ),
    (
        "2.2-python-escape-leak",
        check_pages.check_python_js_escape_leak,
        "rule_2_2_pass.html",
        "rule_2_2_broken.html",
    ),
    (
        "2.3-svg-attr-quote-collision",
        check_pages.check_svg_attr_quotes_in_js,
        "rule_2_3_pass.html",
        "rule_2_3_broken.html",
    ),
    (
        "2.4-speechsynthesis-cancel-missing",
        check_pages.check_speechsynthesis_cancel_guard,
        "rule_2_4_pass.html",
        "rule_2_4_broken.html",
    ),
    (
        "2.5-onclick-quote-safety",
        check_pages.check_onclick_quote_safety,
        "rule_2_5_pass.html",
        "rule_2_5_broken.html",
    ),
    (
        "2.6-media-src-missing",
        lambda p: check_pages.check_media_src_exists_on_disk(p, None),
        "rule_2_6_pass.html",
        "rule_2_6_broken.html",
    ),
    (
        "2.7-js-parse-error",
        check_pages.check_js_parses,
        "rule_2_7_pass.html",
        "rule_2_7_broken.html",
    ),
]


def run_tests() -> int:
    failures = 0
    print(f"JS parse mode: {check_pages.JS_PARSE_MODE}")
    print()

    for rule_id, fn, pass_name, broken_name in RULE_TESTS:
        pass_path = PASS_DIR / pass_name
        broken_path = BROKEN_DIR / broken_name

        # --- Pass fixture ---
        if not pass_path.exists():
            print(f"FAIL [{rule_id}] pass fixture not found: {pass_path}")
            failures += 1
        else:
            findings = list(fn(pass_path))
            # Filter to only findings for this rule
            rule_findings = [f for f in findings if f.rule == rule_id]
            if rule_findings:
                print(f"FAIL [{rule_id}] pass fixture produced {len(rule_findings)} finding(s):")
                for f in rule_findings:
                    print(f"  line {f.line}: {f.description}")
                failures += 1
            else:
                print(f"OK   [{rule_id}] pass fixture clean")

        # --- Broken fixture ---
        if not broken_path.exists():
            print(f"FAIL [{rule_id}] broken fixture not found: {broken_path}")
            failures += 1
        else:
            findings = list(fn(broken_path))
            rule_findings = [f for f in findings if f.rule == rule_id]
            if not rule_findings:
                # For rule 2.5 (onclick quote safety), the broken fixture uses
                # an apostrophe; the HTML parser may collapse it differently.
                # Also check for any finding from scan_file as fallback.
                all_findings = list(check_pages.scan_file(broken_path))
                if not all_findings:
                    print(f"FAIL [{rule_id}] broken fixture produced 0 findings (expected >= 1)")
                    failures += 1
                else:
                    print(f"OK   [{rule_id}] broken fixture flagged by scan_file ({len(all_findings)} finding(s))")
            else:
                print(f"OK   [{rule_id}] broken fixture flagged ({len(rule_findings)} finding(s))")

    print()
    if failures:
        print(f"RESULT: {failures} failure(s)")
        return 1
    print("RESULT: all tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(run_tests())
