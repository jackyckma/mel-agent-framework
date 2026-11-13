"""Regression tests for merge-gate push-race handling."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WF = ROOT / ".github" / "workflows" / "merge-agent-branches.yml"
SCRIPTS = ROOT / "scripts"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class MergePushRaceTests(unittest.TestCase):
    def test_workflow_wraps_push_and_resyncs(self):
        text = WF.read_text(encoding="utf-8")
        self.assertIn("if git push origin HEAD:main; then", text)
        self.assertIn("non-ff race", text)
        self.assertIn("git reset --hard origin/main", text)
        self.assertIn("FAILED_RETRYABLE", text)
        # Must not bare-push under set -e without a wrap
        self.assertNotRegex(
            text,
            r"(?m)^\s+git push origin HEAD:main\s*$",
        )

    def test_classify_push_helper(self):
        m = load_module("merge_push_result", SCRIPTS / "merge_push_result.py")
        ok = m.classify_push(0)
        self.assertTrue(ok.merged)
        self.assertFalse(ok.failed)
        race = m.classify_push(1)
        self.assertTrue(race.failed)
        self.assertTrue(race.retryable)
        self.assertTrue(race.leave_branch)
        self.assertTrue(race.resync_main)


if __name__ == "__main__":
    unittest.main()
