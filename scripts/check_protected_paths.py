#!/usr/bin/env python3
"""Fail if a git branch changes protected paths relative to a base ref.

Protected (agent branches must not touch):
  - .github/**
  - framework/**
  - FRAMEWORK_VERSION
  - team/roles/_base/**
  - scripts/check_protected_paths.py
  - scripts/validate_repo.py
  - scripts/wake_check.py
    (gate scripts: once landed on main they would police future merges / wakes)

Rename-aware: uses `git diff --name-status --no-renames` so a protected file
moved to an unprotected path still fails (delete + add both listed).

Usage:
  python scripts/check_protected_paths.py --base origin/main --head origin/claude/abc
  python scripts/check_protected_paths.py --files path1 path2   # for tests
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


PROTECTED_EXACT = frozenset(
    {
        "FRAMEWORK_VERSION",
        "scripts/check_protected_paths.py",
        "scripts/validate_repo.py",
        "scripts/wake_check.py",
    }
)
PROTECTED_PREFIXES = (
    ".github/",
    "framework/",
    "team/roles/_base/",
)


def is_protected(path: str) -> bool:
    norm = path.replace("\\", "/")
    while norm.startswith("./"):
        norm = norm[2:]
    if norm in PROTECTED_EXACT:
        return True
    return any(norm == p.rstrip("/") or norm.startswith(p) for p in PROTECTED_PREFIXES)


def protected_hits(paths: list[str]) -> list[str]:
    return sorted({p for p in paths if p and is_protected(p)})


def list_changed_files(base: str, head: str, repo: Path) -> list[str]:
    """Return all touched paths, including rename sources (via --no-renames)."""
    proc = subprocess.run(
        ["git", "diff", "--name-status", "--no-renames", f"{base}...{head}"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "git diff failed")
    paths: list[str] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        # Formats: "M\tpath", "A\tpath", "D\tpath", "C100\told\tnew", etc.
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        # status is parts[0]; remaining are paths
        for p in parts[1:]:
            p = p.strip()
            if p:
                paths.append(p)
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guard protected paths on agent branches")
    parser.add_argument("--base", help="Base git ref (e.g. origin/main)")
    parser.add_argument("--head", help="Head git ref (e.g. origin/claude/xyz)")
    parser.add_argument("--root", type=Path, default=Path("."), help="Repo root for git commands")
    parser.add_argument(
        "--files",
        nargs="*",
        default=None,
        help="Explicit file list (skips git); for unit tests",
    )
    args = parser.parse_args(argv)

    if args.files is not None:
        paths = list(args.files)
    else:
        if not args.base or not args.head:
            print("error: --base and --head are required unless --files is used", file=sys.stderr)
            return 2
        try:
            paths = list_changed_files(args.base, args.head, args.root.resolve())
        except RuntimeError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    hits = protected_hits(paths)
    if hits:
        print("Protected paths changed (merge blocked):", file=sys.stderr)
        for h in hits:
            print(f"  - {h}", file=sys.stderr)
        return 1
    print("check_protected_paths: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
