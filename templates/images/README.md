# Image Generation via `generate_images.py` (FLUX Dev on Replicate)

`generate_images.py` handles batch image generation using FLUX Dev on Replicate.
Reads prompts from a JSON file. Requires `REPLICATE_API_TOKEN` in a `.env` file.

```bash
pip install replicate
# .env: REPLICATE_API_TOKEN=r8_your_token_here
```

Cost: ~$0.03-0.05 per image. Token: https://replicate.com/account/api-tokens

## Prompts JSON Format

```json
{
  "style_prefix": "Art style applied to ALL images. ",
  "style_suffix": " Negative constraints appended to all prompts.",
  "output_dir": "imgs/my_output",
  "settings": { "guidance": 3.5, "num_inference_steps": 28, "aspect_ratio": "1:1", "output_format": "png" },
  "images": {
    "image_id": { "prompt": "Scene description for this image" }
  }
}
```

Final prompt: `style_prefix + prompt + style_suffix` (joined with `, `).

## Commands

```bash
python generate_images.py prompts.json --dry-run   # preview prompts, no API calls
python generate_images.py prompts.json --list      # list done vs pending
python generate_images.py prompts.json             # generate all pending
python generate_images.py prompts.json --id animals_cat  # one specific image
python generate_images.py prompts.json --guidance 4 --steps 30 --aspect 16:9
```

Resilience: skips existing, retries 4× with exponential backoff, 3s delay between calls.

## Coloring Page Style Prefix

For children's coloring pages, copy `templates/images/prompt_style_prefix.txt` as
your `style_prefix`. Pair with suffix: `" No color, no shading, no gradients,
no gray areas. Pure black outlines on pure white background only."`

See `config/coloring_prompts_example.json` for a 52-image example across 8 topics.
Naming convention: `{topic}_{word}.png` (e.g., `animals_cat.png`, `food_rice.png`).

## Use-Case to Aspect Ratio

| Use Case | Aspect | Style Key Points |
|----------|--------|-----------------|
| Coloring pages | 1:1 | B&W line art, thick outlines, no shading, white background |
| Story illustrations | 16:9 | Watercolor children's book, warm colors, scene-specific |
| Game assets | 1:1 | Kawaii cartoon, flat design, pastel colors |
| Comic panels | 16:9 or 4:5 | B&W ink, bold lines |

When generating images with people: specify ethnicity matching the learner population
in the style prefix (e.g., "Southeast Asian Thai ethnicity with warm brown skin,
straight black hair" for Thai courses).

## Image Path Convention

```
imgs/tefl/{course_slug}/     ← generated images (gitignored — S3 only)
HTML/tefl/{course_slug}/     ← lesson HTML files (GitHub)
```

HTML src attributes use relative paths from the HTML file's depth:
- Lesson files: `src="../../../imgs/tefl/{course_slug}/{prefix}.png"`
- Syllabus: `src="../imgs/tefl/{course_slug}/hero.png"`

The `imgs/` directory is gitignored (*.png) — upload to S3 separately.

---

## Unicode Emoji Color Reference

**CSS `color` does NOT change emoji rendering.** Emojis have built-in colors.
Always use the correct Unicode codepoint for the intended color.

### Colored Circles

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
