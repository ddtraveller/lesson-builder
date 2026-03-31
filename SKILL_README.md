# Lesson Builder

Generate complete bilingual TEFL/ESL courses with configurable page types — lessons, exams, flashcards, conversations, pronunciation drills, worksheets, and syllabi.

## Features

- **Any language pair** — Configure L1 (learner's language) and L2 (target language)
- **Any topic** — General English, Business English, English through IT, etc.
- **8 page types** — Lessons, activities, exams, flashcards, conversations, pronunciation, worksheets, syllabi
- **Configurable** — JSON config controls which pages each unit gets, page structure, theme colors
- **AI research** — Optional NotebookLM and web search for content verification
- **Fact-checking** — Optional fact-checker integration before generation
- **AI images** — Optional FLUX Dev image generation via Replicate

## Quick Start

Invoke the skill in Claude Code:
```
/lesson-builder
```

It will ask you:
1. What topic to cover
2. What languages (L1 → L2)
3. How many weeks/units
4. Which page types per unit
5. Where to save files

## Configuration

Create a JSON config in `config/` to define a reusable course. See `config/schema.md` for the full spec.

Example: `config/tefl_beginners.json` — 12-week Thai→English beginner course.

## Page Types

| Type | Description |
|------|-------------|
| 📄 Lesson | Vocabulary, grammar, tutorials, section quizzes |
| 📝 Activities | Practice exercises with difficulty levels |
| 📝 Exam | Interactive exam with score tracking |
| 🃏 Flashcards | Flip cards for vocab drilling |
| 💬 Conversation | Dialogue role-play with audio |
| 🔊 Pronunciation | Sound drills for L1 interference |
| 🖨️ Worksheet | Print-friendly exercises |
| 📊 Syllabus | Course overview page |

## Dependencies

**Required:** None (generates standalone HTML/CSS/JS)

**Optional:**
- [NotebookLM skill](https://github.com/teng-lin/notebooklm-py) — AI research
- `fact-checker` skill — Content verification
- [Replicate](https://replicate.com) account — AI image generation

## License

MIT
