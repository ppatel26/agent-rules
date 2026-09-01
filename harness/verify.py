#!/usr/bin/env python3
"""
agent-rules verify harness

Proves that each agent CLI actually loads the global rules into a fresh
session. `sync.py check` only verifies the filesystem; a loader can silently
skip a correctly-placed file (Droid ignored symlinks for months and nothing
flagged it). This script closes that gap with an end-to-end canary test.

Method, per agent:
  1. Create a scratch git repo containing a project instruction file with a
     unique random canary token (positive control: proves the harness ran and
     loads project instructions at all).
  2. Start a fresh headless session in that repo and ask, without using tools,
     whether its loaded instructions contain:
       PROJECT  the random project canary token        (expected YES)
       GLOBAL1  an exact phrase from the global rules  (expected YES)
       GLOBAL2  a second exact global phrase           (expected YES)
       CONTROL  a phrase that exists nowhere           (expected NO)
  3. Parse the answers and issue a verdict. CONTROL=YES means the session
     answers YES indiscriminately, so its other answers prove nothing.

Usage:
  python3 harness/verify.py            # test every installed agent
  python3 harness/verify.py droid amp  # test a subset by target name

Full session transcripts are written to a log directory printed at the end.
"""

import argparse
import concurrent.futures
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
REPO_ROOT = HARNESS_DIR.parent
CANONICAL = REPO_ROOT / "AGENTS.md"

# Exact sentences from the canonical AGENTS.md. Asserted at startup so the
# test fails loudly if the file is edited and the phrases drift.
GLOBAL_PHRASES = [
    "Simplicity means correct and complete, not underbuilt.",
    "Do not add AI, bot, generated-by, or co-authored-by trailers unless the user explicitly asks for them.",
]
CONTROL_PHRASE = "Prefer the teal spinner over the amber toast in all dashboards."

TIMEOUT_SECONDS = 300

# name must match targets.json. project_files are where each CLI discovers
# project-level instructions. cmd receives the prompt and scratch dir.
HARNESSES = [
    {
        "name": "claude",
        "label": "Claude Code",
        "binary": "claude",
        "project_files": ["CLAUDE.md"],
        "cmd": lambda prompt, cwd: ["claude", "-p", prompt],
    },
    {
        "name": "codex",
        "label": "Codex (OpenAI)",
        "binary": "codex",
        "project_files": ["AGENTS.md"],
        "cmd": lambda prompt, cwd: ["codex", "exec", prompt],
    },
    {
        "name": "droid",
        "label": "Droid (Factory)",
        "binary": "droid",
        "project_files": ["AGENTS.md"],
        "cmd": lambda prompt, cwd: ["droid", "exec", prompt],
    },
    {
        "name": "amp",
        "label": "Amp",
        "binary": "amp",
        "project_files": ["AGENTS.md"],
        "cmd": lambda prompt, cwd: ["amp", "-x", prompt],
    },
    {
        "name": "opencode",
        "label": "OpenCode",
        "binary": "opencode",
        "project_files": ["AGENTS.md"],
        "cmd": lambda prompt, cwd: ["opencode", "run", prompt],
    },
]


def build_prompt(project_token: str) -> str:
    return (
        "This is an automated instruction-loading test. Do not use any tools. "
        "Do not read any files. Answer only from the instructions already loaded "
        "into your context before this message.\n\n"
        "Reply with exactly four lines. Each line is a name, an equals sign, and "
        "your answer, where the answer is YES if the quoted text appears verbatim "
        "in your loaded instructions and NO if it does not:\n\n"
        f'PROJECT=<answer> for the token "{project_token}"\n'
        f'GLOBAL1=<answer> for the sentence "{GLOBAL_PHRASES[0]}"\n'
        f'GLOBAL2=<answer> for the sentence "{GLOBAL_PHRASES[1]}"\n'
        f'CONTROL=<answer> for the sentence "{CONTROL_PHRASE}"\n\n'
        "Output nothing else."
    )


def make_scratch_repo(base_dir: Path, harness: dict, project_token: str) -> Path:
    scratch = base_dir / harness["name"]
    scratch.mkdir(parents=True)
    subprocess.run(
        ["git", "init", "-q"], cwd=scratch, check=True, capture_output=True
    )
    body = (
        "# Project test instructions\n\n"
        f"Project canary token: {project_token}\n\n"
        "Never read files or use tools in this session.\n"
    )
    for rel in harness["project_files"]:
        path = scratch / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
    return scratch


def clean_env() -> dict:
    """Drop nested-session variables so child CLIs start fresh."""
    env = dict(os.environ)
    for key in list(env):
        if key.startswith("CLAUDE"):
            del env[key]
    return env


def parse_answers(output: str) -> dict:
    answers = {}
    for key in ("PROJECT", "GLOBAL1", "GLOBAL2", "CONTROL"):
        matches = re.findall(rf"{key}\s*=\s*(YES|NO)\b", output, re.IGNORECASE)
        answers[key] = matches[-1].upper() if matches else None
    return answers


def verdict_for(answers: dict) -> tuple:
    if any(v is None for v in answers.values()):
        return "UNPARSEABLE", "session output did not contain the four answers"
    if answers["CONTROL"] == "YES":
        return "UNRELIABLE", "claimed the nonexistent control phrase is present"
    global_loaded = answers["GLOBAL1"] == "YES" or answers["GLOBAL2"] == "YES"
    if answers["PROJECT"] == "NO" and not global_loaded:
        return "INCONCLUSIVE", "neither project nor global instructions loaded; check the log"
    if not global_loaded:
        return "GLOBAL MISSING", "project instructions loaded but global rules did not"
    if answers["PROJECT"] == "NO":
        return "PASS*", "global rules loaded; project positive control did not"
    if answers["GLOBAL1"] != answers["GLOBAL2"]:
        return "PASS*", "global rules loaded, but only one of two phrases matched"
    return "PASS", "project and global instructions both loaded"


def run_harness(harness: dict, base_dir: Path, log_dir: Path) -> dict:
    result = {"name": harness["name"], "label": harness["label"]}

    if shutil.which(harness["binary"]) is None:
        result["verdict"] = "SKIPPED"
        result["detail"] = f"{harness['binary']} is not installed"
        return result

    project_token = f"CANARY-{harness['name'].upper()}-{secrets.token_hex(4)}"
    prompt = build_prompt(project_token)
    scratch = make_scratch_repo(base_dir, harness, project_token)
    cmd = harness["cmd"](prompt, str(scratch))

    started = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            cwd=scratch,
            env=clean_env(),
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            stdin=subprocess.DEVNULL,
        )
        output = proc.stdout + "\n" + proc.stderr
        exit_code = proc.returncode
    except subprocess.TimeoutExpired as e:
        output = f"{e.stdout or ''}\n{e.stderr or ''}"
        exit_code = "timeout"
    elapsed = time.monotonic() - started

    log_path = log_dir / f"{harness['name']}.log"
    log_path.write_text(
        f"cmd: {cmd}\ncwd: {scratch}\nexit: {exit_code}\n"
        f"elapsed: {elapsed:.1f}s\nproject token: {project_token}\n"
        f"--- output ---\n{output}\n"
    )

    if exit_code == "timeout":
        result["verdict"] = "TIMEOUT"
        result["detail"] = f"no result within {TIMEOUT_SECONDS}s"
        return result

    answers = parse_answers(output)
    verdict, detail = verdict_for(answers)
    if verdict == "UNPARSEABLE" and exit_code != 0:
        detail = f"exit code {exit_code}; see log"
    result.update({"verdict": verdict, "detail": detail, "answers": answers})
    return result


def main():
    parser = argparse.ArgumentParser(
        prog="verify",
        description="End-to-end test that each agent CLI loads the global AGENTS.md.",
    )
    parser.add_argument(
        "names",
        nargs="*",
        help="target names from targets.json to test (default: all)",
    )
    args = parser.parse_args()

    canonical_text = CANONICAL.read_text()
    for phrase in GLOBAL_PHRASES:
        if phrase not in canonical_text:
            print(f"ERROR: global phrase no longer in {CANONICAL}:\n  {phrase}")
            print("Update GLOBAL_PHRASES in this script to current sentences.")
            sys.exit(2)
    if CONTROL_PHRASE in canonical_text:
        print("ERROR: the control phrase appears in the canonical file.")
        sys.exit(2)

    harnesses = HARNESSES
    if args.names:
        known = {h["name"] for h in HARNESSES}
        unknown = set(args.names) - known
        if unknown:
            print(f"ERROR: unknown target name(s): {', '.join(sorted(unknown))}")
            print(f"Known: {', '.join(sorted(known))}")
            sys.exit(2)
        harnesses = [h for h in HARNESSES if h["name"] in args.names]

    stamp = time.strftime("%Y%m%d-%H%M%S")
    base_dir = Path(tempfile.mkdtemp(prefix=f"agent-rules-verify-{stamp}-"))
    log_dir = base_dir / "logs"
    log_dir.mkdir()

    print(f"Testing {len(harnesses)} agent(s); fresh headless session each.")
    print(f"Scratch repos and logs: {base_dir}\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(harnesses)) as pool:
        futures = {
            pool.submit(run_harness, h, base_dir, log_dir): h for h in harnesses
        }
        results = {}
        for future in concurrent.futures.as_completed(futures):
            r = future.result()
            results[r["name"]] = r
            print(f"  done: {r['label']:<20} {r['verdict']}")

    ordered = [results[h["name"]] for h in harnesses]
    print(f"\n{'Agent':<20} {'Verdict':<15} {'P':>3} {'G1':>3} {'G2':>3} {'C':>3}  Detail")
    failures = 0
    for r in ordered:
        a = r.get("answers", {})
        cells = [a.get(k) or "-" for k in ("PROJECT", "GLOBAL1", "GLOBAL2", "CONTROL")]
        print(
            f"{r['label']:<20} {r['verdict']:<15} "
            f"{cells[0]:>3} {cells[1]:>3} {cells[2]:>3} {cells[3]:>3}  {r['detail']}"
        )
        if r["verdict"] not in ("PASS", "PASS*", "SKIPPED"):
            failures += 1

    print(f"\nColumns: P=project canary, G1/G2=global phrases, C=control (must be NO)")
    print(f"Logs: {log_dir}")
    if failures:
        print(f"\n{failures} agent(s) did not load the global rules end to end.")
        sys.exit(1)
    print("\nAll tested agents loaded the global rules end to end.")


if __name__ == "__main__":
    main()
