#!/usr/bin/env python3
"""check_links.py — verify that hrefs and srcs in generated lesson HTML resolve.

Usage:
    python scripts/check_links.py HTML/path/to/course [--imgs imgs/path] [--video video/path] [--audio audio/path] [--html-root HTML]

Checks performed per HTML file:
  1. Relative local refs (`href="foo.html"`, `src="bar.png"`, `src="../imgs/..."`)
     resolve to an existing file on disk.
  2. Relative path depth matches the page's depth under the HTML root.
     Pages at `HTML/a/b/page.html` are depth 2 and must use `../../imgs/...`,
     not `../imgs/...` (which would deploy to `a/imgs/...` on S3 and 404).
  3. Nav footer links point at files that actually exist in the course.
  4. External URLs (http/https) are collected and listed — not fetched by default
     to keep the check offline. Pass `--check-external` to HEAD each one.
  5. `<iframe src="https://www.youtube.com/embed/VIDEO_ID">` video IDs are
     listed for the user to spot-check (cannot validate without YouTube API).

Exit codes:
  0 — all local refs resolved, no structural issues
  1 — one or more broken refs found
  2 — invocation error
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

# Attributes that carry a URL we care about.
URL_ATTRS = ("href", "src", "poster", "data-src")

# Match any attr=value where attr is one of the URL attrs (quoted value).
ATTR_RE = re.compile(
    r'\b(' + '|'.join(URL_ATTRS) + r')\s*=\s*"([^"]+)"',
    re.IGNORECASE,
)

# Match YouTube embed iframes so we can surface the video IDs.
YT_EMBED_RE = re.compile(
    r'<iframe[^>]+src\s*=\s*"https?://(?:www\.)?youtube(?:-nocookie)?\.com/embed/([^"?&]+)',
    re.IGNORECASE,
)


def classify(url: str) -> str:
    """Return one of: anchor, mailto, tel, external, data, local."""
    if not url or url.startswith("#"):
        return "anchor"
    low = url.lower()
    if low.startswith("mailto:"):
        return "mailto"
    if low.startswith("tel:"):
        return "tel"
    if low.startswith("data:"):
        return "data"
    if low.startswith(("http://", "https://", "//")):
        return "external"
    return "local"


def html_depth(html_file: Path, html_root: Path) -> int:
    """How many directories deep `html_file` is under `html_root`."""
    try:
        rel = html_file.resolve().relative_to(html_root.resolve())
    except ValueError:
        return 0
    # Depth = number of parent directories of the file under html_root
    return len(rel.parts) - 1


def expected_depth_for_ref(ref: str) -> int:
    """How many `..` segments the ref starts with (i.e. the depth it assumes)."""
    parts = [p for p in ref.split("/") if p]
    depth = 0
    for p in parts:
        if p == "..":
            depth += 1
        else:
            break
    return depth


def resolve_local(ref: str, html_file: Path) -> Path:
    """Resolve a relative ref against the HTML file's directory."""
    # Strip query/fragment
    clean = ref.split("?", 1)[0].split("#", 1)[0]
    return (html_file.parent / clean).resolve()


def scan_file(html_file: Path, html_root: Path) -> dict:
    """Return dict with keys: broken, depth_issues, external, youtube, total."""
    text = html_file.read_text(encoding="utf-8", errors="replace")
    page_depth = html_depth(html_file, html_root)

    broken: list[tuple[str, str]] = []      # (ref, reason)
    depth_issues: list[tuple[str, str]] = []
    external: list[str] = []
    total = 0

    seen = set()
    for m in ATTR_RE.finditer(text):
        ref = m.group(2).strip()
        if not ref or ref in seen:
            continue
        seen.add(ref)
        total += 1

        kind = classify(ref)
        if kind in ("anchor", "mailto", "tel", "data"):
            continue
        if kind == "external":
            external.append(ref)
            continue

        # local
        target = resolve_local(ref, html_file)
        if not target.exists():
            broken.append((ref, f"file not found: {target}"))
            # Additionally, if it's a media ref (imgs/video/audio) starting with ..,
            # check whether the `..` depth matches page depth.
            ref_depth = expected_depth_for_ref(ref)
            if ref_depth and ref_depth != page_depth:
                depth_issues.append(
                    (ref, f"page depth is {page_depth} but ref uses {ref_depth} `..` segments")
                )

    youtube = list({m.group(1) for m in YT_EMBED_RE.finditer(text)})

    return {
        "file": str(html_file),
        "page_depth": page_depth,
        "broken": broken,
        "depth_issues": depth_issues,
        "external": external,
        "youtube": youtube,
        "total": total,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify links in generated lesson HTML")
    ap.add_argument("course_dir", help="Directory containing the course's .html files")
    ap.add_argument(
        "--html-root",
        default="HTML",
        help="Repo HTML root (default: HTML). Used to compute each page's depth.",
    )
    ap.add_argument(
        "--check-external",
        action="store_true",
        help="HEAD each external URL to verify it's reachable (slow, needs network).",
    )
    ap.add_argument(
        "--quiet",
        action="store_true",
        help="Only print broken refs, skip external-URL listing.",
    )
    args = ap.parse_args()

    course_dir = Path(args.course_dir)
    if not course_dir.is_dir():
        print(f"ERROR: {course_dir} is not a directory", file=sys.stderr)
        return 2

    html_root = Path(args.html_root)
    if not html_root.exists():
        print(f"WARN: --html-root {html_root} does not exist; depth checks may be wrong",
              file=sys.stderr)

    html_files = sorted(course_dir.rglob("*.html"))
    if not html_files:
        print(f"WARN: no .html files found under {course_dir}", file=sys.stderr)
        return 0

    total_broken = 0
    total_depth = 0
    all_external: set[str] = set()
    all_youtube: set[str] = set()

    for hf in html_files:
        r = scan_file(hf, html_root)
        all_external.update(r["external"])
        all_youtube.update(r["youtube"])

        if r["broken"] or r["depth_issues"]:
            rel = hf.relative_to(course_dir) if hf.is_relative_to(course_dir) else hf
            print(f"\n[{rel}] depth={r['page_depth']} refs={r['total']}")
            for ref, reason in r["broken"]:
                print(f"  BROKEN  {ref}  ({reason})")
                total_broken += 1
            for ref, reason in r["depth_issues"]:
                print(f"  DEPTH   {ref}  ({reason})")
                total_depth += 1

    if not args.quiet:
        if all_youtube:
            print(f"\nYouTube embeds ({len(all_youtube)} unique IDs):")
            for yid in sorted(all_youtube):
                print(f"  https://www.youtube.com/watch?v={yid}")
        if all_external:
            print(f"\nExternal URLs ({len(all_external)}):")
            for url in sorted(all_external):
                print(f"  {url}")

    if args.check_external and all_external:
        try:
            import urllib.request
        except ImportError:
            print("urllib not available; skipping --check-external", file=sys.stderr)
        else:
            print("\nHEADing external URLs...")
            ext_broken = 0
            for url in sorted(all_external):
                try:
                    req = urllib.request.Request(url, method="HEAD",
                                                 headers={"User-Agent": "lesson-builder-check"})
                    urllib.request.urlopen(req, timeout=10)
                    print(f"  OK      {url}")
                except Exception as e:  # noqa: BLE001
                    print(f"  FAIL    {url}  ({e})")
                    ext_broken += 1
            if ext_broken:
                print(f"\n{ext_broken} external URLs failed")
                total_broken += ext_broken

    print(
        f"\nSummary: {len(html_files)} files scanned, "
        f"{total_broken} broken, {total_depth} depth issues, "
        f"{len(all_external)} external refs, {len(all_youtube)} YouTube embeds"
    )
    return 1 if (total_broken or total_depth) else 0


if __name__ == "__main__":
    sys.exit(main())
