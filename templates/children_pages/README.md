# Children's Page Types

Template files in this directory:
- `story_example.html`   — minimal story page (Dr. Seuss-style rhyming)
- `game_example.html`    — minimal game page (Match / Tap / Memory)
- `coloring_example.html`— minimal coloring page (two-canvas system)

SKILL.md anchors: Phase 1 §"Page types" Q5 → age-group catalog below.

---

## Page-Type Catalog

### Ages 4-7

| Type | Symbol | Description |
|------|--------|-------------|
| Story | 📖 | Paginated rhyming story, 6 pages, 1 vocab word/page. Each page: unique matching emoji + AABB verse + Thai. See `story_example.html`. |
| Game | 🎮 | 3-tab page: Match, Tap, Memory. All JS self-contained. See `game_example.html`. |
| Song | 🎵 | Embedded YouTube children's song + bilingual sing-along lyrics + TPR actions. |
| Coloring | 🎨 | AI line art (FLUX) + interactive two-canvas paint. See `coloring_example.html`. |
| Stickers | 🏷️ | Click-to-add sticker board; drag to move; stamp trail option. |
| Flashcards | 🃏 | 3×2 flip-card grid + Flip All / Shuffle / Reset / Print toolbar. |
| Reward | 🌟 | Confetti celebration with stars + words-learned counter. |
| Avatar Video | 🎬 | HeyGen AI avatar: Thai intro → interactive game (unique mechanic per unit) → English reveals → Thai outro. |

### Ages 8-12 (can also use all 4-7 types)

| Type | Symbol | Description |
|------|--------|-------------|
| Comic | 💬 | 6-8 panel strip, speech bubbles, bilingual audio, 3 comprehension questions. |
| Quiz Show | 🏆 | Game-show quiz: timer, 3 lifelines, escalating difficulty, 10-15 questions. |
| Word Puzzle | 🧩 | Crossword + word search + word scramble; hint system; printable. |
| Adventure | 🗺️ | Choose-your-own-adventure, 10-15 scenes, 3-4 endings, vocab-gated choices. |
| Journal | 📓 | Guided writing: 3 prompts, word bank, localStorage save, teacher print. |
| Video Lesson | 🎬 | Pre-watch vocab → video → pause-and-answer checks → post-watch quiz. |
| Board Game | 🎲 | Virtual snakes-and-ladders, 2-4 players pass-and-play, localStorage wins. |
| Reading | 📰 | 100-200 word passage + audio + TF/MC/"find the word" comprehension. |

---

## Song Page: Verified YouTube Video IDs

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

To verify/replace a video ID: `https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=VIDEO_ID&format=json`

---

## Story Concept Patterns

| Pattern | Description |
|---------|-------------|
| Cumulative | Each page adds to a growing scene |
| Chain | Characters/items line up one by one |
| Building | Something constructed piece by piece |
| Journey | Character moves through spaces discovering things |
| Feast | Character tries everything |
| Chaos | Situation gets sillier and sillier |
| Introduction | Meet characters who each do something goofy |
| Discovery | Character finds things one by one |

---

## Stickers Page Notes

- 6 themed stickers: animals, food, objects — NOT abstract shapes
- Emoji color rule: CSS `color` does NOT recolor emojis. Use an emoji whose
  native color matches the vocabulary word (e.g., 🐸 green frog, 🔵 blue circle).
- Stamp trail: semi-transparent stamps along drag path (opacity: 0.45)
- Clear Scene button resets board

## Flashcards Page Notes

- Core teacher resource — include in EVERY unit
- Front: large emoji/image (4.5em). Content-appropriate emoji per vocab word
- Back: English word (2.2em bold) + Thai translation on colored gradient
- Toolbar: Flip All / Shuffle / Reset / Print
- Print: @media print hides all UI except 3-column card grid

## Reward Page Notes

- Confetti animation, star display, word-count, "Next Week" link to next unit's story
