#!/usr/bin/env python3
"""
notebooklm_login.py — Manual NotebookLM login helper.

Workaround for when `python -m notebooklm login` fails to open a browser.
Launches Chromium via playwright directly, navigates to NotebookLM,
polls for Google session cookies, then auto-saves the auth state.

No keyboard input required — works under TTY-less invocations like Claude
Code's `!` prefix. The script polls every 2 seconds for the presence of
Google's `SID` cookie (set after successful sign-in) and saves automatically.

Usage:
    python notebooklm_login.py [--timeout 300]
    # or from Claude Code:
    ! python notebooklm_login.py
"""
import argparse
import json
import platform
import sys
import time
from pathlib import Path


def get_storage_path():
    home = Path.home()
    return home / ".notebooklm" / "storage_state.json"


def get_browser_profile_dir():
    home = Path.home()
    return home / ".notebooklm" / "browser_profile"


def has_google_session(context):
    """Return True if Google's session cookies are present (post-login).

    Google sets `SID` and `__Secure-1PSID` after successful Google account sign-in.
    `__Secure-1PSID` is the most reliable indicator on the .google.com domain.
    """
    try:
        cookies = context.cookies()
    except Exception:
        return False
    names = {c.get("name") for c in cookies if ".google.com" in c.get("domain", "")}
    return "__Secure-1PSID" in names or ("SID" in names and "HSID" in names)


def main():
    parser = argparse.ArgumentParser(description="NotebookLM login helper (no keyboard input required).")
    parser.add_argument("--timeout", type=int, default=300, help="Max seconds to wait for login (default: 300)")
    parser.add_argument("--poll-interval", type=float, default=2.0, help="Seconds between auth checks (default: 2.0)")
    args = parser.parse_args()

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
        # Use domcontentloaded (fires once HTML parses) rather than the default
        # "load" event — NotebookLM is a heavy SPA whose full load can exceed
        # 30s and the browser-visible page is usable long before then. Wrap in
        # try/except so even a navigation timeout doesn't abort: the polling
        # loop below is what actually matters, and the user can sign in
        # regardless of whether this goto fully resolves.
        try:
            page.goto("https://notebooklm.google.com/", wait_until="domcontentloaded", timeout=60000)
            print("  [OK] Browser navigated to NotebookLM", flush=True)
        except Exception as e:
            print(f"  [WARN] Initial goto did not fully resolve: {e}", flush=True)
            print("  Browser is still open — proceed with sign-in anyway", flush=True)

        print("Instructions:")
        print("  1. Sign in with your Google account in the browser window")
        print("  2. Wait until you see the NotebookLM homepage")
        print(f"  3. Auth state will save automatically (polling every {args.poll_interval}s)")
        print(f"  4. Will time out after {args.timeout}s if you don't log in")
        print()

        # Helper: write storage state to disk with explicit error reporting
        def save_storage(label):
            try:
                state = context.storage_state()
                with open(storage_path, "w", encoding="utf-8") as f:
                    json.dump(state, f, indent=2)
                size = storage_path.stat().st_size
                cookie_count = len(state.get("cookies", []))
                print(f"  [SAVED:{label}] {storage_path} ({size} bytes, {cookie_count} cookies)", flush=True)
                return True
            except Exception as e:
                print(f"  [SAVE FAILED:{label}] {e}", flush=True)
                return False

        # Poll for the presence of Google's session cookies
        start = time.time()
        last_print = 0
        while True:
            elapsed = time.time() - start
            if has_google_session(context):
                print(f"\n[OK] Google session detected after {elapsed:.1f}s — saving immediately...", flush=True)
                break
            if elapsed > args.timeout:
                print(f"\n[TIMEOUT] No login detected after {args.timeout}s. Aborting.", flush=True)
                context.close()
                sys.exit(2)
            # Print a heartbeat every 10s
            if elapsed - last_print >= 10:
                print(f"  Still waiting for login... ({int(elapsed)}s elapsed)", flush=True)
                last_print = elapsed
            time.sleep(args.poll_interval)

        # IMMEDIATE first save — capture state the moment we detect cookies, BEFORE
        # any navigation that might hang or fail. This is the critical save: even if
        # everything below fails, we already have a valid auth file on disk.
        immediate_ok = save_storage("immediate")

        # Navigate to NotebookLM to ensure all NotebookLM-specific cookies are set,
        # then save AGAIN as a sanity check with the warmed-up cookie set.
        try:
            page.goto("https://notebooklm.google.com/", timeout=20000)
            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                pass  # Tolerate networkidle hangs; cookies are what matter
            save_storage("post-nav")
        except Exception as e:
            print(f"  [WARN] Post-navigation save skipped: {e}", flush=True)

        context.close()

        if not immediate_ok:
            print(f"\n[ERROR] Auth state was NOT saved to {storage_path}.", flush=True)
            print("Check the file path and disk permissions, then retry.", flush=True)
            sys.exit(3)

    # Verify the file actually exists on disk before claiming success
    if not storage_path.exists():
        print(f"\n[ERROR] {storage_path} does not exist after save. Login failed.", flush=True)
        sys.exit(4)

    final_size = storage_path.stat().st_size
    print(f"\n[SUCCESS] Auth state written to: {storage_path}", flush=True)
    print(f"          File size: {final_size} bytes", flush=True)
    print("          Verify with:", flush=True)
    print("            PYTHONIOENCODING=utf-8 python -m notebooklm auth check --test --json", flush=True)


if __name__ == "__main__":
    main()
