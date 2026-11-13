"""Tests for scripts/wake_check.py."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


wake = load_module("wake_check", SCRIPTS / "wake_check.py")


def _write_state(root: Path, folder: str, duties_yaml: str) -> None:
    path = root / "agents" / folder / "state.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# State\n\n## duties\n\n```yaml\n{duties_yaml}\n```\n",
        encoding="utf-8",
    )


def _write_board(root: Path, name: str, frontmatter: str) -> None:
    board = root / "team" / "board"
    board.mkdir(parents=True, exist_ok=True)
    (board / name).write_text(f"---\n{frontmatter}---\n\nbody\n", encoding="utf-8")


class WakeCheckTests(unittest.TestCase):
    def test_noop_when_no_board_and_duties_not_due(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            now = datetime(2026, 11, 13, 12, 0, tzinfo=timezone.utc)
            recent = (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            _write_state(
                root,
                "scout",
                f"duties:\n  - name: signal-scan\n    cadence_hours: 168\n    last_done: {recent}\n",
            )
            work, reasons = wake.evaluate(root, "scout", now=now, check_stuck_branches=False)
            self.assertFalse(work)
            self.assertEqual(reasons, [])
            self.assertEqual(wake.main(["scout", "--root", str(root), "--no-git"]), 1)

    def test_work_when_duty_due_or_never_done(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            now = datetime(2026, 11, 13, 12, 0, tzinfo=timezone.utc)
            _write_state(
                root,
                "data-collector",
                "duties:\n  - name: review-fetch-status\n    cadence_hours: 6\n    last_done: null\n",
            )
            work, reasons = wake.evaluate(root, "data-collector", now=now, check_stuck_branches=False)
            self.assertTrue(work)
            self.assertTrue(any("duty-due:review-fetch-status" in r for r in reasons))

    def test_work_on_open_board_to_slug(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            now = datetime(2026, 11, 13, 12, 0, tzinfo=timezone.utc)
            recent = now.strftime("%Y-%m-%dT%H:%M:%SZ")
            _write_state(
                root,
                "data-collector",
                f"duties:\n  - name: review-fetch-status\n    cadence_hours: 6\n    last_done: {recent}\n",
            )
            _write_board(
                root,
                "2026-11-13_lead-to-collector_001-go.md",
                "from: lead\nto: collector\ntype: task\nstatus: open\npriority: normal\ncreated: 2026-11-13T00:00:00Z\n",
            )
            work, reasons = wake.evaluate(root, "data-collector", now=now, check_stuck_branches=False)
            self.assertTrue(work)
            self.assertTrue(any("to=collector" in r for r in reasons))

    def test_to_all_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            now = datetime(2026, 11, 13, 12, 0, tzinfo=timezone.utc)
            recent = now.strftime("%Y-%m-%dT%H:%M:%SZ")
            _write_state(
                root,
                "scout",
                f"duties:\n  - name: signal-scan\n    cadence_hours: 168\n    last_done: {recent}\n",
            )
            _write_board(
                root,
                "2026-11-13_lead-to-all_001-note.md",
                "from: lead\nto: all\ntype: info\nstatus: open\npriority: normal\ncreated: 2026-11-13T00:00:00Z\n",
            )
            work, reasons = wake.evaluate(root, "scout", now=now, check_stuck_branches=False)
            self.assertTrue(work)
            self.assertTrue(any("to=all" in r for r in reasons))

    def test_closed_messages_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            now = datetime(2026, 11, 13, 12, 0, tzinfo=timezone.utc)
            recent = now.strftime("%Y-%m-%dT%H:%M:%SZ")
            _write_state(
                root,
                "scout",
                f"duties:\n  - name: signal-scan\n    cadence_hours: 168\n    last_done: {recent}\n",
            )
            _write_board(
                root,
                "2026-11-13_lead-to-scout_001-done.md",
                "from: lead\nto: scout\ntype: task\nstatus: done\npriority: normal\ncreated: 2026-11-13T00:00:00Z\n",
            )
            work, reasons = wake.evaluate(root, "scout", now=now, check_stuck_branches=False)
            self.assertFalse(work)

    def test_duty_not_due_when_recent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            now = datetime(2026, 11, 13, 12, 0, tzinfo=timezone.utc)
            recent = (now - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
            _write_state(
                root,
                "data-collector",
                f"duties:\n  - name: review-fetch-status\n    cadence_hours: 6\n    last_done: {recent}\n",
            )
            work, _ = wake.evaluate(root, "collector", now=now, check_stuck_branches=False)
            self.assertFalse(work)

    def test_lead_watches_from_human_and_needs_human(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            now = datetime(2026, 11, 13, 12, 0, tzinfo=timezone.utc)
            recent = now.strftime("%Y-%m-%dT%H:%M:%SZ")
            _write_state(
                root,
                "mel-lead",
                f"duties:\n  - name: daily-digest\n    cadence_hours: 24\n    last_done: {recent}\n"
                f"  - name: stuck-branch-scan\n    cadence_hours: 3\n    last_done: {recent}\n",
            )
            _write_board(
                root,
                "2026-11-13_human-to-collector_001-q.md",
                "from: human\nto: collector\ntype: question\nstatus: open\npriority: normal\ncreated: 2026-11-13T00:00:00Z\n",
            )
            work, reasons = wake.evaluate(root, "mel-lead", now=now, check_stuck_branches=False)
            self.assertTrue(work)
            self.assertTrue(any("from=human" in r for r in reasons))

    def test_repo_template_states_parse(self):
        for role in ("mel-lead", "scout", "data-collector"):
            text = (ROOT / "agents" / role / "state.md").read_text(encoding="utf-8")
            duties = wake.load_duties(text)
            self.assertGreaterEqual(len(duties), 1, msg=role)

    def test_lead_stuck_branch_older_than_24h(self):
        import subprocess
        import os

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            now = datetime(2026, 11, 13, 12, 0, tzinfo=timezone.utc)
            recent = now.strftime("%Y-%m-%dT%H:%M:%SZ")
            _write_state(
                root,
                "mel-lead",
                f"duties:\n  - name: daily-digest\n    cadence_hours: 24\n    last_done: {recent}\n"
                f"  - name: stuck-branch-scan\n    cadence_hours: 3\n    last_done: {recent}\n",
            )
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "t@t"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True)
            (root / "README").write_text("x\n", encoding="utf-8")
            subprocess.run(["git", "add", "README"], cwd=root, check=True, capture_output=True)
            env = os.environ.copy()
            env["GIT_AUTHOR_DATE"] = "2026-11-10T12:00:00Z"
            env["GIT_COMMITTER_DATE"] = "2026-11-10T12:00:00Z"
            subprocess.run(["git", "commit", "-m", "main"], cwd=root, check=True, capture_output=True, env=env)
            subprocess.run(["git", "branch", "-M", "main"], cwd=root, check=True, capture_output=True)
            # Simulate remote tracking refs
            subprocess.run(["git", "checkout", "-b", "claude/old"], cwd=root, check=True, capture_output=True)
            (root / "extra").write_text("y\n", encoding="utf-8")
            subprocess.run(["git", "add", "extra"], cwd=root, check=True, capture_output=True)
            env["GIT_AUTHOR_DATE"] = "2026-11-10T12:00:00Z"
            env["GIT_COMMITTER_DATE"] = "2026-11-10T12:00:00Z"
            subprocess.run(["git", "commit", "-m", "agent"], cwd=root, check=True, capture_output=True, env=env)
            subprocess.run(["git", "checkout", "main"], cwd=root, check=True, capture_output=True)
            # Create refs/remotes/origin/main and origin/claude/old
            subprocess.run(["git", "update-ref", "refs/remotes/origin/main", "main"], cwd=root, check=True)
            subprocess.run(["git", "update-ref", "refs/remotes/origin/claude/old", "claude/old"], cwd=root, check=True)

            work, reasons = wake.evaluate(root, "mel-lead", now=now, check_stuck_branches=True)
            self.assertTrue(work)
            self.assertTrue(any("stuck-branch:claude/old" in r for r in reasons))


if __name__ == "__main__":
    unittest.main()
