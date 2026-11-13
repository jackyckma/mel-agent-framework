#!/usr/bin/env python3
"""Cheap wake gate for scheduled agent runs (stdlib only).

Run AFTER `git fetch origin main` (+ rebase/ff onto origin/main), and BEFORE
reading process.md, role docs, or the mandate.

Usage:
  python scripts/wake_check.py <role-slug> [--root .]

Prints a first line of WORK or NOOP, then reason lines.
Exit codes: 0 = WORK, 1 = NOOP, 2 = usage/error.

Reads only:
  - agents/<folder-slug>/state.md (duties YAML)
  - a light scan of team/board/*.md (filename + status frontmatter)
  - for mel-lead / lead: remote origin/claude/* ages via git (optional)
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# Agent folder slug -> board from/to slug
FOLDER_TO_BOARD = {
    "mel-lead": "lead",
    "scout": "scout",
    "data-collector": "collector",
    "data-curator": "curator",
    "dashboard-analyst": "analyst",
    "narrative-designer": "narrative",
    "project-change-manager": "pcm",
    # allow board slugs passed directly
    "lead": "lead",
    "collector": "collector",
    "curator": "curator",
    "analyst": "analyst",
    "narrative": "narrative",
    "pcm": "pcm",
}

DUTIES_FENCE_RE = re.compile(
    r"```ya?ml\s*\n(?P<body>.*?duties\s*:.*?)\n```",
    re.DOTALL | re.IGNORECASE,
)
BOARD_NAME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}_[a-z0-9-]+-to-(?P<to>[a-z0-9-]+)_\d{3}-[a-z0-9-]+\.md$"
)
OPEN_STATUSES = {"open", "in-progress"}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_iso(ts: str | None) -> datetime | None:
    if not ts or ts in {"null", "None", "never", ""}:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


BOARD_TO_FOLDER = {
    "lead": "mel-lead",
    "scout": "scout",
    "collector": "data-collector",
    "curator": "data-curator",
    "analyst": "dashboard-analyst",
    "narrative": "narrative-designer",
    "pcm": "project-change-manager",
}


def folder_and_board(role_slug: str) -> tuple[str, str]:
    if role_slug in BOARD_TO_FOLDER:
        return BOARD_TO_FOLDER[role_slug], role_slug
    if role_slug in FOLDER_TO_BOARD:
        return role_slug, FOLDER_TO_BOARD[role_slug]
    raise ValueError(f"unknown role slug: {role_slug}")


def load_duties(state_text: str) -> list[dict[str, Any]]:
    """Parse duties from a ```yaml fence containing a top-level duties: list."""
    m = DUTIES_FENCE_RE.search(state_text)
    if not m:
        return []
    body = m.group("body")
    # Minimal YAML list parser for duties entries
    duties: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    in_duties = False
    for raw in body.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if re.match(r"^duties:\s*$", line.strip()):
            in_duties = True
            continue
        if not in_duties:
            continue
        m_item = re.match(r"^-\s+name:\s*(.+)$", line.strip()) or re.match(r"^-\s+name:\s*(.+)$", line)
        # allow indented "- name:"
        m_item = re.match(r"^\s*-\s+name:\s*(.+)$", line)
        if m_item:
            if current:
                duties.append(current)
            current = {"name": _scalar(m_item.group(1)), "cadence_hours": None, "last_done": None}
            continue
        m_key = re.match(r"^\s+([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$", line)
        if m_key and current is not None:
            key, val = m_key.group(1), _scalar(m_key.group(2))
            current[key] = val
    if current:
        duties.append(current)
    return duties


def _scalar(raw: str) -> Any:
    s = raw.strip().strip("\"'")
    if s in {"null", "Null", "~", ""}:
        return None
    if s in {"true", "True"}:
        return True
    if s in {"false", "False"}:
        return False
    try:
        if "." in s:
            return float(s)
        return int(s)
    except ValueError:
        return s


def duties_due(duties: list[dict[str, Any]], now: datetime | None = None) -> list[str]:
    now = now or utc_now()
    due: list[str] = []
    for d in duties:
        name = str(d.get("name") or "unnamed")
        cadence = d.get("cadence_hours")
        if cadence is None:
            continue
        try:
            hours = float(cadence)
        except (TypeError, ValueError):
            continue
        last = parse_iso(str(d["last_done"]) if d.get("last_done") is not None else None)
        if last is None or (now - last) >= timedelta(hours=hours):
            due.append(name)
    return due


def parse_frontmatter_status(text: str) -> str | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end]
    for line in block.splitlines():
        line = line.strip()
        if line.startswith("status:"):
            val = line.split(":", 1)[1].strip().split("#", 1)[0].strip().strip("\"'")
            return val
        if line.startswith("from:"):
            continue
        if line.startswith("type:"):
            continue
        if line.startswith("to:"):
            continue
    return None


def parse_frontmatter_fields(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    if not text.startswith("---"):
        return out
    end = text.find("\n---", 3)
    if end == -1:
        return out
    for line in text[3:end].splitlines():
        line = line.strip()
        if ":" not in line or line.startswith("#"):
            continue
        key, val = line.split(":", 1)
        out[key.strip()] = val.strip().split("#", 1)[0].strip().strip("\"'")
    return out


def board_messages_for(
    board_dir: Path,
    board_slug: str,
    *,
    lead_extra: bool = False,
) -> list[str]:
    """Return reasons for open/in-progress messages addressed to this role (or all)."""
    reasons: list[str] = []
    if not board_dir.is_dir():
        return reasons
    for path in sorted(board_dir.glob("*.md")):
        if path.name == "README.md":
            continue
        m = BOARD_NAME_RE.match(path.name)
        if not m:
            continue
        to = m.group("to")
        addressed = to == board_slug or to == "all"
        text = path.read_text(encoding="utf-8")
        fm = parse_frontmatter_fields(text)
        status = fm.get("status", "")
        if status not in OPEN_STATUSES:
            continue
        if addressed:
            reasons.append(f"board:{path.name} (to={to}, status={status})")
            continue
        if lead_extra and board_slug == "lead":
            # open from:human or type:needs-human
            if fm.get("from") == "human" or fm.get("type") == "needs-human":
                reasons.append(f"board:{path.name} (lead-watch from={fm.get('from')} type={fm.get('type')})")
    return reasons


def stuck_claude_branches(repo: Path, older_than_hours: float = 24.0) -> list[str]:
    """Remote origin/claude/* tips not ancestors of origin/main and older than threshold."""
    reasons: list[str] = []
    try:
        tips = subprocess.run(
            ["git", "for-each-ref", "--format=%(refname:short)|%(committerdate:iso-strict)",
             "refs/remotes/origin/claude/"],
            cwd=repo,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return reasons
    if tips.returncode != 0:
        return reasons
    now = utc_now()
    for line in tips.stdout.splitlines():
        if "|" not in line:
            continue
        ref, date_s = line.split("|", 1)
        branch = ref.removeprefix("origin/")
        # skip if already on main
        anc = subprocess.run(
            ["git", "merge-base", "--is-ancestor", ref, "origin/main"],
            cwd=repo,
            check=False,
            capture_output=True,
        )
        if anc.returncode == 0:
            continue
        when = parse_iso(date_s.strip())
        if when is None:
            reasons.append(f"stuck-branch:{branch} (unknown age)")
            continue
        age_h = (now - when).total_seconds() / 3600.0
        if age_h >= older_than_hours:
            reasons.append(f"stuck-branch:{branch} (age_h={age_h:.1f})")
    return reasons


def evaluate(
    root: Path,
    role_slug: str,
    *,
    now: datetime | None = None,
    check_stuck_branches: bool | None = None,
) -> tuple[bool, list[str]]:
    folder, board = folder_and_board(role_slug)
    state_path = root / "agents" / folder / "state.md"
    reasons: list[str] = []
    if not state_path.exists():
        return True, [f"missing state.md at {state_path.relative_to(root)} — default WORK"]

    state_text = state_path.read_text(encoding="utf-8")
    duties = load_duties(state_text)
    due = duties_due(duties, now=now)
    for name in due:
        reasons.append(f"duty-due:{name}")

    lead = board == "lead"
    board_reasons = board_messages_for(
        root / "team" / "board",
        board,
        lead_extra=lead,
    )
    reasons.extend(board_reasons)

    if check_stuck_branches is None:
        check_stuck_branches = lead
    if check_stuck_branches:
        reasons.extend(stuck_claude_branches(root))

    return (len(reasons) > 0), reasons


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Cheap wake gate for MEL agent roles")
    parser.add_argument("role_slug", help="Agent folder slug (e.g. mel-lead) or board slug (e.g. lead)")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--no-git",
        action="store_true",
        help="Skip stuck-branch git checks (tests)",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        work, reasons = evaluate(
            root,
            args.role_slug,
            check_stuck_branches=False if args.no_git else None,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if work:
        print("WORK")
        for r in reasons:
            print(f"  - {r}")
        return 0
    print("NOOP")
    print("  - no open board messages for this role")
    print("  - no duties due")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
