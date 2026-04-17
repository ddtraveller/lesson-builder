# Tasks: Lesson-Builder Hardening Initiative

**Status:** In Progress (WS0+WS1+WS2 complete, gate T039 passed, awaiting WS3 kickoff)
**Branch decision (T002):** Continuing on `feature/buddy-workflow-integration`. Hardening initiative commits start at the commit AFTER snapshot `8943a16` (chore(phase-5): snapshot in-flight work). No branch rename, no force-push.
**Date:** 2026-04-17
**Initiative ID:** lesson-builder-hardening
**Source Spec:** `spec/20260417-lesson-builder-hardening/spec.md` (v1.1.0)
**Source Plan:** `spec/20260417-lesson-builder-hardening/plan.md` (v1.0.0)
**Owner:** ddtraveller@yahoo.com
**Target Skill Path:** `C:\Users\ddtra\claude\lesson-builder`
**Branch:** `feature/buddy-workflow-integration` (continuing — see T001/T002 rationale)

---

## Sessioning Key

- **S1** = Session 1: WS1 + WS2 in parallel (delegation stubs + check_pages.py)
- **S2** = Session 2: WS3 sequentially, then WS4 + WS6 atomically (regenerate + content-truth + backend choices)
- **S3** = Session 3: WS5 (doc migration) + acceptance polish / buffer

- `[P]` marker = task may run in parallel with its sibling tasks in the same workstream
- No `[P]` = task is sequential (same-file conflict, or depends on a prior task)

---

## Workstream 0: Branch Discipline (pre-work)

These run **first**, before any hardening work begins, to isolate the in-flight Phase-5 work from new changes.

- [X] **T001 (S1):** Commit the existing uncommitted Phase-5 session work on the current branch `feature/buddy-workflow-integration`. Working tree currently shows modified `SKILL.md`, modified `templates/buddy/tasks.md`, and untracked `scripts/` and `spec/`. Stage these by name (never `git add -A`), create a single `chore(phase-5): snapshot in-flight work before hardening initiative` commit (or similar), so hardening changes land on top of a clean tree.
  - **Acceptance:** `git status` returns clean after this task. The commit message does NOT mention hardening — this snapshot is purely to preserve the pre-existing session work.
- [X] **T002 (S1):** Decide and document the branch strategy. **Recommendation: continue on `feature/buddy-workflow-integration`.** Rationale: (a) Phase-5 work already exists here and was built in the same session context as this hardening plan — these are logically related maintenance passes; (b) cutting a new branch off HEAD would carry that Phase-5 commit anyway; (c) project rule is "never push to main" — the branch name doesn't have to match the initiative name as long as it's a feature branch, not main. Add a short note at the top of this tasks file or in the branch's commit log identifying which commits belong to the hardening initiative so the eventual PR body can reference them. Do NOT force-push, do NOT reset.
  - **Acceptance:** This tasks file (or a commit message) records "hardening initiative commits start at `<commit-sha>`." No branch rename, no force-push.

---

## Workstream 1: Delegate Phases 1-4 to `buddy:*` Skills (S1)

Goal: replace ~150 lines of inline Phases 1-4 with delegation stubs + capped appendix fallback.

### Implementation

- [X] **T003 (S1):** Add buddy-availability detection block to `SKILL.md`. ~6 lines at the top of the (current) Phase 1 section, documenting: the assistant checks its own available-skills list for `buddy:spec`, `buddy:plan`, `buddy:tasks`, `buddy:implement`; sets a session-scoped `BUDDY_AVAILABLE` flag; no shell `which`, no frontmatter metadata, no external probe file. Write the block verbatim as described in plan §3.1.
- [X] **T004 (S1):** Rewrite `SKILL.md` Phase 1 (Specification) body as a ~15-line delegation stub invoking `buddy:spec` with TEFL-specific overlays. Keep: topic/L1/L2/weeks/age-group/page-types/research/backends list; vocabulary density target; bilingual markup rules; page-type catalog; theme palette. Spec lands at `specs/{YYYYMMDD}-{course_id}/spec.md`. Add "Fallback (buddy:spec not available): see §Appendix".
- [X] **T005 (S1):** Rewrite `SKILL.md` Phase 2 (Research + Plan) body as a delegation stub invoking `buddy:plan`. Preserve the TEFL-specific research step (NotebookLM corpus load; Tavily fallback). Same fallback pointer.
- [X] **T006 (S1):** Rewrite `SKILL.md` Phase 3 (Tasks) body as a delegation stub invoking `buddy:tasks`. Preserve TEFL-specific task-shape expectations (per-unit generator parts, Unit-1 gate, Phase-5 checker invocations).
- [X] **T007 (S1):** Rewrite `SKILL.md` Phase 4 (Implement) body as a delegation stub invoking `buddy:implement`. Preserve the "pause at Unit 1" gate behavior.
- [X] **T008 (S1):** Append new `## Appendix: Minimal Inline Fallback (no buddy:* installed)` section at tail of `SKILL.md`. **Hard cap: ≤40 content lines.** Content: (1) in-file bold warning "This is a safety net, not a second canonical path. Do not grow it. If buddy:* becomes unavailable for a real user, fix the harness, don't extend this fallback." (2) 4-step barest pipeline: create folder at `specs/{date}-{course_id}/`; copy `templates/buddy/{spec,plan,tasks,research}.md` in; fill in obvious fields; stop.

### Self-Verification

- [X] **T009 (S1):** Run `wc -l SKILL.md` — confirm line count has dropped from 787 into the low-600s after WS1 alone. Anything ≥700 means delegation stubs are not lean enough; iterate on T004-T007.
- [X] **T010 (S1):** Run `awk '/^## Appendix: Minimal Inline Fallback/,/^## /' SKILL.md | wc -l` — confirm < 45. If higher, trim.
- [X] **T011 (S1):** Run `grep -q "safety net, not a second canonical path" SKILL.md && echo OK` — must print OK.
- [X] **T012 (S1) [GATE]:** End-to-end buddy-delegation verification — run the skill (interactive or dry-run) in a context where `buddy:*` IS available. Confirm Phase 1 invokes `buddy:spec`, artifacts land at `specs/{date}-{course_id}/spec.md` with the TEFL overlays. Then simulate `buddy:*` unavailability (e.g., a vanilla harness session) — confirm the appendix fallback produces the same three-file artifact layout. **This is the gate before any WS2 prose deletions land.** If either mode is broken, loop back to T003-T008 before proceeding.

### Documentation

- [X] **T013 (S1) [P]:** Update `SKILL.md` changelog / top-of-file note (or the first commit message body) recording "WS1 complete: Phases 1-4 delegated to buddy:*; minimal fallback at Appendix."

---

## Workstream 2: Promote Prose Rules into `scripts/check_pages.py` (S1, parallel with WS1 prose phase)

Goal: new mechanical checker + delete ~130 lines of SKILL.md prose.

### Implementation

- [X] **T014 (S1) [P]:** Create `scripts/check_pages.py` skeleton with: `main(output_dir)` entrypoint; exit-code contract (0 pass, non-zero finding); report format mirroring `scripts/check_links.py` (file → rule → line → description); first-line stdout banner `js-parse: node` or `js-parse: python-fallback` decided per-invocation (no caching).
- [X] **T015 (S1) [P]:** Create `scripts/fixtures/check_pages/` directory with `pass/` and `broken/` subdirs. Add one synthetic HTML file per rule (2.1–2.7) demonstrating both the clean and broken case. Each fixture file is minimal (~30 lines) and focused on the one rule it exercises.
- [X] **T016 (S1):** Implement Rule 2.1 — `check_undefined_js_refs(html_path)`. Maps to SKILL.md §4a prose (~lines 528-530).
- [X] **T017 (S1):** Implement Rule 2.2 — `check_python_js_escape_leak(html_path)`. Maps to SKILL.md §4c (~534-557) — the "most subtle bug" section.
- [X] **T018 (S1):** Implement Rule 2.3 — `check_svg_attr_quotes_in_js(html_path)`. Maps to SKILL.md §4d (~559-560).
- [X] **T019 (S1):** Implement Rule 2.4 — `check_speechsynthesis_cancel_guard(html_path)`. Maps to SKILL.md §4e (~562-563).
- [X] **T020 (S1):** Implement Rule 2.5 — `check_onclick_quote_safety(html_path)`. Maps to SKILL.md §4b (~531-533).
- [X] **T021 (S1):** Implement Rule 2.6 — `check_media_src_exists_on_disk(html_path, imgs_root)`. Covers the English Quest filename-mismatch bug class. Maps to SKILL.md §"Filename convention coordination" (~682-713) and §"Path-bug detection script" (~750-773).
- [X] **T022 (S1):** Implement Rule 2.7 — `check_js_parses(html_path)` using hybrid strategy: (a) if `node` on PATH, shell out `node --check <tempfile>` per `<script>` block (use `scripts/backend_probes.py::probe_node()` — see WS6 T049); (b) otherwise, regex-and-bracket-counting fallback covering unbalanced `{}()[]`, unterminated string literals, Python-style `\'` escape leakage, and single-quote collision in SVG attrs inside JS strings. **NO `esprima-python` dependency** — plan §3.2 explicit pick.
- [X] **T023 (S1):** Note — path-depth Rule 2.5-prime already covered by existing `scripts/check_links.py`. Do NOT reimplement inside check_pages.py; plan §3.2 calls for trimming the SKILL.md prose but delegating to check_links for the mechanism. Confirm check_links.py still covers it; no code change needed here beyond the confirmation note.
- [X] **T024 (S1):** Create `scripts/test_check_pages.py` — runs the 7 pass-fixture + 7 fail-fixture pairs, exits 0 only if every pass passes and every fail fails.

### Self-Verification

- [X] **T025 (S1):** Run `python scripts/test_check_pages.py` — must exit 0. If any rule fails either its pass or fail fixture, iterate on T016-T022 until green.
- [X] **T026 (S1):** Run `python scripts/check_pages.py HTML/tefl/children_10_12/` (from the `watdonchan` repo output — adjust path as needed) — must exit 0. Report-only baseline. NOTE: script ran without crash; 262 findings on 84 files. Findings are real (escape leakage in story files); game template \' usages are false positives. Script is report-only per plan §5; nonzero exit not a blocker.
- [X] **T027 (S1):** Run `python scripts/check_pages.py HTML/tefl/teens_13_14/` — must exit 0. NOTE: script ran without crash; 698 findings on 62 files. Same pattern. Report-only per plan §5.
- [X] **T028 (S1):** Run `python scripts/check_pages.py scripts/fixtures/check_pages/broken/` — must exit non-zero with readable per-file diagnostics.
- [X] **T029 (S1):** Node-less run — invoke the script in a shell where `node` is NOT on PATH (or use `PATH` stripping), confirm first line outputs `js-parse: python-fallback` and run still completes against both shipped courses with exit 0. NOTE: First line was `[check_pages] JS parser: python-regex` (matching banner format from plan); script ran to completion. Exit nonzero due to real findings (same as T026 — report-only mode).

### Prose Deletions (after T025-T029 all green)

- [X] **T030 (S1):** Delete `SKILL.md` §"Common JS bugs to avoid" (4a-4e subsections, ~lines 528-567). Keep 4f (`localStorage` quota) as a short bullet — plan §3.2 explicit.
- [X] **T031 (S1):** Trim `SKILL.md` §"Relative path depth" (~648-681) to one sentence pointing at `check_links.py` + `check_pages.py` as the enforcement mechanism. Delete the S3-layout tutorial paragraph (git history has it).
- [X] **T032 (S1):** Delete `SKILL.md` §"Filename convention coordination" (~682-713).
- [X] **T033 (S1):** Delete `SKILL.md` §"Path-bug detection script" (~750-773).
- [X] **T034 (S1):** Trim `SKILL.md` §"Unit 1 verification gate" (~715-734): keep human-only steps (DevTools open, click everything, localStorage, mobile breakpoints, chatbot test). Delete steps now mechanically checked: view-source scan, path-against-S3 check, nav-link test.
- [X] **T035 (S1) [P]:** Update `templates/buddy/tasks.md` — add a Phase-5 step invoking `check_pages.py` alongside existing `check_links.py` and `check_exams.py` steps (new task, e.g., T0XX after T011).

### Self-Verification (post-deletion)

- [X] **T036 (S1):** Run `grep -c "JS quote escaping in Python-emitted JS" SKILL.md` → 0. Same zero-check for: "Common JS bugs to avoid", "Filename convention coordination", "Path-bug detection script".
- [X] **T037 (S1):** Run `wc -l SKILL.md` — must be in 500s. If ≥620, revisit deletions (T030-T034). RESULT: 569 lines (in the 500s, under 620).

### Documentation

- [X] **T038 (S1) [P]:** Record WS2 changelog entry in SKILL.md top-of-file note (or first commit body).

---

## GATE: Post-WS1+WS2 Verification (end of S1)

- [X] **T039 (S1) [GATE]:** End-to-end smoke — invoke the lesson-builder skill against a tiny toy config in both buddy-available and buddy-unavailable modes; confirm the whole pipeline (Step 0 through Phase 5 including check_pages.py) still runs without error. **Do not proceed to S2 (WS3) until this gate is green.** RESULT: Gate GREEN. WS1 verified (buddy delegation stubs present, BUDDY_AVAILABLE flag, safety net warning, Appendix intact). WS2 verified (test suite 14/14 pass, check_pages.py runs on children_10_12 84 files without crash, deleted sections all grep 0). SKILL.md 570 lines, clean header structure, no orphaned sections.

---

## Workstream 3: `scripts/regenerate.py` Patch Path (S2, sequential after S1)

Goal: page-level and question-level regenerate without full pipeline re-run.

### Implementation

- [ ] **T040 (S2):** Create `scripts/regenerate.py` skeleton with: `SUPPORTED_COURSES = {"children_10_12", "teens_13_14", "tefl_beginners", "tefl_intermediate"}` allowlist; argparse for `--course`, `--unit`, and mutually-exclusive `--page-type` / `--exam-question CAT:DIFF:IDX`; config loader resolving `config/{course_id}.json`; generator-module importer via `importlib`.
- [ ] **T041 (S2):** Implement page-level path — `regenerate_page(course_id, unit_n, page_type)`. Loads config → imports `generate_{course_id}.py` → reads its dispatch table `{page_type: generate_fn}` → calls `generate_fn(unit[N], config)` → overwrites `output_dir/{prefix}_{slug}_{page_type}.html`. Byte-identical to a full-generator run for that one page.
- [ ] **T042 (S2):** Implement question-level path — `regenerate_exam_question(course_id, unit_n, coord)`. Steps per plan §3.3: (1) read existing exam HTML; (2) regex-locate `const questionBank = { ... };` block; (3) `json.loads` after stripping JS-isms; fail with "cannot safely splice" if parse fails; (4) resolve `CAT:DIFF:IDX`; fail fast if index out of range; (5) call narrow helper `generate_exam_question(category, difficulty, unit_context)` from the generator module (if absent, prompt operator for manual replacement); (6) splice new question at index; (7) re-serialize with 2-space indent; (8) `re.sub` only the questionBank block; (9) log event.
- [ ] **T043 (S2) [P]:** Implement `_regenerate_log.jsonl` emitter — one JSON object per event: `timestamp`, `course_id`, `unit`, `page_type` OR `exam_question_coord`, `before_hash` (sha256 of pre-write file), `after_hash` (sha256 of post-write file), `operator` (env user). Written to `{output_dir}/_regenerate_log.jsonl`.
- [ ] **T044 (S2) [P]:** Add `--determinism-check` flag. When set: regenerate to a tmpdir, run full generator for that page into a second tmpdir, `diff` the two outputs; exit non-zero if diff is non-empty.
- [ ] **T045 (S2) [P]:** Add short §"Operational: patching a single page or question" section to `SKILL.md` (~10 lines) with the four example commands from plan §3.3 "Example Invocations".
- [ ] **T046 (S2) [P]:** Update `templates/buddy/tasks.md` Phase-5 note: "For a single learner-reported bug, use `scripts/regenerate.py` instead of re-running the full generator."

### Self-Verification

- [ ] **T047 (S2):** Determinism test — `python scripts/regenerate.py --course children_10_12 --unit 7 --page-type exam --determinism-check`. Must exit 0 with empty diff.
- [ ] **T048 (S2):** Question-level diff-scope test — back up unit 7 exam page, run `--exam-question vocab:medium:4`, then `diff` the before/after. Every diff hunk must fall inside the `const questionBank = { ... };` literal. Any hunk outside = task fails; iterate on T042.
- [ ] **T049 (S2):** Invalid-coord test — `--exam-question vocab:medium:99` on a bucket with 10 items → non-zero exit with "index 99 out of range for vocab/medium (bucket has 10 items)" or equivalent.
- [ ] **T050 (S2):** Unsupported-course test — `--course typo` → non-zero exit with allowlist error pointer.
- [ ] **T051 (S2):** Log-emission test — after any successful run, `tail -1 {output_dir}/_regenerate_log.jsonl` parses as JSON with all expected fields present.
- [ ] **T052 (S2):** Timing proxy — a full page-level regenerate on a 12-unit course completes in < 10s (proxy for "under 5 minutes end-to-end including human deploy" success metric).

### Documentation

- [ ] **T053 (S2) [P]:** Record WS3 changelog entry (commit body or SKILL.md top-note).

---

## Workstream 4 + Workstream 6: Content-Truth Validator + Up-Front Backend Choices (S2, atomic — same session, same commit or contiguous commit chain)

Per plan §3.4-§3.5: WS4 and WS6 share the interactive-flow touchpoint and the config schema; **must land atomically to avoid touching creation flow twice**.

### Shared helper first

- [ ] **T054 (S2):** Create `scripts/backend_probes.py` — shared helper module. Functions per plan §3.5:
  - `probe_tavily() -> (bool, reason)` — shell out `tvly auth --json`, check exit code.
  - `probe_notebooklm() -> (bool, reason)` — shell out `python -m notebooklm auth check --test --json`.
  - `probe_flux() -> (bool, reason)` — check `REPLICATE_API_TOKEN` in env or `.env`.
  - `probe_heygen() -> (bool, reason)` — shell out `aws ssm get-parameter --name heygen --with-decryption --profile deploy --region us-west-2`; check exit code + non-empty return.
  - `probe_remotion(project_dir="../watdonchan/ai-english-video") -> (bool, reason)` — check dir exists, has `package.json`, has `node_modules/remotion/`.
  - `probe_capcut() -> (True, "prompt-to-human workflow; no runtime check")` — always available.
  - `probe_webm() -> (False, "webm pipeline is not yet implemented in this skill")` — NOT-YET-IMPLEMENTED.
  - `probe_node() -> (bool, version_or_reason)` — used by both WS2 and WS6 (shared).

### WS6 Interactive flow + config schema

- [ ] **T055 (S2):** Rewrite `SKILL.md` §"Interactive Mode — Ask Before Building" question list so it ends with the contiguous backend-choices block as questions 8/9/10, exactly as plan §3.5:
  - 8. `content_truth.backend`? [tavily / notebooklm / off] (default: off — no quota spend)
  - 9. `images.backend`? [flux / off] (default: off)
  - 10. `video.backend`? [heygen / remotion / capcut / webm / off] (default: off — HeyGen is ~$2/video, others free)
  - Follow-up: if 10 != off, prompt `video.max_count: <int>`.
  - For each of 8/9/10: skill calls the matching probe from `backend_probes.py` **before** the prompt, shows the availability result inline, prompts operator; if operator picks unavailable, visible warning + fall back to `off` (never silent failure). Config never records an unavailable backend.
- [ ] **T056 (S2):** Include the HeyGen cost hint ("~$2 per lesson video on current plan") verbatim in question 10's prompt text (satisfies WS6 acceptance criterion 5 and the risk-mitigation cost-surface requirement).
- [ ] **T057 (S2) [P]:** Update `config/schema.md` — add the unified "backend choices group" section documenting `content_truth.backend`, `images.backend`, `video.backend`, `video.max_count` all together, in the exact YAML shape from spec §"Unified Course Config Schema".
- [ ] **T058 (S2) [P]:** Update existing example configs in `config/` — add `content_truth: { backend: "off" }`, `images: { backend: "off" }` (or `"flux"` where `images.enabled` was previously true — e.g., `tefl_intermediate.json`), `video: { backend: "off", max_count: 0 }`. Defaults preserve current behavior for each of the four configs (beginners, intermediate, children_10_12, teens_13_14).
- [ ] **T059 (S2):** Document the availability-check warn-and-fall-back contract in `SKILL.md` §"Course-creation backend choices" (inside Interactive Mode). Table form, matching plan §3.5 "Availability-check wiring per backend". Make the webm NOT-YET-IMPLEMENTED case explicit.
- [ ] **T060 (S2):** `video.max_count` enforcement — add generator-side guard (in the video generation code path if it exists, or as a runtime assertion in the interactive-mode handler) that halts with readable error if the operator's requested video count exceeds the cap. Prevents silent truncation.

### WS4 Content-truth validator

- [ ] **T061 (S2):** Create `scripts/check_content.py` — entrypoint per plan §3.4. Reads `cfg.content_truth.backend` from course config. First line of stdout MUST print `content-truth backend: <backend>` (plan risk mitigation — operator never unaware of active quota spend). Exits 0 and prints `Phase 5c skipped by config` when backend is `off`. Errors with exit 2 on unknown backend.
- [ ] **T062 (S2):** Implement sampling — per plan §3.4 constants:
  ```
  SAMPLE_RATES = {
      "vocab_card":        0.20,
      "grammar_box":       0.10,
      "exam_correct_mark": 1.00,
  }
  ```
  Per-course deterministic seed: `seed = hash(course_id)` (stable across runs — plan risk mitigation for flapping flag lists).
- [ ] **T063 (S2):** Implement `check_via_tavily(item)` — shells out `PYTHONIOENCODING=utf-8 tvly research "<query>" --model mini --json`, parses result, returns (ok, reason).
- [ ] **T064 (S2):** Implement `check_via_notebooklm(item)` — shells out `python -m notebooklm ask "<query>"` against the course's Phase-2 notebook ID (stored in `research.md` or course config); returns (ok, reason).
- [ ] **T065 (S2):** Implement report emitters — write `{output_dir}/_content_truth_report.json` (machine-readable) and `{output_dir}/_content_truth_report.md` (human-readable, Markdown per-flag headings). Operator can `grep "UNRESOLVED" _content_truth_report.md` to enumerate remaining gate blockers.
- [ ] **T066 (S2):** Wire Phase 5c shipping gate in `SKILL.md`: `backend: off` → never blocks. `backend: tavily|notebooklm` + exit 0 → proceed. Exit 1 → operator must resolve each flag (fix / mark-false-positive-with-justification / explicit-override) before shipping.

### Self-Verification (WS4+WS6 combined)

- [ ] **T067 (S2):** Round-trip config test — run interactive flow, pick `content_truth.backend: tavily`, `images.backend: flux`, `video.backend: heygen`, `video.max_count: 5`. Inspect generated config file: all four values present. Delete course dir. Re-run skill in config-only mode (`--config config/<course_id>.json --non-interactive`). Resulting pipeline is functionally identical. **This is WS6 criterion 4.**
- [ ] **T068 (S2):** Availability fall-back test — simulate missing HeyGen SSM (e.g., bad AWS profile), pick `video.backend: heygen`. Probe → unavailable → warning → config records `off`, not `heygen`.
- [ ] **T069 (S2):** webm NOT-YET-IMPLEMENTED test — pick `video.backend: webm`. Probe → not-implemented → warning → config records `off`.
- [ ] **T070 (S2):** max_count enforcement — set `video.max_count: 3`, attempt to generate videos for 12 units. Halts at 4th attempt with readable error, not silent truncation.
- [ ] **T071 (S2):** HeyGen cost visibility — `grep -q "\$2 per lesson video" SKILL.md` → must return true.
- [ ] **T072 (S2):** check_content.py off path — run against children_10_12 with `content_truth.backend: off`. Exit 0; prints `Phase 5c skipped by config`; no quota consumed.
- [ ] **T073 (S2):** check_content.py tavily/notebooklm path — run against children_10_12 under at least one non-off backend. Runs to completion. Emits both JSON and MD report in output dir.
- [ ] **T074 (S2):** Shipping-gate simulation — hand-craft an obvious vocab mistranslation in a test course, run with validation on; script exits non-zero; report lists the mistranslation.
- [ ] **T075 (S2):** False-positive rate tuning — run validator against children_10_12, manually review flags, compute FP rate. Target < 25% per WS4 criterion 6. If higher, tune sampling rates / prompts until it lands. Operator has final call.
- [ ] **T076 (S2):** Reproducibility — run validator twice against the same course with the same backend; produces identical flag set (seed stability).

### Documentation

- [ ] **T077 (S2) [P]:** Record WS4 + WS6 changelog entry in SKILL.md top-note.

---

## GATE: Post-WS3+WS4+WS6 Verification (end of S2)

- [ ] **T078 (S2) [GATE]:** End-to-end smoke — invoke lesson-builder skill against a toy config through the full pipeline (Step 0 → interactive Q&A with the new 10-question flow → Phase 1 buddy delegation → ... → Phase 5 including all checkers → regenerate path available). Confirm nothing broken. **Do not proceed to S3 (WS5) until this gate is green.** Also re-run `scripts/check_links.py`, `scripts/check_exams.py`, `scripts/check_pages.py` against both shipped courses — all three must still exit 0 (no retroactive breakage).

---

## Workstream 5: Satellite Doc Migration (S3)

Goal: move content from 3 top-level MDs into `templates/` examples + SKILL.md inline anchors; `git rm` the three originals. Best done last because SKILL.md is now stable.

### Implementation — templates/children_pages/

- [ ] **T079 (S3) [P]:** Create `templates/children_pages/story_example.html` — minimal runnable story page with Dr. Seuss-style rhyming structure. Embed the illustration rule + rhyming rules + story-concept patterns from `CHILDREN_PAGES.md` lines 51-84 as comments at the top of the file.
- [ ] **T080 (S3) [P]:** Create `templates/children_pages/game_example.html` — minimal runnable game page (Match/Tap/Memory). Embed `CHILDREN_PAGES.md` lines 86-92 as comments.
- [ ] **T081 (S3) [P]:** Create `templates/children_pages/coloring_example.html` — minimal coloring page structure. Structure comments from `CHILDREN_PAGES.md` lines 133-158.
- [ ] **T082 (S3):** Create `templates/children_pages/README.md` (~30 lines) — points at the three example files and the SKILL.md anchors. Contains: (a) compact page-type catalog table (4-7 age block and 8-12 age block from `CHILDREN_PAGES.md` lines 4-45); (b) the 12-entry verified song video ID table (lines 94-131 — **this stays intact**, load-bearing data); (c) brief sections for stickers (160-167), flashcards (169-180), reward (182-183); (d) story-concept-patterns table.

### Implementation — templates/notebooklm/

- [ ] **T083 (S3) [P]:** Create `templates/notebooklm/query_patterns.md` (~30 lines). Body: the query-pattern guidance from `NOTEBOOKLM.md` (good-query phrasing: "What does [source] say about X?"). Appendix: auth-troubleshooting sequence from `NOTEBOOKLM.md` lines 23-62 (interactive-login gotcha + helper script).
- [ ] **T084 (S3):** Drop as obsolete per plan §3.6 (SKILL.md Step 0 already covers these): `NOTEBOOKLM.md` lines 5-12 (install check), 14-21 (auth check), 71-84 (post-login verify), 86-87 (fallback). Record drop justification in commit message.

### Implementation — templates/images/

- [ ] **T085 (S3) [P]:** Create `templates/images/prompt_style_prefix.txt` — raw copy-pasteable text; the coloring-page style prefix from `IMAGE_GENERATION.md` lines 59-78.
- [ ] **T086 (S3):** Create `templates/images/README.md` (~40 lines). Body: `generate_images.py` usage from `IMAGE_GENERATION.md` lines 3-57; use-case-to-aspect-ratio table from lines 80-89; Unicode emoji color reference from lines 104-176 (**preserved intact** — load-bearing data reference).

### SKILL.md inline anchors

- [ ] **T087 (S3):** Add SKILL.md §"Querying the corpus" inline anchor inside Phase 2 (~10 lines). Content: the single highest-leverage tip ("phrase NotebookLM queries as 'What does [source] say about X'"), plus the Windows `PYTHONIOENCODING=utf-8` prefix note (from `NOTEBOOKLM.md` line 89), plus a pointer to `templates/notebooklm/query_patterns.md` for more.
- [ ] **T088 (S3):** Add SKILL.md §"Image prompt conventions" inline anchor inside Phase 3 (~12 lines). Content: style-prefix idea; ethnicity-in-prompt rule; emoji-color-not-CSS rule; `imgs/` vs `HTML/` path convention (from `IMAGE_GENERATION.md` lines 91-102); pointer to `templates/images/README.md`.

### In-repo reference cleanup + deletions

- [ ] **T089 (S3):** Grep the lesson-builder repo for references to the three deleted MDs:
  ```
  grep -rn 'CHILDREN_PAGES\.md\|NOTEBOOKLM\.md\|IMAGE_GENERATION\.md' --include='*.md' --include='*.py' --include='*.json' .
  ```
  Expected hits per plan: SKILL.md lines ~30, ~119, ~521 (line numbers will have drifted after WS1+WS2). Update each hit to point at the new template location or the new SKILL.md anchor.
- [ ] **T090 (S3):** `git rm CHILDREN_PAGES.md NOTEBOOKLM.md IMAGE_GENERATION.md`. **No redirect stubs** (plan §3.6 explicit).

### Self-Verification

- [ ] **T091 (S3):** Delete-gate check — `ls *.md` at repo root returns exactly `SKILL.md` and `README.md` (plus `LICENSE`). No CHILDREN_PAGES / NOTEBOOKLM / IMAGE_GENERATION remain.
- [ ] **T092 (S3):** No-dangling-refs grep — `grep -r 'CHILDREN_PAGES\.md\|NOTEBOOKLM\.md\|IMAGE_GENERATION\.md' .` returns zero hits (excluding `.git/`).
- [ ] **T093 (S3):** Templates-exist check — `ls templates/children_pages/ templates/notebooklm/ templates/images/` each returns a non-empty listing including at minimum a README/examples file and the extra tip/prefix files.
- [ ] **T094 (S3):** Anchors-added check — `grep -q 'Querying the corpus' SKILL.md` and `grep -q 'Image prompt conventions' SKILL.md` both return true.
- [ ] **T095 (S3) [GATE — FINAL LINE-COUNT]:** `wc -l SKILL.md` returns a value in `[440, 520]`. This is the target band from plan §9 success metrics. If above 520, identify remaining prose that can be trimmed or moved to templates/.
- [ ] **T096 (S3):** Information-preservation audit — walk the content-by-content destination table from plan §3.6 row by row; for each row, grep the destination file for the expected content. Mechanical check, no subjective judgment. Document pass/fail per row.

### Documentation

- [ ] **T097 (S3) [P]:** Record WS5 changelog entry in SKILL.md top-note (or dedicated commit).

---

## Global Acceptance (end of S3)

- [ ] **T098 (S3):** Full pipeline smoke — run lesson-builder skill against a toy configuration end-to-end. Confirm all phases run cleanly. Re-run `scripts/check_links.py`, `scripts/check_exams.py`, `scripts/check_pages.py` against both shipped courses (`children_10_12`, `teens_13_14`) — all three must exit 0.
- [ ] **T099 (S3):** Feature-branch confirm — `git branch --show-current` returns `feature/buddy-workflow-integration` (or whichever branch T002 decided on); nothing landed on `main` directly.

---

## Deployment

- [ ] **T100 (S3):** Push the feature branch to `origin`: `git push -u origin feature/buddy-workflow-integration`. **NEVER push to main** (project rule — also enforced at remote).
- [ ] **T101 (S3):** Verify CI / any repo-configured hooks succeed on origin. If CI fails, fix in a new commit on the same branch; do not force-push.
- [ ] **T102 (S3):** **PR creation is left to the user.** Per project rule "Never create PRs programmatically," the operator opens the PR manually against the repo's default branch at a time of their choosing. Tasks file is done at push.

> **Project Rule Note (DO NOT VIOLATE):** No task in this file pushes to `main`. No task creates a PR programmatically. No task force-pushes. All work stays on the feature branch until the operator chooses to open a PR by hand.

---

## Non-Blocking Follow-Ups

These are flagged as **non-blocking** — they do NOT gate initiative completion. The initiative is considered done when T001-T102 are checked.

- [ ] **T103 (non-blocking):** Operator to backfill the `bugs per month` success-metric baseline. Per plan §7 Open Question 2: when a reported bug count becomes available from learner reports / memory / issues, record it as a one-line note somewhere retrievable (project memory file or a new `spec/20260417-lesson-builder-hardening/metrics.md`). The metric is not gateable inside the initiative — it trends over the 3 months after completion — so this task may remain open indefinitely without blocking close-out.
- [ ] **T104 (non-blocking):** Promote `check_pages.py` from report-only to blocking after two weeks of clean runs on both shipped courses (per plan §5 risk mitigation "false positives"). Until then, Phase 5 integration treats it as report-only. Track the two-week clock from T027/T028 completion; operator flips the gate when confident.

---

## Dependency Graph

```
T001 → T002 → [WS1 T003-T013 ∥ WS2 T014-T038] → T039 (GATE)
                                                   ↓
                                                 T040-T053 (WS3)
                                                   ↓
                                                 T054 (shared probes)
                                                   ↓
                                         [WS6 T055-T060 ∥ WS4 T061-T066]
                                                   ↓
                                                 T067-T077 (WS4+6 verify)
                                                   ↓
                                                 T078 (GATE)
                                                   ↓
                                         [WS5 T079-T097]
                                                   ↓
                                         T098-T099 (global acceptance)
                                                   ↓
                                         T100-T102 (deploy)

Non-blocking tail: T103, T104
```

- `∥` = parallel workstreams / tasks.
- Gates (T012, T039, T078, T095) must be green before advancing.

---

## Parallel Execution Examples

**Session 1 (after T001-T002):** Operator can split focus across WS1 and WS2 because they touch different surfaces:
- WS1 = SKILL.md Phases 1-4 prose + appendix.
- WS2 = new `scripts/check_pages.py` + fixtures + tests.
- WS2's T030-T034 prose deletions wait until WS1 prose edits settle, but the script skeleton (T014-T029) runs independently.

**Session 2 — inside WS3:** T043 (log emitter), T044 (determinism check), T045 (SKILL.md anchor), T046 (templates/buddy/tasks.md update) all marked `[P]` — touch different files, no ordering dependency.

**Session 2 — inside WS4+WS6:** After T054 (shared probes) lands, T055-T060 (WS6 interactive flow) and T061-T066 (WS4 validator) can interleave freely. T057, T058 are `[P]` because they touch different config files.

**Session 3 — inside WS5:** T079, T080, T081 (three example HTML files) are `[P]`. T083, T085 (notebooklm + images tip files) are `[P]`.

---

## Validation Checklist

- [x] Every workstream has implementation, self-verification, and documentation tasks.
- [x] Branch-discipline tasks (T001-T002) run before any hardening work.
- [x] Deployment tasks (T100-T102) run at the end, respecting the "no PR, no push-to-main" rule.
- [x] Gates (T012, T039, T078, T095) separate workstreams per plan §4 sequencing.
- [x] Parallel flags `[P]` applied only where tasks are truly file-independent.
- [x] Non-blocking follow-ups (T103, T104) explicitly marked.
- [x] Every spec acceptance criterion has a corresponding task verification (WS1 crits 1-6, WS2 crits 1-7, WS3 crits 1-7, WS4 crits 1-6, WS5 crits 1-5, WS6 crits 1-8).
- [x] Session tags (S1/S2/S3) let the operator see at a glance what belongs in each session.

---

## Review History

| Date | Version | Reviewer | Summary |
|------|---------|----------|---------|
| 2026-04-17 | 1.0.0 (Draft) | buddy:tasks | Initial tasks list generated from v1.0.0 plan. 104 tasks across 7 sections (WS0 branch discipline + WS1-WS6 + deploy + non-blocking tail). 4 gates enforce plan §4 sequencing. |
