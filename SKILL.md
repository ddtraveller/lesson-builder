---
name: lesson-builder
description: "Generates bilingual TEFL/ESL courses with lessons, exams, flashcards, conversations, pronunciation drills, worksheets, and syllabi for any language pair."
---

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

The lesson builder uses a structured spec → plan → tasks → implement pipeline adapted from the buddy workflow. This ensures each course is well-designed before code generation begins.

**Templates and worked example:**
- `templates/buddy/{spec,plan,tasks,research}.md` — placeholder skeletons to copy for a new course
- `specs/EXAMPLE-tefl_children_10_12/` — complete worked example (Thai children ages 10-12, 12 units, 84 files) showing what each artifact looks like filled in. Read this before starting a new course to understand the proven shape and detail level.

### Phase 1: Specification (`/buddy:spec` pattern)

After gathering requirements interactively (or loading a config), create a course specification:

1. Create folder: `specs/{YYYYMMDD}-{course_id}/`
2. Write `specs/{YYYYMMDD}-{course_id}/spec.md` containing:
   - Course identity (title, languages, level, schedule)
   - Target audience and age group
   - Unit breakdown with topics, vocabulary themes, and grammar points
   - Page types per unit (with assignment modes)
   - Research method and available services (from Step 0)
   - Image generation availability
   - Theme and output configuration
   - Acceptance criteria (what "done" looks like for this course)
3. Mark unclear aspects with `[NEEDS CLARIFICATION: ...]`
4. Present clarification questions to the user
5. Update spec with answers, set status to "Ready for Review"

### Phase 2: Research & Planning (`/buddy:plan` pattern)

Once the spec is confirmed, research content and create an implementation plan:

1. **Research** using the method determined in Step 0:

   **Tavily → NotebookLM bridge** (best quality — both ready):
   - Run `tvly research` for 2–3 queries covering curriculum, L1 interference, and (optionally) niche vocab. Use `--model pro` for the comprehensive multi-angle pass and `--json` so we get structured sources to feed NotebookLM. **Always set `PYTHONIOENCODING=utf-8`** — the CLI crashes on Windows cp1252 when the API returns Unicode whitespace characters:
     ```bash
     mkdir -p specs/{YYYYMMDD}-{course_id}/tavily
     PYTHONIOENCODING=utf-8 tvly research "{topic} curriculum CEFR {level} for {audience}" \
       --model pro --json \
       -o specs/{YYYYMMDD}-{course_id}/tavily/curriculum.json
     PYTHONIOENCODING=utf-8 tvly research "teaching {L2} to {L1} speakers {level} common errors pronunciation" \
       --model pro --json \
       -o specs/{YYYYMMDD}-{course_id}/tavily/l1_interference.json
     # Optional 3rd query for niche vocab topics
     PYTHONIOENCODING=utf-8 tvly research "{topic} essential vocabulary {level} authoritative wordlists" \
       --model pro --json \
       -o specs/{YYYYMMDD}-{course_id}/tavily/vocab.json
     ```
   - **Bridge into NotebookLM** — for each Tavily report, create the notebook (once), then ingest the markdown report (`content` field) as a text source AND ingest each source URL (`sources[*].url`) as a URL source. Verified JSON shape (as of `tavily-cli 0.1.0`): `{"content": "<markdown>", "sources": [{"url": "...", "title": "...", "favicon": "..."}], "status", "created_at", "response_time", "request_id"}`. Cap source ingestion to stay under NotebookLM's 50-source free-tier ceiling:
     ```bash
     NB_ID=$(PYTHONIOENCODING=utf-8 python -m notebooklm create "Course: {topic}" --json \
              | python -c "import sys,json;print(json.load(sys.stdin)['id'])")

     for FILE in specs/{YYYYMMDD}-{course_id}/tavily/*.json; do
       # 1. Extract markdown report (content field) and ingest as text source
       python -c "import json; print(json.load(open(r'$FILE', encoding='utf-8'))['content'])" \
         > "${FILE%.json}.md"
       PYTHONIOENCODING=utf-8 python -m notebooklm source add "$NB_ID" --file "${FILE%.json}.md"

       # 2. Extract source URLs (sources[*].url) and ingest each (cap at 10 per query)
       python -c "
import json
d = json.load(open(r'$FILE', encoding='utf-8'))
for s in d.get('sources', [])[:10]:
    if s.get('url'): print(s['url'])
" | while read URL; do
         PYTHONIOENCODING=utf-8 python -m notebooklm source add "$NB_ID" --url "$URL"
       done

       PYTHONIOENCODING=utf-8 python -m notebooklm source wait "$NB_ID"
     done
     ```
   - Run the existing `notebooklm ask` loop against the enriched corpus to get per-unit content.
   - Save Q&A answers + Tavily report file paths to `specs/{YYYYMMDD}-{course_id}/research.md` for traceability.

   > **Tip:** Tavily's `mini` model returns ~7 sources, `pro` returns more. Spot-check the top URLs before bulk ingestion — Tavily can surface low-quality results for niche queries. If the JSON shape ever changes in a future `tavily-cli` release, run `PYTHONIOENCODING=utf-8 tvly research "test" --model mini --json -o /tmp/t.json` and inspect `t.json` to update the key paths above.

   **NotebookLM only** (NotebookLM ready, Tavily not):
   - Create a research notebook:
     ```bash
     PYTHONIOENCODING=utf-8 python -m notebooklm create "Course: {topic}" --json
     ```
   - Add research sources (2-3 queries covering curriculum, grammar, and L1 interference):
     ```bash
     PYTHONIOENCODING=utf-8 python -m notebooklm source add-research "{topic} curriculum CEFR {level}"
     PYTHONIOENCODING=utf-8 python -m notebooklm source add-research "teaching English {L1} speakers {level} common errors"
     ```
   - Query for content per topic area:
     ```bash
     PYTHONIOENCODING=utf-8 python -m notebooklm ask "What are the key grammar topics for {level}?" --json
     PYTHONIOENCODING=utf-8 python -m notebooklm ask "What vocabulary is essential for {topic area}?" --json
     ```
   - Save research findings to `specs/{YYYYMMDD}-{course_id}/research.md`

   **Tavily Research standalone** (Tavily ready, NotebookLM not):
   - Run the same 2–3 `tvly research --model pro` queries from the bridge block above, but write directly to markdown instead of JSON (always with `PYTHONIOENCODING=utf-8`):
     ```bash
     PYTHONIOENCODING=utf-8 tvly research "{topic} curriculum CEFR {level}" --model pro \
       -o specs/{YYYYMMDD}-{course_id}/research_curriculum.md
     PYTHONIOENCODING=utf-8 tvly research "teaching {L2} to {L1} speakers common errors" --model pro \
       -o specs/{YYYYMMDD}-{course_id}/research_l1.md
     ```
   - Concatenate or summarize these reports into the final `specs/{YYYYMMDD}-{course_id}/research.md`
   - No Q&A grounding layer; tell the user this is degraded mode

   **Web Search** (fallback — neither ready):
   - Search for curriculum references, grammar examples, and vocabulary verification from 2+ authoritative sources
   - Verify vocabulary definitions and L1 translations
   - Save source citations to `specs/{YYYYMMDD}-{course_id}/research.md`

   **Training data only** (if user chose speed):
   - Inform: *"Generating from training data. For higher accuracy, re-run with Tavily Research or NotebookLM."*

2. **Fact-Check** using the `fact-checker` skill (if available) to verify grammar rules, vocabulary, quiz answers, and real-world examples.

3. Write `specs/{YYYYMMDD}-{course_id}/plan.md` containing:
   - Research summary and sources used
   - Generation strategy (which units first, page type order)
   - Python generator script architecture (functions, modules, line count estimates)
   - Unit content outlines (vocabulary lists, grammar topics, activity ideas per unit — informed by research)
   - Image generation plan (if Replicate available)
   - Video plan (if applicable)
   - Risk assessment (large script splitting, encoding issues, etc.)
4. Mark unclear aspects, get clarifications, set status to "Ready for Review"

### Phase 3: Task Breakdown (`/buddy:tasks` pattern)

Convert the plan into executable tasks. Start from `templates/buddy/tasks.md` — it already encodes the proven shape from `specs/EXAMPLE-tefl_children_10_12/tasks.md`:

1. Write `specs/{YYYYMMDD}-{course_id}/tasks.md` with ordered tasks. The load-bearing structure is:
   - **Setup** (T001): create output directory
   - **Generator script** (T002–T004): write the script. Collapse to a single task for small courses (<2000 lines); split into Part 1 / Part 2 / COURSE_DATA for larger ones
   - **Unit 1 gate** (T005–T006): generate Unit 1 only, browser-verify it. **Do not proceed past this gate until Unit 1 is clean.**
   - **Bulk generation** (T007): all remaining units
   - **Polish** (T008–T009): cross-file consistency check, syllabus
   - **Optional extras** (T0XX): image generation if Replicate available, video if requested

2. Keep tasks terse. Per-task file paths, acceptance criteria, and `[P]` parallel flags are not required — for single-script generator courses they add ceremony without payoff. The Unit 1 gate is the only structural rule that has to hold.
3. Set status to "Ready for Review".

### Phase 4: Implementation (`/buddy:implement` pattern)

Execute the tasks in order:

1. Read all docs in `specs/{YYYYMMDD}-{course_id}/` (spec, plan, tasks, research)
2. Execute phase-by-phase:
   - **Setup first** — directories, config, script skeleton
   - **Unit 1 first** — generate only unit 1 as a test
   - **Verify Unit 1** — check in browser before proceeding
   - **Remaining units** — generate after Unit 1 passes
   - **Images** — if Replicate available
   - **Video** — if user wants it
   - **Polish** — consistency checks, final testing
3. Update `tasks.md` after each task: `- [ ]` → `- [X]`
4. Report progress after each completed task
5. On completion, update tasks.md status to "Completed"

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

### 4. Common JS bugs to avoid
- **Never reference undefined functions.** Every function used in `onclick`, `innerHTML` strings, or event handlers must be defined in the same script block.
- **Quote safety in inline handlers.** When building `onclick="speak('word')"` via string concatenation, the word itself must not contain single quotes.
- **Always cancel speechSynthesis** before speaking to prevent queue buildup.

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
