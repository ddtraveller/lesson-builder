# Implementation Plan: TEFL Children 10-12

**Status:** Ready for Review
**Date:** 2026-04-06

## Strategy

Write a Python generator script that creates all 84 HTML files programmatically. This follows the same pattern as the existing children_8_10 course. The script will be modular with one function per page type.

## Architecture

### Generator Script: `generate_tefl_children_10_12.py`

Located at: `C:/Users/ddtra/claude/watdonchan/generate_tefl_children_10_12.py`

**Structure:**
```
1. COURSE_DATA — all 12 units with vocab, stories, songs, readings, quiz data
2. CSS_BASE — shared CSS template (from children_8_10 pattern)
3. generate_story(unit) — 6-page story with comprehension
4. generate_game(unit) — 3-tab game (match, scramble, spell)
5. generate_song(unit) — YouTube embed + lyrics + fill-in
6. generate_reading(unit) — Thai vocab passage + English reading + questions
7. generate_flashcards(unit) — flip cards with emoji/word/thai/definition
8. generate_quiz(unit) — 10 mixed questions
9. generate_reward(unit) — celebration + word review
10. main() — iterate units, write files
```

**Estimated size:** ~2500-3000 lines (within the 3000 line limit)

### Content Per Unit

Each unit in COURSE_DATA contains:
- `topic`, `topic_th`, `emoji`, `week` — identity
- `grammar`, `grammar_th` — grammar focus
- `vocab` — list of [english, thai, emoji, definition] tuples
- `story_pages` — 6 story page objects with text, Thai, emoji
- `story_questions` — 3 comprehension questions
- `song` — title, youtube_id, lyrics lines (en + th)
- `reading_vocab_passage` — Thai passage with embedded English vocab
- `reading_passage` — English reading passage
- `reading_questions` — 4 comprehension questions

### YouTube Song IDs (verified for ages 10-12)

| Week | Song | YouTube ID |
|------|------|-----------|
| 1 | Technology Song | to be researched |
| 2 | Travel the World | to be researched |
| ... | ... | ... |

Songs will use popular children's English learning songs from Super Simple Songs, English Singsing, or similar channels.

## Phases

### Phase 1: Setup
- Create output directory `HTML/tefl/children_10_12/`
- Write course config JSON (optional, for future re-generation)

### Phase 2: Generator Script (Unit 1 only)
- Write generator with all 7 page type functions
- Generate only Unit 1 (Technology) as test
- Verify all pages work in browser

### Phase 3: Full Generation
- After Unit 1 passes, populate remaining 11 units
- Generate all 84 files
- Cross-check nav footers and links

### Phase 4: Polish
- Verify no JS errors across all pages
- Check mobile responsiveness
- Validate all YouTube IDs (if using songs)

## Risk Assessment

- **Script size:** May approach 3000 lines. If too large, split COURSE_DATA into a separate JSON file
- **YouTube IDs:** Need valid video IDs for each topic. Fallback: use a generic "learn English" song
- **Encoding:** Must use `encoding='utf-8'` everywhere (Windows cp1252 issue)
- **Thai text in Python strings:** Use triple-quoted strings carefully, avoid f-string issues with curly braces in CSS
