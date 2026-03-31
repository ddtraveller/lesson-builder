# Templates

Starter configs for common course types. Copy one, fill in the details, and run `/lesson-builder`.

| Template | Description | L1 | Ready to use? |
|----------|-------------|----|----|
| `business_english.json` | 12-week workplace English (meetings, emails, presentations) | Thai | Yes |
| `english_through_it.json` | 12-week IT skills course (hardware, networking, security, help desk) | Any — fill in L1 translations | Needs L1 |
| `minimal_starter.json` | Blank 1-unit template — fill in everything | Any | Template only |

## How to use

1. Copy a template to your project's `config/` directory
2. Edit the `CHANGE_ME` fields
3. Run `/lesson-builder` — it will detect and load the config

## Customizing

- **Change colors**: Edit the `theme` object
- **Change page mix**: Edit `page_types` — use `"every"`, `"none"`, `"random:N"`, or `"units:1,5,9"`
- **Add units**: Copy a unit object and increment the `week` number
- **Enable images**: Set `images.enabled` to `true` and add a Replicate API token
