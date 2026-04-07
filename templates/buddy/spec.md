# Specification: {{course_title}}

**Status:** Draft | Ready for Review | Approved
**Date:** {{YYYY-MM-DD}}
**Course ID:** {{course_id}}

## Course Identity

| Field | Value |
|-------|-------|
| Title | {{title_l2}} |
| Title ({{l1_name}}) | {{title_l1}} |
| Level | {{CEFR_level}} |
| Target | {{audience description}} |
| Schedule | {{sessions/week}} x {{n_weeks}} weeks |
| L1 | {{l1_name}} ({{l1_code}}) |
| L2 | {{l2_name}} ({{l2_code}}) |

## Target Audience

{{1-2 paragraphs: who the learner is, what they can already do, what real-world interests/topics matter to them, what reading/cognitive level to assume}}

## Unit Breakdown

| Week | Topic (L2) | Topic (L1) | Emoji | Grammar Focus |
|------|-----------|-----------|-------|---------------|
| 1 | {{topic}} | {{topic_l1}} | {{emoji}} | {{grammar_point}} |
| 2 | ... | ... | ... | ... |
| {{n}} | ... | ... | ... | ... |

## Vocabulary ({{n}} words per unit)

### Week 1: {{topic}}
{{word1}} ({{translation1}}), {{word2}} ({{translation2}}), ...

### Week 2: {{topic}}
...

## Page Types Per Unit

| Page Type | Assignment | Description |
|-----------|-----------|-------------|
| {{page_type}} | every \| random:N \| units:1,5,9 \| none | {{one-line description}} |
| ... | ... | ... |

**Total files: {{n_units}} x {{n_page_types}} page types = {{total}} HTML files**

## File Naming Convention

Pattern: `{{prefix}}_{topic}_{pagetype}.html`

Examples:
- `{{prefix}}_{{topic_slug}}_{{page_type}}.html`

## Theme

```css
--primary: {{#hex}}; --primary-dark: {{#hex}};
--primary-light: {{#hex}}; --primary-pale: {{#hex}};
```

## Output Directory

`{{HTML/courses/course_id/}}`

## Navigation

- Nav footer links to all {{n}} page types for that unit
- Home link to `{{../../syllabus_course_id.html}}`
- {{any unit-to-unit linking rules — e.g., "next" buttons}}
- Footer text: `{{course title — bilingual tagline}}`

## Research

- NotebookLM: {{authenticated | unavailable}} — {{purpose}}
- Web search: {{used | fallback}}
- Sources added: {{list of source categories}}

## Images

- Replicate: {{token available | not available}}
- Provider: {{model_id}}
- {{plan: hero per unit, vocab cards, etc., or "skipped"}}

## Acceptance Criteria

1. All {{total}} HTML files generated and functional
2. Every page is standalone (inline CSS/JS, no external dependencies except Google Fonts)
3. All interactive features work ({{list relevant: games, quizzes, flashcards, TTS}})
4. Bilingual content throughout ({{L1}} first, {{L2}} second)
5. Nav footer on every page links to all page types for that unit
6. No JS console errors
7. Mobile responsive (768px and 480px breakpoints)
8. {{any course-specific criteria}}
