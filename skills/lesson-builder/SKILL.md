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
5. **Age group** — "Who is this course for?"
   - 👶 **Children (4-7)** — Audio-first, big visuals, tap/drag interactions, no reading required
   - 👦 **Older children (8-12)** — Can read simple text, handle basic game rules
   - 🧑 **Adults** — Full text-based lessons with grammar explanations
6. **Page types** — "Which page types per unit?" Show options based on age group:

   **Adult page types:**
   - 📄 **Lesson** — Main content with vocabulary, grammar, tutorials, section quizzes
   - 📝 **Activities** — Hands-on practice with difficulty levels (Easy/Medium/Hard)
   - 📝 **Exam** — Interactive exam with difficulty selector and score tracking
   - 🃏 **Flashcards** — Interactive flip cards for vocabulary drilling
   - 💬 **Conversation** — Dialogue scenarios with role-play and audio
   - 🔊 **Pronunciation** — Sound drills targeting L1 interference patterns
   - 🖨️ **Worksheet** — Print-friendly exercises with hidden answer key
   - 📊 **Syllabus** — Course overview page

   **Children's page types (ages 4-7):**
   - 📖 **Story** — Illustrated story with big images, 1-2 sentences per page, audio narration, tap-to-hear vocabulary (4-6 words per unit). **Each page's illustration (emoji or image) MUST match the page's text content** — e.g., a page about "The apple is red" should show 🍎 not 🌈. Never reuse the same generic image across all pages
   - 🎮 **Game** — Interactive mini-games: match (tap English then Thai pair), tap (hear word → tap correct answer from 3 choices), memory (flip card pairs). Config/vocab feeds the content. **Do not use undefined helper functions** — all string escaping must be inline or use the word directly if it contains no quotes
   - 🎵 **Song** — Embedded YouTube video of a real children's ESL song (sung, not spoken) with bilingual sing-along lyrics below, Thai translations per line, and TPR action instructions per line (e.g., "Clap hands", "Point to blue")
   - 🎨 **Coloring** — AI-generated black-and-white line art coloring pages (via `generate_images.py` + FLUX Dev). Each vocab word gets a dedicated outline image. Interactive canvas paint-over: pick a color from the palette, then finger-paint/draw directly on the line art. Eraser tool, adjustable brush size. Outline stays visible via `multiply` blend mode compositing. Two print modes: "Print Blank" outputs clean outlines only (for crayons/markers), "Print Colored" outputs the child's painted version. Tap word label to hear TTS pronunciation
   - 🏷️ **Stickers** — Click-to-add themed stickers (animals, objects — not abstract shapes) onto a scene. Stickers appear at random positions, are draggable after placement, and speak English name on click. Includes stamp trail checkbox (leaves semi-transparent stamps while dragging). Thai instructions explaining click-to-add and drag-to-move. Clear Scene button resets board
   - 🃏 **Flashcards** — Flip-card grid (3x2) with emoji/image on front, English word + Thai translation on back. Tap to flip + hear TTS. Teacher toolbar: "Flip All to Text/Images" toggle, Shuffle, Reset, Print. Counter shows flipped/total. Print button triggers `window.print()` with `@media print` CSS that hides all UI except the card grid, showing emoji + English word + Thai translation per card. Core page type — include in every unit as a teacher's resource
   - 🌟 **Reward** — Progress/celebration page with stars, stickers collected, words learned counter. Congratulations animation
   - 🎬 **Avatar Video** — Interactive vocabulary game page powered by HeyGen AI avatar videos. Each unit gets a unique game mechanic and a unique avatar "look" (talking photo). Structure: Thai intro video → interactive game with 6 vocab items in a simple HTML table (2x3 grid, fixed-size cells with min/max constraints) → per-item HeyGen reveal video (English with Sara Cheerful voice) → Thai outro video reviewing all words + confetti. **Game mechanic varies per unit** — never repeat the same mechanic. Proven mechanics include:
     - **Phone guessing game** (Family) — Thai family voice plays, kid guesses, avatar reveals in English
     - **Shake the tree** (Food) — Tap trees, catch falling food with bounce physics
     - **Build a robot** (Body) — Tap body parts to assemble a robot outline
     - **Princess dress-up** (Clothes) — Tap wardrobe items onto a princess silhouette with sparkle effects
     - **Toy shop listening** (Toys) — Avatar asks for a toy by name, kid taps the correct one; wrong tap shakes
     - **Weather wizard** (Weather) — Tap spell orbs to transform the sky with CSS animations (rain, snow, wind, sun)
     - **Scavenger hunt** (School) — Avatar asks "where is the ___?", kid finds and taps the correct item
     - **Dream home builder** (Home) — Tap items to build rooms in a house cross-section
     - **Paint the mountain** (Nature) — Tap palette to bring color back to a grayscale mountain scene

     **Implementation rules:**
     - All interactive items use simple HTML `<table>` with `<tbody>` — never CSS grid or flexbox for item layouts (causes visibility/sizing bugs)
     - Every `<td>` must have `width`, `min-width`, `max-width`, `height`, `min-height`, `max-height` set to identical values + `overflow: hidden`
     - Use `transition: background 0.2s, border-color 0.2s` — never `transition: all` (causes size animation side effects)
     - Game screen must use `overflow-y: auto; justify-content: flex-start; padding-top: 16px` to prevent bottom-row clipping
     - HeyGen videos: intro/outro use Thai voice (Achara Friendly `f2846fb5...`), item reveals use English voice (Sara Cheerful `1bd001e7...`)
     - Video generation via HeyGen `/v2/video/generate` with `talking_photo` character type. Thai text must be sent via Python (not bash) to avoid encoding errors
     - Each unit needs a unique HeyGen "look" (talking photo ID) matching the unit theme
     - Store video IDs in `{unit}_video_ids.json` alongside the HTML page
     - Videos are `.mp4` files stored in `video/` directory, referenced as `../../video/{unit}_{item}.mp4` from the page
     - Emoji selection: avoid emojis that look like other objects (e.g., 🪑 for desk, 🍽️ for table). When no good emoji exists, use a styled text badge instead

   **Older children's page types (ages 8-12):**
   Can also use any of the 4-7 page types above, plus:
   - 💬 **Comic** — Illustrated comic strip with speech bubbles teaching vocabulary in context. 6-8 panels per strip, bilingual dialogue, audio per bubble, 3 comprehension questions at the end. Characters and scenarios match the unit theme
   - 🏆 **Quiz Show** — Game-show style quiz with countdown timer (15s per question), 3 lifelines (50/50, skip, hint), escalating difficulty levels, animated score counter, sound effects. 10-15 questions mixing vocab, grammar, and reading comprehension
   - 🧩 **Word Puzzle** — Three puzzle types per page: crossword (clues in L1, answers in L2), word search grid with hidden vocabulary, and word scramble (unscramble letters). Timer optional, hint system reveals one letter at a time. Printable version
   - 🗺️ **Adventure** — Choose-your-own-adventure branching story (10-15 scenes, 3-4 endings). Each choice point tests vocabulary or grammar — correct choices lead to better outcomes. Tracks path taken, shows vocabulary learned at the end. Replayable for different endings
   - 📓 **Journal** — Guided creative writing with sentence starters, word bank from unit vocab, and example sentences. 3 writing prompts per unit, increasing difficulty. Typed responses saved to localStorage. Teacher can view/print completed journals
   - 🎬 **Video Lesson** — Structured video learning page: pre-watch vocabulary preview with audio, embedded video player (YouTube/MP4), pause-and-answer comprehension checks at timestamps, post-watch quiz, key phrases summary. Video URL configured per unit
   - 🎲 **Board Game** — Virtual board game (snakes-and-ladders or path style). Roll dice, land on squares with vocabulary challenges — answer correctly to stay, wrong answer slides back. 2-4 player support (pass-and-play). Tracks wins in localStorage
   - 📰 **Reading** — Short illustrated reading passage (100-200 words) at appropriate level with highlighted vocabulary, audio read-aloud, adjustable speed. Followed by true/false, multiple choice, and "find the word" comprehension exercises. Bilingual glossary sidebar
7. **Output location** — "Where should files go?" (default: `HTML/courses/{topic_slug}/`)
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

**CRITICAL: The login command is INTERACTIVE — it requires the user to press ENTER after signing in.** You CANNOT run it from the Bash tool (it will abort because there's no stdin). The user MUST run it themselves using the `!` prefix in the Claude Code prompt.

Tell the user:
> NotebookLM needs to authenticate with your Google account. Please run this command:
> ```
> ! python -m notebooklm login
> ```
> A browser window will open. Sign in with your Google account, wait until you see the NotebookLM homepage, then press ENTER in the terminal to save.

**Troubleshooting sequence** (go through these in order if the browser doesn't open):

1. **Install Chromium first** (most common fix):
   > ```
   > ! python -m playwright install chromium
   > ```
   > Then retry `! python -m notebooklm login`

2. **Delete stale auth** (if browser opens but login fails):
   > ```
   > ! del %USERPROFILE%\.notebooklm\storage_state.json
   > ! python -m notebooklm login
   > ```
   > (Mac/Linux: `rm ~/.notebooklm/storage_state.json`)

3. **Full reset** (nuclear option — delete auth + reinstall browser):
   > ```
   > ! del %USERPROFILE%\.notebooklm\storage_state.json
   > ! python -m playwright install chromium
   > ! python -m notebooklm login
   > ```

4. **Use the helper script** (if `notebooklm login` still won't open a browser):
   The `! python -m notebooklm login` command sometimes fails to launch a visible browser window on Windows. Use the helper script instead:
   > ```
   > ! python notebooklm_login.py
   > ```
   This script (`notebooklm_login.py` in the watdonchan project root) launches Chromium directly via playwright, navigates to NotebookLM, waits for user login, then saves auth state to the same location as `notebooklm login`.

**Key gotchas learned from experience:**
- The Bash tool CANNOT run `notebooklm login` — it's interactive (waits for ENTER). Always tell the user to use `!` prefix
- `! python -m notebooklm login` sometimes fails to open a browser window on Windows even with playwright installed. Use `! python notebooklm_login.py` as a reliable fallback
- The "Chromium pre-flight check failed" warning is normal if playwright wasn't installed — install it with `playwright install chromium`
- Auth expires frequently (every few days). If `token_fetch` is `false`, the user needs to re-login
- On Windows, the browser profile is stored at `%USERPROFILE%\.notebooklm\browser_profile\`
- Auth state is saved to `%USERPROFILE%\.notebooklm\storage_state.json`

### 4. Verify auth works after login
```bash
PYTHONIOENCODING=utf-8 python -m notebooklm auth check --test --json
```
Check that `checks.token_fetch` is `true`. If so, auth is confirmed.

Alternatively, create a test notebook:
```bash
PYTHONIOENCODING=utf-8 python -m notebooklm create "test" --json
```
If this succeeds (returns a notebook ID), delete the test notebook:
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

**IMPORTANT: Image path convention.** Images are stored in `imgs/` at the project root (sibling to `HTML/`), NOT inside `HTML/`. The structure is:
```
imgs/tefl/{course_slug}/          ← generated images (hero.png, {prefix}.png)
HTML/tefl/{course_slug}/          ← lesson HTML files
```
Image `src` attributes in HTML use relative paths from the HTML file's location:
- Lesson files: `src="../../../imgs/tefl/{course_slug}/{prefix}.png"`
- Syllabus file (in `HTML/`): `src="../imgs/tefl/{course_slug}/hero.png"`

The `imgs/` directory is gitignored (*.png) — images are uploaded to S3 separately.

### Step 6: Hero Video (optional)
After generating all pages and images, **ask the user** if they want a hero video for the course:

> "Would you like a hero video for this course? Options:
> 1. 🎬 **HeyGen** — AI avatar presents the course intro (realistic talking-head video)
> 2. 🎥 **Remotion** — Animated motion graphics intro (React-based video)
> 3. ⏭️ **Skip** — No hero video"

If the user chooses **HeyGen**: invoke the `/heygen` skill (or `/avatar-video` for precise control) with:
- A script introducing the course in L1 (the learner's language), with key L2 phrases
- The hero image as background or overlay
- Course title and key selling points (level, duration, topics covered)

If the user chooses **Remotion**: invoke the `/remotion-best-practices` skill with:
- A course intro animation using the course's color theme
- Title cards showing course name in both L1 and L2
- Quick preview of weekly topics with icons/emojis
- The hero image as a featured visual element

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

## Children's Page Type Specifications (Ages 4-7)

### 📖 Story Page
Paginated story with prev/next buttons and page dots. Each page has:
- **Illustration** (`.story-emoji` div) — a large emoji matching that specific page's content. **CRITICAL: each page gets a DIFFERENT emoji that matches its vocabulary word** (e.g., page about "cat" → 🐱, page about "dog" → 🐶). Never use the same emoji on every page.
- **English sentences** (`.story-text`) — 2-4 lines of **rhyming verse** with the vocab word in `<b>` tags. Clickable to hear TTS.
- **Thai translation** (`.story-thai`) — matching translation with vocab word bolded.
- **Speak button** — pronounces the target vocabulary word.
- Arrow key navigation (Left/Right). 6 pages per story (one per vocab word).

#### Dr. Seuss-Style Rhyming Story Strategy

Stories MUST be written as **rhyming mini-narratives**, NOT flat flashcard sentences. Each story should feel like a tiny Dr. Seuss book — silly, rhythmic, and fun to read aloud.

**Rhyming rules:**
- Use **AABB rhyming couplets** (pairs of lines that rhyme) — easy for kids to predict and chant along
- Each page introduces ONE vocab word but weaves it into 2-4 lines of verse
- The story should have a **narrative arc** — a character doing something, a situation building, a silly conclusion
- Use **cumulative/building** structure where possible — each page references or builds on what came before
- Include **absurd humor** — Dr. Seuss's secret weapon (a dog wearing a log, a robot with wobbly eyes, a fish in a dish)
- Add **sound effects and onomatopoeia** — CRASH! SPLAT! ZOOM! POP! — kids love these
- Use **repetition and refrains** — repeating phrases kids can chant ("Oh me! Oh my!", "What do you see?")

**Story concept patterns (pick one per unit):**
| Pattern | Description | Example |
|---------|-------------|---------|
| **Cumulative** | Each page adds to a growing scene | Painter adding colors to a rainbow |
| **Chain/Parade** | Characters or items line up one by one | Animals joining a silly parade |
| **Building/Assembly** | Something is constructed piece by piece | Robot being built, getting dressed |
| **Journey/Exploration** | Character moves through spaces discovering things | Mouse exploring a house, nature walk |
| **Feast/Appetite** | Character tries everything | Hungry monster at a buffet |
| **Chaos/Escalation** | Situation gets sillier and sillier | Weather changing every minute |
| **Introduction** | Meet characters who each do something goofy | Family members with funny habits |
| **Discovery** | Character finds things one by one | First day of school, toy chest |

**Thai translations** should be natural and conversational — do NOT force the Thai to rhyme. The Thai explains what's happening in the story clearly for the child.

### 🎮 Game Page
Three game tabs in one page: Match, Tap, Memory.
- **Match**: 3 random vocab pairs displayed as cards (English + Thai). Tap one, then tap its match. Correct = green + score. Wrong = red shake + reset.
- **Tap**: Shows a prompt with one English word + Thai translation. 3 Thai answer cards — tap the correct one. Auto-advances after 1 second on correct answer.
- **Memory**: 3 pairs (6 cards) face-down. Flip two to find matches. English cards trigger TTS on flip.

**JS rules**: All functions must be self-contained in the file. The `initTap()` function builds the prompt with an inline `onclick="speak('word')"` — use the vocab word directly in the string, do NOT call helper functions that aren't defined (e.g., never use `ss()`, `escape()`, or any function not explicitly declared in the script block).

### 🎵 Song Page
Embeds a real, publicly available children's song via **YouTube iframe embed** with bilingual sing-along lyrics below. No TTS or Web Audio API — children hear actual sung music from established ESL channels.

**Structure:**
- **Song info box** (`.song-info`): Song title in L2 + L1, channel credit line.
- **YouTube embed** (`.video-wrapper`): Responsive 16:9 iframe using `youtube-nocookie.com/embed/{VIDEO_ID}?rel=0` for privacy-enhanced mode. Uses `loading="lazy"` and `allowfullscreen`.
- **Sing-along tip** (`.sing-tip`): Bilingual instruction for how to participate (e.g., "Point to things that match each color!").
- **Lyrics section** (`.lyrics-header` + `.song-line` divs): 6 lyric lines, each with:
  - **Line number** (`.song-num`) — numbered circle badge
  - **English lyric** (`.song-en`) — key phrase from the song
  - **Thai translation** (`.song-th`) — matching translation
  - **Action instruction** (`.song-action`) — physical action for TPR (e.g., "Clap hands", "Stomp feet")

**Song selection criteria:**
- Must be freely embeddable on YouTube (public videos with embedding enabled)
- From established children's ESL channels: Super Simple Songs, Dream English Kids, Pinkfong, Fun Kids English, Busy Beavers
- Age-appropriate for 4-7 year olds
- Vocabulary must align with the unit's topic and target words
- Sung (not spoken) — children should hear actual music, not TTS

**Current song assignments (verified YouTube IDs):**

| Unit | Song | Channel | Video ID |
|------|------|---------|----------|
| Colors | I See Something Blue | Super Simple Songs | `jYAWf8Y91hA` |
| Numbers | Let's Count 1 to 10 | Dream English Kids | `85M1yxIcHpw` |
| Animals | It's a Dog | Dream English Kids | `tNK0ToOgntw` |
| Family | The Family Song | Busy Beavers | `dH5RTW0gh30` |
| Food | Do You Like Broccoli Ice Cream? | Super Simple Songs | `frN3nvhIHUk` |
| Body | Head Shoulders Knees & Toes | Super Simple Songs | `ZanHgPprl-0` |
| Clothes | Clothing Song For Kids | Dream English Kids | `KFQxBCvgx70` |
| Toys | My Teddy Bear | Super Simple Songs | `666UZRBO5q8` |
| Weather | Weather Song: Sun Comes Up | Dream English Kids | `XcW9Ct000yY` |
| School | School Supplies Song | Fun Kids English | `BwBTozQisb4` |
| Home | My House | Pinkfong | `qZyJPZxsmZk` |
| Nature | Walking In The Jungle | Super Simple Songs | `GoSq-yZcJ-4` |

**To replace a song:** Update the `video_id` in the song data, verify the new ID works via `https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=NEW_ID&format=json`, and update the lyrics/translations to match.

### 🎨 Coloring Page
AI-generated black-and-white line art with interactive canvas paint-over. Each vocabulary word has a dedicated coloring outline image generated via `generate_images.py` (Replicate FLUX Dev) with a style prefix enforcing thick clean outlines, no shading, pure white background.

**Image generation:**
- Create a JSON prompts file (e.g., `coloring_prompts.json`) with `style_prefix` for coloring page style, 1:1 aspect ratio, one image per vocab word
- Run `python generate_images.py coloring_prompts.json` to batch-generate all outline images
- Images saved to `imgs/coloring/{topic}_{word}.png`

**Interactive canvas architecture (two-canvas system per card):**
- **Draw canvas** (hidden, z-index 2) — captures user's paint strokes at 300x300px resolution
- **Display canvas** (visible, z-index 1) — composites: white background → user's drawing → line art on top via `globalCompositeOperation='multiply'`
- This keeps the black outlines always visible on top of the user's coloring
- Touch and mouse events with `touch-action: none` for mobile finger painting

**UI controls:**
- **Color palette** — 10 color circles + eraser button. Active color highlighted with border
- **Brush size slider** — range 4-40px with live preview dot
- **Eraser** — uses `destination-out` composite operation to remove paint strokes
- **Clear All** — clears all draw canvases and re-renders composites
- **Print Blank** — temporarily strips user drawing from display canvases, calls `window.print()`, then restores composites after 500ms timeout
- **Print Colored** — calls `window.print()` directly with user's artwork visible
- **Word labels** — below each card, tap to hear TTS pronunciation

**Print CSS** (`@media print`): hides header, palette, brush slider, toolbar, nav footer, footer, and word labels. Cards print in a 3-column grid with no box shadow, just a light border. Output is either clean outlines (Print Blank) or the child's colored version (Print Colored).

**Fallback**: If images haven't been generated yet, the canvas shows a gray placeholder with the word text and "(image pending)" message.

### 🏷️ Stickers Page
Click-to-add interactive sticker board:
- **Sticker tray**: 6 themed stickers (animals, food, objects — NOT abstract shapes like circles/squares). Each sticker shows the emoji + color name or vocab word. **Emoji color rule**: CSS `color` does NOT change emoji rendering on most platforms — emojis have built-in colors. When a unit teaches colors, choose animals/objects whose native emoji color matches the target color (e.g., 🐸 green frog, 🐳 blue whale, 🐞 red ladybug, 🐥 yellow chick, 🦊 orange fox, 🐙 purple octopus). Do NOT rely on CSS to recolor emojis.
- **Click to add**: Clicking a tray sticker places it at a **random position** on the scene board (10-80% range) and speaks the English word. New sticker animates in with a pop effect.
- **Drag to move**: Placed stickers are draggable via mouse/touch.
- **Stamp trail**: A checkbox labeled in both languages. When enabled, dragging a sticker leaves semi-transparent emoji stamps (`.stamp` class, `opacity: 0.45`, `pointer-events: none`) along the drag path, spaced ~20px apart.
- **Thai instructions**: Two lines explaining (1) click to add a sticker and (2) drag to reposition.
- **Clear Scene**: Removes all placed stickers and stamps.

### 🃏 Flashcards Page
Core teacher resource — include in **every unit**. 3x2 grid (2 columns on mobile) of flip cards with CSS 3D transforms:
- **Front**: Large emoji/image (`.card-img`, 4.5em) on a light gradient background. Content-appropriate emoji per vocabulary word (same rules as Story page).
- **Back**: English word (`.card-word`, 2.2em bold white) + Thai translation (`.card-thai`) on a colored gradient.
- **Tap to flip**: Toggles `.flipped` class which rotates `.card-inner` 180° via `transform: rotateY(180deg)`. Also triggers `speak()` for the English word.
- **Toolbar** (4 buttons):
  - **Flip All** — Toggles all cards between image side and text side. Button text changes between "Flip All to Text" and "Flip All to Images". Useful for teachers showing all words at once.
  - **Shuffle** — Randomizes card order in the grid by rearranging DOM children.
  - **Reset** — Flips all cards back to image side.
  - **Print** — Calls `window.print()`. `@media print` CSS hides header, toolbar, counter, nav-footer, footer, and instructional text. Cards display as a 3-column grid showing emoji (`.card-front`), English word (`.card-word`), and Thai translation (`.card-thai`) on each card. Both `.card-front` and `.card-back` are visible in print (no flip transform). Cards have a light border for cut lines.
- **Counter**: Shows "N / 6 flipped" updated on every flip action.
- Uses `perspective: 800px` on the card container and `backface-visibility: hidden` on both faces for clean 3D flip effect.

### 🌟 Reward Page
Celebration page with confetti animation, star display, word count, and a "Next Week" link to the next unit's story page.

## Nav Footer (All Pages)

Every page in a unit MUST include a `.nav-footer` with links to **ALL** page types generated for that unit, not just a subset. For example, if a unit has Story, Game, Song, Coloring, Stickers, and Reward, then every one of those 6 pages must link to all 6 plus the Home/Syllabus link. This ensures students can navigate freely between activities without returning to the syllabus.

The generator script must track which page types each unit has and inject the complete nav footer into every page for that unit.

## Syllabus Page Layout

When a syllabus includes both a hero video and hero image:
- **Video** goes first (inside `.hero-video` div, no `poster` attribute)
- **Image** goes below as a separate element (inside `.hero-img` div)
- They must NOT overlap — use `margin-top: 20px` on the image container for spacing
- Never use the video `poster` attribute to double as the hero image display

## Quality Checklist — Run Before Delivery

After generating all files for a course, verify these before delivering to the user:

### 1. Test one unit end-to-end first
Generate **only unit 1** first. Open every page in a browser and verify:
- [ ] All interactive features work (games load, songs play, stickers place)
- [ ] No JS console errors
- [ ] Nav footer links to all pages in the unit
- [ ] Story emojis vary per page
- [ ] TTS speaks correctly on all buttons

Only after unit 1 passes, generate remaining units using the same templates.

### 2. Cross-file consistency
- [ ] Every function called in JS is defined in the same `<script>` block — pages are standalone HTML with no shared JS files
- [ ] Nav footer on every page lists ALL page types for that unit
- [ ] No hardcoded page-type subsets (e.g., only Story/Game/Song) — always derive from the unit's actual page list

### 3. Content-specific visuals
- [ ] Story page emojis: each of the 6 pages shows a DIFFERENT emoji matching its vocabulary word
- [ ] Sticker page: uses themed concrete objects (animals, food, etc.), not abstract shapes
- [ ] Emoji colors match the text: if the label says "blue bird", the emoji must naturally render as blue (🐳 not 🐦). CSS `color` does NOT recolor emojis — choose emojis whose built-in rendering matches the intended color
- [ ] Song page: embeds a real YouTube children's song (verify video ID is valid and not removed)

### 4. Common JS bugs to avoid
- **Never reference undefined functions.** Every function used in `onclick`, `innerHTML` strings, or event handlers must be defined in the same script block. Grep all generated files for function calls and verify each is defined.
- **Quote safety in inline handlers.** When building `onclick="speak('word')"` via string concatenation, the word itself must not contain single quotes. For safe words (no quotes), use the string directly — do NOT wrap in an escape helper unless that helper is defined.
- **Always cancel speechSynthesis** before speaking to prevent queue buildup.

## Unicode Emoji Color Reference

**CSS `color` does NOT change emoji rendering.** Emojis have built-in colors baked into the font. Always use the correct Unicode codepoint for the intended color. Verify by rendering in a browser before bulk-generating.

### Colored Circles (for coloring pages, targets, indicators)

| Color | Emoji | Decimal | Hex | Name |
|-------|-------|---------|-----|------|
| Red | 🔴 | `&#128308;` | `&#x1F534;` | Large Red Circle |
| Orange | 🟠 | `&#128992;` | `&#x1F7E0;` | Large Orange Circle |
| Yellow | 🟡 | `&#128993;` | `&#x1F7E1;` | Large Yellow Circle |
| Green | 🟢 | `&#128994;` | `&#x1F7E2;` | Large Green Circle |
| Blue | 🔵 | `&#128309;` | `&#x1F535;` | Large Blue Circle |
| Purple | 🟣 | `&#128995;` | `&#x1F7E3;` | Large Purple Circle |
| Brown | 🟤 | `&#128996;` | `&#x1F7E4;` | Large Brown Circle |
| Black | ⚫ | `&#9899;` | `&#x26AB;` | Black Circle |
| White | ⚪ | `&#9898;` | `&#x26AA;` | White Circle |

### Colored Squares

| Color | Emoji | Decimal | Hex | Name |
|-------|-------|---------|-----|------|
| Red | 🟥 | `&#128997;` | `&#x1F7E5;` | Large Red Square |
| Orange | 🟧 | `&#128999;` | `&#x1F7E7;` | Large Orange Square |
| Yellow | 🟨 | `&#129000;` | `&#x1F7E8;` | Large Yellow Square |
| Green | 🟩 | `&#129001;` | `&#x1F7E9;` | Large Green Square |
| Blue | 🟦 | `&#128998;` | `&#x1F7E6;` | Large Blue Square |
| Purple | 🟪 | `&#129002;` | `&#x1F7EA;` | Large Purple Square |

### Colored Hearts

| Color | Emoji | Decimal | Hex | Name |
|-------|-------|---------|-----|------|
| Red | ❤️ | `&#10084;&#65039;` | `&#x2764;&#xFE0F;` | Red Heart |
| Orange | 🧡 | `&#129505;` | `&#x1F9E1;` | Orange Heart |
| Yellow | 💛 | `&#128155;` | `&#x1F49B;` | Yellow Heart |
| Green | 💚 | `&#128154;` | `&#x1F49A;` | Green Heart |
| Blue | 💙 | `&#128153;` | `&#x1F499;` | Blue Heart |
| Purple | 💜 | `&#128156;` | `&#x1F49C;` | Purple Heart |
| Brown | 🤎 | `&#129294;` | `&#x1F90E;` | Brown Heart |
| Black | 🖤 | `&#128420;` | `&#x1F5A4;` | Black Heart |
| White | 🤍 | `&#129293;` | `&#x1F90D;` | White Heart |
| Pink | 🩷 | `&#129527;` | `&#x1FA77;` | Pink Heart |

### Color-Accurate Animals (for stickers, stories)

Use these when you need an animal emoji that naturally renders in the target color:

| Color | Animals |
|-------|---------|
| Red | 🐞 ladybug, 🦞 lobster, 🦀 crab, 🐙 octopus (reddish) |
| Orange | 🦊 fox, 🐅 tiger, 🐈 cat (orange tabby), 🦁 lion |
| Yellow | 🐥 chick, 🐤 baby chick, 🐝 bee, ⭐ star |
| Green | 🐸 frog, 🐢 turtle, 🐊 crocodile, 🦎 lizard |
| Blue | 🐳 whale, 🐬 dolphin, 🦋 butterfly (blue), 🐟 fish |
| Purple | 🐙 octopus, 🦄 unicorn (purple mane), 🪼 jellyfish |
| Brown | 🐻 bear, 🐵 monkey, 🦉 owl, 🐿️ chipmunk |
| Pink | 🐷 pig, 🦩 flamingo, 🌸 cherry blossom |
| White | 🐰 rabbit, 🐑 sheep, 🦢 swan, ☁️ cloud |
| Black | 🐧 penguin, 🦇 bat, 🕷️ spider, 🐈‍⬛ black cat |
| Gray | 🐘 elephant, 🦏 rhino, 🐺 wolf, 🐭 mouse |

### Common Pitfalls

| Wrong | Codepoint | Actually renders as | Use instead |
|-------|-----------|-------------------|-------------|
| "Yellow diamond" | `&#128311;` 🔷 | **Blue** diamond | `&#128993;` 🟡 Yellow circle |
| "Blue diamond" | `&#128310;` 🔶 | **Orange** diamond | `&#128309;` 🔵 Blue circle |
| "Colored bird" | `&#128038;` 🐦 | Red/brown bird | 🐳 whale or 🐬 dolphin for blue |
| "Colored cat" | `&#128008;` 🐈 | Brown/gray cat | 🐞 ladybug for red, 🦊 fox for orange |

## Image Generation via `generate_images.py` (FLUX Dev on Replicate)

A bundled `generate_images.py` script handles batch image generation using [FLUX Dev](https://replicate.com/black-forest-labs/flux-dev) on [Replicate](https://replicate.com/). It reads prompts from a JSON file and generates images in one command. Requires `REPLICATE_API_TOKEN` in a `.env` file.

**Setup:**
```bash
pip install replicate
# Create .env with: REPLICATE_API_TOKEN=r8_your_token_here
```

**Cost:** ~$0.03-0.05 per image. Token from: https://replicate.com/account/api-tokens

### Prompts JSON Format

Create a JSON file with `style_prefix`, `style_suffix`, per-image prompts, and generation settings:

```json
{
  "style_prefix": "Art style and constraints that apply to ALL images. ",
  "style_suffix": " Negative constraints appended to all prompts.",
  "output_dir": "imgs/my_output",
  "settings": {
    "guidance": 3.5,
    "num_inference_steps": 28,
    "aspect_ratio": "1:1",
    "output_format": "png"
  },
  "images": {
    "image_id": {
      "prompt": "Specific scene description for this image"
    }
  }
}
```

The script assembles the final prompt as: `style_prefix + prompt + style_suffix` (joined with `, `).

### Commands

```bash
# Preview all prompts without spending API credits
python generate_images.py prompts.json --dry-run

# List all images and which are done vs pending
python generate_images.py prompts.json --list

# Generate all pending images (skips existing files)
python generate_images.py prompts.json

# Generate one specific image
python generate_images.py prompts.json --id animals_cat

# Override settings from CLI
python generate_images.py prompts.json --guidance 4 --steps 30 --aspect 16:9
```

**Resilience:** Skips existing images automatically. Retries 4 times with exponential backoff on rate limits. 3-second delay between API calls.

### Coloring Page Image Generation

For children's coloring pages, use a style prefix that enforces black-and-white line art:

```json
{
  "style_prefix": "Simple black and white line drawing coloring page for young children ages 4-7. Thick clean bold outlines, no shading, no fill, no gray tones, no crosshatching, pure white background. Large simple shapes easy to color with crayons or markers. Single object centered in frame, cute friendly child-appropriate style. ",
  "style_suffix": " No color, no shading, no gradients, no gray areas. Pure black outlines on pure white background only.",
  "output_dir": "imgs/coloring",
  "settings": { "aspect_ratio": "1:1" },
  "images": {
    "animals_cat": { "prompt": "A cute sitting cat with round face, whiskers, pointy ears, curled tail. Simple cartoon style." },
    "animals_dog": { "prompt": "A happy puppy sitting with floppy ears and wagging tail. Simple cartoon style." }
  }
}
```

See `config/coloring_prompts_example.json` for a complete 52-image example across 8 topics.

**Naming convention:** `{topic}_{word}.png` (e.g., `animals_cat.png`, `food_rice.png`). The coloring page HTML references images at `imgs/coloring/{topic}_{word}.png`.

### Other Image Use Cases

| Use Case | Aspect | Style Prefix Key Points |
|----------|--------|------------------------|
| Coloring pages | 1:1 | B&W line art, thick outlines, no shading, white background |
| Story illustrations | 16:9 | Watercolor children's book, warm colors, scene-specific |
| Game assets | 1:1 | Kawaii cartoon, flat design, pastel colors |
| Comic panels | 16:9 or 4:5 | B&W ink, bold lines, Love and Rockets style |

**Important:** When generating images with people, specify the ethnicity/appearance matching the target learner population in the style prefix (e.g., "Southeast Asian Thai ethnicity with warm brown skin, straight black hair" for Thai courses).

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
