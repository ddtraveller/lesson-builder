---
name: lesson-builder
description: "Generates bilingual TEFL/ESL courses with lessons, exams, flashcards, conversations, pronunciation drills, worksheets, and syllabi for any language pair."
---
<!-- Changelog (most recent first)
  WS3 complete (2026-04-17): scripts/regenerate.py added — page-level and question-level patch paths; config/children_10_12.json added; §Operational: Patching a Single Page or Question anchor added to SKILL.md; templates/buddy/tasks.md patch-path note added. Architecture note: children_10_12 quiz pages use inline HTML question blocks (not questionBank JS object); determinism check correctly flags generator's random distractor shuffle.
  WS2 complete (2026-04-17): check_pages.py (rules 2.1-2.7) added; §Common JS bugs 4a-4e, §Relative path depth tutorial, §Filename convention coordination, §Path-bug detection script deleted; Unit 1 gate trimmed. SKILL.md now 569 lines.
  WS1 complete (2026-04-17): Phases 1-4 delegated to buddy:*; minimal fallback at Appendix.
-->

## When to use

Use this skill when:
- The user asks to create a lesson, course, syllabus, or curriculum
- The user asks to generate activities, exams, flashcards, or other course pages
- The user says "build lesson", "create course", "generate syllabus", etc.

## Step 0: Authenticate Services (ALWAYS RUN FIRST)

**On every invocation**, before asking any questions, immediately check NotebookLM, Tavily Research, and Replicate. Report results to the user upfront so they know what's available.

### 0a. Check NotebookLM

```bash
pip show notebooklm-py 2>&1
```
If installed, test auth:
```bash
PYTHONIOENCODING=utf-8 python -m notebooklm auth check --test --json
```

**If `checks.token_fetch` is `true`:** NotebookLM is ready. Tell the user:
> "NotebookLM: authenticated and ready for AI-powered research."

**If auth fails or package not installed:** Guide the user through login per [NOTEBOOKLM.md](NOTEBOOKLM.md). If they decline or login fails after troubleshooting, set research fallback to **web search** and tell the user:
> "NotebookLM: not available. Will use web search for content research instead."

### 0b. Check Tavily Research (`tvly` CLI)

The lesson builder uses the [tavily-research](https://github.com/tavily-ai/skills) skill (installed at `~/.agents/skills/tavily-research/`) to conduct cited deep research that feeds into NotebookLM. It wraps the `tvly` CLI from Tavily.

Check the CLI is installed and authenticated:

```bash
which tvly 2>&1
PYTHONIOENCODING=utf-8 tvly auth --json 2>&1
```

Parse the JSON: `{"authenticated": true, "source": "config file (...)"}` means good. `false` means a key is needed.

**If `tvly` is on PATH AND `authenticated` is `true`:** Tell the user:
> "Tavily Research: authenticated. Will be used for deep cited research feeding NotebookLM."

**If `tvly` is on PATH but not authenticated:** Try pulling the key from SSM Parameter Store first (this matches the project convention for API keys):
```bash
TAVILY_KEY=$(aws ssm get-parameter --name tavily --with-decryption \
  --region us-west-2 --profile deploy --query 'Parameter.Value' --output text 2>/dev/null)
if [ -n "$TAVILY_KEY" ]; then
  tvly login --api-key "$TAVILY_KEY"
fi
```
If that fails or no SSM parameter exists, tell the user:
> "Tavily Research: CLI installed but not authenticated and no key in SSM. To enable, get a key from https://app.tavily.com/ and run `! tvly login --api-key tvly-YOUR_KEY` in the prompt."

**If `tvly` is not on PATH:** Tell the user how to install it:
> "Tavily Research: CLI not installed. To enable deep cited research, run:
> ```
> ! curl -fsSL https://cli.tavily.com/install.sh | bash
> ```
> After install, the CLI lands in your Python user `Scripts` directory — make sure it's on PATH. Falling back to plain NotebookLM research for now."

**IMPORTANT Windows note:** Always prefix `tvly` commands with `PYTHONIOENCODING=utf-8` and use `-o file` for output instead of stdout. The CLI uses `click.echo` which crashes on cp1252 when the API returns Unicode characters like `\u202f` (narrow no-break space). Same gotcha as `notebooklm`.

Set `research.tavily = true` only if both the CLI is on PATH and `authenticated` is `true` (after attempting SSM auto-login).

### 0c. Check Replicate

```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); token=os.getenv('REPLICATE_API_TOKEN',''); print('HAS_TOKEN' if token and token.startswith('r8_') else 'NO_TOKEN')" 2>&1
```

If that fails (no dotenv), try:
```bash
python -c "import os; token=os.environ.get('REPLICATE_API_TOKEN',''); print('HAS_TOKEN' if token and token.startswith('r8_') else 'NO_TOKEN')" 2>&1
```

Also check for a `.env` file in the project root containing `REPLICATE_API_TOKEN`.

**If token found:** Tell the user:
> "Replicate: API token found. Image generation is available."

**If no token:** Tell the user:
> "Replicate: No API token found. Image generation will be skipped. To enable it later, add `REPLICATE_API_TOKEN=r8_yourtoken` to a `.env` file and get a token from https://replicate.com/account/api-tokens"

Set `images.enabled = false` in the course config regardless of what the config file says.

### 0d. Report Summary

After all checks, present a status box:

> **Service Status:**
> - NotebookLM: [Ready / Unavailable — using web search]
> - Tavily Research: [Ready / Unavailable — using plain NotebookLM source add-research]
> - Replicate: [Ready / Unavailable — skipping image generation]

Then proceed to interactive mode.

## Interactive Mode — Ask Before Building

**If the user invokes this skill without specifying all parameters, ASK:**

1. **Topic/Subject** — "What topic should the course cover?" (e.g., "General English for beginners", "Business English", "English through IT skills")
2. **Languages** — "What is the learner's first language (L1) and target language (L2)?" (default: Thai → English)
3. **Number of weeks/units** — "How many units?" (default: 12)
4. **Age group** — "Who is this course for?"
   - **Children (4-7)** — Audio-first, big visuals, tap/drag interactions, no reading required
   - **Older children (8-12)** — Can read simple text, handle basic game rules
   - **Adults** — Full text-based lessons with grammar explanations
5. **Page types** — "Which page types per unit?" Show options based on age group:

   **Adult page types:**
   - Lesson, Activities, Exam, Flashcards, Conversation, Pronunciation, Worksheet, Syllabus

   **Children's page types:** See [CHILDREN_PAGES.md](CHILDREN_PAGES.md) for full list and specifications (Story, Game, Song, Coloring, Stickers, Flashcards, Reward, Avatar Video for ages 4-7; Comic, Quiz Show, Word Puzzle, Adventure, Journal, Video Lesson, Board Game, Reading for ages 8-12)

6. **Output location** — "Where should files go?" (default: `HTML/courses/{topic_slug}/`)
7. **Color theme** — "Any color preference?" (or auto-pick)

**Research method is auto-selected** based on Step 0 results:
- If Tavily Research + NotebookLM both ready → use **Tavily → NotebookLM bridge** (best quality)
- If only NotebookLM ready → use plain NotebookLM `source add-research`
- If only Tavily Research ready → use Tavily standalone (writes report directly to research.md)
- If neither → use Web Search
- User can override to "training data only" if they want speed over accuracy

**If a config file exists** in `config/` matching the topic, load it instead of asking. Still respect the auth results from Step 0 (e.g., if config has `notebooklm: true` but auth failed, fall back to web search; if config has `images.enabled: true` but no Replicate token, disable images).

## How it works — Buddy Workflow Integration

The lesson builder uses a structured spec → plan → tasks → implement pipeline, delegated to the `buddy:*` skill suite when available. This ensures each course is well-designed before code generation begins.

**Templates and worked example:**
- `templates/buddy/{spec,plan,tasks,research}.md` — placeholder skeletons to copy for a new course
- `specs/EXAMPLE-tefl_children_10_12/` — complete worked example (Thai children ages 10-12, 12 units, 84 files) showing what each artifact looks like filled in. Read this before starting a new course to understand the proven shape and detail level.

### Buddy-availability detection (runs once at Phase 1 start)

Before delegating, check whether `buddy:spec`, `buddy:plan`, `buddy:tasks`, and `buddy:implement` appear in the current session's available skills list (the same list visible in the system-reminder). This is a self-awareness check — the assistant scans its own skill list. No shell `which` call; `buddy:*` are harness-registered skills, not PATH binaries. If all four are present, set `BUDDY_AVAILABLE=1` and use the delegation path below. If any are absent, set `BUDDY_AVAILABLE=0` and use the fallback at `§Appendix: Minimal Inline Fallback`.

### Phase 1: Specification

**Delegate to `buddy:spec` with TEFL-specific overlays.**

Pass inputs from Step 0 + interactive Q&A (topic, L1/L2, weeks, age group, page types, research method, backend choices). TEFL overlays to include: vocabulary density target (10-12 words/unit adults; 6-8 children); bilingual markup rules (§Bilingual Content Rules); page-type catalog for chosen age group (§Adult Page Type Specifications or `templates/children_pages/`); theme palette. Spec lands at `specs/{YYYYMMDD}-{course_id}/spec.md`. Reference: `specs/EXAMPLE-tefl_children_10_12/spec.md`.

**Fallback (buddy:spec not available):** see §Appendix: Minimal Inline Fallback.

### Phase 2: Research & Planning

**Delegate to `buddy:plan` with TEFL-specific research step.**

Run the TEFL-specific corpus loading first (buddy can't do this): use the research method from Step 0 (Tavily→NotebookLM bridge, NotebookLM only, Tavily standalone, or web search). Save findings to `specs/{YYYYMMDD}-{course_id}/research.md`. Then invoke buddy:plan with the research.md content as context. Windows note: always prefix notebooklm/tvly commands with `PYTHONIOENCODING=utf-8`. Plan lands at `specs/{YYYYMMDD}-{course_id}/plan.md`.

**Fallback (buddy:plan not available):** see §Appendix: Minimal Inline Fallback.

### Phase 3: Task Breakdown

**Delegate to `buddy:tasks`.** Pass spec + plan as context. TEFL constraints: include a Unit 1 gate task; include `check_links.py`, `check_exams.py`, `check_pages.py` invocations in Phase 5 tasks; keep tasks terse. Tasks land at `specs/{YYYYMMDD}-{course_id}/tasks.md`.

**Fallback (buddy:tasks not available):** see §Appendix: Minimal Inline Fallback.

### Phase 4: Implementation

**Delegate to `buddy:implement`.** Pass the full `specs/{YYYYMMDD}-{course_id}/` directory as context.

TEFL-specific constraint: **pause at Unit 1 gate.** buddy:implement must stop after generating Unit 1, report that Unit 1 is ready for browser verification, and wait for operator confirmation before proceeding to bulk generation. This is the single most important structural rule — do not let buddy:implement auto-proceed past Unit 1.

**Fallback (buddy:implement not available):** see §Appendix: Minimal Inline Fallback.

### Phase 5: Post-Generation Verification (REQUIRED)

Before declaring the course complete, run two automated checks and one semantic review. These catch the two classes of bugs that have shipped to users and been reported back as complaints: **broken links** and **unanswerable exam questions**.

#### 5a. Link check (always run)

```bash
python scripts/check_links.py {output_dir} --html-root HTML
```

The script walks every `.html` file in the course directory and reports:
- **BROKEN** — a `href` or `src` points at a local file that doesn't exist on disk
- **DEPTH** — a media ref like `../imgs/foo.png` uses the wrong number of `..` for the page's depth (so it deploys correctly locally but 404s on S3 — this is the bug we hit on the English Quest teens_13_14 course)
- **YouTube embeds** — list of video IDs for the user to spot-check
- **External URLs** — list of external refs for the user to review (optional `--check-external` flag HEADs each one)

Fix every BROKEN and DEPTH finding by editing the generator (not the HTML — the HTML is a build output), then regenerate the affected pages. Don't proceed until the script exits 0.

#### 5b. Exam answerability check (if course has exam pages)

Exam pages ship with embedded question banks. The common complaints from learners are:
- "The question is incomplete" — e.g. the vocabulary word got stripped and the question reads `What is the meaning of ""?`
- "None of the answers are right" — the distractors are fine but the correct option was swapped with a near-miss
- "Two answers look correct" — the distractors aren't actually distinct from the correct answer

Step 1 — run the structural check:

```bash
python scripts/check_exams.py {output_dir} --review-out {output_dir}/_exam_review.json
```

This catches: empty/placeholder question text, fewer than 2 real options, duplicate options, `correct` index out of range, explanation that quotes a string no option matches. Fix any structural issues in the generator and regenerate.

Step 2 — **semantic review** (mandatory). The script writes `_exam_review.json` containing every question with its options, correct index, and explanation. You (the skill) MUST read this file and for each question verify:

1. **Is the question complete?** A question like `What is the meaning of ""?` or `Choose the correct form of to` is incomplete — a word was stripped during generation.
2. **Does `options[correct_index]` actually answer the question?** E.g. if the question is "What is the past tense of 'go'?" and `options[correct]` is `"going"`, that is wrong.
3. **Are any *other* options also correct?** A question like "Which is a greeting?" with options `["hello", "hi", "bye", "goodbye"]` has two right answers — unanswerable as written.
4. **Are the distractors plausible but clearly wrong?** If the distractors are nonsense strings or identical in meaning to the correct one, the question is either trivial or broken.

Report findings back in this format:

```
Exam review: N questions across M exam files

Issues:
  begin_greetings_exam.html / vocabulary/easy #3
    Q: "What is the meaning of \"\"?"
    → question is truncated (empty quoted word)
    → fix generator: vocab loop lost the word variable

  begin_food_exam.html / grammar/medium #7
    Q: "Which is the correct plural of 'fish'?"
    Options: ["fish", "fishes", "fishies", "none of these"]
    correct=0 ("fish")
    → "fishes" is also accepted as plural in several contexts (different species);
      rewrite the distractor or add specificity to the question
```

Then fix the generator and regenerate the affected exam pages. Re-run both checks until clean.

#### 5c. When to skip

- **Skip 5b if `page_structure.exam` is `"none"`** for this course.
- **Never skip 5a.** Every course has links; every course needs the check.

### Operational: Patching a Single Page or Question

For a single learner-reported bug, use `scripts/regenerate.py` instead of re-running the full generator. This avoids touching the other 80+ files in the course.

```bash
# Page-level: regenerate unit 7's quiz page only
python scripts/regenerate.py --course-config config/children_10_12.json --unit 7 --page-type quiz

# Page-level: regenerate unit 3's story page
python scripts/regenerate.py --course-config config/children_10_12.json --unit 3 --page-type story

# Question-level: replace just question 4 (0-based) in unit 7's quiz
python scripts/regenerate.py --course-config config/children_10_12.json --unit 7 --exam-question vocabulary:medium:4

# Determinism check: verify regenerated output matches full-generator for that page
python scripts/regenerate.py --course-config config/children_10_12.json --unit 7 --page-type quiz --determinism-check
```

Supported courses: `children_10_12`, `teens_13_14`, `tefl_beginners`, `tefl_intermediate`. Each run appends a JSON event to `{output_dir}/_regenerate_log.jsonl` for audit.

### Stepping Through vs. Auto-Run

By default, **pause after Phase 1 (spec)** to confirm with the user before proceeding. The user can say:
- "Looks good, continue" → proceed through phases 2-4 automatically
- "Change X" → update spec and re-confirm
- "Just generate" → skip remaining phases, go straight to generation (legacy mode)

## Legacy Mode (Direct Generation)

If the user says "just generate" or "skip planning", bypass the buddy workflow and generate directly:

1. Gather requirements (interactive or config)
2. Research (NotebookLM/web search/training data)
3. Fact-check
4. Write Python generator script (`generate_{course_id}.py`) and run it
5. Images (if Replicate available)
6. Hero video (optional — ask user)

This preserves backward compatibility for quick one-off generation.

## Configuration System

Courses are defined by JSON config files in `config/`. See `config/schema.md` for the full specification.

### Key config fields

```jsonc
{
  "course_id": "my_course",         // Used for filenames
  "l1": "th", "l2": "en",           // Language pair
  "output_dir": "HTML/courses/my_course",
  "theme": { "primary": "#f97316", ... },

  // Page types per unit — flexible assignment
  "page_types": {
    "lesson": "every",              // Generate for every unit
    "activities": "every",
    "exam": "every",
    "flashcards": "random:3",       // Randomly assign to 3 units
    "conversation": "random:4",
    "pronunciation": "units:6,9,12", // Only these specific units
    "worksheet": "random:3",
    "syllabus": true                 // One per course
  },

  // Page structure — what sections each page type contains
  "page_structure": {
    "lesson": {
      "sections": ["introduction", "vocabulary", "grammar", "tutorial_steps", "activity", "reference_table", "summary"],
      "section_checks": true,
      "homework": true,
      "audio_buttons": true
    },
    "exam": {
      "categories": 5,
      "difficulty_selector": true,
      "gradebook": true
    }
    // ... see schema.md for all options
  },

  // Research & quality
  "research": {
    "tavily": true,              // Run tvly research and feed results into NotebookLM (best quality)
    "notebooklm": true,
    "web_search": true,          // Fallback if neither tavily nor notebooklm available
    "fact_check": true
  },

  // AI image generation (requires Replicate account)
  "images": {
    "enabled": false,
    "provider": "replicate",
    "model": "black-forest-labs/flux-dev"
  },

  // The actual course content
  "units": [ ... ]          // See schema.md for unit format
}
```

### Page type assignment modes

| Mode | Example | Behavior |
|------|---------|----------|
| `"every"` | `"lesson": "every"` | Generate for all units |
| `"none"` | `"exam": "none"` | Never generate |
| `"random:N"` | `"flashcards": "random:3"` | Randomly assign to N units |
| `"units:1,5,9"` | `"pronunciation": "units:6,9,12"` | Only specific units |
| Override per unit | `"page_types_override": {"conversation": true}` | Force on/off for one unit |

## Adult Page Type Specifications

All pages use inline CSS (no external dependencies except Google Fonts). All content is bilingual (L1 first, L2 second).

### Lesson Page
7 sections: Introduction (bilingual box + fun facts), Vocabulary (10-12 flip cards with audio), Grammar Focus (rules + examples in both languages), Tutorial Steps (guided practice), Hands-On Activity, Reference Table, Summary. Includes section-check quizzes (configurable count), homework section, and references.

### Activities Page
5-6 activity cards with difficulty badges (Easy/Medium/Hard). Types: fill-in-the-blank, matching, labeling, role-play, writing, troubleshooting. Mark-as-complete buttons.

### Exam Page
Interactive exam with difficulty selector (Easy/Medium/Hard controlling question count). Question bank with configurable categories. Full exam engine JS with score calculation, answer review, and optional gradebook integration (localStorage).

### Flashcard Page
Interactive flip cards. Front: L2 term + pronunciation button. Back: L1 translation + definition + example sentence. Controls: shuffle, progress counter, prev/next, keyboard navigation (Space/arrows).

### Conversation Page
Situation setup (bilingual), dialogue with speech bubbles and speaker labels, audio buttons per line, key phrases box, comprehension questions, role-play prompts.

### Pronunciation Page
Target sound description (bilingual), L1 interference callout, minimal pairs with audio, listen-and-repeat with slow mode (0.6x), tongue twisters, practice sentences.

### Worksheet Page
Print-optimized (`@media print`). Fill-in-the-blank, matching, unscramble, writing prompts with dotted lines. Hidden answer key with toggle button.

### Syllabus Page
Course overview with sticky header, week navigation, hero section, scope table, week cards (objectives + vocab + grammar pattern), assessment rubric, outcomes, and **References & Research Basis** section. Uses different font stack (DM Sans/Noto Sans Thai/DM Serif Display).

**References & Research Basis section (REQUIRED):**

Every syllabus MUST include a "References & Research Basis" section that documents the evidence base behind the course design. This serves three purposes:
1. **Transparency for learners and parents** — they can see this isn't a random course, it's grounded in peer-reviewed research
2. **Provenance for teachers and reviewers** — they can trace pedagogical decisions back to their sources
3. **Defensibility if challenged** — academic-grade citation chain protects the course content

The section must include:
- **Research files used** — list every Tavily Research file in `specs/{date}-{course_id}/tavily/` (filename + brief topic + source count)
- **Total cited sources** — aggregate count across all research files (e.g., "94 peer-reviewed sources")
- **Pedagogical principles list** — bullet list of every evidence-based principle baked into the course design, each citing the underlying research file
- **External corpus references** if used (TLE, ICNALE, CEFR Companion Volume, etc.)
- **Citation footer note** pointing to where the original research artifacts live (e.g., "Full research reports available in `specs/{date}-{course_id}/tavily/`")
- **NotebookLM notebook ID** if a per-unit Q&A grounding pass was run in Phase 2 (allows future re-querying against the same corpus)
- **Optional: links to external research databases** (Cambridge ReCALL, MDPI, NCBI/PMC, ScienceDirect, Springer, ERIC, Council of Europe CEFR portal)

The section should be visually distinct (use a `.references-section` class) and placed near the bottom of the syllabus, after assessment rubric and outcomes but before the footer. Use a slightly muted background (e.g., `--primary-pale` from the course theme) so it reads as supplementary metadata rather than primary content.

When a syllabus includes both a hero video and hero image:
- **Video** goes first (inside `.hero-video` div, no `poster` attribute)
- **Image** goes below as a separate element (inside `.hero-img` div)
- They must NOT overlap — use `margin-top: 20px` on the image container for spacing

## Nav Footer (All Pages)

Every page in a unit MUST include a `.nav-footer` with links to **ALL** page types generated for that unit, not just a subset. The generator script must track which page types each unit has and inject the complete nav footer into every page for that unit.

## Quality Checklist — Run Before Delivery

### 1. Test one unit end-to-end first
Generate **only unit 1** first. Open every page in a browser and verify:
- All interactive features work (games load, songs play, stickers place)
- No JS console errors
- Nav footer links to all pages in the unit
- Story emojis vary per page
- TTS speaks correctly on all buttons

Only after unit 1 passes, generate remaining units using the same templates.

### 2. Cross-file consistency
- Every function called in JS is defined in the same `<script>` block — pages are standalone HTML with no shared JS files
- Nav footer on every page lists ALL page types for that unit
- No hardcoded page-type subsets — always derive from the unit's actual page list

### 3. Content-specific visuals
- Story page emojis: each of the 6 pages shows a DIFFERENT emoji matching its vocabulary word
- Sticker page: uses themed concrete objects (animals, food, etc.), not abstract shapes
- Emoji colors match the text: if the label says "blue bird", the emoji must naturally render as blue. See [IMAGE_GENERATION.md](IMAGE_GENERATION.md) for emoji color reference
- Song page: embeds a real YouTube children's song (verify video ID is valid)

### 4. JS quality checks

Rules 2.1–2.5 and 2.7 are mechanically enforced by `scripts/check_pages.py` (run in Phase 5). One operational concern that remains:

#### localStorage quota
Each page-type's localStorage keys should have a per-key size budget. For a 12-unit course with chat history + quiz scores + project drafts + vocab tracking, total budget should stay under 1 MB. If quota is hit, fall back to clearing oldest entries first.

## Bilingual Content Rules

- L1 text appears **first** (left column in bilingual boxes)
- L2 text appears **second** (right column)
- L1 orange background (`#fff3e0` with `#FF9800` border)
- L2 blue background (`#e3f2fd` with `#2196F3` border)
- All grammar explanations in **both** languages
- All quiz questions have L1 translation
- All vocab cards have L1 translation **and** bilingual definition
- Homework tasks must be bilingual

## CSS Theme Variables

Each course defines a color theme in its config. Lesson pages use:
```css
:root {
  --primary: {from config};
  --primary-dark: {from config};
  --primary-light: {from config};
  --primary-pale: {from config};
  --accent: {from config};
}
```

Fonts: `'Sarabun','Nunito',sans-serif` for lesson/activity/exam pages.
Fonts: `'DM Sans','Noto Sans Thai',sans-serif` for syllabus pages.

## JS Components

### speak() — Text-to-Speech
```javascript
function speak(text) {
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.rate = 0.9; u.lang = '{l2 locale}';
    window.speechSynthesis.speak(u);
}
```

### scAnswer() — Section Check Engine
Interactive quiz engine with score tracking. See `config/schema.md` for ID conventions.

### Exam Engine
Difficulty selector → question rendering → answer checking → score display → gradebook save.
Gradebook: `wdc_saveScore(examKey, percentage, grade)` saves to localStorage.

## Generator Script Pattern

For bulk generation, write a Python script rather than individual files:

```python
import os, json

# Load config
with open('config/my_course.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

OUT_DIR = config['output_dir']
os.makedirs(OUT_DIR, exist_ok=True)

def generate_lesson(unit, config): ...
def generate_activities(unit, config): ...
def generate_exam(unit, config): ...
def generate_flashcards(unit, config): ...
# ... one function per page type

for unit in config['units']:
    for page_type, gen_fn in page_generators.items():
        if should_generate(page_type, unit, config):
            path = os.path.join(OUT_DIR, f"{unit['prefix']}_{page_type}.html")
            with open(path, 'w', encoding='utf-8') as f:
                f.write(gen_fn(unit, config))
```

### Critical implementation notes
- **Always `encoding='utf-8'`** for all file operations (non-ASCII text breaks on Windows default cp1252)
- **Keep scripts under ~3000 lines** — split into parts if larger
- **Sequential generation only** — never launch multiple heavy agents in parallel (they exhaust token budget and all fail)
- **One course at a time** — verify output before starting the next

### Relative path depth

The number of `..` segments in a relative path must equal the page's depth from `HTML/` root — enforced by `scripts/check_links.py` (depth check) and `scripts/check_pages.py` (rule 2.6 src existence). Make `html_relative_path` configurable in the course config, not hardcoded in the generator.


### Unit 1 verification gate — what to actually verify

**The Unit 1 gate is load-bearing.** Run `scripts/check_pages.py`, `scripts/check_links.py`, and `scripts/check_exams.py` first; they catch mechanical issues automatically. Then do the human-only checks:

1. **Open DevTools Console.** ANY red error or warning is a fail. Most subtle bugs surface here.
2. **Click every interactive element on every page** — every vocab card flip, every quiz answer button, every chat scenario chip, every "Next" button, every "Save to Portfolio" button. Watch the console while doing it.
3. **Refresh the page** after entering quiz/project/chat data. Verify `localStorage` persistence — data should still be there.
4. **Test mobile breakpoints** — DevTools responsive mode at 768px and 480px. Check for layout breakage, button overlap, text overflow.
5. **For chatbot pages: send a real test message and verify the response renders + speaks correctly.** This proves the Lambda endpoint is reachable.

If ANY of these checks fail, fix the generator (not the HTML — the HTML is a build output) and re-run generation before re-checking.

### FLUX safety filter false positives

**This came up on English Quest where `quest_health_fitness_vocab_sleep.png` was rejected as NSFW.** FLUX Dev's safety filter can flag prompts that combine common words in unexpected ways, especially:
- "teen" or "child" + bedroom/sleep/bed words
- "teen" + bath/shower/changing words
- "teen" + medical/body words

**Mitigation:** when a vocab item triggers a content filter false positive, retry with a more constrained prompt that explicitly anchors the context. Example for "sleep":
- ❌ Triggers: "A Thai teenager sleeping"
- ✓ Works: "A Thai teenager studying late at a desk, then yawning, with a clock showing it's bedtime"
- ✓ Works: "A clean educational illustration showing the abstract concept of rest — a closed book, a moon icon, an alarm clock"

The image generator script should support per-vocab prompt overrides via the config so the rare problematic items can be re-prompted without changing the global style prefix.


## Example Configs

- `config/tefl_beginners.json` — 12-week Thai→English beginner course (everyday + work), web search research
- `config/tefl_intermediate.json` — 12-week Thai→English intermediate course (career growth), NotebookLM research
- `config/schema.md` — Full configuration schema documentation

## Extending

To add a new page type:
1. Add it to `page_types` in the config schema
2. Add its structure options to `page_structure`
3. Write a `generate_{type}(unit, config)` function in the generator script
4. Document it in this skill file

## Appendix: Minimal Inline Fallback (no buddy:* installed)

**WARNING — This is a safety net, not a second canonical path. Do not grow it. If `buddy:*` becomes unavailable for a real user, fix the harness installation, not this fallback. Never add workflow logic here that duplicates or competes with what `buddy:spec / buddy:plan / buddy:tasks / buddy:implement` do.**

Use this fallback only when `BUDDY_AVAILABLE=0` (buddy:* skills not in the available-skills list).

**4-step barest pipeline:**

1. **Create the course folder:**
   ```bash
   mkdir -p specs/{YYYYMMDD}-{course_id}/
   ```

2. **Copy templates in:**
   ```bash
   cp templates/buddy/spec.md     specs/{YYYYMMDD}-{course_id}/spec.md
   cp templates/buddy/plan.md     specs/{YYYYMMDD}-{course_id}/plan.md
   cp templates/buddy/tasks.md    specs/{YYYYMMDD}-{course_id}/tasks.md
   cp templates/buddy/research.md specs/{YYYYMMDD}-{course_id}/research.md
   ```

3. **Fill in the obvious fields** in each template (course_id, topic, L1/L2, weeks, age group, page types, output_dir, theme). Use `specs/EXAMPLE-tefl_children_10_12/` as the reference shape for content and detail level.

4. **Stop and hand off to the operator** — present the filled-in spec.md for review before proceeding to any generation. The operator must confirm the spec before the course is built. This fallback does not implement the full buddy workflow; it only produces the file scaffold.
