#!/usr/bin/env python3
"""Validate MEL instance structure, board messages, and basics.

Checks:
  - Required paths/files exist
  - Board filenames and YAML frontmatter (inline # comments stripped)
  - Board from/to slugs against team/roles/README.md map (+ human, all)
  - Placeholder-aware: {{…}} left in mandate/roles is OK for a template;
    use --strict-placeholders to require them filled

Commit ownership by author is **not** enforced here: git authorship on
Scheduled Task commits is often a single bot identity, so folder rules cannot
be reliably inferred from history. Ownership is enforced by process docs and
agent prompts instead.

Usage (from instance / template root):
  python scripts/validate_repo.py
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

BOARD_NAME_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})_"
    r"(?P<from>[a-z0-9-]+)-to-(?P<to>[a-z0-9-]+)_"
    r"(?P<nnn>\d{3})-"
    r"(?P<slug>[a-z0-9-]+)\.md$"
)

ALLOWED_TYPES = {
    "task",
    "info",
    "question",
    "blocker",
    "proposal",
    "framework-feedback",
    "needs-human",
}
ALLOWED_STATUS = {"open", "in-progress", "done", "dropped"}
ALLOWED_PRIORITY = {"low", "normal", "high", "urgent"}

# Always allowed even if README table drifts
DEFAULT_BOARD_SLUGS = {
    "lead",
    "scout",
    "collector",
    "curator",
    "analyst",
    "narrative",
    "pcm",
    "human",
    "all",
}

REQUIRED_PATHS = [
    "FRAMEWORK_VERSION",
    "README.md",
    "team/mandate.md",
    "team/process.md",
    "team/SETUP_STATUS.md",
    "team/roles/README.md",
    "team/board/README.md",
    "team/board/_templates/message.md",
    "team/projects/README.md",
    "team/framework-feedback/README.md",
    "data/sources.yml",
    "data/fetch_status.json",
    "docs/index.html",
    "scripts/fetch.py",
    "scripts/transform.py",
    "scripts/build_dashboard.py",
    "scripts/validate_repo.py",
    "scripts/check_protected_paths.py",
    ".github/workflows/merge-agent-branches.yml",
    ".github/workflows/merge-agent-trigger.yml",
]

REQUIRED_ROLES = [
    "mel-lead",
    "scout",
    "data-collector",
    "data-curator",
    "dashboard-analyst",
    "narrative-designer",
    "project-change-manager",
]

PLACEHOLDER_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")
SLUG_MAP_ROW_RE = re.compile(
    r"\|\s*[^|]+\s*\|\s*`?([a-z0-9-]+)`?\s*\|\s*`?([a-z0-9-]+)`?\s*\|"
)


def strip_inline_comment(val: str) -> str:
    """Remove trailing YAML-style inline comments outside quotes."""
    in_single = False
    in_double = False
    for i, ch in enumerate(val):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            return val[:i].rstrip()
    return val.rstrip()


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str] | tuple[None, str]:
    if not text.startswith("---"):
        return None, "missing opening ---"
    end = text.find("\n---", 3)
    if end == -1:
        return None, "missing closing ---"
    block = text[3:end].strip()
    body = text[end + 4 :]
    data: dict[str, Any] = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            return None, f"bad frontmatter line: {line}"
        key, val = line.split(":", 1)
        key = key.strip()
        val = strip_inline_comment(val.strip())
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            data[key] = [p.strip().strip("'\"") for p in inner.split(",") if p.strip()] if inner else []
        else:
            data[key] = val.strip("\"'")
    return data, body


def load_board_slugs(root: Path) -> set[str]:
    """Parse board from/to slugs from team/roles/README.md; always include defaults."""
    slugs = set(DEFAULT_BOARD_SLUGS)
    readme = root / "team" / "roles" / "README.md"
    if not readme.exists():
        return slugs
    text = readme.read_text(encoding="utf-8")
    # Prefer rows in the "Slug map" table: Role | Agent folder slug | Board from/to slug
    in_table = False
    for line in text.splitlines():
        if "Board from/to" in line or "Board from" in line:
            in_table = True
            continue
        if in_table:
            if not line.strip().startswith("|"):
                if in_table and line.strip() and not line.strip().startswith("|"):
                    break
                if not line.strip():
                    break
                continue
            if re.match(r"^\|\s*-+", line):
                continue
            parts = [p.strip().strip("`") for p in line.split("|")]
            parts = [p for p in parts if p != ""]
            if len(parts) >= 3 and parts[2] and parts[2] != "Board from/to slug":
                slugs.add(parts[2])
    return slugs


def validate_board_file(path: Path, allowed_slugs: set[str] | None = None) -> list[str]:
    errors: list[str] = []
    allowed = allowed_slugs or DEFAULT_BOARD_SLUGS
    m = BOARD_NAME_RE.match(path.name)
    if not m:
        errors.append(f"{path.name}: filename does not match YYYY-MM-DD_<from>-to-<to>_<nnn>-<slug>.md")
        return errors
    text = path.read_text(encoding="utf-8")
    fm, err_or_body = parse_frontmatter(text)
    if fm is None:
        errors.append(f"{path.name}: {err_or_body}")
        return errors
    for key in ("from", "to", "type", "status", "priority", "created"):
        if key not in fm:
            errors.append(f"{path.name}: missing frontmatter key '{key}'")
    if fm.get("from") and fm["from"] != m.group("from"):
        errors.append(f"{path.name}: frontmatter from '{fm['from']}' != filename from '{m.group('from')}'")
    if fm.get("to") and fm["to"] != m.group("to"):
        errors.append(f"{path.name}: frontmatter to '{fm['to']}' != filename to '{m.group('to')}'")
    if fm.get("from") and fm["from"] not in allowed:
        errors.append(f"{path.name}: unknown from slug '{fm['from']}' (allowed: {sorted(allowed)})")
    if fm.get("to") and fm["to"] not in allowed:
        errors.append(f"{path.name}: unknown to slug '{fm['to']}' (allowed: {sorted(allowed)})")
    if m.group("from") not in allowed:
        errors.append(f"{path.name}: unknown filename from slug '{m.group('from')}'")
    if m.group("to") not in allowed:
        errors.append(f"{path.name}: unknown filename to slug '{m.group('to')}'")
    if fm.get("type") and fm["type"] not in ALLOWED_TYPES:
        errors.append(f"{path.name}: invalid type '{fm['type']}'")
    if fm.get("status") and fm["status"] not in ALLOWED_STATUS:
        errors.append(f"{path.name}: invalid status '{fm['status']}'")
    if fm.get("priority") and fm["priority"] not in ALLOWED_PRIORITY:
        errors.append(f"{path.name}: invalid priority '{fm['priority']}'")
    return errors


def collect_board_files(board: Path) -> list[Path]:
    if not board.exists():
        return []
    files: list[Path] = []
    for path in board.rglob("*.md"):
        if path.name == "README.md":
            continue
        if "_templates" in path.parts:
            continue
        files.append(path)
    return files


def validate_root(root: Path, strict_placeholders: bool = False) -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            errors.append(f"missing required path: {rel}")

    for role in REQUIRED_ROLES:
        for rel in (
            f"team/roles/_base/{role}.md",
            f"team/roles/{role}.md",
            f"agents/{role}/state.md",
        ):
            if not (root / rel).exists():
                errors.append(f"missing required path: {rel}")

    allowed_slugs = load_board_slugs(root)
    for path in collect_board_files(root / "team" / "board"):
        errors.extend(validate_board_file(path, allowed_slugs))

    if strict_placeholders:
        for rel in ("team/mandate.md", "README.md"):
            path = root / rel
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            found = PLACEHOLDER_RE.findall(text)
            if found:
                errors.append(f"{rel}: unresolved placeholders: {', '.join(sorted(set(found)))}")

    version = root / "FRAMEWORK_VERSION"
    if version.exists():
        ver = version.read_text(encoding="utf-8").strip()
        if not re.match(r"^\d+\.\d+\.\d+", ver):
            errors.append(f"FRAMEWORK_VERSION looks invalid: {ver!r}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate MEL agent-team repo structure")
    parser.add_argument("--root", type=Path, default=Path("."), help="Repo root to validate")
    parser.add_argument(
        "--strict-placeholders",
        action="store_true",
        help="Fail if mandate/README still contain {{PLACEHOLDERS}} (use on live instances)",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    errors = validate_root(root, strict_placeholders=args.strict_placeholders)
    if errors:
        print(f"validate_repo: {len(errors)} issue(s) under {root}", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"validate_repo: OK ({root})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
