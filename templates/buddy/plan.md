# Implementation Plan: {{course_id}}

**Status:** Draft | Ready for Review | Approved
**Date:** {{YYYY-MM-DD}}

## Strategy

{{1-2 paragraphs: high-level approach. Usually: write a Python generator script that produces all HTML files programmatically, modular with one function per page type. Note any prior course this pattern is borrowed from.}}

## Architecture

### Generator Script: `generate_{{course_id}}.py`

Located at: `{{absolute or repo-relative path}}`

**Structure:**
```
1. COURSE_DATA — all {{n}} units with vocab, stories, etc.
2. CSS_BASE — shared CSS template
3. generate_{{page_type_1}}(unit) — {{description}}
4. generate_{{page_type_2}}(unit) — {{description}}
...
N. main() — iterate units, write files
```

**Estimated size:** ~{{n}} lines (keep under 3000; split COURSE_DATA into separate JSON if larger)

### Content Per Unit

Each unit in COURSE_DATA contains:
- `topic`, `topic_l1`, `emoji`, `week` — identity
- `grammar`, `grammar_l1` — grammar focus
- `vocab` — list of {{[l2, l1, emoji, definition]}} tuples
- {{per-page-type fields: story_pages, song, reading_passage, etc.}}

### Research-Backed Content (if applicable)

{{Any external content sources that need to be looked up before generation: YouTube IDs for songs, image references, real-world examples, etc. Mark as "to be researched" with a fallback strategy.}}

## Phases

### Phase 1: Setup
- Create output directory `{{output_dir}}`
- {{Optional: write course config JSON for future re-generation}}

### Phase 2: Generator Script (Unit 1 only)
- Write generator with all page type functions
- Generate only Unit 1 as test
- Verify all pages work in browser

### Phase 3: Full Generation
- After Unit 1 passes, populate remaining units
- Generate all {{total}} files
- Cross-check nav footers and links

### Phase 4: Polish
- Verify no JS errors across all pages
- Check mobile responsiveness
- {{Validate any external references — YouTube IDs, image URLs, etc.}}

## Risk Assessment

- **Script size:** {{If approaches 3000 lines, plan split into Part 1 / Part 2 / Part 3 or extract COURSE_DATA to JSON}}
- **External references:** {{YouTube IDs, image URLs, etc. — what's the fallback if any are invalid}}
- **Encoding:** Must use `encoding='utf-8'` everywhere (Windows cp1252 issue)
- **{{L1}} text in Python strings:** {{Curly-brace conflicts in CSS f-strings, single-quote conflicts in inline handlers}}
- {{Any course-specific risks}}
