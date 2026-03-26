#!/usr/bin/env python3
"""
notebooklm_login.py — Manual NotebookLM login helper.

Workaround for when `python -m notebooklm login` fails to open a browser.
Launches Chromium via playwright directly, navigates to NotebookLM,
waits for user to sign in, then saves the auth state.

Usage:
    python notebooklm_login.py
    # or from Claude Code:
    ! python notebooklm_login.py
"""
import json
import platform
import sys
from pathlib import Path


def get_storage_path():
    home = Path.home()
    return home / ".notebooklm" / "storage_state.json"


def get_browser_profile_dir():
    home = Path.home()
    return home / ".notebooklm" / "browser_profile"


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright not installed. Run:")
        print("  pip install playwright")
        print("  python -m playwright install chromium")
        sys.exit(1)

    # Windows event loop fix
    if platform.system() == "Windows":
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    storage_path = get_storage_path()
    browser_profile = get_browser_profile_dir()
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    browser_profile.mkdir(parents=True, exist_ok=True)

    print("Opening browser to NotebookLM...")
    print(f"Profile: {browser_profile}")
    print()

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(browser_profile),
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--password-store=basic",
            ],
            ignore_default_args=["--enable-automation"],
        )

        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://notebooklm.google.com/")

        print("Instructions:")
        print("  1. Sign in with your Google account in the browser")
        print("  2. Wait until you see the NotebookLM homepage")
        print("  3. Press ENTER here to save and close")
        print()

        input("[Press ENTER when logged in] ")

        # Navigate to ensure cookies are set
        page.goto("https://notebooklm.google.com/")
        page.wait_for_load_state("load")

        # Save storage state
        state = context.storage_state()
        with open(storage_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

        context.close()

    print(f"\nAuth saved to: {storage_path}")
    print("You can now use NotebookLM commands.")


if __name__ == "__main__":
    main()
