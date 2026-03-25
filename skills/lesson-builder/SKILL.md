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

1. **Topic/Subject** — "What topic should the course cover?" (e.g., "General English for beginners", "Business English", "English through IT skills")
2. **Languages** — "What is the learner's first language (L1) and target language (L2)?" (default: Thai → English)
3. **Number of weeks/units** — "How many units?" (default: 12)
4. **Page types** — "Which page types per unit?" Show options:
   - 📄 **Lesson** — Main content with vocabulary, grammar, tutorials, section quizzes
   - 📝 **Activities** — Hands-on practice with difficulty levels (Easy/Medium/Hard)
   - 📝 **Exam** — Interactive exam with difficulty selector and score tracking
   - 🃏 **Flashcards** — Interactive flip cards for vocabulary drilling
   - 💬 **Conversation** — Dialogue scenarios with role-play and audio
   - 🔊 **Pronunciation** — Sound drills targeting L1 interference patterns
   - 🖨️ **Worksheet** — Print-friendly exercises with hidden answer key
   - 📊 **Syllabus** — Course overview page
5. **Output location** — "Where should files go?" (default: `HTML/courses/{topic_slug}/`)
6. **Color theme** — "Any color preference?" (or auto-pick)
7. **AI Images** — "Would you like to generate hero images for each lesson using Replicate FLUX Dev? Requires a `REPLICATE_API_TOKEN` in `.env`. Cost: ~$0.03-0.05 per image." (default: no)

**If a config file exists** in `config/` matching the topic, load it instead of asking.

## How it works

### Step 1: Gather Requirements
Either load from a config JSON (`config/{course_id}.json`) or ask interactively.

### Step 2: Research
Verify course content against authoritative sources **before** generating.

**NotebookLM** (default — use if `notebooklm` skill/CLI is available):
```bash
notebooklm create "Course: {topic}"
notebooklm source add-research "{topic} curriculum CEFR"
notebooklm ask "What are the key concepts of {week topic}?"
```

**If NotebookLM is not available**, fall back to **WebSearch/WebFetch**:
- Search for the unit's subject topic from 2+ authoritative sources
- Search for the grammar point with examples
- Verify vocabulary definitions and L1 translations
- Save source citations for the references section

**If neither is available**, inform the user: *"I'll generate content from my training data. For higher accuracy, consider installing the NotebookLM skill or enabling web search."*

### Step 3: Fact-Check
Use the `fact-checker` skill (default — if available) to verify:
- Grammar rules and examples are correct
- Vocabulary definitions and translations are accurate
- Quiz answers are correct
- Real-world examples are current

**If fact-checker is not available**, inform the user: *"I'll do my best to verify content, but consider reviewing grammar rules and translations before publishing."*

### Step 4: Generate
Write a Python generator script (`generate_{course_id}.py`) that produces all files, then run it.

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

## Image Location Rules

Images are **never committed to git** — they are generated locally and uploaded to S3 separately.

### Directory structure
```
(site root)
├── HTML/
│   └── courses/
│       └── {course_id}/       ← generated HTML files live here
│           └── *.html
└── imgs/
    └── {course_id}/           ← images live here (S3 sibling to HTML/)
        └── {prefix}_hero.png
```

### Path convention in HTML
From `HTML/courses/{course_id}/`, images are referenced with a **relative path** going up three levels to the site root:
```html
<img src="../../../imgs/{course_id}/{image_name}.png" alt="...">
```

### Hero images
Each lesson page should include a hero image in the header section:
```html
<img class="hero-img" src="../../../imgs/{course_id}/{unit_prefix}_hero.png"
     alt="{unit title}" onerror="this.style.display='none'">
```
The `onerror` handler hides the image gracefully if it hasn't been uploaded to S3 yet.

### Key rules
- **NEVER commit image files to git.** The `.gitignore` blocks `imgs/`, `*.png`, `*.jpg`, etc.
- Images are uploaded to S3 to match the relative path structure from the HTML directory
- Use `onerror="this.style.display='none'"` on all `<img>` tags so pages render cleanly before images are uploaded
- Image filenames follow the pattern: `{unit_prefix}_{type}.png` (e.g., `claude_intro_hero.png`, `perm_building_hero.png`)

## Image Generation (Optional)

This skill includes `generate_images.py` — a generic batch image generator using Replicate FLUX Dev. It reads prompts from a JSON file and generates images.

### Bundled tool: `generate_images.py`

Located at: `{skill_dir}/generate_images.py`

```bash
# Generate all images from a prompts JSON
python generate_images.py heygen_prompts.json --output-dir imgs/heygen

# List status (which images exist vs pending)
python generate_images.py heygen_prompts.json --list

# Preview prompts without spending credits
python generate_images.py heygen_prompts.json --dry-run

# Generate one specific image
python generate_images.py heygen_prompts.json --id heygen_intro_hero
```

### Image prompts JSON format

The generator script creates a `{course_id}_prompts.json` alongside the course config:

```json
{
  "style_prefix": "Warm, friendly educational illustration, ...",
  "style_suffix": ", professional quality, no text in image",
  "output_dir": "imgs/{course_id}",
  "images": {
    "{unit_prefix}_hero": {
      "prompt": "Scene description for this unit's hero image",
      "aspect_ratio": "16:9"
    }
  }
}
```

### Workflow

1. Generator script creates HTML files with `<img>` tags pointing to `../../../imgs/{course_id}/`
2. Generator script also creates `{course_id}_prompts.json` with image prompts
3. Run `python generate_images.py {course_id}_prompts.json` to generate images
4. Upload images to S3

Requires `REPLICATE_API_TOKEN` in `.env`. Cost: ~$0.03-0.05 per image. Token from: https://replicate.com/account/api-tokens

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

- `config/tefl_beginners.json` — 12-week Thai→English beginner course (everyday + work)
- `config/schema.md` — Full configuration schema documentation

## Extending

To add a new page type:
1. Add it to `page_types` in the config schema
2. Add its structure options to `page_structure`
3. Write a `generate_{type}(unit, config)` function in the generator script
4. Document it in this skill file
