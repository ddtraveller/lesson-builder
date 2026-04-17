# Tasks: {{course_id}}

**Status:** Draft | In Progress | Completed
**Date:** {{YYYY-MM-DD}}

## Tasks

- [ ] T001: Create output directory `{{output_dir}}`
- [ ] T002: Write generator script Part 1 — CSS, helpers, {{first half of page-type functions}} (~{{n}} lines)
- [ ] T003: Write generator script Part 2 — {{second half of page-type functions}} (~{{n}} lines)
- [ ] T004: Write generator script Part 3 — COURSE_DATA for all {{n}} units (~{{n}} lines)
- [ ] T005: Generate Unit 1 only — test all page types
- [ ] T006: Browser-verify Unit 1 (check JS console, nav footer, mobile breakpoints)
- [ ] T007: Generate all remaining units (2-{{n}})
- [ ] T008: Cross-file consistency check (nav footers, links between units)
- [ ] T009: Generate syllabus page
- [ ] T010: Run `python scripts/check_links.py {{output_dir}} --html-root HTML` — fix BROKEN and DEPTH findings in the generator, regenerate, re-run until exit 0
- [ ] T011: Run `python scripts/check_exams.py {{output_dir}} --review-out {{output_dir}}/_exam_review.json` — fix structural issues, then read `_exam_review.json` and verify every question is answerable (complete question, exactly one correct option, plausible distractors). Skip if course has no exam pages.
- [ ] T012: Run `python scripts/check_pages.py {{output_dir}}` — review findings (report-only until promoted to blocking after two clean runs on shipped courses). Fix any JS escape leakage, undefined function references, or missing media src findings in the generator, then regenerate.

{{Optional additional tasks if applicable:}}
- [ ] T0XX: Generate hero images via Replicate (if `images.enabled`)
- [ ] T0XX: Generate hero video (if requested)
- [ ] T0XX: {{any course-specific polish task}}

## Notes

- T002-T004 may collapse into a single task for small courses (<2000 lines total)
- T005 and T006 are the load-bearing gate: do not proceed to T007 until Unit 1 verifies clean
- T010 and T011 are the final delivery gate: a course is NOT done until link check exits 0 and every exam question has been semantically reviewed
- Mark each task `[X]` as completed; do not batch
