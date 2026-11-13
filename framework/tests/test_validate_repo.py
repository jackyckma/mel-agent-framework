"""Unit tests for scripts/validate_repo.py and related helpers."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
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


validate_repo = load_module("validate_repo", SCRIPTS / "validate_repo.py")


class ValidateRepoTests(unittest.TestCase):
    def test_repo_root_passes(self):
        errors = validate_repo.validate_root(ROOT, strict_placeholders=False)
        self.assertEqual(errors, [], msg="\n".join(errors))

    def test_placeholders_when_strict(self):
        errors = validate_repo.validate_root(ROOT, strict_placeholders=True)
        self.assertTrue(any("unresolved placeholders" in e for e in errors))

    def test_board_filename_and_frontmatter_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._minimal_tree(root)
            board = root / "team" / "board"
            name = "2026-11-11_lead-to-collector_001-hello.md"
            (board / name).write_text(
                "---\n"
                "from: lead\n"
                "to: collector\n"
                "type: task\n"
                "status: open\n"
                "priority: normal\n"
                "created: 2026-11-11T12:00:00Z\n"
                "refs: []\n"
                "---\n\n# Hello\n",
                encoding="utf-8",
            )
            errors = validate_repo.validate_root(root)
            self.assertEqual(errors, [], msg="\n".join(errors))

    def test_board_bad_filename(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad-name.md"
            path.write_text(
                "---\nfrom: lead\nto: collector\ntype: task\nstatus: open\npriority: normal\ncreated: 2026-11-11T00:00:00Z\n---\n",
                encoding="utf-8",
            )
            errs = validate_repo.validate_board_file(path)
            self.assertTrue(any("filename" in e for e in errs))

    def test_board_type_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "2026-11-11_lead-to-collector_001-x.md"
            path.write_text(
                "---\n"
                "from: lead\n"
                "to: collector\n"
                "type: nope\n"
                "status: open\n"
                "priority: normal\n"
                "created: 2026-11-11T12:00:00Z\n"
                "---\n",
                encoding="utf-8",
            )
            errs = validate_repo.validate_board_file(path)
            self.assertTrue(any("invalid type" in e for e in errs))

    def test_frontmatter_strips_inline_comments(self):
        text = (
            "---\n"
            "from: lead  # author\n"
            "to: collector\n"
            'type: "task"  # allowed\n'
            "status: open\n"
            "priority: normal\n"
            "created: 2026-11-11T12:00:00Z\n"
            "refs: []\n"
            "---\n\nbody\n"
        )
        fm, body = validate_repo.parse_frontmatter(text)
        self.assertIsNotNone(fm)
        assert fm is not None
        self.assertEqual(fm["from"], "lead")
        self.assertEqual(fm["type"], "task")
        self.assertIn("body", body)

    def test_unknown_board_slug_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "2026-11-11_lead-to-nobody_001-x.md"
            path.write_text(
                "---\n"
                "from: lead\n"
                "to: nobody\n"
                "type: task\n"
                "status: open\n"
                "priority: normal\n"
                "created: 2026-11-11T12:00:00Z\n"
                "---\n",
                encoding="utf-8",
            )
            errs = validate_repo.validate_board_file(path, validate_repo.DEFAULT_BOARD_SLUGS)
            self.assertTrue(any("unknown to slug" in e for e in errs))

    def test_load_board_slugs_from_roles_readme(self):
        slugs = validate_repo.load_board_slugs(ROOT)
        for expected in ("lead", "scout", "collector", "curator", "analyst", "narrative", "pcm", "human", "all"):
            self.assertIn(expected, slugs)

    def _minimal_tree(self, root: Path) -> None:
        for rel in validate_repo.REQUIRED_PATHS:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                if path.suffix == ".json":
                    path.write_text("{}\n", encoding="utf-8")
                elif path.name == "FRAMEWORK_VERSION":
                    path.write_text("0.1.0\n", encoding="utf-8")
                else:
                    path.write_text("# stub\n", encoding="utf-8")
        # Slug map table so load_board_slugs works in temp trees if validate_root calls it
        roles_readme = root / "team" / "roles" / "README.md"
        roles_readme.write_text(
            "| Role | Agent folder slug | Board from/to slug |\n"
            "|------|-------------------|--------------------|\n"
            "| MEL Lead | `mel-lead` | `lead` |\n"
            "| Scout | `scout` | `scout` |\n"
            "| Data Collector | `data-collector` | `collector` |\n"
            "| Data Curator | `data-curator` | `curator` |\n"
            "| Analyst | `dashboard-analyst` | `analyst` |\n"
            "| Narrative | `narrative-designer` | `narrative` |\n"
            "| PCM | `project-change-manager` | `pcm` |\n",
            encoding="utf-8",
        )
        for role in validate_repo.REQUIRED_ROLES:
            for rel in (
                f"team/roles/_base/{role}.md",
                f"team/roles/{role}.md",
            ):
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("# stub\n", encoding="utf-8")
            state = root / "agents" / role / "state.md"
            state.parent.mkdir(parents=True, exist_ok=True)
            state.write_text(
                f"# State: {role}\n\n## duties\n\n"
                "```yaml\n"
                "duties:\n"
                "  - name: stub-duty\n"
                "    cadence_hours: 24\n"
                "    last_done: null\n"
                "```\n",
                encoding="utf-8",
            )
        (root / "team" / "board" / "archive").mkdir(parents=True, exist_ok=True)


class YamlUtilTests(unittest.TestCase):
    def test_load_sources_yaml(self):
        yaml_util = load_module("yaml_util", SCRIPTS / "yaml_util.py")
        text = (ROOT / "data" / "sources.yml").read_text(encoding="utf-8")
        data = yaml_util.load_simple_sources_yaml(text)
        self.assertIn("sources", data)
        self.assertGreaterEqual(len(data["sources"]), 1)
        self.assertEqual(data["sources"][0]["id"], "example-jsonplaceholder")
        self.assertIs(data["sources"][0]["enabled"], False)


class TransformBuildTests(unittest.TestCase):
    def test_transform_and_build_offline_empty(self):
        transform = load_module("transform", SCRIPTS / "transform.py")
        build = load_module("build_dashboard", SCRIPTS / "build_dashboard.py")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data" / "raw").mkdir(parents=True)
            (root / "data" / "processed").mkdir(parents=True)
            (root / "docs" / "data").mkdir(parents=True)
            self.assertEqual(transform.main(["--root", str(root)]), 0)
            self.assertEqual(build.main(["--root", str(root)]), 0)
            dash = json.loads((root / "docs" / "data" / "dashboard.json").read_text(encoding="utf-8"))
            self.assertIsNone(dash["last_updated"])
            self.assertIsNone(dash["input_fresh_at"])
            self.assertTrue(dash["stale"])

    def test_input_freshness_survives_retransform(self):
        from datetime import datetime, timezone

        transform = load_module("transform", SCRIPTS / "transform.py")
        build = load_module("build_dashboard", SCRIPTS / "build_dashboard.py")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = root / "data" / "raw" / "demo"
            raw.mkdir(parents=True)
            (raw / "latest.json").write_text('[{"n": 1}]\n', encoding="utf-8")
            (root / "data" / "processed").mkdir(parents=True)
            (root / "docs" / "data").mkdir(parents=True)
            old = "2020-01-01T00:00:00Z"
            (root / "data" / "fetch_status.json").write_text(
                json.dumps(
                    {
                        "updated_at": old,
                        "sources": {
                            "demo": {
                                "last_success": old,
                                "last_error": "URLError: offline",
                                "last_attempt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            }
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            self.assertEqual(transform.main(["--root", str(root)]), 0)
            summary = json.loads((root / "data" / "processed" / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["input_fresh_at"], old)
            self.assertNotEqual(summary["updated_at"], old)
            self.assertEqual(build.main(["--root", str(root), "--stale-hours", "48"]), 0)
            dash = json.loads((root / "docs" / "data" / "dashboard.json").read_text(encoding="utf-8"))
            self.assertEqual(dash["input_fresh_at"], old)
            self.assertEqual(dash["last_updated"], old)
            self.assertTrue(dash["stale"])

    def test_world_bank_shape_in_transform_source(self):
        transform = load_module("transform", SCRIPTS / "transform.py")
        with tempfile.TemporaryDirectory() as tmp:
            source_dir = Path(tmp) / "wb"
            source_dir.mkdir()
            payload = [
                {"page": 1, "pages": 1},
                [{"country": {"id": "US"}, "value": 1}, {"country": {"id": "US"}, "value": 2}],
            ]
            (source_dir / "latest.json").write_text(json.dumps(payload) + "\n", encoding="utf-8")
            rows = transform.transform_source("wb", source_dir)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["source_id"], "wb")


if __name__ == "__main__":
    unittest.main()
