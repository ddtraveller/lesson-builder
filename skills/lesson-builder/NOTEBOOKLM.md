# NotebookLM Setup Guide

When the user chooses NotebookLM (or a config has `notebooklm: true`), run this setup sequence:

## 1. Check if notebooklm-py is installed
```bash
pip show notebooklm-py 2>&1
```
If not found, install it:
```bash
pip install notebooklm-py
```

## 2. Check authentication (use PYTHONIOENCODING=utf-8 on Windows to avoid encoding crashes)
```bash
PYTHONIOENCODING=utf-8 python -m notebooklm auth check --test --json
```

Parse the JSON result:
- If `checks.token_fetch` is `true` → auth is good, proceed
- If `checks.token_fetch` is `false` or `null` → auth expired or missing

## 3. If auth is expired/missing, guide the user through login

**CRITICAL: The login command is INTERACTIVE — it requires the user to press ENTER after signing in.** You CANNOT run it from the Bash tool (it will abort because there's no stdin). The user MUST run it themselves using the `!` prefix in the Claude Code prompt.

Tell the user:
> NotebookLM needs to authenticate with your Google account. Please run this command:
> ```
> ! python -m notebooklm login
> ```
> A browser window will open. Sign in with your Google account, wait until you see the NotebookLM homepage, then press ENTER in the terminal to save.

**Troubleshooting sequence** (go through these in order if the browser doesn't open):

1. **Install Chromium first** (most common fix):
   > ```
   > ! python -m playwright install chromium
   > ```
   > Then retry `! python -m notebooklm login`

2. **Delete stale auth** (if browser opens but login fails):
   > ```
   > ! del %USERPROFILE%\.notebooklm\storage_state.json
   > ! python -m notebooklm login
   > ```
   > (Mac/Linux: `rm ~/.notebooklm/storage_state.json`)

3. **Full reset** (nuclear option — delete auth + reinstall browser):
   > ```
   > ! del %USERPROFILE%\.notebooklm\storage_state.json
   > ! python -m playwright install chromium
   > ! python -m notebooklm login
   > ```

4. **Use the helper script** (if `notebooklm login` still won't open a browser):
   The `! python -m notebooklm login` command sometimes fails to launch a visible browser window on Windows. Use the helper script instead:
   > ```
   > ! python notebooklm_login.py
   > ```
   This script (`notebooklm_login.py` in the watdonchan project root) launches Chromium directly via playwright, navigates to NotebookLM, waits for user login, then saves auth state to the same location as `notebooklm login`.

**Key gotchas learned from experience:**
- The Bash tool CANNOT run `notebooklm login` — it's interactive (waits for ENTER). Always tell the user to use `!` prefix
- `! python -m notebooklm login` sometimes fails to open a browser window on Windows even with playwright installed. Use `! python notebooklm_login.py` as a reliable fallback
- The "Chromium pre-flight check failed" warning is normal if playwright wasn't installed — install it with `playwright install chromium`
- Auth expires frequently (every few days). If `token_fetch` is `false`, the user needs to re-login
- On Windows, the browser profile is stored at `%USERPROFILE%\.notebooklm\browser_profile\`
- Auth state is saved to `%USERPROFILE%\.notebooklm\storage_state.json`

## 4. Verify auth works after login
```bash
PYTHONIOENCODING=utf-8 python -m notebooklm auth check --test --json
```
Check that `checks.token_fetch` is `true`. If so, auth is confirmed.

Alternatively, create a test notebook:
```bash
PYTHONIOENCODING=utf-8 python -m notebooklm create "test" --json
```
If this succeeds (returns a notebook ID), delete the test notebook:
```bash
PYTHONIOENCODING=utf-8 python -m notebooklm notebook delete <id>
```

## 5. If auth cannot be established, offer fallback
Tell the user: *"NotebookLM authentication couldn't be set up. Would you like to fall back to web search or training data instead?"*

**IMPORTANT Windows note:** Always prefix notebooklm commands with `PYTHONIOENCODING=utf-8` when running via Bash tool. The CLI uses the `rich` library which crashes on Windows cp1252 encoding when outputting unicode characters (checkmarks, tables). The `--json` flag also helps avoid this, but set the env var as a safety measure.
