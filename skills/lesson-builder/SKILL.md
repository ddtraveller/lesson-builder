---
name: lesson-builder
description: Generate complete bilingual TEFL/ESL courses with configurable page types — lessons, exams, flashcards, conversations, pronunciation drills, worksheets, and syllabi. Works for any language pair and topic. Includes AI research and fact-checking.
user_invocable: true
metadata:
  tags: lesson, course, education, TEFL, ESL, language-learning, curriculum
---

## When to use

Use this skill when:
- The user asks to create a lesson, course, syllabus, or curriculum
- The user asks to generate activities, exams, flashcards, or other course pages
- The user says "build lesson", "create course", "generate syllabus", etc.

## Interactive Mode — Ask Before Building

**If the user invokes this skill without specifying all parameters, ASK:**

1. **Research method** (ask FIRST) — "How should I research course content?"
   - 🔬 **NotebookLM** (default, recommended) — AI-powered research using Google NotebookLM. Creates a research notebook, imports web sources on the topic, and queries them for verified content per unit. Produces higher-quality, citation-backed material.
   - 🌐 **Web Search** — Search the web directly for curriculum references, grammar examples, and vocabulary verification.
   - 📚 **Training data only** — Generate from AI knowledge without external research. Fastest but least verified.

   If the user picks NotebookLM, **immediately verify it is set up** before asking remaining questions (see "NotebookLM Setup Guide" below). Do NOT proceed to content generation until auth is confirmed.

2. **Topic/Subject** — "What topic should the course cover?" (e.g., "General English for beginners", "Business English", "English through IT skills")
3. **Languages** — "What is the learner's first language (L1) and target language (L2)?" (default: Thai → English)
4. **Number of weeks/units** — "How many units?" (default: 12)
5. **Page types** — "Which page types per unit?" Show options:
   - 📄 **Lesson** — Main content with vocabulary, grammar, tutorials, section quizzes
   - 📝 **Activities** — Hands-on practice with difficulty levels (Easy/Medium/Hard)
   - 📝 **Exam** — Interactive exam with difficulty selector and score tracking
   - 🃏 **Flashcards** — Interactive flip cards for vocabulary drilling
   - 💬 **Conversation** — Dialogue scenarios with role-play and audio
   - 🔊 **Pronunciation** — Sound drills targeting L1 interference patterns
   - 🖨️ **Worksheet** — Print-friendly exercises with hidden answer key
   - 📊 **Syllabus** — Course overview page
6. **Output location** — "Where should files go?" (default: `HTML/courses/{topic_slug}/`)
7. **Color theme** — "Any color preference?" (or auto-pick)

**If a config file exists** in `config/` matching the topic, load it instead of asking. Still check that the research method in the config is available (e.g., if `notebooklm: true`, verify auth before proceeding).

## NotebookLM Setup Guide

When the user chooses NotebookLM (or a config has `notebooklm: true`), run this setup sequence:

### 1. Check if notebooklm-py is installed
```bash
pip show notebooklm-py 2>&1
```
If not found, install it:
```bash
pip install notebooklm-py
```

### 2. Check authentication (use PYTHONIOENCODING=utf-8 on Windows to avoid encoding crashes)
```bash
PYTHONIOENCODING=utf-8 python -m notebooklm auth check --test --json
```

Parse the JSON result:
- If `checks.token_fetch` is `true` → auth is good, proceed
- If `checks.token_fetch` is `false` or `null` → auth expired or missing

### 3. If auth is expired/missing, guide the user through login
Tell the user:
> NotebookLM needs to authenticate with your Google account. Please run this command in your terminal (outside Claude Code):
> ```
> python -m notebooklm login
> ```
> This will open a browser window. Sign in with your Google account and wait for the CLI to confirm success.

If the user reports the browser didn't open, suggest:
> Try installing the browser first:
> ```
> python -m playwright install chromium
> ```
> Then retry `python -m notebooklm login`.

If login still fails, suggest deleting stale auth and retrying:
> ```
> del %USERPROFILE%\.notebooklm\storage_state.json   (Windows)
> rm ~/.notebooklm/storage_state.json                 (Mac/Linux)
> python -m notebooklm login
> ```

### 4. Verify auth works after login
```bash
PYTHONIOENCODING=utf-8 python -m notebooklm create "test" --json
```
If this succeeds (returns a notebook ID), auth is confirmed. Delete the test notebook:
```bash
PYTHONIOENCODING=utf-8 python -m notebooklm notebook delete <id>
```

### 5. If auth cannot be established, offer fallback
Tell the user: *"NotebookLM authentication couldn't be set up. Would you like to fall back to web search or training data instead?"*

**IMPORTANT Windows note:** Always prefix notebooklm commands with `PYTHONIOENCODING=utf-8` when running via Bash tool. The CLI uses the `rich` library which crashes on Windows cp1252 encoding when outputting unicode characters (checkmarks, tables). The `--json` flag also helps avoid this, but set the env var as a safety measure.

## How it works

### Step 1: Gather Requirements
Either load from a config JSON (`config/{course_id}.json`) or ask interactively.

### Step 2: Research
Verify course content against authoritative sources **before** generating. Use whichever method the user chose (or config specifies).

**NotebookLM** (default):
1. Create a research notebook:
   ```bash
   PYTHONIOENCODING=utf-8 python -m notebooklm create "Course: {topic}" --json
   ```
2. Add research sources (2-3 queries covering curriculum, grammar, and L1 interference):
   ```bash
   PYTHONIOENCODING=utf-8 python -m notebooklm source add-research "{topic} curriculum CEFR {level}"
   PYTHONIOENCODING=utf-8 python -m notebooklm source add-research "teaching English {L1} speakers {level} common errors"
   ```
3. Query for content per topic area:
   ```bash
   PYTHONIOENCODING=utf-8 python -m notebooklm ask "What are the key grammar topics for {level}?" --json
   PYTHONIOENCODING=utf-8 python -m notebooklm ask "What vocabulary is essential for {topic area}?" --json
   ```
4. Use the research answers to inform the generated course content.

**Web Search** (fallback or if user chose it):
- Search for the unit's subject topic from 2+ authoritative sources
- Search for the grammar point with examples
- Verify vocabulary definitions and L1 translations
- Save source citations for the references section

**Training data only** (last resort):
Inform the user: *"Generating content from training data. For higher accuracy, consider using NotebookLM or web search."*

### Step 3: Fact-Check
Use the `fact-checker` skill (default — if available) to verify:
- Grammar rules and examples are correct
- Vocabulary definitions and translations are accurate
- Quiz answers are correct
- Real-world examples are current

**If fact-checker is not available**, inform the user: *"I'll do my best to verify content, but consider reviewing grammar rules and translations before publishing."*

### Step 4: Generate
Write a Python generator script (`generate_{course_id}.py`) that produces all files, then run it. The script filename MUST match the `course_id` from the config (e.g., `generate_tefl_intermediate.py` for course_id `tefl_intermediate`). Never reuse or overwrite another course's generator.

### Step 5: Images (optional)
If configured and Replicate API token is available, generate illustrations using FLUX Dev.

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
    "notebooklm": true,   // Default true — falls back to WebSearch if unavailable
    "web_search": true,    // Default true — used as fallback or supplement
    "fact_check": true     // Default true — falls back to self-review if unavailable
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

## Page Type Specifications

All pages use inline CSS (no external dependencies except Google Fonts). All content is bilingual (L1 first, L2 second).

### 📄 Lesson Page
7 sections: Introduction (bilingual box + fun facts), Vocabulary (10-12 flip cards with audio), Grammar Focus (rules + examples in both languages), Tutorial Steps (guided practice), Hands-On Activity, Reference Table, Summary. Includes section-check quizzes (configurable count), homework section, and references.

### 📝 Activities Page
5-6 activity cards with difficulty badges (Easy/Medium/Hard). Types: fill-in-the-blank, matching, labeling, role-play, writing, troubleshooting. Mark-as-complete buttons.

### 📝 Exam Page
Interactive exam with difficulty selector (Easy/Medium/Hard controlling question count). Question bank with configurable categories. Full exam engine JS with score calculation, answer review, and optional gradebook integration (localStorage).

### 🃏 Flashcard Page
Interactive flip cards. Front: L2 term + pronunciation button. Back: L1 translation + definition + example sentence. Controls: shuffle, progress counter, prev/next, keyboard navigation (Space/arrows).

### 💬 Conversation Page
Situation setup (bilingual), dialogue with speech bubbles and speaker labels, audio buttons per line, key phrases box, comprehension questions, role-play prompts.

### 🔊 Pronunciation Page
Target sound description (bilingual), L1 interference callout, minimal pairs with audio, listen-and-repeat with slow mode (0.6x), tongue twisters, practice sentences.

### 🖨️ Worksheet Page
Print-optimized (`@media print`). Fill-in-the-blank, matching, unscramble, writing prompts with dotted lines. Hidden answer key with toggle button.

### 📊 Syllabus Page
Course overview with sticky header, week navigation, hero section, scope table, week cards (objectives + vocab + grammar pattern), assessment rubric, outcomes. Uses different font stack (DM Sans/Noto Sans Thai/DM Serif Display).

## Image Generation (Optional)

Generate AI illustrations using FLUX Dev on Replicate. Requires `REPLICATE_API_TOKEN` in `.env`.

```python
import replicate
output = replicate.run("black-forest-labs/flux-dev", input={
    "prompt": style_prefix + scene_description + style_suffix,
    "guidance": 3.5, "num_outputs": 1,
    "aspect_ratio": "16:9",  # or "1:1", "4:5"
    "output_format": "png", "num_inference_steps": 28,
})
```

Cost: ~$0.03-0.05 per image. Token from: https://replicate.com/account/api-tokens

**Important:** When generating images with people, specify the ethnicity/appearance matching the target learner population in the style prefix (e.g., "Southeast Asian Thai adults" for Thai courses).

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
