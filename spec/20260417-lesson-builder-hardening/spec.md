# Specification: Lesson-Builder Hardening Initiative

**Status:** Ready for Review
**Date:** 2026-04-17
**Initiative ID:** lesson-builder-hardening
**Owner:** ddtraveller@yahoo.com
**Foundation Version:** 1.0.0
**Target Skill Path:** `C:\Users\ddtra\claude\lesson-builder`

## Overview

This specification defines a single coherent improvement initiative for the `lesson-builder` Claude Code skill, organized as **six prioritized workstreams**. Together the workstreams form the next phase of investment in the skill: they thin prose documentation, push correctness rules into executable scripts, add an operational patch path for bug fixes, close the content-truth validation gap aligned with the project mission, consolidate satellite documentation into concrete template examples, and generalize the up-front-backend-choice pattern so all AI/media service decisions (content-truth, image generation, video generation) are surfaced at course-creation time and recorded in the course config.

The initiative is scoped as **ONE investment spanning 2-3 work sessions**. No new page types, no new tracks, and no new research integrations are in scope until workstreams 1-3 have landed.

## Motivation

The lesson-builder skill currently ships real output — the `children_10_12` course (84 files) and `teens_13_14` course (~65 files) are live on krueng.ai. A PM assessment of the skill identified five areas where the current shape of the skill creates drag on future course production:

1. **Workflow duplication.** SKILL.md Phases 1-4 (~150 lines) duplicate the generic spec → plan → tasks → implement workflow that is now available as `buddy:*` skills in the harness.
2. **Prose-encoded correctness rules.** Rules like "avoid these JS bugs" and "verify relative-path depth" are documented as prose the operator must re-read each time; they should be mechanically enforced by scripts in the same spirit as the newly added `check_links.py` and `check_exams.py` (Phase 5).
3. **All-or-nothing regeneration.** A single reported bug (e.g. exam question 12 in unit 7) currently requires touching the full generator pipeline instead of surgical patching.
4. **No content-truth validation.** Phase 5 verifies structural integrity (broken links, malformed exams). The project's core mission is "pedagogical truth > polish," yet nothing verifies translations, grammar explanations, or vocabulary definitions against the research corpus. Because validation consumes real API quota (NotebookLM / Tavily / LLM calls), it is structured as an **opt-in-at-course-creation** capability rather than a forced cost on every course — the operator decides, per course, whether the quota spend is warranted.
5. **Satellite doc rot.** `CHILDREN_PAGES.md` (183 lines), `NOTEBOOKLM.md` (89 lines), and `IMAGE_GENERATION.md` (175 lines) live alongside `SKILL.md` as loose prose that drifts from reality; they should become concrete template examples or inline anchors and the top-level files deleted outright.

## Scope

### In Scope

- Five workstreams enumerated below, delivered in priority order.
- Changes to `SKILL.md`, new scripts under `scripts/`, new example files under `templates/`, and targeted file deletions.
- Quality bar defined by the acceptance criteria per workstream and the global success metrics.

### Out of Scope (Non-Goals)

- New page types (no new exam formats, no new game mechanics, no new story structures).
- New learner tracks beyond the two shipped courses.
- New research integrations beyond existing NotebookLM and Tavily backends.
- Platform-ification (no multi-user support, no UI, no web dashboard).
- Retrofitting of already-shipped courses — `children_10_12` and `teens_13_14` generator scripts remain untouched. New rules apply to future courses.

### Backward Compatibility

The two shipped courses (`children_10_12`, `teens_13_14`) MUST NOT break as a result of this initiative. Their generator scripts may be left alone. Any new validators (workstreams 2 and 4) MAY be run against shipped output in a "report-only" mode but MUST NOT block the deploy of already-shipped content.

## Foundation Alignment

This initiative aligns with the project foundation (version 1.0.0) as follows:

| Principle | Alignment |
|-----------|-----------|
| 1. Zero-Dependency Static Architecture | New scripts are build-time Python tools — exempt from runtime-dependency rules. Generated HTML remains standalone. |
| 2. Thai-First Bilingual Content Design | Workstream 4 (content-truth validator) directly protects the Thai-first pedagogical commitment by verifying translations against the research corpus. |
| 3. Strict Deployment Separation | No changes to HTML/media deployment. New scripts stay in the skill repo. |
| 4. Feature Branch Git Workflow | All implementation work MUST occur on a feature branch (e.g. `lesson-builder-hardening`). |
| 5. AI-Assisted Content Generation Pipeline | Core intent is to strengthen the pipeline: more validation, more surgical regeneration, better delegation to reusable skills. |

## Workstream 1: Delegate Phases 1-4 to `buddy:*` Skills

**Priority:** 1 (highest leverage, lowest risk)

### Goal

Replace the ~150 lines of inline spec/plan/tasks/implement workflow in SKILL.md Phases 1-4 with invocations of the corresponding `buddy:*` plugin skills (`buddy:spec`, `buddy:plan`, `buddy:tasks`, `buddy:implement`).

### Rationale

The `buddy:*` namespace already provides the generic workflow logic. Maintaining a parallel copy in lesson-builder is duplication that ages poorly — bug fixes and template improvements in `buddy:*` never flow back to lesson-builder. By delegating, lesson-builder becomes a thin, TEFL-specific shell on top of shared infrastructure.

### Behavior

- SKILL.md Phases 1-4 are rewritten to (a) invoke the relevant `buddy:*` skill with the TEFL-specific context and (b) document the TEFL-specific overlays (templates, worked example, research integration with NotebookLM/Tavily) that are not part of the generic buddy workflow.
- Spec/plan/tasks artifacts still land at `specs/{YYYYMMDD}-{course_id}/` (matching the existing convention used by `EXAMPLE-tefl_children_10_12/`).
- TEFL-specific templates (vocabulary density, bilingual markup, page-type catalog, theme palette conventions) remain inlined or linked from SKILL.md Phase 1-4 sections.
- The skill continues to handle the TEFL-specific research integration (NotebookLM corpus loading, Tavily fallback) during its delegated Phase 2 call.

### Graceful Fallback (No Hard Dependency)

Lesson-builder MUST detect at runtime whether `buddy:spec`, `buddy:plan`, `buddy:tasks`, and `buddy:implement` are present in the harness. Detection happens once, at the start of Phase 1.

- **If the `buddy:*` skills are available:** delegate Phases 1-4 to them and treat that as the canonical path.
- **If any of the `buddy:*` skills are NOT available:** fall back to a **minimal inline workflow** that produces the **same artifact shape** (`specs/{YYYYMMDD}-{course_id}/spec.md`, `plan.md`, `tasks.md`) so the skill still runs standalone.

The inline fallback is intentionally minimal — it is a **safety net, not a second canonical path**. It MUST NOT re-grow into a full parallel implementation of the buddy workflow. Its sole job is to let a user without `buddy:*` installed still produce spec/plan/tasks artifacts in the expected file layout. SKILL.md should state this explicitly so future contributors do not "improve" the fallback into a second system to maintain.

### Acceptance Criteria

1. `SKILL.md` shrinks by approximately 150 lines relative to its current 787-line state.
2. A dry-run course authoring session (e.g. "create a course for adult learners A2-B1") produces spec, plan, and tasks artifacts at `specs/{YYYYMMDD}-{course_id}/spec.md`, `plan.md`, `tasks.md`.
3. TEFL-specific templates and conventions continue to apply (vocabulary density, bilingual markup, file naming).
4. The worked example (children_10_12) remains referenced and discoverable from SKILL.md.
5. Skill works both **with** `buddy:*` installed (delegated path) and **without** (minimal inline fallback), and produces identically-shaped artifact directories in both modes.
6. SKILL.md explicitly documents that the inline fallback is a safety net and MUST remain minimal.

## Workstream 2: Promote Prose Rules into `check_pages.py`

**Priority:** 2 (high leverage)

### Goal

Extend the Phase 5 verification scripts with a new `scripts/check_pages.py` that mechanically enforces rules currently written as prose in SKILL.md, then delete those prose sections.

### Rationale

Prose rules must be re-read by the operator (human or AI) before each generation, and there is no guarantee they are applied. Mechanical checks run every time and never forget. This also lets the skill evolve: as new failure modes are observed, they become test cases rather than new paragraphs of prose.

### Rules To Mechanically Enforce

The new `scripts/check_pages.py` script MUST, for each generated HTML file under the course's `output_dir`, check:

| # | Rule | Failure Example |
|---|------|-----------------|
| 2.1 | **No undefined function references in JS** | A `<script>` block calls `playSound()` but no function of that name is defined in the same block or file. |
| 2.2 | **No Python-style `\'` escapes inside emitted JS strings** | Generator emits `onclick="handleClick(\'foo\')"` where `\\'` should have been `'`. |
| 2.3 | **No SVG attribute quote collisions inside single-quoted JS strings** | `innerHTML = '<svg viewBox=\'0 0 10 10\'>...'` — inner `'` collides with outer `'`. |
| 2.4 | **`speechSynthesis.cancel()` guard present before `.speak()`** | Every call site that kicks off new TTS speech has a preceding `speechSynthesis.cancel()` to prevent queue stacking. |
| 2.5 | **Relative-path depth matches `output_dir`** | A file at `HTML/tefl/children_10_12/foo.html` using `../../imgs/bar.png` must resolve to a path that actually exists. May consolidate with or extend the existing check in `check_links.py`. |
| 2.6 | **`<img>`/`<video>` `src` attributes match actual files on disk** | The English Quest filename-mismatch bug class: HTML references `quest_cover.png` but the file on disk is `quest-cover.png`. |
| 2.7 | **Every `<script>` block parses as valid JS** | Use `node --check` when Node is on PATH; otherwise fall back to a pure-Python check focused on the highest-value failure patterns. |

### JS Parsing Strategy — Hybrid (Node-First, Python-Fallback)

Rule 2.7 uses a **runtime-detected hybrid strategy** so Node.js is NOT a hard install requirement:

1. **Node available (preferred):** If `node` is on PATH, shell out to `node --check <tempfile>` per `<script>` block. This gives accurate, full-grammar JS parsing that catches the broadest class of syntax errors.
2. **Node absent (fallback):** If `node` is not on PATH, use a pure-Python check that covers the **highest-value failure patterns** observed in prior generation bugs — things like unbalanced brackets/braces/parens, unterminated string literals, obvious quote-collision patterns, and Python-style escape leakage (`\'` inside emitted JS). This is deliberately narrower than a full parser but catches the bugs this skill has historically shipped.
3. **Implementation preference for fallback:** Start with a regex-and-bracket-counting sanity check. Only reach for a dependency like `esprima-python` if the regex layer proves insufficient AND the dependency stays lightweight and pure-Python.
4. **Reporting:** `check_pages.py` MUST log which mode it ran in (`"js-parse: node"` or `"js-parse: python-fallback"`) so the operator knows what level of rigor was applied.

Detection happens per-invocation; do not cache across runs.

### Interface

- Command: `python scripts/check_pages.py <output_dir>`
- Exit code: `0` on pass, non-zero on any rule violation.
- Output: per-file, per-rule summary with file path, line number (where derivable), and human-readable failure description. First line of output declares the JS-parse mode in use.

### Prose Deletions

Once the script exists and passes against `children_10_12` and `teens_13_14`, the following prose sections MUST be deleted from `SKILL.md`:

- "Common JS bugs to avoid"
- "Relative path depth" (if fully subsumed by the script)
- "Filename convention coordination"
- The portions of "Unit 1 verification gate" that are now mechanically checked

### Acceptance Criteria

1. Every failure mode listed in the Rules table (2.1 through 2.7) has a corresponding **unit test case** in `scripts/check_pages.py` (or a sibling test file) that exercises both the pass and fail path.
2. Running `python scripts/check_pages.py HTML/tefl/children_10_12/` on the shipped course produces exit code 0 (report-only mode — no blocking regressions).
3. Running against a deliberately broken fixture produces a non-zero exit code and a readable diagnostic.
4. The corresponding prose sections are deleted from SKILL.md, further reducing line count beyond workstream 1.
5. The tasks.md template's Phase 5 entry includes a `check_pages.py` step alongside `check_links.py` and `check_exams.py`.
6. Rule 2.7 runs successfully **both** with Node installed and without — verified by temporarily unsetting Node on PATH and re-running the script against the two shipped courses.
7. Script output states which JS-parse mode (`node` vs `python-fallback`) was used on this run.

## Workstream 3: Add a `regenerate --page` / `--question` Patch Path

**Priority:** 3 (operational win)

### Goal

Provide a `scripts/regenerate.py` utility that lets the operator fix a single reported bug by regenerating exactly one page (or, optionally, one exam question) without touching the other 83 files in a 12-unit course.

### Rationale

When a learner reports "unit 7's exam question 12 has a wrong answer," the current workflow requires either (a) re-running the full generator — which touches all files, risks re-introducing previously-fixed issues, and is slow — or (b) hand-editing the HTML, which drifts the generated output away from the config that produced it. A targeted regenerate script solves both problems.

### Behavior

`regenerate.py` ships with **both** page-level and question-level granularity from day one:

- **Page-level (the 80% case):** regenerate one full page — an exam, a flashcards set, a story, etc. — for a given unit. Loads the course config, locates the generator function for the specified page type, regenerates **only** that one output file, and overwrites it in place.
- **Question-level (the surgical case):** regenerate a single exam question inside an existing exam page, identified by `CATEGORY:DIFFICULTY:INDEX`. Edits the embedded JS data structure within the existing page, leaving all other questions and the surrounding page chrome untouched. This path exists specifically for learner-reported single-question bugs where regenerating the whole exam page would perturb unrelated questions the learner has already trusted.

Both paths share the course-config loader, the generator dispatch table, and the determinism check; the question-level path adds an extra "surgically splice into existing HTML" step on top.

### Command Shape

- `python scripts/regenerate.py --course <course_id> --unit <N> --page-type <type>` — page-level
- `python scripts/regenerate.py --course <course_id> --unit <N> --exam-question <CATEGORY>:<DIFFICULTY>:<INDEX>` — question-level

### Example Invocations

```
# Page-level: regenerate unit 7's exam page only
python scripts/regenerate.py --course children_10_12 --unit 7 --page-type exam

# Page-level: regenerate unit 3's flashcards page
python scripts/regenerate.py --course teens_13_14 --unit 3 --page-type flashcards

# Question-level: regenerate just question 4 in the medium-difficulty vocab bucket of unit 7's exam
python scripts/regenerate.py --course children_10_12 --unit 7 --exam-question vocab:medium:4

# Question-level: fix a single grammar question a learner flagged in unit 9
python scripts/regenerate.py --course teens_13_14 --unit 9 --exam-question grammar:hard:2
```

### Acceptance Criteria

1. An operator can, given a bug report pinpointing one page, regenerate and redeploy the fix in **under 5 minutes** without touching other pages.
2. An operator can, given a bug report pinpointing one exam question, regenerate just that question and leave sibling questions byte-identical.
3. The regenerate script refuses to run against a course that is not in its supported courses list (guard against unintentional mass regeneration).
4. The page-level output is byte-for-byte equivalent to what the full generator would produce for that one page (determinism check).
5. The question-level path, when invoked with the same inputs a full generator would use, produces a page whose diff against a full regenerate is limited to exactly the targeted question block.
6. Regeneration events (both page-level and question-level) are logged to the course's directory so the operator can audit what was patched when.
7. Invalid or unresolvable question coordinates (e.g. `vocab:medium:99` when the bucket has only 10 items) fail fast with a readable error, not silent success.

## Workstream 4: Phase 5c Content-Truth Validator

**Priority:** 4 (mission-aligned)

### Goal

Close the content-truth gap in Phase 5 verification. The current Phase 5 scripts check structural issues (`check_links.py`, `check_exams.py`) and — after workstream 2 — common page-level bugs (`check_pages.py`). None of these verify that a Thai translation is **correct**, that a grammar explanation is **accurate**, or that a vocabulary definition matches **canonical sources**. This workstream adds a content-truth validator aligned with the mission "pedagogical truth > polish."

### Rationale

The worst learner-impacting bug class is not a broken link — it is a confidently stated wrong answer. An exam that marks the wrong option as correct teaches the learner incorrectly. A vocabulary card with a slightly-off Thai gloss teaches a meaning the learner will have to unlearn later. These bugs are invisible to structural checks.

### Opt-In Backend Choice (Set at Course-Creation Time)

Content-truth validation is **opt-in per course** because it consumes real API quota (NotebookLM sessions, Tavily credits, or second-model LLM calls). The operator chooses a backend once, when the course is created, and the choice is persisted in the course config.

This is one instance of a **generalized up-front-backend-choice pattern** (see Workstream 6). The course-creation flow surfaces three backend questions up-front — content-truth (this workstream), image generation, and video generation — and records all three in the course config as a coherent group. Content-truth validation is not a one-off; it is the exemplar of the pattern.

#### Config Field

The course config gains a new field:

```yaml
content_truth:
  backend: tavily | notebooklm | off
```

- **`tavily`** — Validator uses `tvly research` against the live web to cross-check sampled items (e.g. "Is the Thai gloss for 'abundant' actually 'อุดมสมบูรณ์'?"). Appropriate when a research notebook wasn't built or the topic is better served by live-web cross-reference.
- **`notebooklm`** — Validator queries the research notebook built during Phase 2. Appropriate when the course has a dedicated NotebookLM corpus and the operator wants the checker to stay inside that curated body of sources.
- **`off`** — Phase 5c is skipped entirely. No quota is spent.

#### Prompting at Course Creation

In interactive mode, when the user creates a new course, the skill MUST prompt up-front:

> Content-truth validation backend? [tavily / notebooklm / off]

In config-driven (non-interactive) mode, the operator sets `content_truth.backend` directly in the course config file.

#### Default Behavior

If the operator gives no answer and the config does not set `content_truth.backend`, the default is **`off`**. This keeps quota spend opt-in and prevents surprise costs. The operator may override per-course in the config.

### Approach

When `content_truth.backend` is `tavily` or `notebooklm`, `scripts/check_content.py` samples items from the course and cross-checks them against the chosen source of truth:

| Content Type | Sample Rate | Source of Truth (tavily) | Source of Truth (notebooklm) |
|--------------|-------------|--------------------------|------------------------------|
| Vocabulary cards (Thai gloss) | ~20% per unit | `tvly research` query per sampled pair | NotebookLM corpus query |
| Grammar explanation boxes | ~10% per unit | `tvly research` query citing authoritative sources | NotebookLM corpus citation check |
| Exam correct-answer markings | 100% of exam questions | Second-model adversarial pass, optionally grounded by `tvly research` | Second-model adversarial pass grounded by NotebookLM |

For each sampled item, the script:

1. Extracts the item from its generated HTML (vocabulary pair, grammar rule, exam Q + correct-answer tag).
2. Poses the check to the chosen backend.
3. If the backend disagrees or cannot confirm, raises a **content-truth flag** tied to that item.

When `content_truth.backend` is `off`, `check_content.py` exits cleanly and reports "Phase 5c skipped by config" — Phase 5 proceeds with only the structural checks (`check_links.py`, `check_exams.py`, `check_pages.py`).

### Shipping Gate

A course **with content-truth validation enabled** (`tavily` or `notebooklm`) that has any **unresolved** content-truth flag MUST NOT ship. Flags may be resolved by (a) fixing the item, (b) marking the flag as a false positive with a written justification, or (c) the operator explicitly overriding on a per-flag basis.

A course with `content_truth.backend: off` has no content-truth gate; the operator has explicitly accepted the trade-off.

### Tuning

False-positive rate tuning is expected — the first pass will likely flag true-correct items that the source of truth cannot disambiguate. Thresholds, sample rates, and model prompts MUST be iterated until false-positive rate is low enough for routine use. Workstream 4 is considered "complete" when the validator can run on the `children_10_12` course under at least one backend (`tavily` or `notebooklm`) and produce a flag set the operator agrees is either real or explicitly overridable.

### Acceptance Criteria

1. `scripts/check_content.py` exists and runs to completion against a shipped course without crashing, under any of the three `content_truth.backend` values.
2. When `backend: off`, the script exits 0 and reports that Phase 5c was skipped by config — no quota is consumed.
3. When `backend: tavily` or `backend: notebooklm`, the script produces a structured flag report (JSON or Markdown) listing flagged items with their location, the source-of-truth disagreement, and a suggested resolution.
4. A course with validation enabled CANNOT ship (per the new Phase 5c gate documented in SKILL.md) with unresolved flags. A course with validation off has no Phase 5c gate.
5. Interactive course-creation flow prompts the operator for the backend choice up front and records the answer in the course config.
6. The initial run's false-positive rate is low enough to be usable — target less than 25% false positives on the two shipped courses during tuning (using whichever backend the operator elects for each), with the final acceptable rate determined by the operator during tuning.

## Workstream 5: Fold Satellite Docs into `templates/`

**Priority:** 5 (housekeeping)

### Goal

Eliminate the top-level prose documentation files `CHILDREN_PAGES.md`, `NOTEBOOKLM.md`, and `IMAGE_GENERATION.md` by migrating their content into either concrete example files under `templates/` or inline anchors in `SKILL.md`.

### Rationale

Prose documentation rots. A 183-line file describing "how children pages should look" goes stale the moment the style evolves. A concrete example file (`templates/children_pages/story_example.html`) that gets updated alongside the style stays in sync by construction — it's either correct or the example is broken in a visible way. Tips that truly need to be prose (e.g. "when querying NotebookLM for grammar rules, prefer questions phrased as 'What does [source] say about...'") become short tip files or inline anchors.

### Migration Plan — Outright Delete, No Redirect Stubs

The three satellite docs are not referenced from anywhere outside the repo, so they are **deleted outright** after their content lands in its new home. No redirect stubs are left behind.

| Source File | Content Lands At | Final State |
|-------------|------------------|-------------|
| `CHILDREN_PAGES.md` (183 lines) | `templates/children_pages/story_example.html`, `templates/children_pages/game_example.html`, `templates/children_pages/README.md` (short, example-focused — points at the example files) | Source file **deleted** |
| `NOTEBOOKLM.md` (89 lines) | `templates/notebooklm/query_patterns.md` (short tip file) plus inline "Querying the corpus" anchor inside SKILL.md Phase 2 | Source file **deleted** |
| `IMAGE_GENERATION.md` (175 lines) | `templates/images/prompt_style_prefix.txt`, `templates/images/README.md`, plus inline "Image prompt conventions" anchor inside SKILL.md Phase 3 | Source file **deleted** |

For each of the three migrations:

1. Extract the prose into the listed target files (examples + short READMEs under `templates/`, plus inline SKILL.md anchors where the guidance is better positioned alongside the phase it applies to).
2. Update any in-repo references (SKILL.md body text, cross-links between the satellite docs themselves) to point at the new locations.
3. `git rm` the original top-level file.

Do not leave a one-line stub pointing at the new location — the git history preserves the old content for anyone who ever needs it, and a stub is just another file to age.

### Acceptance Criteria

1. The top-level directory contains **no loose prose `.md` files** beyond `SKILL.md`, `README.md`, and the existing `LICENSE`. The three satellite docs are gone, with no redirect stubs.
2. The `templates/children_pages/`, `templates/notebooklm/`, and `templates/images/` directories exist and each contains at least one concrete example file plus a short `README.md`.
3. SKILL.md contains inline anchors (short subsections) for "Querying the corpus" (Phase 2) and "Image prompt conventions" (Phase 3) covering the highest-leverage tips migrated from the deleted files.
4. No information is lost in the migration — each piece of prose has either been (a) turned into an example, (b) turned into a short tip file, (c) inlined as a SKILL.md anchor, or (d) explicitly determined to be obsolete and dropped with justification recorded in the commit message.
5. All in-repo references to the deleted satellite docs (grep `CHILDREN_PAGES.md`, `NOTEBOOKLM.md`, `IMAGE_GENERATION.md` across the repo) are updated or removed.

## Workstream 6: Up-Front Media Backend Choices (Generalized Pattern)

**Priority:** 6 (consistency / operator-clarity)

### Goal

Generalize the up-front-backend-choice pattern introduced by Workstream 4 so that **image generation** and **video generation** backends are also chosen at course-creation time, not buried as defaults the operator only discovers when something breaks. All three backend choices — content-truth (Workstream 4), images, and video — are surfaced together near the top of the interactive course-creation questionnaire and recorded in the course config as a coherent group.

### Rationale

Today the image-generation backend is implied by whether `REPLICATE_API_TOKEN` is set and the `images.enabled` config flag is on, and there is no first-class video backend choice at all (HeyGen and Remotion are assumed wherever referenced in prose). That means operators discover their media-pipeline configuration late — often after a lesson has been drafted and the generator is ready to emit media — and mis-configured pipelines either silently fall back to no-media or surprise-spend on paid APIs. Pulling the decisions to the top of the flow, in the same shape as the content-truth backend choice, makes every AI/media service decision explicit, auditable, and reproducible from the course config alone.

This workstream is **scope-limited to asking the question and wiring the config fields**. It does NOT build any new media backend. If a listed backend (e.g. the `webm` pipeline) is not yet implemented in the repo, the spec acknowledges that and `off` is the effective runtime result for that choice until a future initiative implements the backend.

### Image Generation Backend Choice

#### Config Field

The course config gains a new field that **replaces / supplements** the existing `images.enabled + images.provider + images.model` trio:

```yaml
images:
  backend: flux | off
```

- **`flux`** — Generate images via Black Forest Labs FLUX through Replicate (the current default path when `REPLICATE_API_TOKEN` is set). Matches the existing behavior the skill already implements.
- **`off`** — No image generation. Existing shipped images are left alone; no new images are created.

The field is intentionally forward-compatible: additional backends (e.g. Stability AI, nano-banana) can be added as enum values without spec rework.

#### Interactive Prompt

In interactive mode, when the user creates a new course, the skill MUST prompt:

> Image generation backend? [flux / off]

#### Default and Availability Check

- **Default when unspecified:** `off`. This matches the current Step 0 behavior when the Replicate token is missing and keeps operators from incurring surprise spend.
- **Availability check:** If the operator chooses `flux` but `REPLICATE_API_TOKEN` is not available in the environment, the skill MUST warn visibly and fall back to `off`. Silent fall-through is forbidden — the operator must know the backend they picked isn't actually reachable.

### Video Generation Backend Choice

#### Config Field

The course config gains a new field:

```yaml
video:
  backend: heygen | remotion | capcut | webm | off
  max_count: <int>   # per-course cap; see Risks
```

- **`heygen`** — Avatar / lipsync video via the HeyGen API. HeyGen lesson videos cost approximately **$2 each** on the operator's current plan (per user memory `reference_heygen_video_cost.md`).
- **`remotion`** — React-based programmatic video, leveraging the existing Remotion project at `watdonchan/ai-english-video/`. Free beyond compute cost.
- **`capcut`** — Prompt-to-human workflow. The skill emits an edit plan and an asset manifest; the operator assembles the final video manually in CapCut. Free (manual labor only).
- **`webm`** — Lightweight screen-capture / slides-to-webm pipeline (e.g. `ffmpeg`-driven). Free beyond compute cost. **Note:** this pipeline may not yet be implemented in the repo at the time Workstream 6 lands. If absent, the operator choosing `webm` triggers a fall-back to `off` with a visible warning, exactly the same shape as a missing API key.
- **`off`** — No video generation for this course.

#### Interactive Prompt

In interactive mode, when the user creates a new course, the skill MUST prompt:

> Video generation backend? [heygen / remotion / capcut / webm / off]
> (HeyGen: ~$2 per lesson video on current plan. Remotion / CapCut / webm: free.)

Cost awareness is surfaced inline so the operator picks knowingly.

#### Default and Availability Check

- **Default when unspecified:** `off`.
- **Availability check per backend:**
  - **`heygen`:** probe SSM for the `heygen` API key (`aws ssm get-parameter --name heygen --profile deploy --region us-west-2`). If absent or unreadable, warn and fall back to `off`.
  - **`remotion`:** probe for a usable Node install and a reachable Remotion project (e.g. the existing `watdonchan/ai-english-video/` directory with `remotion` in its `node_modules`). If absent, warn and fall back to `off`.
  - **`capcut`:** no availability check — it's a prompt-to-human workflow. The skill emits an edit plan regardless; the operator is responsible for running that plan through CapCut.
  - **`webm`:** probe for whatever tooling the webm pipeline uses (e.g. `ffmpeg` on PATH, plus the webm pipeline scripts themselves). If the pipeline hasn't been built yet, treat as **NOT-YET-IMPLEMENTED** and fall back to `off` with a clear warning ("webm pipeline is not yet implemented in this skill; falling back to `off`").

All availability checks happen **before** the operator's choice is committed to the config, so the config never records a backend the environment can't actually service.

### Unified Course Config Schema (Backend Group)

After Workstreams 4 and 6, the course config includes the following cohesive **backend choices group**, which operators should see together as one logical section of the config:

```yaml
# AI / media service backends — all chosen up-front at course-creation time
content_truth:
  backend: tavily | notebooklm | off   # see Workstream 4

images:
  backend: flux | off                   # see Workstream 6

video:
  backend: heygen | remotion | capcut | webm | off   # see Workstream 6
  max_count: <int>                      # per-course cap to bound spend
```

No implicit backend choices. A course can be recreated from config alone.

### Interactive Flow — Ordering

The three backend questions MUST be asked together, up-front, near the top of the interactive course-creation questionnaire — immediately after the existing topic / language-pair / weeks questions and **before** any content drafting begins. They are not sprinkled through phases. Operator reads the group and answers it as one decision about "what services this course will use," then never has to revisit these choices unless they explicitly edit the config.

### Acceptance Criteria

1. The interactive course-creation prompt asks all **three** backend questions up-front — content-truth, images, video — in addition to the existing topic/language/weeks questions. The three prompts appear as a contiguous block near the top of the questionnaire.
2. All three choices are recorded in the course config under the documented field names (`content_truth.backend`, `images.backend`, `video.backend`).
3. Each backend's availability is probed **before** the operator's choice is committed. Unavailable backends fall back to `off` with a visible warning — never silent failure.
4. A course can be recreated from config alone: running the skill in non-interactive / config-driven mode with all three fields present produces the same pipeline configuration as an equivalent interactive session.
5. The HeyGen cost note (~$2 per video, per user memory) is surfaced in the interactive prompt when `heygen` is offered, so the operator chooses knowingly.
6. `video.max_count` is honored: if generation would exceed the cap, the skill halts with a readable error rather than silently producing more than the cap.
7. The `webm` backend, if not yet implemented, is handled explicitly — the operator choosing `webm` sees a "not-yet-implemented, falling back to `off`" warning rather than a crash or silent no-op.
8. SKILL.md documents the backend-choices group as one coherent up-front step, with the three fields shown together and the ordering rule (up-front, contiguous block) stated explicitly.

> **Footnote on "FLEX":** The original requirement text referred to "FLEX" as a possible image backend. This spec interprets that as **FLUX** (Black Forest Labs FLUX, invoked via Replicate), which is the image model the skill already uses per the existing `images.enabled` config. No separate "FLEX" backend is introduced; the name is normalized to FLUX for traceability.

## Success Metrics

The initiative succeeds if **all three** of the following improve relative to a baseline taken before work begins:

| Metric | Baseline (2026-04-17) | Target |
|--------|-----------------------|--------|
| `SKILL.md` line count | 787 lines | Approximately 450-500 lines (~35-40% reduction) after workstreams 1 and 2 |
| Shipped bugs learners report per month | TBD (operator to record baseline) | Downward trend over the three months following completion |
| Time-to-patch for a reported page-level bug | Full pipeline re-run (minutes to tens of minutes) | Under 5 minutes after workstream 3 lands |

## Dependencies and Sequencing

- Workstream 1 (buddy delegation) and Workstream 2 (`check_pages.py`) are **independent** and may proceed in parallel.
- Workstream 3 (`regenerate.py`) depends on Workstream 1 being done or at least having a stable artifact directory convention — regenerate needs to know where to write.
- Workstream 4 (content-truth) depends on Phase 2 research integration being unchanged; it leverages the NotebookLM corpus already loaded by the skill.
- Workstream 5 (docs migration) can happen any time but is best done **last** because inlining anchors into SKILL.md is easier after workstreams 1 and 2 have finished reshaping SKILL.md.
- Workstream 6 (up-front media backend choices) is tightly coupled to Workstream 4 — they share the interactive-prompt touchpoint and the course-config schema. Doing them in the same session avoids touching the creation flow twice.

Recommended order: **1, 2 (parallel) → 3 → 4 + 6 (together) → 5**.

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| `buddy:*` skills have subtle behavior differences from the current inline Phases 1-4 | Medium | Medium | Run a dry-run course-authoring session after workstream 1; compare output artifacts against a current-state baseline. |
| Graceful-fallback path grows into a second canonical implementation | Medium | Medium | SKILL.md explicitly documents the fallback as minimal-safety-net-only; acceptance criterion 6 for Workstream 1 reinforces this in-repo. |
| `check_pages.py` false positives block legitimate output | Medium | Low | Report-only mode initially; promote to blocking only after a clean run on the two shipped courses. |
| Python-fallback JS check misses errors `node --check` would have caught | Medium | Low | Scope fallback to historically-observed failure patterns; script logs which mode ran so the operator can re-run under Node when rigor matters. |
| `regenerate.py` drifts from full-generator output (non-determinism) | Low | Medium | Add a determinism check: regenerate + diff against full-generator output for the same target; fail the acceptance test if diff is non-empty. |
| Question-level splice corrupts surrounding exam HTML | Low | Medium | Diff-scope acceptance test (criterion 5 of Workstream 3) fails if the question-level path changes anything outside the targeted question block. |
| Content-truth validator produces too many false positives to be usable | Medium | Medium | Tuning phase built into Workstream 4's acceptance criteria; backend is opt-in so operators can disable it while tuning. |
| Operator forgets they selected `tavily` or `notebooklm` and burns unexpected quota | Low | Low | Backend choice is recorded in the course config; `check_content.py` prints the active backend on startup. |
| Operator picks `heygen` without realizing per-video cost → course racks up $50+ unexpectedly | Medium | Medium | Cost note surfaced inline in the interactive prompt (~$2/video); per-course `video.max_count` cap enforced before generation proceeds. |
| Operator selects `webm` before the webm pipeline is implemented → silent no-media course | Low | Low | Availability check treats missing webm pipeline as NOT-YET-IMPLEMENTED and falls back to `off` with a visible warning (acceptance criterion 7 of Workstream 6). |
| Operator selects `remotion` but the `ai-english-video/` Remotion project isn't reachable → generator fails mid-run | Low | Medium | Availability check probes the Remotion install before committing the choice; falls back to `off` with a visible warning rather than failing mid-generation. |

## Assumptions Made

- The `buddy:*` plugin is commonly available in the user's harness (evidenced by its appearance in the available-skills list), but the skill MUST NOT require it — graceful fallback is specified in Workstream 1.
- The existing `EXAMPLE-tefl_children_10_12/` spec layout is the canonical template for course-level artifacts and the same convention applies to this skill-level spec (placed under `spec/` rather than `specs/` to distinguish skill-hardening work from course-authoring work).
- NotebookLM access is stable enough to support Workstream 4's validator queries when the `notebooklm` backend is selected; Tavily (`tvly research`) is stable enough when the `tavily` backend is selected.
- Node.js MAY or MAY NOT be on PATH; Workstream 2's hybrid JS-parse strategy handles both cases without requiring a change in user environment.
- The two shipped courses (`children_10_12`, `teens_13_14`) are considered frozen for the purposes of this initiative — their generator scripts are not modified. Retroactively setting `content_truth.backend` for these courses is optional; the default of `off` means they remain shippable without new validation work.
- The HeyGen API key is stored in AWS SSM Parameter Store at parameter name `heygen` (us-west-2, retrievable via the `deploy` profile), per the project's standard SSM convention.
- A Remotion-capable project already exists at `watdonchan/ai-english-video/` and is the assumed entry point for the `remotion` video backend. Workstream 6's availability check probes for this project; it does not create one.
- The `webm` video pipeline MAY NOT yet exist in the repo at the time Workstream 6 lands. The spec explicitly calls this out as possibly-unimplemented-at-plan-time; Workstream 6 wires the config slot and the availability check, but does NOT commit to implementing the pipeline itself.
- The operator's current HeyGen plan pricing (~$2 per lesson video, per user memory `reference_heygen_video_cost.md`) is stable for the duration of this initiative; if pricing changes, the interactive prompt's cost hint can be updated in a follow-up change without invalidating the spec.

## Out-of-Scope Clarifications

The following are explicitly NOT part of this initiative and should be deferred to a future spec:

- A UI or web dashboard for the skill.
- Multi-user support or collaboration features.
- Additional page types (e.g. listening comprehension with audio, interactive dialogues with TTS).
- New research backends beyond NotebookLM and Tavily.
- Retrofitting shipped courses to conform to new validation rules.
- **Implementing new media backends.** Workstream 6 wires the config fields and the up-front prompts for `heygen / remotion / capcut / webm`, but it does NOT build any of those pipelines that don't already exist in the repo. In particular, if the `webm` pipeline has not been built, this initiative does NOT build it — the `webm` choice falls back to `off` with a visible warning until a future initiative implements it. Likewise, the `capcut` workflow beyond "emit an edit plan + asset manifest" is out of scope here.
- Adding image generation backends beyond `flux` (e.g. Stability AI, nano-banana). The `images.backend` enum is designed to accept future values, but adding them is out of scope for this initiative.

## Clarifications Received

All five open clarifications from the initial draft were resolved by the operator on **2026-04-17**. The answers are recorded below and have been folded into the corresponding workstream sections above.

### 1. Workstream 1 — Buddy dependency

**Question:** Is it acceptable for lesson-builder to have a hard dependency on the `buddy:*` plugin, or should it degrade gracefully if `buddy:*` is not installed?

**Answer — Graceful fallback.** Lesson-builder should detect whether `buddy:spec / buddy:plan / buddy:tasks / buddy:implement` are available. If yes, delegate. If not, fall back to a minimal inline workflow that produces the same artifact shape (`specs/{date}-{course_id}/spec.md` etc.) so the skill still works standalone. The spec notes that the inline fallback is intentionally minimal — it's a safety net, not a second canonical path to maintain.

### 2. Workstream 2 — Node.js availability

**Question:** Is Node.js available in the user's environment for `check_pages.py` to use `node --check` for JS parsing (rule 2.7), or must the script be pure Python?

**Answer — Hybrid.** `check_pages.py` should use `node --check` when Node is on PATH (more accurate JS parsing), and fall back to a pure-Python check (regex-based for the highest-value failure patterns, or `esprima-python` if lightweight enough) when Node isn't available. Detect at runtime; don't make Node a hard install requirement.

### 3. Workstream 3 — Regenerate granularity

**Question:** What granularity matters most from day one — page-level, question-level, or both? If only one, which?

**Answer — Both.** `scripts/regenerate.py` should support both page-level (`--unit N --page-type exam`) and question-level (`--unit N --exam-question CATEGORY:DIFFICULTY:INDEX`) from day one. Page-level is the 80% case; question-level is the surgical case for learner-reported single-question bugs. Implement both.

### 4. Workstream 4 — Content-truth cost

**Question:** Is the operator willing to spend NotebookLM / API quota on validation passes for every future course, or should content-truth validation be opt-in per course? If opt-in, what is the default?

**Answer — Opt-in at course-creation time, with backend choice.** When the user creates a new course (interactive mode or config), prompt up-front: "Content-truth validation backend? [tavily / notebooklm / off]". The choice is recorded in the course config (`content_truth.backend`). Neither tavily nor notebooklm is forced on every course. Default behavior when the user gives no answer: **off** (can be overridden in config). If `tavily` is chosen, the validator uses `tvly research` to cross-check sampled items; if `notebooklm`, it queries the research notebook built during Phase 2; if `off`, Phase 5c is skipped entirely. This keeps quota spend opt-in while still offering a real validation path when the user wants it.

### 5. Workstream 5 — External references

**Question:** Are any of the satellite docs (`CHILDREN_PAGES.md`, `NOTEBOOKLM.md`, `IMAGE_GENERATION.md`) referenced externally such that deleting them would break a reference?

**Answer — No external references; delete outright.** The three files are not referenced from anywhere outside the repo. Workstream 5 plans a clean delete: migrate the content into `templates/` example files (`templates/children_pages/`, `templates/notebooklm/`, `templates/images/`) plus short inline anchors in SKILL.md, then delete the three top-level MD files outright — no redirect stubs.

## Review History

| Date | Version | Reviewer | Summary |
|------|---------|----------|---------|
| 2026-04-17 | 0.1.0 (Draft) | buddy:spec | Initial specification drafted from PM assessment |
| 2026-04-17 | 1.0.0 (Ready for Review) | buddy:spec | All five clarifications resolved; Workstreams 1-5 updated with concrete decisions (graceful fallback, Node/Python hybrid, both regenerate granularities, opt-in `content_truth.backend`, outright satellite-doc deletion) |
| 2026-04-17 | 1.1.0 (Ready for Review) | buddy:spec | Added Workstream 6: generalized up-front backend-choice pattern. Image backend (`images.backend: flux / off`) and video backend (`video.backend: heygen / remotion / capcut / webm / off`, plus `video.max_count`) are now chosen up-front at course creation, alongside `content_truth.backend`. Availability checks, HeyGen cost note, FLEX→FLUX name normalization, and "not implementing new backends" out-of-scope clarification all folded in. Workstream 4 updated to cross-reference the generalized pattern. Status remains Ready for Review (scope expanded, no open clarifications). |
