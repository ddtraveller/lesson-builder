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

## Architecture

Lesson Builder is a single Claude Code skill that orchestrates a four-phase pipeline adapted from the buddy workflow (`spec → plan → tasks → implement`). It is **auth-first, research-pluggable, and generation-gated**: every invocation begins by checking which optional services are available, then picks the highest-quality research backend that fits, then commits to a single Python generator script that produces all course HTML in one batch — but only after a Unit 1 verification gate has passed.

```mermaid
flowchart TD
    %% Inputs
    User["User Input<br/>topic · L1·L2 · age · page types · n_units"]
    Config[("Optional<br/>course config<br/>JSON")]

    %% Step 0 — parallel auth checks
    subgraph S0["Step 0 — Service Auth Checks (parallel)"]
        NB["NotebookLM<br/>auth check"]
        TV["Tavily Research<br/>tvly auth status"]
        RP["Replicate<br/>API token check"]
    end

    User --> S0
    Config --> S0

    %% Phase 1 — Spec
    S0 --> P1["Phase 1 — Spec<br/>(buddy:spec pattern)"]
    P1 -->|"copies templates/buddy/spec.md"| Spec[("specs/YYYYMMDD-course_id/<br/>spec.md")]

    %% Phase 2 — Research + Plan
    Spec --> P2["Phase 2 — Research &amp; Plan<br/>(buddy:plan pattern)"]
    P2 --> RBranch{"Which research<br/>backend?"}
    RBranch -->|"Tavily + NotebookLM"| Bridge["Tavily → NotebookLM bridge<br/>tvly research --json<br/>→ ingest URLs + reports"]
    RBranch -->|"NotebookLM only"| NBOnly["notebooklm source add-research<br/>+ ask loop"]
    RBranch -->|"Tavily only"| TVOnly["tvly research -o research.md"]
    RBranch -->|"neither"| Web["Web Search<br/>(2+ authoritative sources)"]
    Bridge --> Research[("research.md<br/>+ plan.md")]
    NBOnly --> Research
    TVOnly --> Research
    Web --> Research

    %% Phase 3 — Tasks
    Research --> P3["Phase 3 — Tasks<br/>(buddy:tasks pattern)<br/>T001–T009"]
    P3 --> Tasks[("tasks.md")]

    %% Phase 4 — Implement
    Tasks --> P4["Phase 4 — Implement<br/>(buddy:implement pattern)"]
    P4 --> Gen["generate_{course_id}.py<br/>one function per page type"]
    Gen --> Unit1["Generate Unit 1 only<br/>(verification gate)"]
    Unit1 --> Verify{"Browser<br/>verify?"}
    Verify -->|"fails"| Gen
    Verify -->|"passes"| Bulk["Generate units 2…N"]
    Bulk --> Polish["Cross-file consistency<br/>nav footers · syllabus"]

    %% Optional images
    Polish --> ImgCheck{"Replicate<br/>available?"}
    ImgCheck -->|"yes"| Imgs["generate_images.py<br/>FLUX Dev hero images"]
    ImgCheck -->|"no"| Out
    Imgs --> Out

    %% Output
    Out[("HTML/courses/course_id/<br/>standalone bilingual HTML files<br/>+ syllabus + optional images")]

    %% Styling
    classDef input fill:#fff3e0,stroke:#ff9800,color:#000
    classDef artifact fill:#e3f2fd,stroke:#2196f3,color:#000
    classDef phase fill:#f3e5f5,stroke:#9c27b0,color:#000
    classDef decision fill:#fffde7,stroke:#fbc02d,color:#000
    class User,Config input
    class Spec,Research,Tasks,Out artifact
    class P1,P2,P3,P4 phase
    class RBranch,Verify,ImgCheck decision
```

### Pipeline Phases

| Phase | Pattern | Produces | Purpose |
|---|---|---|---|
| **Phase 1 — Spec** | `buddy:spec` | `spec.md` | Course identity, unit breakdown, vocab lists, page types, theme, acceptance criteria. Copied from `templates/buddy/spec.md` and filled in interactively or from a config. |
| **Phase 2 — Research & Plan** | `buddy:plan` | `research.md`, `plan.md` | Cited research from the best available backend, plus an implementation plan with generator script architecture, content per unit, and risk assessment. |
| **Phase 3 — Tasks** | `buddy:tasks` | `tasks.md` | Ordered work breakdown (T001–T009). Load-bearing rule: T005 (Unit 1) and T006 (browser verify) form a hard gate before bulk generation. |
| **Phase 4 — Implement** | `buddy:implement` | Generator script + HTML output | Writes one Python script per course, runs it on Unit 1 first, verifies in browser, then bulk-generates remaining units. |

A complete worked example lives in `specs/EXAMPLE-tefl_children_10_12/` — Thai children ages 10-12, 12 units, 84 HTML files. Read it before starting a new course to see the proven shape of each artifact.

### Pluggable Research Backends

Phase 2 selects a research method automatically based on what Step 0 detected. The skill always picks the highest-quality backend that's actually available, with graceful degradation:

| Available | Method | Quality |
|---|---|---|
| Tavily Research **+** NotebookLM | **Tavily → NotebookLM bridge** — `tvly research --json` produces cited reports, citation URLs are ingested into NotebookLM as URL sources, then the existing `notebooklm ask` loop runs against the enriched corpus | Best |
| NotebookLM only | Plain `notebooklm source add-research` + `ask` loop | Good |
| Tavily only | `tvly research -o research.md`, no Q&A grounding | Good |
| Neither | Built-in web search, 2+ authoritative sources | Adequate |
| User opts for speed | Training data only | Fast but unverified |

### Generation Strategy

A single Python generator script per course (`generate_{course_id}.py`) produces all HTML files in one batch. Each page type is a function (`generate_lesson`, `generate_exam`, `generate_flashcards`, …). Pages are intentionally **standalone** — inline CSS and JS, no external bundles, no runtime dependencies beyond Google Fonts. This means every page works on any static host, in any browser, with no build step.

The Unit 1 verification gate is the load-bearing rule that keeps generation reliable: the script generates only Unit 1 first, the user opens every page in a browser to confirm interactive features work and there are no JS errors, *then* the remaining units are generated using the same templates. No bulk generation runs against an unverified template.

### Repo Layout

```
lesson-builder/
├── SKILL.md                          # The skill itself (read by Claude Code)
├── README.md                         # This file
├── NOTEBOOKLM.md                     # NotebookLM setup guide
├── CHILDREN_PAGES.md                 # Children's page-type specifications
├── IMAGE_GENERATION.md               # Replicate / FLUX Dev image generation
├── config/                           # Course config JSONs (12-week TEFL examples)
├── templates/
│   ├── *.json                        # Course config templates (business, IT, starter)
│   └── buddy/                        # Buddy workflow artifact templates
│       ├── spec.md                   # Phase 1 skeleton
│       ├── plan.md                   # Phase 2 skeleton
│       ├── tasks.md                  # Phase 3 skeleton
│       └── research.md               # Phase 2 research notes skeleton
└── specs/
    └── EXAMPLE-tefl_children_10_12/  # Complete worked example (5 artifacts)
```

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
| [Tavily Research](https://github.com/tavily-ai/skills) | Deep cited research via the `tvly` CLI; can feed citation URLs and synthesized reports directly into NotebookLM as sources |
| `fact-checker` skill | Validates grammar rules, translations, and quiz answers before generation |
| [Replicate](https://replicate.com) | AI image generation (FLUX Dev) for lesson illustrations (~$0.03/image) |

### Optional: Secrets Manager Auto-Login

If you store API keys in a secrets manager (AWS SSM Parameter Store, AWS Secrets Manager, HashiCorp Vault, GCP Secret Manager, Azure Key Vault, 1Password CLI, etc.), the skill's Step 0 auth checks can pull credentials from there automatically instead of prompting the user.

For example, with **AWS SSM Parameter Store** and the AWS CLI configured:

```bash
# In Step 0b, if `tvly auth` reports unauthenticated:
TAVILY_KEY=$(aws ssm get-parameter --name tavily --with-decryption \
  --region us-west-2 --query 'Parameter.Value' --output text 2>/dev/null)
[ -n "$TAVILY_KEY" ] && tvly login --api-key "$TAVILY_KEY"
```

Adapt the lookup line to whatever secrets backend you use. The skill's auth check just needs to end with `tvly login --api-key` (or the equivalent for NotebookLM / Replicate). This pattern keeps API keys out of `.env` files and out of shell history while still letting the skill bootstrap itself non-interactively on a fresh machine.

## Built With This

**[krueng.ai](https://krueng.ai)** — A 6-course IT career training program teaching English through technology to Thai learners at Wat Don Chan, Chiang Mai. 72 weeks of lessons, activities, and exams across Digital Foundations, IT Essentials, AI & English, Networking, Help Desk, and Security.

## License

MIT — see [LICENSE](LICENSE).
