"""Tests for scripts/check_protected_paths.py."""

from __future__ import annotations

import importlib.util
import sys
import unittest
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


guard = load_module("check_protected_paths", SCRIPTS / "check_protected_paths.py")


class ProtectedPathsTests(unittest.TestCase):
    def test_allows_agent_owned_paths(self):
        hits = guard.protected_hits(
            [
                "agents/mel-lead/state.md",
                "team/board/2026-11-12_lead-to-collector_001-x.md",
                "data/raw/demo/latest.json",
                "docs/data/dashboard.json",
            ]
        )
        self.assertEqual(hits, [])

    def test_blocks_github_workflows(self):
        hits = guard.protected_hits([".github/workflows/fetch.yml"])
        self.assertEqual(hits, [".github/workflows/fetch.yml"])

    def test_blocks_framework_and_version_and_base_roles(self):
        hits = guard.protected_hits(
            [
                "framework/README.md",
                "FRAMEWORK_VERSION",
                "team/roles/_base/mel-lead.md",
                "team/roles/mel-lead.md",
            ]
        )
        self.assertEqual(
            hits,
            [
                "FRAMEWORK_VERSION",
                "framework/README.md",
                "team/roles/_base/mel-lead.md",
            ],
        )

    def test_blocks_gate_scripts(self):
        hits = guard.protected_hits(
            [
                "scripts/validate_repo.py",
                "scripts/check_protected_paths.py",
                "scripts/wake_check.py",
                "scripts/fetch.py",
            ]
        )
        self.assertEqual(
            hits,
            [
                "scripts/check_protected_paths.py",
                "scripts/validate_repo.py",
                "scripts/wake_check.py",
            ],
        )

    def test_rename_out_of_framework_caught_when_both_paths_listed(self):
        # Simulates --no-renames output: delete old + add new
        hits = guard.protected_hits(["framework/example.md", "moved.md"])
        self.assertIn("framework/example.md", hits)

    def test_cli_files_ok(self):
        self.assertEqual(guard.main(["--files", "agents/scout/state.md"]), 0)

    def test_cli_files_blocked(self):
        self.assertEqual(guard.main(["--files", ".github/workflows/x.yml"]), 1)


if __name__ == "__main__":
    unittest.main()
