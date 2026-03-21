#!/usr/bin/env python3
"""
agent-rules sync harness

Commands:
  sync      Create/fix symlinks so all agents read the canonical AGENTS.md
  check     Report whether each target is correctly linked (no changes)
  dry-run   Show what sync would do without touching the filesystem
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
REPO_ROOT = HARNESS_DIR.parent
TARGETS_FILE = HARNESS_DIR / "targets.json"


def load_targets():
    with open(TARGETS_FILE) as f:
        data = json.load(f)
    canonical = REPO_ROOT / data["canonical"]
    return canonical, data["targets"]


def expand(p: str) -> Path:
    return Path(os.path.expanduser(p))


def status_for(target: dict, canonical: Path) -> dict:
    link = expand(target["link_path"])
    result = {
        "name": target["name"],
        "label": target["label"],
        "link": str(link),
        "canonical": str(canonical),
    }

    if not link.exists() and not link.is_symlink():
        result["status"] = "missing"
        result["detail"] = "does not exist"
        return result

    if link.is_symlink():
        dest = link.resolve()
        if dest == canonical.resolve():
            result["status"] = "ok"
            result["detail"] = f"symlink -> {canonical}"
        else:
            result["status"] = "wrong_target"
            result["detail"] = f"symlink -> {dest} (expected {canonical})"
        return result

    result["status"] = "regular_file"
    result["detail"] = "exists as regular file, not a symlink"
    return result


def print_status(s: dict, prefix: str = ""):
    icons = {"ok": "OK", "missing": "MISSING", "wrong_target": "WRONG", "regular_file": "FILE"}
    tag = icons.get(s["status"], s["status"].upper())
    print(f"  {prefix}[{tag:>7}]  {s['label']:<20}  {s['link']}")
    if s["status"] != "ok":
        print(f"           {'':20}  {s['detail']}")


def cmd_check(args):
    canonical, targets = load_targets()
    if not canonical.exists():
        print(f"ERROR: canonical file not found: {canonical}")
        sys.exit(1)

    all_ok = True
    print(f"Canonical: {canonical}\n")
    for t in targets:
        s = status_for(t, canonical)
        print_status(s)
        if s["status"] != "ok":
            all_ok = False

    print()
    if all_ok:
        print("All targets are correctly linked.")
    else:
        print("Some targets need attention. Run 'sync' to fix.")
        sys.exit(1)


def cmd_dryrun(args):
    canonical, targets = load_targets()
    if not canonical.exists():
        print(f"ERROR: canonical file not found: {canonical}")
        sys.exit(1)

    print(f"Canonical: {canonical}\n")
    print("Dry run -- no changes will be made:\n")
    changes = 0
    for t in targets:
        s = status_for(t, canonical)
        link = expand(t["link_path"])

        if s["status"] == "ok":
            print(f"  [  SKIP]  {t['label']:<20}  already correct")
            continue

        changes += 1
        if s["status"] == "missing":
            parent = link.parent
            if not parent.exists():
                print(f"  [MKDIR ]  {t['label']:<20}  create {parent}")
            print(f"  [ LINK ]  {t['label']:<20}  {link} -> {canonical}")

        elif s["status"] == "regular_file":
            backup = link.with_suffix(link.suffix + ".bak")
            print(f"  [BACKUP]  {t['label']:<20}  {link} -> {backup}")
            print(f"  [ LINK ]  {t['label']:<20}  {link} -> {canonical}")

        elif s["status"] == "wrong_target":
            print(f"  [RELINK]  {t['label']:<20}  {link} -> {canonical}")

    print()
    if changes == 0:
        print("Nothing to do.")
    else:
        print(f"{changes} target(s) would be changed. Run 'sync' to apply.")


def cmd_sync(args):
    canonical, targets = load_targets()
    if not canonical.exists():
        print(f"ERROR: canonical file not found: {canonical}")
        sys.exit(1)

    print(f"Canonical: {canonical}\n")
    changed = 0
    for t in targets:
        s = status_for(t, canonical)
        link = expand(t["link_path"])

        if s["status"] == "ok":
            print(f"  [  SKIP]  {t['label']:<20}  already correct")
            continue

        parent = link.parent
        if not parent.exists():
            parent.mkdir(parents=True, exist_ok=True)
            print(f"  [MKDIR ]  {t['label']:<20}  created {parent}")

        if s["status"] == "regular_file":
            backup = link.with_suffix(link.suffix + ".bak")
            shutil.move(str(link), str(backup))
            print(f"  [BACKUP]  {t['label']:<20}  {link} -> {backup}")

        if link.is_symlink():
            link.unlink()

        link.symlink_to(canonical)
        changed += 1
        print(f"  [ LINK ]  {t['label']:<20}  {link} -> {canonical}")

    print()
    if changed == 0:
        print("Everything was already in sync.")
    else:
        print(f"Synced {changed} target(s).")


def main():
    parser = argparse.ArgumentParser(
        prog="agent-rules",
        description="Sync a canonical AGENTS.md to all your coding agents.",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("sync", help="Create or fix symlinks for all targets")
    sub.add_parser("check", help="Verify all targets are correctly linked")
    sub.add_parser("dry-run", help="Show what sync would do without changes")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)

    cmds = {"sync": cmd_sync, "check": cmd_check, "dry-run": cmd_dryrun}
    cmds[args.command](args)


if __name__ == "__main__":
    main()
