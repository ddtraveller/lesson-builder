# Lesson Builder — Claude Code Skill

Generate complete, standalone bilingual courses from a single prompt. Lessons, exams, flashcards, conversations, pronunciation drills, worksheets, and syllabi — any language pair, any topic, zero dependencies.

## Install

Add the marketplace and install:

```
/plugin marketplace add ddtraveller/lesson-builder
/plugin install lesson-builder
```

Or copy directly into your skills directory:

```bash
git clone https://github.com/ddtraveller/lesson-builder.git
cp -r lesson-builder/skills/lesson-builder ~/.claude/skills/
```

## Usage

```
/lesson-builder
```

The skill walks you through setup interactively — or reads from a JSON config file for repeatable builds.

## What It Generates

Each unit produces standalone HTML/CSS/JS files with no external dependencies (except Google Fonts). Everything is bilingual — learner's language (L1) first, target language (L2) second.

| Page Type | What It Does |
|-----------|-------------|
| 📄 **Lesson** | Vocabulary cards, grammar focus, guided tutorials, section quizzes, homework |
| 📝 **Activities** | 5-6 exercises per unit with Easy/Medium/Hard difficulty badges |
| 📝 **Exam** | Interactive exam engine with difficulty selector, score tracking, and gradebook |
| 🃏 **Flashcards** | Flip cards with pronunciation audio, shuffle, keyboard navigation |
| 💬 **Conversation** | Dialogue role-play scenarios with speech bubbles and comprehension questions |
| 🔊 **Pronunciation** | Minimal pairs, listen-and-repeat drills, tongue twisters targeting L1 interference |
| 🖨️ **Worksheet** | Print-optimized exercises with hidden answer key |
| 📊 **Syllabus** | Course overview with week navigation, scope table, and assessment rubric |

## Example Use Cases

**Language Schools & TEFL Programs**
- Thai→English, Japanese→English, Spanish→English — any L1→L2 pair
- CEFR-aligned courses from Pre-A1 through B1+
- Classroom supplements with printable worksheets and exam score tracking

**Vocational & Career Training**
- English through IT — teach networking, cybersecurity, or web dev vocabulary in English
- Business English — meetings, email, presentations
- Medical or hospitality English — domain-specific vocabulary for career pathways

**Self-Paced E-Learning**
- Host on S3, GitHub Pages, or any static server — no backend required
- Full 12-week courses from a single JSON config
- One-off lessons on any topic in minutes

**Content at Scale**
- Python generator scripts produce dozens of pages at once
- JSON configs make courses repeatable and version-controlled
- Mix and match page types per unit — exams every week, flashcards for 3 random units, pronunciation drills at weeks 6, 9, and 12

## Configuration

Define a reusable course as a JSON config. Control everything — languages, page types per unit, section structure, color theme, and vocabulary targets.

```jsonc
{
  "course_id": "my_course",
  "l1": "th", "l2": "en",
  "output_dir": "HTML/courses/my_course",
  "theme": { "primary": "#f97316" },

  "page_types": {
    "lesson": "every",
    "exam": "every",
    "flashcards": "random:3",
    "conversation": "random:4",
    "pronunciation": "units:6,9,12",
    "syllabus": true
  },

  "units": [ ... ]
}
```

See [`config/schema.md`](skills/lesson-builder/config/schema.md) for the full specification and examples.

## Optional Integrations

These are not required — the skill works standalone using Claude's training data.

| Integration | What It Does |
|-------------|-------------|
| [NotebookLM](https://github.com/teng-lin/notebooklm-py) | AI-powered research to verify course content against authoritative sources |
| `fact-checker` skill | Validates grammar rules, translations, and quiz answers before generation |
| [Replicate](https://replicate.com) | AI image generation (FLUX Dev) for lesson illustrations (~$0.03/image) |

## Built With This

**[krueng.ai](https://krueng.ai)** — A 6-course IT career training program teaching English through technology to Thai learners at Wat Don Chan, Chiang Mai. 72 weeks of lessons, activities, and exams across Digital Foundations, IT Essentials, AI & English, Networking, Help Desk, and Security.

## License

MIT — see [LICENSE](LICENSE).
