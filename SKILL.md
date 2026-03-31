---
name: lesson-builder
description: "Generates bilingual TEFL/ESL courses with lessons, exams, flashcards, conversations, pronunciation drills, worksheets, and syllabi for any language pair."
---

## When to use

Use this skill when:
- The user asks to create a lesson, course, syllabus, or curriculum
- The user asks to generate activities, exams, flashcards, or other course pages
- The user says "build lesson", "create course", "generate syllabus", etc.

## Interactive Mode — Ask Before Building

**If the user invokes this skill without specifying all parameters, ASK:**

1. **Research method** (ask FIRST) — "How should I research course content?"
   - **NotebookLM** (default, recommended) — AI-powered research using Google NotebookLM. Creates a research notebook, imports web sources on the topic, and queries them for verified content per unit. Produces higher-quality, citation-backed material.
   - **Web Search** — Search the web directly for curriculum references, grammar examples, and vocabulary verification.
   - **Training data only** — Generate from AI knowledge without external research. Fastest but least verified.

   If the user picks NotebookLM, **immediately verify it is set up** before asking remaining questions. See [NOTEBOOKLM.md](NOTEBOOKLM.md) for setup guide. Do NOT proceed to content generation until auth is confirmed.

2. **Topic/Subject** — "What topic should the course cover?" (e.g., "General English for beginners", "Business English", "English through IT skills")
3. **Languages** — "What is the learner's first language (L1) and target language (L2)?" (default: Thai → English)
4. **Number of weeks/units** — "How many units?" (default: 12)
5. **Age group** — "Who is this course for?"
   - **Children (4-7)** — Audio-first, big visuals, tap/drag interactions, no reading required
   - **Older children (8-12)** — Can read simple text, handle basic game rules
   - **Adults** — Full text-based lessons with grammar explanations
6. **Page types** — "Which page types per unit?" Show options based on age group:

   **Adult page types:**
   - Lesson, Activities, Exam, Flashcards, Conversation, Pronunciation, Worksheet, Syllabus

   **Children's page types:** See [CHILDREN_PAGES.md](CHILDREN_PAGES.md) for full list and specifications (Story, Game, Song, Coloring, Stickers, Flashcards, Reward, Avatar Video for ages 4-7; Comic, Quiz Show, Word Puzzle, Adventure, Journal, Video Lesson, Board Game, Reading for ages 8-12)

7. **Output location** — "Where should files go?" (default: `HTML/courses/{topic_slug}/`)
8. **Color theme** — "Any color preference?" (or auto-pick)

**If a config file exists** in `config/` matching the topic, load it instead of asking. Still check that the research method in the config is available (e.g., if `notebooklm: true`, verify auth before proceeding).

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
- Verify vocabulary definitions and L1 translations
- Save source citations for the references section

**Training data only** (last resort):
Inform the user: *"Generating content from training data. For higher accuracy, consider using NotebookLM or web search."*

### Step 3: Fact-Check
Use the `fact-checker` skill (if available) to verify grammar rules, vocabulary, quiz answers, and real-world examples.

### Step 4: Generate
Write a Python generator script (`generate_{course_id}.py`) that produces all files, then run it. The script filename MUST match the `course_id` from the config. Never reuse or overwrite another course's generator.

### Step 5: Images (optional)
If configured and Replicate API token is available, generate illustrations using FLUX Dev. See [IMAGE_GENERATION.md](IMAGE_GENERATION.md) for the full guide, prompts format, and emoji color reference.

### Step 6: Hero Video (optional)
After generating all pages and images, **ask the user** if they want a hero video for the course:

> "Would you like a hero video for this course? Options:
> 1. **HeyGen** — AI avatar presents the course intro (realistic talking-head video)
> 2. **Remotion** — Animated motion graphics intro (React-based video)
> 3. **Skip** — No hero video"

The video should be embedded in the syllabus page as the hero section.

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
    "notebooklm": true,
    "web_search": true,
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
Course overview with sticky header, week navigation, hero section, scope table, week cards (objectives + vocab + grammar pattern), assessment rubric, outcomes. Uses different font stack (DM Sans/Noto Sans Thai/DM Serif Display).

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
