# Children's Page Types

## Interactive Mode Options

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

---

## Detailed Page Type Specifications (Ages 4-7)

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
