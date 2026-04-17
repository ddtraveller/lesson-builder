# NotebookLM Query Patterns

## The single highest-leverage query tip

Phrase every question as:

> "What does [source] say about X?"

rather than "What is X?" or "Tell me about X". The source-attributed form forces
NotebookLM to pull from the uploaded corpus rather than answering from general
knowledge. Works for vocabulary pedagogy, grammar rule sourcing, CEFR mapping, etc.

**Examples:**
- "What does the Tavily TEFL research report say about vocabulary density for beginners?"
- "What does the Cambridge CEFR companion say about A1 grammar structures?"
- "What does the corpus say about common Thai learner errors with English articles?"

## Other effective patterns

- **Cross-source synthesis:** "What do [source A] and [source B] say together about X?"
- **Contrastive:** "How does [source] distinguish between X and Y?"
- **Evidence-gathering:** "What evidence does [source] give for claim X?"
- **Practical application:** "What does [source] recommend for teaching X to young learners?"

## Windows note

Always prefix notebooklm commands with `PYTHONIOENCODING=utf-8` to avoid cp1252
encoding crashes on Windows when the CLI outputs unicode characters:

```bash
PYTHONIOENCODING=utf-8 python -m notebooklm ask "What does the report say about X?"
```

---

## Appendix: Auth Troubleshooting

If `python -m notebooklm auth check --test --json` returns `token_fetch: false`:

**CRITICAL:** The login command is INTERACTIVE — requires user to press ENTER after
signing in. The Bash tool CANNOT run it. The user MUST run it with the `!` prefix:

```
! python -m notebooklm login
```

A browser opens. Sign in with Google, wait for the NotebookLM homepage, press ENTER.

**Troubleshooting sequence (try in order):**

1. **Install Chromium first** (most common fix):
   ```
   ! python -m playwright install chromium
   ```
   Then retry `! python -m notebooklm login`

2. **Delete stale auth** (browser opens but login fails):
   ```
   ! del %USERPROFILE%\.notebooklm\storage_state.json
   ! python -m notebooklm login
   ```
   Mac/Linux: `rm ~/.notebooklm/storage_state.json`

3. **Full reset** (nuclear option):
   ```
   ! del %USERPROFILE%\.notebooklm\storage_state.json
   ! python -m playwright install chromium
   ! python -m notebooklm login
   ```

4. **Use the helper script** (if login still won't open a browser on Windows):
   ```
   ! python notebooklm_login.py
   ```
   Launches Chromium directly via playwright, waits for login, saves auth state.

**Key gotchas:**
- Auth expires every few days — `token_fetch: false` means re-login
- Browser profile: `%USERPROFILE%\.notebooklm\browser_profile\`
- Auth state: `%USERPROFILE%\.notebooklm\storage_state.json`
- "Chromium pre-flight check failed" is normal if playwright not installed
