#!/usr/bin/env python3
"""
Generic image generation script using Replicate FLUX Dev.

Reads prompts from a JSON file or text file and generates images.

Input formats supported:
  1. JSON with "images" dict:   {"images": {"id": {"prompt": "...", "aspect_ratio": "16:9"}}}
  2. JSON with "images" array:  {"images": [{"id": "name", "prompt": "..."}]}
  3. JSON with "prompts" dict:  {"prompts": {"id": {"prompt": "...", "aspect_ratio": "16:9"}}}
     (compatible with generate_star_images.py prompts format)
  4. Plain text file:           One prompt per line (image named line_01.png, line_02.png, etc.)

Optional JSON fields:
  "style_prefix"  — prepended to every prompt
  "style_suffix"  — appended to every prompt
  "output_dir"    — default output directory (overridden by --output-dir)
  "settings"      — default generation settings:
      "guidance", "num_inference_steps", "aspect_ratio", "output_format", "model"

Usage:
    python generate_images.py prompts.json                       # Generate all
    python generate_images.py prompts.json --output-dir ./out    # Custom output
    python generate_images.py prompts.json --list                # List images & status
    python generate_images.py prompts.json --dry-run             # Show prompts, don't generate
    python generate_images.py prompts.json --id scene_03         # Generate one image
    python generate_images.py prompts.txt                        # Plain text, one prompt per line
    python generate_images.py prompts.json --guidance 4 --steps 30  # Override settings
    python generate_images.py prompts.json --aspect 1:1          # Override aspect ratio

Environment:
    REPLICATE_API_TOKEN  — Required. Get from https://replicate.com/account/api-tokens
"""
import sys
import os
import json
import time
import argparse
import urllib.request
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# ── Defaults ──────────────────────────────────────────────────────────────

DEFAULT_MODEL = "black-forest-labs/flux-dev"
DEFAULT_GUIDANCE = 3.5
DEFAULT_STEPS = 28
DEFAULT_ASPECT = "16:9"
DEFAULT_FORMAT = "png"


def load_env():
    """Load API keys from .env file."""
    # Check worktree .claude/.env, then project root, then common locations
    worktree_claude_env = PROJECT_ROOT.parent.parent / ".env"
    env_locations = [
        worktree_claude_env,
        PROJECT_ROOT / ".env",
        PROJECT_ROOT / ".claude" / ".env",
        PROJECT_ROOT / "HTML" / ".env",
        Path(__file__).parent / ".env",
        Path.cwd() / ".env",
    ]
    for env_path in env_locations:
        if env_path.exists():
            with open(env_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key and value and not os.environ.get(key):
                            os.environ[key] = value
            print(f"  Loaded keys from {env_path}")
            return
    print("  No .env found — using environment variables")


def load_input(filepath):
    """
    Load prompts from a JSON or text file.

    Returns:
        images: dict of {id: {"prompt": str, "aspect_ratio": str, ...}}
        config: dict with optional style_prefix, style_suffix, settings, output_dir
    """
    filepath = Path(filepath)
    if not filepath.exists():
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)

    ext = filepath.suffix.lower()

    # ── Plain text: one prompt per line ──
    if ext in (".txt", ".text"):
        lines = filepath.read_text(encoding="utf-8").strip().splitlines()
        lines = [l.strip() for l in lines if l.strip() and not l.strip().startswith("#")]
        images = {}
        for i, line in enumerate(lines, 1):
            img_id = f"line_{i:02d}"
            images[img_id] = {"prompt": line}
        return images, {}

    # ── JSON ──
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    config = {}
    if "style_prefix" in data:
        config["style_prefix"] = data["style_prefix"]
    if "style_suffix" in data:
        config["style_suffix"] = data["style_suffix"]
    if "output_dir" in data:
        config["output_dir"] = data["output_dir"]
    if "settings" in data:
        config["settings"] = data["settings"]

    # Also support the style object from star prompts format
    if "style" in data and isinstance(data["style"], dict):
        if "prefix" in data["style"]:
            config.setdefault("style_prefix", data["style"]["prefix"])
        if "suffix" in data["style"]:
            config.setdefault("style_suffix", data["style"]["suffix"])

    images = {}

    # Format 1: "images" as dict  {"images": {"id": {...}}}
    if "images" in data and isinstance(data["images"], dict):
        images = data["images"]

    # Format 2: "images" as array  {"images": [{"id": "name", ...}]}
    elif "images" in data and isinstance(data["images"], list):
        for item in data["images"]:
            img_id = item.get("id") or item.get("name", f"image_{len(images)+1:02d}")
            # Strip id/name from the entry so it's not passed to generation
            entry = {k: v for k, v in item.items() if k not in ("id",)}
            images[img_id] = entry

    # Format 3: "prompts" dict (generate_star_images.py compatible)
    elif "prompts" in data and isinstance(data["prompts"], dict):
        images = data["prompts"]

    else:
        print("ERROR: JSON must have an 'images' or 'prompts' key.")
        print("  Supported formats:")
        print('    {"images": {"id": {"prompt": "..."}}}')
        print('    {"images": [{"id": "name", "prompt": "..."}]}')
        print('    {"prompts": {"id": {"prompt": "..."}}}')
        sys.exit(1)

    return images, config


def build_prompt(image_data, config):
    """Assemble the final prompt with optional style prefix/suffix."""
    prompt = image_data.get("prompt", "")
    prefix = config.get("style_prefix", "")
    suffix = config.get("style_suffix", "")

    parts = []
    if prefix:
        parts.append(prefix.rstrip(", "))
    parts.append(prompt)
    if suffix:
        parts.append(suffix.lstrip(", "))

    full = ", ".join(parts) if prefix or suffix else prompt

    # FLUX has ~2000 char limit
    if len(full) > 2000:
        full = full[:1997] + "..."

    return full


def generate_image(image_id, image_data, config, output_dir, settings, dry_run=False):
    """Generate a single image using FLUX Dev."""
    import replicate

    prompt = build_prompt(image_data, config)

    # Resolve settings: image-level > file-level > CLI defaults
    file_settings = config.get("settings", {})
    aspect = image_data.get("aspect_ratio",
             image_data.get("aspect",
             file_settings.get("aspect_ratio",
             settings.get("aspect_ratio", DEFAULT_ASPECT))))
    guidance = image_data.get("guidance",
               file_settings.get("guidance",
               settings.get("guidance", DEFAULT_GUIDANCE)))
    steps = image_data.get("num_inference_steps",
            image_data.get("steps",
            file_settings.get("num_inference_steps",
            settings.get("num_inference_steps", DEFAULT_STEPS))))
    out_fmt = image_data.get("output_format",
              file_settings.get("output_format",
              settings.get("output_format", DEFAULT_FORMAT)))
    model = image_data.get("model",
            file_settings.get("model",
            settings.get("model", DEFAULT_MODEL)))

    # Determine filename
    filename = image_data.get("filename") or image_data.get("name")
    if not filename:
        filename = f"{image_id}.{out_fmt}"
    elif not Path(filename).suffix:
        filename = f"{filename}.{out_fmt}"

    output_dir.mkdir(parents=True, exist_ok=True)
    image_path = output_dir / filename

    # Skip if already exists
    if image_path.exists():
        print(f"  [{image_id}] Already exists — skipping")
        return str(image_path)

    title = image_data.get("title", image_id)
    print(f"\n  [{image_id}] {title}")
    print(f"  Aspect: {aspect}  Guidance: {guidance}  Steps: {steps}")
    print(f"  Prompt: {prompt[:120]}...")

    if dry_run:
        print(f"  [DRY RUN] Would generate {image_path}")
        print(f"  Full prompt ({len(prompt)} chars):")
        print(f"    {prompt}")
        return ""

    try:
        output = replicate.run(
            model,
            input={
                "prompt": prompt,
                "guidance": float(guidance),
                "num_outputs": 1,
                "aspect_ratio": aspect,
                "output_format": out_fmt,
                "num_inference_steps": int(steps),
            }
        )

        # Get URL from output
        if isinstance(output, list) and len(output) > 0:
            image_url = str(output[0])
        elif hasattr(output, "url"):
            image_url = output.url
        else:
            image_url = str(output)

        # Download
        print(f"  Downloading...")
        urllib.request.urlretrieve(image_url, str(image_path))
        print(f"  Saved: {image_path}")
        return str(image_path)

    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "auth" in error_msg.lower() or "token" in error_msg.lower():
            print(f"  ERROR: Invalid Replicate API token.")
            print(f"  Set REPLICATE_API_TOKEN in .env or environment.")
            sys.exit(1)
        elif "429" in error_msg or "rate" in error_msg.lower():
            print(f"  RATE LIMITED — will retry")
            raise
        else:
            print(f"  ERROR: {error_msg}")
        return ""


def main():
    parser = argparse.ArgumentParser(
        description="Generate images from a JSON or text prompt file using Replicate FLUX Dev.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Input file formats:
  JSON (dict):   {"images": {"id": {"prompt": "...", "aspect_ratio": "16:9"}}}
  JSON (array):  {"images": [{"id": "name", "prompt": "..."}]}
  JSON (compat): {"prompts": {"id": {"prompt": "..."}}}
  Text file:     One prompt per line (lines starting with # are skipped)

Optional JSON keys:
  "style_prefix"  — prepended to every prompt
  "style_suffix"  — appended to every prompt
  "output_dir"    — default output directory
  "settings"      — {"guidance": 3.5, "num_inference_steps": 28, ...}

Examples:
  python generate_images.py my_prompts.json
  python generate_images.py ideas.txt --output-dir ./renders --aspect 1:1
  python generate_images.py prompts.json --dry-run --id scene_03
        """,
    )
    parser.add_argument("input_file", help="JSON or text file with image prompts")
    parser.add_argument("--output-dir", "-o", type=str, default=None,
                        help="Output directory for generated images")
    parser.add_argument("--id", type=str, default=None,
                        help="Generate only this image ID")
    parser.add_argument("--list", action="store_true",
                        help="List all images and their generation status")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show prompts without generating images")
    parser.add_argument("--guidance", type=float, default=None,
                        help=f"FLUX guidance scale (default: {DEFAULT_GUIDANCE})")
    parser.add_argument("--steps", type=int, default=None,
                        help=f"Number of inference steps (default: {DEFAULT_STEPS})")
    parser.add_argument("--aspect", type=str, default=None,
                        help=f"Aspect ratio (default: {DEFAULT_ASPECT})")
    parser.add_argument("--format", type=str, default=None, choices=["png", "jpg", "webp"],
                        help=f"Output image format (default: {DEFAULT_FORMAT})")
    parser.add_argument("--model", type=str, default=None,
                        help=f"Replicate model (default: {DEFAULT_MODEL})")
    parser.add_argument("--delay", type=float, default=3.0,
                        help="Delay between API calls in seconds (default: 3)")
    parser.add_argument("--retries", type=int, default=4,
                        help="Max retry attempts on failure (default: 4)")
    args = parser.parse_args()

    # Load input
    images, config = load_input(args.input_file)

    if not images:
        print("ERROR: No images found in input file.")
        sys.exit(1)

    # Resolve output directory: CLI > JSON config > input file directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    elif config.get("output_dir"):
        cfg_dir = Path(config["output_dir"])
        if cfg_dir.is_absolute():
            output_dir = cfg_dir
        else:
            output_dir = PROJECT_ROOT / cfg_dir
    else:
        input_stem = Path(args.input_file).stem
        output_dir = PROJECT_ROOT / "imgs" / input_stem

    # Build CLI overrides into settings dict
    cli_settings = {}
    if args.guidance is not None:
        cli_settings["guidance"] = args.guidance
    if args.steps is not None:
        cli_settings["num_inference_steps"] = args.steps
    if args.aspect is not None:
        cli_settings["aspect_ratio"] = args.aspect
    if args.format is not None:
        cli_settings["output_format"] = args.format
    if args.model is not None:
        cli_settings["model"] = args.model

    # ── List mode ──
    if args.list:
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n{'='*60}")
        print(f"  Image Generation Status")
        print(f"{'='*60}")
        print(f"  Input:  {args.input_file}")
        print(f"  Output: {output_dir}")
        print(f"  Total:  {len(images)} images\n")

        print(f"  {'ID':<30} {'Aspect':<8} {'Status'}")
        print(f"  {'-'*30} {'-'*8} {'-'*10}")
        done = 0
        for img_id, img_data in images.items():
            out_fmt = img_data.get("output_format",
                      config.get("settings", {}).get("output_format",
                      cli_settings.get("output_format", DEFAULT_FORMAT)))
            filename = img_data.get("filename") or img_data.get("name") or f"{img_id}.{out_fmt}"
            if not Path(filename).suffix:
                filename = f"{filename}.{out_fmt}"
            img_path = output_dir / filename
            file_aspect = config.get("settings", {}).get("aspect_ratio",
                          cli_settings.get("aspect_ratio", DEFAULT_ASPECT))
            aspect = img_data.get("aspect_ratio", img_data.get("aspect", file_aspect))
            status = "DONE" if img_path.exists() else "pending"
            if img_path.exists():
                done += 1
            print(f"  {img_id:<30} {aspect:<8} {status}")
        print(f"\n  {done}/{len(images)} images generated")
        return

    # ── Load API key ──
    load_env()
    if not args.dry_run and not os.environ.get("REPLICATE_API_TOKEN"):
        print("\n  ERROR: REPLICATE_API_TOKEN not set.")
        print("  Set it in a .env file or: export REPLICATE_API_TOKEN=r8_...")
        print("  Get a token: https://replicate.com/account/api-tokens")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  Image Generator")
    print(f"{'='*60}")
    print(f"  Input:  {args.input_file}")
    print(f"  Output: {output_dir}")
    print(f"  Images: {len(images)}")
    if config.get("style_prefix"):
        print(f"  Style prefix: {config['style_prefix'][:60]}...")
    if config.get("style_suffix"):
        print(f"  Style suffix: {config['style_suffix'][:60]}...")

    # ── Single image mode ──
    if args.id:
        if args.id not in images:
            print(f"\nERROR: Unknown image ID '{args.id}'")
            print(f"Valid IDs: {', '.join(list(images.keys())[:20])}")
            if len(images) > 20:
                print(f"  ... and {len(images) - 20} more")
            sys.exit(1)
        generate_image(args.id, images[args.id], config, output_dir,
                       cli_settings, dry_run=args.dry_run)
        return

    # ── Generate all ──
    total = len(images)
    generated = 0
    skipped = 0
    failed = 0

    for i, (img_id, img_data) in enumerate(images.items()):
        print(f"\n[{i+1}/{total}]", end="")

        # Check if exists
        out_fmt = img_data.get("output_format",
                  config.get("settings", {}).get("output_format",
                  cli_settings.get("output_format", DEFAULT_FORMAT)))
        filename = img_data.get("filename") or img_data.get("name") or f"{img_id}.{out_fmt}"
        if not Path(filename).suffix:
            filename = f"{filename}.{out_fmt}"
        img_path = output_dir / filename
        if img_path.exists():
            print(f"  [{img_id}] Already exists — skipping")
            skipped += 1
            continue

        # Retry with backoff
        success = False
        for attempt in range(args.retries):
            try:
                result = generate_image(img_id, img_data, config, output_dir,
                                        cli_settings, dry_run=args.dry_run)
                if result or args.dry_run:
                    generated += 1
                    success = True
                    break
            except Exception:
                pass

            if attempt < args.retries - 1:
                wait = 10 * (attempt + 1)
                print(f"  Retrying in {wait}s (attempt {attempt+2}/{args.retries})...")
                time.sleep(wait)

        if not success:
            failed += 1
            print(f"  [{img_id}] FAILED after {args.retries} attempts")

        # Rate limit delay between calls
        if i < total - 1 and not args.dry_run:
            time.sleep(args.delay)

    print(f"\n{'='*60}")
    print(f"  DONE!")
    print(f"{'='*60}")
    print(f"  Generated: {generated}")
    print(f"  Skipped:   {skipped}")
    print(f"  Failed:    {failed}")
    print(f"  Output:    {output_dir}")
    print()


if __name__ == "__main__":
    main()
