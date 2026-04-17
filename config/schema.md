# Lesson Builder Configuration Schema

A course config is a JSON file that fully describes what to generate. Place configs in this directory and reference them by name.

## Top-Level Fields

```jsonc
{
  // === Course Identity ===
  "course_id": "tefl_beginners",           // Unique slug, used for filenames
  "title": "English for Everyday Life",     // Display title (L2)
  "title_l1": "ภาษาอังกฤษสำหรับชีวิตประจำวัน",  // Display title (L1)
  "description": "A 12-week course...",     // Course description
  "level": "Pre-A1 → A1",                  // Proficiency level (CEFR or custom)
  "schedule": "1 hour/week × 12 weeks",    // Schedule description

  // === Languages ===
  "l1": "th",                // Learner's first language (ISO 639-1)
  "l1_name": "Thai",         // L1 display name in English
  "l1_name_native": "ภาษาไทย", // L1 display name in L1
  "l2": "en",                // Target language being taught
  "l2_name": "English",

  // === Output ===
  "output_dir": "HTML/tefl/beginners",   // Relative to project root
  "file_prefix": "begin",               // Prefix for generated files
  "syllabus_file": "syllabus_tefl_beginners.html",  // Relative to HTML/

  // === Color Theme ===
  "theme": {
    "primary": "#f97316",
    "primary_dark": "#ea580c",
    "primary_light": "#fdba74",
    "primary_pale": "#fff7ed",
    "accent": "#f59e0b",
    "header_gradient_start": "#ea580c",
    "header_gradient_end": "#9a3412"
  },

  // === Page Types ===
  // Controls which pages are generated per unit.
  "page_types": {
    // "every" — generate for every unit
    // "none" — never generate
    // "random:N" — randomly assign to N units (e.g., "random:4" = 4 random units)
    // "units:1,3,5,7" — generate only for specific units
    // [list] — pick randomly from list for each unit (e.g., ["flashcards","conversation"])
    "lesson": "every",
    "activities": "every",
    "exam": "every",
    "flashcards": "random:3",
    "conversation": "random:4",
    "pronunciation": "random:3",
    "worksheet": "random:3",
    "syllabus": true              // boolean — one per course, not per unit
  },

  // === Page Structure ===
  // Controls which sections appear in each page type.
  "page_structure": {
    "lesson": {
      "sections": [
        "introduction",     // Bilingual intro box + fun facts
        "vocabulary",       // Vocab cards grid (count controlled by vocab_per_unit)
        "grammar",          // Grammar focus box with examples
        "tutorial_steps",   // Step-by-step guided practice
        "activity",         // Hands-on exercise
        "reference_table",  // Comparison/reference table
        "summary"           // What you learned + encouragement
      ],
      "section_checks": true,       // Include quiz after each section?
      "section_check_questions": 3,  // Questions per section check
      "homework": true,              // Include homework section?
      "references": true,            // Include references/citations section?
      "audio_buttons": true,         // Include speak() pronunciation buttons?
      "hero_image": true             // Include hero image at top?
    },
    "activities": {
      "activity_count": 5,           // Number of activity cards per page
      "difficulty_levels": ["easy", "medium", "hard"],
      "mark_complete_buttons": true
    },
    "exam": {
      "categories": 5,              // Number of question categories
      "questions_per_category": {
        "easy": 2,                   // Questions per category at each difficulty
        "medium": 3,
        "hard": 4
      },
      "difficulty_selector": true,   // Let student pick difficulty?
      "gradebook": true              // Save scores to localStorage?
    },
    "flashcards": {
      "cards_per_page": 12,
      "show_phonetic": true,
      "shuffle_button": true,
      "keyboard_nav": true           // Space to flip, arrows to navigate
    },
    "conversation": {
      "dialogue_lines": 8,
      "comprehension_questions": 3,
      "role_play_prompts": 3
    },
    "pronunciation": {
      "minimal_pairs": 6,
      "listen_repeat_items": 6,
      "tongue_twisters": 2,
      "slow_mode": true              // 0.6x speed option
    },
    "worksheet": {
      "exercises": 5,
      "print_optimized": true,
      "answer_key": true             // Hidden toggle answer key
    }
  },

  // === Vocabulary ===
  "vocab_per_unit": 12,              // Target vocab items per unit

  // === Research & Quality ===
  "research": {
    "notebooklm": true,              // Use NotebookLM for research?
    "web_search": true,              // Use WebSearch/WebFetch?
    "fact_check": true               // Run fact-checker skill?
  },

  // === Backend Choices Group ===
  // Set at course-creation time (interactive Q8/9/10). Each field is confirmed
  // available by scripts/backend_probes.py before being recorded; the config
  // never stores an unavailable backend. All defaults are "off" to prevent
  // accidental quota spend.

  // Content-truth validation (Phase 5c)
  "content_truth": {
    "backend": "off"                  // "tavily" | "notebooklm" | "off"
    //   tavily:      cross-check vocab/grammar/exam via Tavily Research CLI
    //   notebooklm:  query Phase-2 research notebook (ID from research.md)
    //   off:         skip Phase 5c — no quota consumed
  },

  // Image generation
  "images": {
    "backend": "off",                 // "flux" | "off"  (replaces enabled+provider)
    //   flux: generate via Replicate FLUX Dev model (requires REPLICATE_API_TOKEN)
    //   off:  no image generation
    // Legacy fields below kept for backward compatibility with old configs:
    "enabled": false,                 // Deprecated — use backend instead
    "provider": "replicate",          // "replicate" or "none"
    "model": "black-forest-labs/flux-dev",
    "style_prefix": "Warm educational illustration...",
    "style_suffix": ", professional quality...",
    "hero_image": true,               // Generate course hero?
    "per_unit_image": true,           // Generate per-lesson image?
    "aspect_ratio": "16:9"
  },

  // Video generation
  "video": {
    "backend": "off",                 // "heygen" | "remotion" | "capcut" | "webm" | "off"
    //   heygen:   AI avatar video via HeyGen API (~$2/video — probe SSM for key)
    //   remotion: React video via watdonchan/ai-english-video Remotion project
    //   capcut:   prompt-to-human workflow; operator assembles manually
    //   webm:     NOT YET IMPLEMENTED (probe returns unavailable, falls back to off)
    //   off:      no video generation
    "max_count": 0                    // Per-course cap on video generation (0 = no limit when backend=off)
    //   Required (> 0) when backend != off; prevents surprise spend.
    //   Generator halts with a readable error when this count is reached.
  },

  // === Navigation ===
  "navigation": {
    "show_syllabus_link": true,
    "show_prev_next": true,
    "cross_links": []                 // Links to other courses/pages
  },

  // === Units (the actual course content) ===
  "units": [
    // See Unit Schema below
  ]
}
```

## Unit Schema

Each unit in the `units` array:

```jsonc
{
  "week": 1,
  "prefix": "begin_greetings",        // File prefix
  "topic_l2": "Greetings & Introductions",
  "topic_l1": "การทักทายและการแนะนำตัว",
  "grammar_l2": "Pronouns + Verb 'to be'",
  "grammar_l1": "สรรพนาม + กริยา to be",
  "emoji": "👋",

  // Vocabulary — array of [term, l1_translation, definition]
  "vocab": [
    ["hello", "สวัสดี", "A common greeting"],
    ["goodbye", "ลาก่อน", "Said when leaving"],
    // ... 10-12 items
  ],

  // English objectives (displayed in L1)
  "objectives_l2": [
    "สร้างประโยคด้วย I am / You are / He is",
    "แนะนำตัวเองเป็นภาษาอังกฤษ"
  ],

  // Subject/tech objectives (L1 with L2 notes)
  "objectives_subject": [
    "ทักทายผู้คนอย่างสุภาพ<span class=\"thai-note\">Greet people politely</span>",
    "บอกชื่อและถามชื่อ<span class=\"thai-note\">Say your name and ask others' names</span>"
  ],

  // Grammar pattern box (HTML)
  "pattern_box": "I <strong>am</strong> a student.<br>She <strong>is</strong> a teacher.",

  // Homework description
  "homework": "Practice introducing yourself to 3 people; write 5 'I am...' sentences",

  // Optional: override page types for this specific unit
  "page_types_override": {
    "conversation": true,    // Force conversation page for this unit
    "flashcards": false      // No flashcards for this unit
  },

  // Optional: pronunciation focus for this unit
  "pronunciation_focus": {
    "target_sounds": ["/r/ vs /l/"],
    "l1_note": "คนไทยมักสับสนระหว่างเสียง r กับ l",
    "minimal_pairs": [["right", "light"], ["read", "lead"]]
  },

  // Optional: conversation scenario for this unit
  "conversation": {
    "scenario_l2": "Meeting a new colleague at the office",
    "scenario_l1": "พบเพื่อนร่วมงานใหม่ที่ออฟฟิศ",
    "speakers": [
      {"label": "You", "label_l1": "คุณ", "emoji": "🧑"},
      {"label": "Colleague", "label_l1": "เพื่อนร่วมงาน", "emoji": "👩‍💼"}
    ]
  }
}
```

## Page Type Assignment Logic

When `page_types` uses `"random:N"`:
1. Randomly select N units from the total
2. Assign the page type to those units
3. Ensure no unit gets duplicate random assignments unless explicitly configured
4. Use a seed based on `course_id` for reproducible randomness

When `page_types` uses a list like `["flashcards", "conversation", "pronunciation"]`:
1. For each unit, randomly pick one from the list
2. Ensures variety across the course

When `page_types` uses `"units:1,5,9"`:
1. Only generate for the specified unit numbers

## Example: "I want an exam every unit + random extras"

```json
{
  "page_types": {
    "lesson": "every",
    "activities": "every",
    "exam": "every",
    "flashcards": "random:2",
    "conversation": "random:4",
    "pronunciation": "units:6,9,12",
    "worksheet": "random:3",
    "syllabus": true
  }
}
```

## Example: "Just lessons and worksheets, no exams"

```json
{
  "page_types": {
    "lesson": "every",
    "activities": "none",
    "exam": "none",
    "worksheet": "every",
    "syllabus": true
  }
}
```
