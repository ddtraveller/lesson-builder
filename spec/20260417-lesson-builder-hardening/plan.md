# Implementation Plan: Lesson-Builder Hardening Initiative

**Status:** Ready for Review
**Date:** 2026-04-17
**Initiative ID:** lesson-builder-hardening
**Source Spec:** `spec/20260417-lesson-builder-hardening/spec.md` (v1.1.0, Ready for Review)
**Owner:** ddtraveller@yahoo.com
**Target Skill Path:** `C:\Users\ddtra\claude\lesson-builder`
**Plan Version:** 1.0.0

---

## 1. Summary

Execute the six-workstream hardening initiative against the `lesson-builder` skill over **2–3 work sessions**. The end state:

- `SKILL.md` drops from 787 to ~450–500 lines by delegating the generic spec→plan→tasks→implement workflow to `buddy:*` skills (workstream 1) and promoting prose correctness rules into a `check_pages.py` script (workstream 2).
- `scripts/regenerate.py` provides both page-level and question-level patch paths so a single reported bug no longer forces a full re-run (workstream 3).
- `scripts/check_content.py` closes the content-truth gap with an **opt-in** per-course `content_truth.backend` field (workstream 4), unified with `images.backend` and `video.backend` into a single up-front backend-choices group asked at course-creation time (workstream 6).
- Three satellite MD files (`CHILDREN_PAGES.md`, `NOTEBOOKLM.md`, `IMAGE_GENERATION.md`) are migrated to `templates/` examples + short SKILL.md anchors, then deleted outright (workstream 5).

All work happens on a feature branch (`lesson-builder-hardening`). The two shipped courses (`children_10_12`, `teens_13_14`) stay untouched — validators are report-only against them. No new page types, no new media backends are built. Workstream 6 wires config slots and availability probes for backends that may not yet exist (`webm`) but explicitly does not implement them.

### Sizing the 2-3 session cap

| Session | Workstreams | Rationale |
|---------|-------------|-----------|
| **Session 1** | 1 + 2 (parallel-friendly) | Both touch SKILL.md but different concerns — delegation stubs vs. prose deletions. Do 1 first (establishes the new SKILL.md shape), then 2 on top. |
| **Session 2** | 3, then 4 + 6 together | Regenerate stands alone (operational win). 4 + 6 share the interactive course-creation flow and the config schema — must be one atomic change to avoid touching creation flow twice. |
| **Session 3 (optional buffer)** | 5 (doc migration) + tuning/acceptance polish | Best done last because SKILL.md is now stable. If sessions 1–2 run long, 5 can slip or roll into a quick follow-up commit. |

If the work runs short, session 3 collapses into session 2; if it runs long, session 3 absorbs overflow. The cap is real — scope is calibrated so nothing on this list requires a fourth session.

---

## 2. Research Summary

The spec has already surfaced all the prior context required:

- **Failure modes** catalogued in SKILL.md §Common JS bugs (lines 524–567), §Relative path depth (648–681), §Filename convention coordination (682–713), §Unit 1 verification gate (715–734), §FLUX safety filter false positives (736–748), §Path-bug detection script (750–773). These map 1:1 to workstream 2 rules 2.1–2.7.
- **Existing Phase 5 scripts:** `scripts/check_links.py` (covers refs + depth + YouTube + external list) and `scripts/check_exams.py` (already emits `_exam_review.json`) are the idiom to mirror for the new scripts.
- **Course output structures:** `specs/EXAMPLE-tefl_children_10_12/` (the worked example), plus the two live courses at `HTML/tefl/children_10_12/` and `HTML/tefl/teens_13_14/` in the `watdonchan` repo.
- **Config convention:** see `config/schema.md`, `config/tefl_beginners.json`, `config/tefl_intermediate.json`. The `images.{enabled, provider, model}` trio already exists and is what workstream 6 replaces.
- **SSM key names** per project CLAUDE.md: `heygen`, `tavily`, `REPLICATE_API_TOKEN` (env var, not SSM), `ANTHROPIC_API_KEY`, `google_gemini_api_key`. The `deploy` AWS profile is the only credential path.
- **Remotion project location:** `C:\Users\ddtra\claude\watdonchan\ai-english-video\` — has `package.json`, `node_modules`, `src/`, `public/`. Workstream 6 probes for this directory, does not create it.
- **HeyGen cost note:** per user memory `reference_heygen_video_cost.md`, ~$2 per lesson video on current plan (not the $3–10 an earlier version of the spec assumed).
- **Existing `buddy:*` skills in harness** (per available-skills list): `buddy:spec`, `buddy:plan`, `buddy:tasks`, `buddy:implement`. All four are present. But **detection still matters** — the skill ships to users who may not have the `buddy:*` plugin installed.

**No external research needed.** Every decision in this plan traces either to the spec, to files already in the repo, or to project memory recorded in CLAUDE.md / MEMORY.md.

---

## 3. Architecture / Approach per Workstream

Each section below specifies: the concrete approach, the files created/modified, and the integration with existing SKILL.md and `scripts/`.

### 3.1 Workstream 1 — Delegate Phases 1-4 to `buddy:*`

**Files modified:**
- `SKILL.md` — replace the bulk of Phases 1–4 (current lines ~133 through ~373) with a condensed delegation section.

**Files added:**
- None. Templates at `templates/buddy/{spec,plan,tasks,research}.md` already exist and stay where they are.

**SKILL.md section mapping — replace vs. keep vs. anchor:**

| Current SKILL.md lines (approx.) | Current content | Action |
|---|---|---|
| 1–12 | frontmatter + "When to use" | **keep** |
| 13–102 | Step 0 auth checks (NotebookLM / Tavily / Replicate) | **keep** as-is (this is TEFL-specific; buddy can't do it) |
| 103–131 | Interactive mode Q&A | **augment** — the three new backend questions (workstream 6) splice in here |
| 133–140 | "How it works — Buddy Workflow Integration" preamble | **rewrite** — becomes the delegation doc |
| 141–271 | Phase 1 (spec), Phase 2 (research+plan), Phase 3 (tasks), Phase 4 (implement) inline bodies | **replace** with ~15-line stubs per phase, each invoking the corresponding `buddy:*` skill and listing the TEFL-specific overlays |
| 272–361 | Phase 5 (a, b, c) + Stepping Through | **keep** (Phase 5 is the TEFL-specific validation layer; not in buddy's scope) |
| 362–373 | Legacy Mode | **keep** |
| 374+ | Config / page-type / JS bug prose | handled by workstreams 2 + 5 |

**Delegation stub pattern** — each Phase 1–4 section becomes roughly:

> **Phase 1: Specification**
>
> Delegate to `buddy:spec` with TEFL-specific overlays.
> - Pass topic, L1/L2, weeks, age group, page types, research method, backend choices from Step 0 and the interactive Q&A.
> - TEFL-specific overlays that go in the spec body: vocabulary density target, bilingual markup rules, page-type catalog, theme palette.
> - Spec lands at `specs/{YYYYMMDD}-{course_id}/spec.md`.
>
> **Fallback (buddy:spec not available):** see §Fallback workflow below.

Same shape for Phases 2, 3, 4 — each about a paragraph plus a 3–5 line list of TEFL overlays to pass in.

**Detection pattern — concrete code:**

The detection happens at the top of Phase 1, runs once per skill invocation, and uses a **single Bash probe** (not skill frontmatter, not a separate metadata file — the simplest thing that answers the question). The probe looks for the `buddy:*` skill names in the harness's advertised skill list the same way they appear in the system-reminder's available-skills section. Pseudocode in SKILL.md:

```bash
# Detect buddy:* availability once at Phase 1 start.
# Probe strategy: check whether buddy:spec / buddy:plan / buddy:tasks / buddy:implement
# appear in the current session's available skills. If the harness exposes them as
# slash-commands, the user-visible test is: can we describe invoking /buddy:spec?
# Operationally: the skill asks the assistant to attempt a delegation and if the
# assistant reports the skill is unavailable, we flip to fallback.
#
# Minimal heuristic used in SKILL.md: attempt to invoke buddy:spec with a trivial
# ping payload. If the harness returns "skill not found" or similar, set
# BUDDY_AVAILABLE=0. Otherwise set BUDDY_AVAILABLE=1.
```

In practice, because SKILL.md is read by an LLM running inside the same harness, the detection reduces to: **the assistant checks its own list of available skills for `buddy:spec`, `buddy:plan`, `buddy:tasks`, `buddy:implement`**, and sets a mode flag for the rest of the session. Documented in SKILL.md as a 6-line block. No shell-level `which buddy` — `buddy:*` isn't a PATH-installed binary, it's a harness-registered skill.

**Fallback location:**
- The fallback inline workflow lives at **the tail of SKILL.md**, in a new `## Appendix: Minimal Inline Fallback (no `buddy:*` installed)` section.
- **Size cap:** the fallback MUST fit in approximately 40 lines. It's the barest artifact-shape-preserving pipeline: "create the folder, copy the templates from `templates/buddy/` into it, fill in the obvious fields, stop." Not a second workflow engine.
- SKILL.md adds a bold warning at the top of the appendix: *"This is a safety net, not a second canonical path. Do not grow it. If `buddy:*` becomes unavailable for a real user, fix the harness, don't extend this fallback."*

**Expected line delta:** replacing ~180 lines of Phase 1–4 body with ~60 lines of delegation stubs + 40 lines of appendix = net ~80-line reduction from workstream 1 alone.

### 3.2 Workstream 2 — Promote Prose Rules into `check_pages.py`

**Files added:**
- `scripts/check_pages.py` — the new mechanical checker.
- `scripts/test_check_pages.py` — unit test file with pass/fail fixtures for each of rules 2.1–2.7.
- `scripts/fixtures/check_pages/` — a small directory of synthetic HTML files that trigger each rule, used by the tests.

**Files modified:**
- `SKILL.md` — delete the prose sections enumerated below.
- `templates/buddy/tasks.md` — add a Phase 5 step invoking `check_pages.py` alongside `check_links.py` and `check_exams.py`.

**Prose → script mapping (this is the substance of "which sections get deleted"):**

| SKILL.md prose (current lines) | Corresponding `check_pages.py` function | Deletion plan |
|---|---|---|
| §"Common JS bugs to avoid" / §4a "Never reference undefined functions" (~528–530) | `check_undefined_js_refs(html_path) -> [Finding]` | **delete** prose; script enforces. |
| §4b "Quote safety in inline handlers" (~531–533) | `check_onclick_quote_safety(html_path)` | **delete** prose; script enforces. |
| §4c "JS quote escaping in Python-emitted JS — THE MOST SUBTLE BUG" (~534–557) | `check_python_js_escape_leak(html_path)` | **delete** prose; script enforces. (The most battle-scarred rule — worth keeping one sentence in SKILL.md pointing at the script as the enforcement mechanism.) |
| §4d "SVG / HTML attribute quoting inside JS string literals" (~559–560) | `check_svg_attr_quotes_in_js(html_path)` | **delete** prose; script enforces. |
| §4e "Always cancel speechSynthesis" (~562–563) | `check_speechsynthesis_cancel_guard(html_path)` | **delete** prose; script enforces. |
| §"Relative path depth" (~648–681) | partially covered by existing `check_links.py`; extend it rather than duplicating | **trim heavily** — keep only the one-line rule ("`..` depth must equal page depth"), delete the ~35-line S3-layout tutorial (git history has it). |
| §"Filename convention coordination" (~682–713) | `check_media_src_exists_on_disk(html_path, imgs_root)` — covers the English Quest filename-mismatch class | **delete** prose; script enforces. Rule 2.6. |
| §"Path-bug detection script" (~750–773) | Rule 2.6 + cross-reference to script | **delete** the inline python one-liner; `check_pages.py` covers it. |
| §"Unit 1 verification gate" (~715–734) | Rule 2.1 (undefined refs), 2.6 (filename), 2.7 (JS parse), plus remaining human steps | **shorten** — keep steps 1 (DevTools), 2 (click everything), 5 (localStorage), 6 (mobile), 8 (chatbot test). Delete steps 3 (view-source scan), 4 (path against S3), 7 (nav link test) — all three are now mechanically checked. |
| §4f "localStorage quota" (~565–567) | (not in scope for check_pages — operational, not page-level) | **keep** as a short bullet; don't delete. |

**JS-parse strategy — explicit pick:**

For rule 2.7 (valid JS), the fallback is **regex-and-bracket-counting only**. No `esprima-python` dependency. Rationale:

- The historical bug catalogue is narrow: unbalanced `{}`, unterminated string literals, `\'` escape leakage, single-quote collision in SVG attrs. All four are detectable with regex + a bracket-depth counter.
- Adding `esprima-python` adds a pip dependency for a gain (full grammar coverage) that only matters for classes of bugs we haven't historically shipped. Not worth it.
- If Node is on PATH, `node --check` already handles the long tail. So the fallback only has to beat "nothing" — regex+brackets does.
- If later we observe a shipped bug the regex layer can't see, we add a targeted regex, not a parser.

The script logs which mode ran on line 1 of output: `js-parse: node` or `js-parse: python-fallback`. Per-invocation detection; no caching.

**Interface:** `python scripts/check_pages.py <output_dir>`, exit 0 clean / non-zero on any finding, report format mirrors `check_links.py` (file → rule → line → description).

**Acceptance smoke-test commands** (see §7 Testing Strategy for the full test plan):

```bash
# Must exit 0 on both shipped courses (report-only baseline).
python scripts/check_pages.py HTML/tefl/children_10_12/
python scripts/check_pages.py HTML/tefl/teens_13_14/

# Must exit non-zero on the broken-fixture dir.
python scripts/check_pages.py scripts/fixtures/check_pages/broken/
```

**Expected line delta:** workstream 2 deletes approximately 130 lines of SKILL.md prose across the sections above. Combined with workstream 1 (~80 lines), total reduction lands SKILL.md near ~570–600. The remaining ~70–100 lines to hit the 450–500 target come from workstream 5's inline-anchor consolidation.

### 3.3 Workstream 3 — `regenerate.py` Patch Path

**Files added:**
- `scripts/regenerate.py` — single script with two subcommands (page-level, question-level).

**Files modified:**
- `SKILL.md` — add a short §"Operational: patching a single page or question" subsection pointing at the script.
- `templates/buddy/tasks.md` — add a note in the Phase-5 section: "For a single learner-reported bug, use `scripts/regenerate.py` instead of re-running the full generator."

**Data flow — page-level (the 80% case):**

```
course config JSON (config/{course_id}.json)
  → load + resolve output_dir, file_prefix, page_structure, units
  → import generator module (generate_{course_id}.py located by convention)
  → look up generator dispatch table: {page_type: generate_fn}
  → call generate_fn(unit[N], config) → HTML string
  → overwrite output_dir/{prefix}_{slug}_{page_type}.html
  → log the regenerate event to {output_dir}/_regenerate_log.jsonl
```

The generator module is imported the same way the full-run script imports it — via `importlib`, giving back the exact same dispatch table. This guarantees byte-for-byte determinism with a full generator run for that one page. Acceptance criterion 4 is proved by diff-ing against a full regenerate.

**Data flow — question-level (the surgical case):**

**Pick: parse-and-patch the existing HTML, do NOT re-run the generator.** Rationale:

- Re-running the generator regenerates the whole exam page, which means the distractors and other questions regenerate too (LLM or sampling can produce sibling differences even with the same inputs). That violates acceptance criterion 5 ("sibling questions byte-identical").
- The exam pages embed the `questionBank` as a literal JS object in an inline `<script>` — easy to extract, mutate, re-emit. No generator re-entry needed for the rest of the page.

Concrete splice procedure inside `regenerate.py::regenerate_exam_question(course_id, unit_n, coord)`:

1. Read the existing HTML for that unit's exam page.
2. Locate the `questionBank = { ... };` block via a narrowly-scoped regex anchored on the opening `const questionBank` identifier.
3. Parse the object literal via `json.loads` after stripping JS-isms (trailing commas, `//` comments — defensive for authored content, though the generator never emits them). If parsing fails, error out with "cannot safely splice — question bank is not clean JSON; use --page-type exam to regenerate the whole page."
4. Resolve `coord = CATEGORY:DIFFICULTY:INDEX` against the parsed structure. If the index doesn't exist, fail fast (acceptance criterion 7).
5. Regenerate **just that one question object** by calling a narrow generator helper — `generate_exam_question(category, difficulty, unit_context)` — which must exist in the generator module. If the module doesn't expose that helper, fall back to prompting the user to provide the corrected question manually.
6. Splice the new question object into the parsed list at the resolved index.
7. Re-serialize the list back to a JS object literal (stable key order, 2-space indent matching existing style).
8. Write the result back with `re.sub` replacing only the `questionBank = { ... };` block — everything else in the file is unchanged.
9. Log to `_regenerate_log.jsonl`.

The diff-scope acceptance test (workstream 3 criterion 5) runs `diff old.html new.html` after a question-level regenerate and asserts the diff hunks touch only lines inside the `questionBank` block. This is the test that proves the surgical splice didn't perturb the rest.

**Safety guard** (acceptance criterion 3): the script reads an allowlist from itself — `SUPPORTED_COURSES = {"children_10_12", "teens_13_14", "tefl_beginners", "tefl_intermediate"}`. If `--course` isn't in the set, refuse with a pointer to how to add it. Prevents `python scripts/regenerate.py --course typo --unit 1 ...` from silently running.

**Log format** (`_regenerate_log.jsonl`): one JSON object per line per event, fields: `timestamp, course_id, unit, page_type (or exam_question_coord), before_hash, after_hash, operator`. Satisfies acceptance criterion 6.

### 3.4 Workstream 4 — Content-Truth Validator (`check_content.py`)

**Files added:**
- `scripts/check_content.py` — the validator.

**Files modified:**
- `SKILL.md` — Phase 5c subsection pointing at the new script; backend choice added to the interactive Q&A (coupled with workstream 6).
- `config/schema.md` — add the `content_truth.backend` field to the documented schema.
- All example configs in `config/` — add `content_truth: { backend: "off" }` to preserve current behavior.

**Prompt-at-creation integration point — explicit pick:**

The `content_truth.backend` prompt lands as **a new sub-question inside the existing §"Interactive Mode — Ask Before Building" block, immediately after question 7 (Color theme)**, as part of a new "Backend choices (up-front)" group that includes the workstream 6 prompts as well. **Not a Step 0 sub-step** — Step 0 is for environment discovery (what's available), this is operator intent (what do you want to use). Those are different questions and shouldn't share a section.

So the interactive Q&A grows from 7 questions to 10, with the last three being the new coherent backend group asked contiguously:

> 8. **Content-truth validation backend?** [tavily / notebooklm / off] (default: off — no quota spend)
> 9. **Image generation backend?** [flux / off] (default: off)
> 10. **Video generation backend?** [heygen / remotion / capcut / webm / off] (default: off — HeyGen is ~$2/video, others free)

Plus a follow-up `video.max_count` question if anything other than `off` is picked for video.

**Sampling logic location:** inside `scripts/check_content.py`. Not a separate module.

**Sampling proportions — concrete code constants:**

```python
SAMPLE_RATES = {
    "vocab_card":        0.20,   # 20% per unit
    "grammar_box":       0.10,   # 10% per unit
    "exam_correct_mark": 1.00,   # 100% of exam questions
}
```

Reproducibility: use a per-course random seed derived from `course_id` so two runs of the validator against the same course produce the same sampled set — prevents flapping flag lists across re-runs during tuning.

**Script shape:**

```python
# scripts/check_content.py (sketch)
def main(output_dir, config_path):
    cfg = load_config(config_path)
    backend = cfg.get("content_truth", {}).get("backend", "off")
    print(f"content-truth backend: {backend}")
    if backend == "off":
        print("Phase 5c skipped by config — no quota consumed.")
        return 0
    if backend not in ("tavily", "notebooklm"):
        print(f"ERROR: unknown backend '{backend}'"); return 2
    items = sample_items(output_dir, SAMPLE_RATES, seed=course_id_seed(cfg))
    flags = []
    for item in items:
        ok, reason = check_item(item, backend)
        if not ok: flags.append({"item": item, "reason": reason})
    emit_report(flags, output_dir)
    return 1 if flags else 0
```

`check_item` dispatches to one of:
- `check_via_tavily(item)` — shells out `PYTHONIOENCODING=utf-8 tvly research "..." --model mini --json` and inspects the result.
- `check_via_notebooklm(item)` — uses `python -m notebooklm ask "..."` against the course's Phase-2 notebook (ID stored in research.md).

**Shipping gate wiring:** Phase 5c exit codes feed back into the SKILL.md Phase 5 wrap-up:
- `backend: off` → never blocks.
- `backend: tavily|notebooklm` + exit 0 → proceed.
- `backend: tavily|notebooklm` + exit 1 → operator must resolve each flag (fix / mark-false-positive-with-note / explicit-override) before shipping.

**Report format:** emits both `{output_dir}/_content_truth_report.json` (machine-readable) and `{output_dir}/_content_truth_report.md` (human-readable, Markdown with headings per flag). Operator can grep the MD for "UNRESOLVED" to enumerate the remaining gate blockers.

### 3.5 Workstream 6 — Up-Front Media Backend Choices

**Files modified:**
- `SKILL.md` — new §"Course-creation backend choices" near the top of the Interactive Mode section (coupled with workstream 4).
- `config/schema.md` — document all three fields as one coherent "backends" group.
- All example configs in `config/` — add the three fields (defaulting to `off` or matching current behavior where applicable — e.g. `tefl_intermediate.json` currently has `notebooklm: true` and `images.enabled: true`; those translate to `content_truth.backend: notebooklm` and `images.backend: flux`).

**Files added:**
- `scripts/backend_probes.py` — a **shared helper module** (this is the explicit pick — one module, not per-backend files). Exposes:
  - `probe_tavily() -> (available: bool, reason: str)`
  - `probe_notebooklm() -> (available: bool, reason: str)`
  - `probe_flux() -> (available: bool, reason: str)` — checks for `REPLICATE_API_TOKEN` in env / `.env`.
  - `probe_heygen() -> (available: bool, reason: str)` — shells out `aws ssm get-parameter --name heygen --with-decryption --profile deploy --region us-west-2` and checks exit code + non-empty return.
  - `probe_remotion(project_dir="watdonchan/ai-english-video") -> (available: bool, reason: str)` — checks the directory exists, has `package.json`, and `node_modules/remotion` exists.
  - `probe_capcut() -> (True, "prompt-to-human workflow; no runtime check")` — always available; it's manual.
  - `probe_webm() -> (False, "webm pipeline is not yet implemented in this skill")` until such a pipeline lands. Returns `False` for now; this is the NOT-YET-IMPLEMENTED behavior.
  - `probe_node() -> (bool, version_or_reason)` — used by workstream 2 as well for the Node-vs-Python JS-parse dispatch. Shared.

**Shared helper rationale:** per-backend modules (one file each) is more OO but overkill for a script repo — we have six backends, each probe is 5–15 lines, one file stays navigable and means the check_pages.py / regenerate.py / check_content.py / course-creation flow all hit the same probe surface. No reason to spread them.

**Interactive-flow integration** — exactly where the three questions go:

The spec requires the three prompts appear as a **contiguous block near the top of the questionnaire**. Concretely, SKILL.md §"Interactive Mode — Ask Before Building" gets rewritten so the question list becomes:

> 1. Topic/Subject
> 2. Languages
> 3. Number of weeks/units
> 4. Age group
> 5. Page types
> 6. Output location
> 7. Color theme
> 8. **[Backend choices block]** — content_truth / images / video (with `video.max_count` follow-up if not `off`)
>
> For each of 8a/8b/8c, the skill **probes availability first** (via `scripts/backend_probes.py`), shows the result inline, then prompts. If the operator picks something the probe said is unavailable, the skill warns visibly and falls back to `off`.

**Config schema section writer:** `config/schema.md` gets the consolidated backends group written by the same commit that adds the three fields. The author is the implementer of workstream 4+6 (they're a single session). **Not a separate docs task.**

**Availability-check wiring per backend:**

| Backend | Probe shells out to | On unavailable |
|---------|---------------------|----------------|
| `content_truth.backend: tavily` | `tvly auth --json` | warn, fall back to `off` |
| `content_truth.backend: notebooklm` | `python -m notebooklm auth check --test --json` | warn, fall back to `off` |
| `images.backend: flux` | `echo $REPLICATE_API_TOKEN` / check `.env` | warn, fall back to `off` |
| `video.backend: heygen` | `aws ssm get-parameter --name heygen --profile deploy --region us-west-2` | warn, fall back to `off` |
| `video.backend: remotion` | check `watdonchan/ai-english-video/node_modules/remotion/` exists | warn, fall back to `off` |
| `video.backend: capcut` | no probe — always available | n/a |
| `video.backend: webm` | check for pipeline marker file `scripts/webm_pipeline.py` (doesn't exist yet) | warn "not yet implemented", fall back to `off` |

Exactly one shared helper module owns these; no duplication.

### 3.6 Workstream 5 — Satellite Doc Migration

**Files added:**
- `templates/children_pages/story_example.html` — a minimal runnable story page with the Dr. Seuss-style structure.
- `templates/children_pages/game_example.html` — a minimal runnable game page (Match/Tap/Memory).
- `templates/children_pages/README.md` — ~30 lines, points at the two examples and the SKILL.md anchors; lists the full page-type catalog as a short table.
- `templates/notebooklm/query_patterns.md` — ~30 lines: the authoring patterns for good NotebookLM queries ("What does {source} say about X?"), plus the auth-troubleshooting sequence from the deleted NOTEBOOKLM.md.
- `templates/images/prompt_style_prefix.txt` — raw text: the coloring-page style prefix, copy-pasteable.
- `templates/images/README.md` — ~40 lines: generate_images.py usage examples, use-case-to-aspect-ratio table, the Unicode emoji color reference (preserved as a data table — it's the kind of content that actually belongs in a file not in SKILL.md).

**Files modified:**
- `SKILL.md` — add two new short anchors:
  - §"Querying the corpus" inside Phase 2, ~10 lines — the single highest-leverage tip ("phrase NotebookLM queries as 'What does [source] say about X'"), with a pointer to `templates/notebooklm/query_patterns.md` for more.
  - §"Image prompt conventions" inside Phase 3, ~12 lines — the style-prefix idea, the ethnicity-in-prompt rule, the emoji-color-not-CSS rule, with a pointer to `templates/images/README.md`.

**Files deleted outright (no redirect stubs):**
- `CHILDREN_PAGES.md`
- `NOTEBOOKLM.md`
- `IMAGE_GENERATION.md`

**Content-by-content destination table** — every paragraph of each deleted file accounted for:

**CHILDREN_PAGES.md (183 lines):**
| Source content | Destination |
|---|---|
| Interactive-mode page-type catalog for ages 4-7 (lines 4–35) | `templates/children_pages/README.md` as a compact table |
| Older-children page-type catalog for 8-12 (36–45) | `templates/children_pages/README.md` (same table, second half) |
| Story page spec (51–84) — illustration rule, Dr. Seuss rhyming rules, story-concept-patterns table | Embedded as comments at the top of `templates/children_pages/story_example.html`; the story-concept-patterns table stays in the README |
| Game page spec (86–92) | `templates/children_pages/game_example.html` (as comments) |
| Song page spec (94–131) — song-selection criteria + the 12-entry verified video ID table | `templates/children_pages/README.md` — the video ID table **stays** (it's load-bearing data for the children_10_12 course) |
| Coloring page spec (133–158) | Cross-referenced: structure comments in a new `templates/children_pages/coloring_example.html` file; style-prefix content goes to `templates/images/` |
| Stickers page spec (160–167) | brief section in `templates/children_pages/README.md` |
| Flashcards page spec (169–180) | brief section in `templates/children_pages/README.md` |
| Reward page spec (182–183) | brief section in `templates/children_pages/README.md` |

**NOTEBOOKLM.md (89 lines):**
| Source content | Destination |
|---|---|
| "Check if notebooklm-py is installed / install" (5–12) | **dropped as obsolete** — SKILL.md Step 0 already does this check; duplication |
| "Check authentication" (14–21) | **dropped as obsolete** — SKILL.md Step 0 already does this |
| "If auth expired, guide user through login" (23–62) — interactive-login gotcha + troubleshooting sequence + helper script | `templates/notebooklm/query_patterns.md` as an "Auth troubleshooting" appendix section |
| "Verify auth works after login" (71–84) | **dropped as obsolete** — SKILL.md Step 0 covers |
| "If auth cannot be established, offer fallback" (86–87) | **dropped as obsolete** — SKILL.md Step 0 covers |
| "IMPORTANT Windows note" (89) | **inline anchor** in SKILL.md Phase 2 §"Querying the corpus" (one line: "Always prefix `notebooklm` commands with `PYTHONIOENCODING=utf-8` on Windows.") |
| Query-pattern guidance | `templates/notebooklm/query_patterns.md` (body) |

**IMAGE_GENERATION.md (175 lines):**
| Source content | Destination |
|---|---|
| generate_images.py usage + prompts JSON format (3–57) | `templates/images/README.md` |
| Coloring page image generation / style prefix (59–78) | `templates/images/README.md` + the style prefix as `templates/images/prompt_style_prefix.txt` |
| Other image use cases table (80–89) | `templates/images/README.md` |
| Image path convention (91–102) | inline anchor in SKILL.md Phase 3 §"Image prompt conventions" (3 lines: the `imgs/` vs `HTML/` convention; relative-path depth already covered by workstream 2's `check_pages.py`) |
| Unicode emoji color reference (104–176) — the three tables (circles, squares, hearts, animals, pitfalls) | `templates/images/README.md` — stays intact as a data reference. This is exactly the kind of large lookup table that should be in a file, not in SKILL.md |

**In-repo reference updates** — before deletion, grep the repo for `CHILDREN_PAGES.md`, `NOTEBOOKLM.md`, `IMAGE_GENERATION.md`:

```bash
grep -rn 'CHILDREN_PAGES\.md\|NOTEBOOKLM\.md\|IMAGE_GENERATION\.md' \
  --include='*.md' --include='*.py' --include='*.json' \
  /c/Users/ddtra/claude/lesson-builder/
```

Expected hits: SKILL.md links at lines 30, 119, 521. All three are updated to point at the new locations in the same commit that deletes the source files.

---

## 4. Dependency Graph / Concrete Sequence

The spec-recommended sequence is **1, 2 (parallel) → 3 → 4 + 6 (together) → 5**. The concrete implementation order per workstream, with parallelizable tasks marked:

```
Session 1:
  [WS1] SKILL.md Phase 1-4 delegation stubs                    (sequential, touches SKILL.md)
  [WS1] SKILL.md minimal inline fallback appendix               (sequential, touches SKILL.md)
  [WS1] Detection pattern documentation                         (sequential)
  ─────
  [WS2] scripts/check_pages.py skeleton + probe_node helper    (parallel with WS1 prose edits)
  [WS2] scripts/fixtures/check_pages/ synthetic HTML            (parallel)
  [WS2] Rules 2.1–2.7 implementations, one per function         (sequential — regex work shares utilities)
  [WS2] scripts/test_check_pages.py                             (sequential after rules exist)
  [WS2] Run against both shipped courses → exit 0               (gate)
  [WS2] SKILL.md prose deletions from mapping table              (sequential, after WS1 prose edits settle)
  [WS2] templates/buddy/tasks.md Phase-5 step update            (parallel with prose deletions)

Session 2:
  [WS3] scripts/regenerate.py — shared loader + dispatch        (sequential)
  [WS3] Page-level path                                          (sequential)
  [WS3] Question-level splice                                    (sequential)
  [WS3] Determinism test harness (diff vs full regenerate)      (parallel with splice dev)
  [WS3] _regenerate_log.jsonl emitter                           (sequential, trivial)
  [WS3] SUPPORTED_COURSES allowlist                              (trivial)
  [WS3] SKILL.md Operational anchor                              (parallel)
  ─────
  [WS4+6] scripts/backend_probes.py (shared helper)             (sequential — touched by both)
  [WS4+6] config/schema.md backend-group documentation          (parallel with probes)
  [WS4+6] Example config updates (off defaults)                  (parallel)
  [WS4] scripts/check_content.py                                 (sequential, depends on probes)
  [WS4] Sampling / flagging / report emitters                   (sequential)
  [WS6] SKILL.md §"Course-creation backend choices" rewrite      (sequential — replaces 3 questions, depends on probes)
  [WS6] Availability-check warn-and-fall-back logic doc          (sequential)

Session 3 (or tail of session 2):
  [WS5] templates/ directory creation + examples + READMEs       (sequential per subdir, three subdirs parallel)
  [WS5] SKILL.md inline anchors (Querying the corpus, Image prompt conventions)  (sequential)
  [WS5] grep repo for old MD references, update                  (sequential)
  [WS5] git rm the three satellite MDs                            (final step)
  [WS5] Final SKILL.md line-count check: target ~450–500          (gate)
```

**Parallelism inside a workstream** is marked explicitly. Crossing workstreams is sequential per the dependency order above.

---

## 5. Risks (Restated with Concrete Mitigation)

Every risk in the spec gets a concrete plan-level mitigation step:

| Risk (spec) | Concrete mitigation in this plan |
|---|---|
| `buddy:*` behavioral drift from current inline Phases 1-4 | Workstream 1 acceptance gate: run a dry-run course-authoring session before deleting anything; diff the resulting spec.md/plan.md/tasks.md artifacts against `specs/EXAMPLE-tefl_children_10_12/` shape. If buddy-produced files diverge meaningfully, adjust the TEFL overlays passed into `buddy:*`, don't revert. |
| Fallback grows into a second system | Fallback lives in an `## Appendix: Minimal Inline Fallback` section, capped at ~40 lines, prefaced with an in-file bold warning. Workstream 1 acceptance criterion 6 is a grep check: `grep -c "^" <fallback-section> < 45`. |
| `check_pages.py` false positives block legit output | Script exits non-zero but SKILL.md Phase 5 integration explicitly labels it REPORT-ONLY for the first two weeks. Promotion to blocking happens in a follow-up change after clean runs on both shipped courses. |
| Python-fallback JS check misses errors `node --check` would have caught | Script's first-line output states which mode ran. Operator running on a Node-less box sees `js-parse: python-fallback` and knows to re-run under Node when stakes are high. Rule 2.7 acceptance criterion 6 forces one CI-equivalent check: unset Node and run against shipped courses, confirm no regressions. |
| `regenerate.py` drifts from full-generator output | Workstream 3 ships with a `--determinism-check` flag that: regenerates the target once, runs the full generator into a tmpdir, diffs the target file. Acceptance criterion 4 gates on this diff being empty for page-level. |
| Question-level splice corrupts surrounding exam HTML | Acceptance criterion 5: diff hunks must touch only lines inside the `questionBank` block. Plan adds a test fixture: a real exam page from `children_10_12`, run question-level regenerate against it, assert diff scope. If the test fails, regenerate refuses to write. |
| Content-truth validator too noisy | Opt-in default `off`; reproducible seed per course so flag lists are stable across runs during tuning. Workstream 4 acceptance criterion 6 gates on <25% false-positive rate, but the operator has the final call. |
| Operator forgets they selected tavily/notebooklm and burns quota | `check_content.py` first-line output: `content-truth backend: tavily` (or notebooklm). Printed to stdout at every run. No way to run the validator silently. |
| HeyGen surprise cost | Interactive prompt surfaces the ~$2/video note inline (per `reference_heygen_video_cost.md`). `video.max_count` is required if `video.backend != off`; generator halts before exceeding. |
| Operator picks `webm` before pipeline exists | `probe_webm()` returns `(False, "not yet implemented")`. Interactive flow warns and flips the choice to `off` before writing the config. Config never records `webm`. |
| Operator picks `remotion` but ai-english-video/ not reachable | `probe_remotion()` checks the directory + `node_modules/remotion`. Same warn-and-fall-back pattern. |

---

## 6. Testing Strategy

"Acceptance criteria met" looks concrete and scriptable for each workstream:

### WS1 — buddy delegation
- **Test:** dry-run course authoring prompt in a session where `buddy:*` is available. Assert the three artifacts `specs/{date}-test_course/{spec,plan,tasks}.md` exist and conform to the shape of `specs/EXAMPLE-tefl_children_10_12/`.
- **Test:** simulate buddy unavailability (e.g., operator in a vanilla harness without the buddy plugin). Assert the fallback path produces the same three file paths, possibly with thinner content but the same layout.
- **SKILL.md line-count check:** `wc -l SKILL.md` should drop from 787 into the low 600s after WS1 alone. Hard to predict exactly, but anything above 700 means the delegation stubs aren't lean enough.
- **Fallback-size check:** `awk '/^## Appendix: Minimal Inline Fallback/,/^## /' SKILL.md | wc -l < 45`.
- **Fallback-warning grep:** `grep -q "safety net, not a second canonical path" SKILL.md`.

### WS2 — check_pages.py
- **Unit tests:** each rule 2.1–2.7 has a pass fixture and a fail fixture in `scripts/fixtures/check_pages/`. `python scripts/test_check_pages.py` runs all of them, exits 0 only if every pass-fixture passes and every fail-fixture fails.
- **Shipped-course smoke:** `python scripts/check_pages.py HTML/tefl/children_10_12/` and same for `teens_13_14` — both exit 0 (report-only success).
- **Broken-fixture smoke:** `python scripts/check_pages.py scripts/fixtures/check_pages/broken/` exits non-zero with readable diagnostics.
- **Mode banner check:** first line of script stdout starts with `js-parse: ` followed by `node` or `python-fallback`.
- **Node-less run:** manually unset Node on PATH (or use `PATH=/usr/bin:/bin python scripts/check_pages.py ...`) and confirm the script still completes and says `js-parse: python-fallback`.
- **Prose-deletion grep:** `grep -c "JS quote escaping in Python-emitted JS" SKILL.md` returns 0 (section has been deleted); same for the other deleted headers from the mapping table.
- **Line-count check:** `wc -l SKILL.md` should now be in the 500s.

### WS3 — regenerate.py
- **Determinism test:** `python scripts/regenerate.py --course children_10_12 --unit 7 --page-type exam --determinism-check` — regenerates into a tmpdir, runs full generator into another tmpdir for unit 7's exam page, diffs. Must be byte-identical.
- **Question-level diff-scope test:** `python scripts/regenerate.py --course children_10_12 --unit 7 --exam-question vocab:medium:4`. Post-run, `diff HTML/tefl/children_10_12/foo_unit7_exam.html.bak HTML/tefl/children_10_12/foo_unit7_exam.html` — diff hunks must only touch lines inside the `const questionBank = { ... };` literal. Any hunk outside that block = test fail.
- **Invalid-coord test:** `--exam-question vocab:medium:99` → non-zero exit with "index 99 out of range for vocab/medium (bucket has 10 items)".
- **Unsupported-course test:** `--course typo` → non-zero exit with "typo not in SUPPORTED_COURSES allowlist".
- **Log-emission test:** after any run, `tail -1 HTML/tefl/children_10_12/_regenerate_log.jsonl` is a valid JSON object with the expected fields.
- **Timing check:** a full page-level regenerate completes in `<10s` on a 12-unit course (proxy for the "under 5 minutes end-to-end including human deploy" success metric).

### WS4 — check_content.py
- **Off path:** `python scripts/check_content.py HTML/tefl/children_10_12/ config/children_10_12.json` (with `content_truth.backend: off`) exits 0 and prints `Phase 5c skipped by config`.
- **Tavily path:** `python scripts/check_content.py ... ` (with `backend: tavily`) runs to completion. Emits `_content_truth_report.{json,md}` in the output dir.
- **NotebookLM path:** same as tavily path, different backend.
- **Shipping-gate simulation:** hand-craft an obvious vocab mistranslation in a test course, run with validation on, assert the script exits non-zero and the report lists the mistranslation.
- **False-positive target:** run against `children_10_12` under one backend, manual-review the flags, compute FP rate. Target < 25% per workstream 4 criterion 6. If higher, tune sampling rates / prompts until it lands.
- **Reproducibility:** two runs against the same course produce the same flag list (seed stability).

### WS6 — backend choices
- **Round-trip test (the headline):** operator runs the interactive creation flow, picks `content_truth.backend: tavily`, `images.backend: flux`, `video.backend: heygen`, `video.max_count: 5`. Inspect the resulting config file — all four values present. Delete the course dir. Re-run the skill in config-only mode (`--config config/<course_id>.json --non-interactive`). Resulting pipeline must be functionally identical — same backends picked, same prompts, same max_count cap. This is workstream 6 criterion 4 made concrete.
- **Availability fall-back test:** pick `video.backend: heygen` in an environment where `heygen` SSM param is absent (simulate by using a bad profile). Probe says unavailable → warning printed → config records `off`, not `heygen`.
- **webm NOT-YET-IMPLEMENTED test:** pick `video.backend: webm`. Probe says not-implemented → warning printed → config records `off`.
- **max_count enforcement:** set `video.max_count: 3`, request video generation for a 12-unit course → generator halts at the 4th attempt with a readable error, not silent truncation.
- **HeyGen cost surface:** inspect the SKILL.md interactive-mode prompt text — contains the "HeyGen: ~$2 per lesson video" note verbatim.

### WS5 — doc migration
- **Delete gate:** `ls *.md` in the skill root returns exactly `SKILL.md`, `README.md` (plus `LICENSE`). No CHILDREN_PAGES / NOTEBOOKLM / IMAGE_GENERATION.
- **No dangling refs:** `grep -r 'CHILDREN_PAGES\.md\|NOTEBOOKLM\.md\|IMAGE_GENERATION\.md' /c/Users/ddtra/claude/lesson-builder/` returns zero hits (excluding `.git/`).
- **Templates exist:** `ls templates/children_pages/ templates/notebooklm/ templates/images/` each return a non-empty listing with at least a README.md plus one example/tip file.
- **Anchors added:** `grep -q 'Querying the corpus' SKILL.md` and `grep -q 'Image prompt conventions' SKILL.md` both return true.
- **Line-count final gate:** `wc -l SKILL.md` returns a value in `[440, 520]`. (Tolerance band around the 450–500 target; the band accommodates minor drift from the exact deletion math.)
- **Information-preservation audit:** walk the content-by-content destination table from §3.6, verify each row's destination file contains the expected content. Mechanical audit, done by grep.

### Global acceptance — cross-workstream
- **Feature branch only:** all work in branch `lesson-builder-hardening`; never direct to main.
- **No retroactive breakage:** re-run `scripts/check_links.py`, `scripts/check_exams.py`, `scripts/check_pages.py` against both shipped courses after all workstreams land — all exit 0.
- **Skill invocation end-to-end:** at the end of session 2 (and again after session 3), invoke `lesson-builder` against a toy config to verify the pipeline still runs.

---

## 7. Open Questions

The spec was thoroughly clarified — five questions resolved before this plan started. Planning surfaced no new blocking questions. Two minor items are worth flagging, but neither blocks kickoff:

1. **Is there a preferred location for the `lesson-builder-hardening` feature branch's remote?** The skill repo at `C:\Users\ddtra\claude\lesson-builder` has `.git/` but the plan assumes "feature branch in the local repo" without committing to a push destination. If the skill repo has a GitHub remote that this branch should push to, naming it explicitly would prevent a late-session scramble. Default assumption: local-only feature branch, merge to local main by hand. Flag for operator confirmation at kickoff.

2. **Baseline for the `bugs per month` success metric.** The spec says "TBD (operator to record baseline)". The plan doesn't block on this — workstreams 1–6 can complete without a baseline — but if the operator wants the metric to mean something, they should note the current per-month count (from learner reports / issues / memory) before session 1 begins. One-line note in a file or memory is enough.

Neither of these blocks work. Session 1 can start immediately.

---

## 8. Key Decisions Summary (Where Alternatives Were Available)

Pulled out here for quick review:

| Decision point | Alternatives considered | Pick | Why |
|---|---|---|---|
| JS-parse Python fallback | regex+brackets vs. `esprima-python` | **regex+brackets only** | Covers the historically-observed bug catalogue; esprima adds a dep for bugs we don't ship. |
| Question-level regenerate mechanism | re-run generator vs. parse-and-patch HTML | **parse-and-patch** | Re-running regenerates siblings; violates criterion 5. |
| Backend-choice interactive placement | Step 0 sub-step vs. new question in interactive Q&A | **new questions 8/9/10 in interactive Q&A** | Step 0 is environment discovery; these are operator intent — different section. |
| Per-backend probes organization | per-backend files vs. one shared module | **one shared module (`scripts/backend_probes.py`)** | Six backends × ~10 lines each is trivially navigable; no reason to spread. |
| Buddy detection mechanism | bash `which`, skill frontmatter metadata, harness skill list check | **harness skill list check (via assistant self-awareness)** | `buddy:*` isn't a PATH binary; frontmatter would require a new convention. Lightest touch that actually answers the question. |
| Fallback location | separate file vs. SKILL.md appendix | **SKILL.md appendix, size-capped, with in-file warning** | Keeping it in-file with a visible warning is the only way to prevent it drifting into a second system. |
| Image emoji color reference table | drop vs. preserve in templates | **preserve in `templates/images/README.md`** | Large lookup table that's still load-bearing data; belongs in a file, not dropped. |
| NotebookLM.md auth-duplicate sections | dedupe vs. preserve | **drop as obsolete** — SKILL.md Step 0 already covers the same checks | Duplication was the whole rot story; deduping is the point. |
| Content-truth sample seed | random per run vs. deterministic per course | **deterministic seed per course_id** | Stable flag lists across re-runs during tuning; prevents chasing noise. |

---

## 9. Success Metrics Checkpoint

Ties the plan's completion gates back to the spec's success metrics:

| Metric | Target | Plan gate |
|---|---|---|
| SKILL.md line count | 787 → ~450–500 | WS1+2+5 complete; `wc -l SKILL.md` in `[440, 520]` |
| Shipped bugs/month | downward trend | Not gateable inside the initiative — tracked over 3 months post-completion; operator to record baseline before session 1 (see Open Question 2) |
| Time-to-patch | under 5 minutes | WS3 complete; page-level determinism + <10s regenerate runtime proxy. Full "5 min" includes human deploy; the plan can only bound the tool time. |

---

## 10. Status

**Draft → Ready for Review.** All six workstreams planned to a level of detail sufficient for `/buddy:tasks` to generate a concrete tasks list without further questions. Two non-blocking open questions flagged in §7 for operator confirmation at kickoff.

## Review History

| Date | Version | Reviewer | Summary |
|------|---------|----------|---------|
| 2026-04-17 | 1.0.0 (Ready for Review) | buddy:plan | Initial plan drafted from v1.1.0 spec; all six workstreams concretized with file paths, explicit picks where alternatives existed, and scriptable acceptance gates. |
