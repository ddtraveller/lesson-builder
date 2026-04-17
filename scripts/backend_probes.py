#!/usr/bin/env python3
"""backend_probes.py — availability probes for all AI/media backends used by lesson-builder.

Each probe returns a (available: bool, reason: str) tuple.

Probes:
  probe_node()       — Node.js on PATH (shared with check_pages.py)
  probe_tavily()     — tvly CLI authenticated
  probe_notebooklm() — notebooklm-py authenticated
  probe_flux()       — REPLICATE_API_TOKEN in env or .env
  probe_heygen()     — heygen SSM parameter retrievable via AWS deploy profile
  probe_remotion()   — watdonchan/ai-english-video Remotion project present
  probe_capcut()     — always available (prompt-to-human workflow)
  probe_webm()       — NOT YET IMPLEMENTED (returns False)

Usage as a script (smoke-test all probes):
  python scripts/backend_probes.py

Import in other scripts:
  from scripts.backend_probes import probe_heygen, probe_flux
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# probe_node — shared with check_pages.py
# ---------------------------------------------------------------------------

def probe_node() -> tuple[bool, str]:
    """Return (True, version_string) if node is on PATH, else (False, reason)."""
    if shutil.which("node") is None:
        return False, "node not found on PATH"
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, f"node --version exited {result.returncode}"
    except Exception as exc:
        return False, f"node probe error: {exc}"


# ---------------------------------------------------------------------------
# probe_tavily
# ---------------------------------------------------------------------------

def probe_tavily() -> tuple[bool, str]:
    """Return (True, reason) if tvly CLI is on PATH and authenticated."""
    if shutil.which("tvly") is None:
        return False, "tvly CLI not found on PATH"
    try:
        result = subprocess.run(
            ["tvly", "auth", "--json"],
            capture_output=True, text=True, timeout=10,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"}
        )
        output = result.stdout.strip() or result.stderr.strip()
        try:
            data = json.loads(output)
            if data.get("authenticated"):
                return True, f"tavily authenticated via {data.get('source', 'config')}"
            return False, f"tavily not authenticated: {data}"
        except json.JSONDecodeError:
            # Non-JSON output — check exit code as fallback
            if result.returncode == 0:
                return True, "tvly auth exited 0 (non-JSON output)"
            return False, f"tvly auth failed: {output[:120]}"
    except subprocess.TimeoutExpired:
        return False, "tvly auth timed out"
    except Exception as exc:
        return False, f"tavily probe error: {exc}"


# ---------------------------------------------------------------------------
# probe_notebooklm
# ---------------------------------------------------------------------------

def probe_notebooklm() -> tuple[bool, str]:
    """Return (True, reason) if notebooklm-py is installed and authenticated."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "notebooklm", "auth", "check", "--test", "--json"],
            capture_output=True, text=True, timeout=15,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"}
        )
        output = result.stdout.strip() or result.stderr.strip()
        try:
            data = json.loads(output)
            if data.get("checks", {}).get("token_fetch") is True:
                return True, "notebooklm authenticated (token_fetch=true)"
            return False, f"notebooklm auth check failed: {data}"
        except json.JSONDecodeError:
            if result.returncode == 0:
                return True, "notebooklm auth check exited 0"
            return False, f"notebooklm not available: {output[:120]}"
    except subprocess.TimeoutExpired:
        return False, "notebooklm auth check timed out"
    except Exception as exc:
        return False, f"notebooklm probe error: {exc}"


# ---------------------------------------------------------------------------
# probe_flux (Replicate API token)
# ---------------------------------------------------------------------------

def probe_flux() -> tuple[bool, str]:
    """Return (True, reason) if REPLICATE_API_TOKEN is present in env or .env."""
    # Check environment first
    token = os.environ.get("REPLICATE_API_TOKEN", "")
    if token and token.startswith("r8_"):
        return True, "REPLICATE_API_TOKEN found in environment"

    # Check .env file in cwd or project root
    for dotenv_path in [Path(".env"), Path(__file__).parent.parent / ".env"]:
        if dotenv_path.exists():
            try:
                content = dotenv_path.read_text(encoding="utf-8")
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith("REPLICATE_API_TOKEN="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val.startswith("r8_"):
                            return True, f"REPLICATE_API_TOKEN found in {dotenv_path}"
            except Exception:
                pass

    return False, "REPLICATE_API_TOKEN not found in environment or .env"


# ---------------------------------------------------------------------------
# probe_heygen (AWS SSM Parameter Store)
# ---------------------------------------------------------------------------

def probe_heygen() -> tuple[bool, str]:
    """Return (True, reason) if the HeyGen API key is retrievable from SSM."""
    if shutil.which("aws") is None:
        return False, "aws CLI not found on PATH"
    try:
        result = subprocess.run(
            [
                "aws", "ssm", "get-parameter",
                "--name", "heygen",
                "--with-decryption",
                "--profile", "deploy",
                "--region", "us-west-2",
                "--query", "Parameter.Value",
                "--output", "text",
            ],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            value = result.stdout.strip()
            if value:
                return True, "HeyGen SSM parameter retrieved successfully"
            return False, "HeyGen SSM parameter returned empty value"
        return False, f"aws ssm get-parameter failed (exit {result.returncode}): {result.stderr.strip()[:120]}"
    except subprocess.TimeoutExpired:
        return False, "aws SSM probe timed out"
    except Exception as exc:
        return False, f"heygen probe error: {exc}"


# ---------------------------------------------------------------------------
# probe_remotion
# ---------------------------------------------------------------------------

def probe_remotion(project_dir: str = "../watdonchan/ai-english-video") -> tuple[bool, str]:
    """Return (True, reason) if the Remotion project exists with node_modules."""
    base = Path(__file__).parent.parent  # lesson-builder root
    # Resolve relative to lesson-builder root OR as an absolute path
    candidate = base / project_dir
    if not candidate.exists():
        # Try as-is (could be absolute)
        candidate = Path(project_dir)

    if not candidate.exists():
        return False, f"Remotion project directory not found: {project_dir}"
    if not (candidate / "package.json").exists():
        return False, f"Remotion project missing package.json at {candidate}"
    remotion_module = candidate / "node_modules" / "remotion"
    if not remotion_module.exists():
        return False, f"Remotion not installed: {remotion_module} not found (run npm install)"
    return True, f"Remotion project found at {candidate}"


# ---------------------------------------------------------------------------
# probe_capcut — always available (manual workflow)
# ---------------------------------------------------------------------------

def probe_capcut() -> tuple[bool, str]:
    """CapCut is a prompt-to-human workflow; always returns available."""
    return True, "prompt-to-human workflow; no runtime check required"


# ---------------------------------------------------------------------------
# probe_webm — NOT YET IMPLEMENTED
# ---------------------------------------------------------------------------

def probe_webm() -> tuple[bool, str]:
    """webm pipeline is not yet implemented in this skill."""
    return False, "webm pipeline is not yet implemented in this skill"


# ---------------------------------------------------------------------------
# Smoke-test all probes when run as a script
# ---------------------------------------------------------------------------

ALL_PROBES = [
    ("node",        probe_node),
    ("tavily",      probe_tavily),
    ("notebooklm",  probe_notebooklm),
    ("flux",        probe_flux),
    ("heygen",      probe_heygen),
    ("remotion",    probe_remotion),
    ("capcut",      probe_capcut),
    ("webm",        probe_webm),
]


def main() -> int:
    print("backend_probes.py — availability check for all lesson-builder backends\n")
    max_name = max(len(name) for name, _ in ALL_PROBES)
    results = []
    for name, fn in ALL_PROBES:
        available, reason = fn()
        status = "OK  " if available else "SKIP"
        print(f"  [{status}] {name:<{max_name}}  {reason}")
        results.append(available)
    print()
    ok_count = sum(results)
    print(f"{ok_count}/{len(results)} backends available")
    return 0


if __name__ == "__main__":
    sys.exit(main())
