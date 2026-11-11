"""Unit tests for template/scripts/validate_repo.py."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "template"
SCRIPTS = TEMPLATE / "scripts"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


validate_repo = load_module("validate_repo", SCRIPTS / "validate_repo.py")


class ValidateRepoTests(unittest.TestCase):
    def test_template_passes(self):
        errors = validate_repo.validate_root(TEMPLATE, strict_placeholders=False)
        self.assertEqual(errors, [], msg="\n".join(errors))

    def test_template_has_placeholders_when_strict(self):
        errors = validate_repo.validate_root(TEMPLATE, strict_placeholders=True)
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
            path.write_text("---\nfrom: lead\nto: collector\ntype: task\nstatus: open\npriority: normal\ncreated: 2026-11-11T00:00:00Z\n---\n", encoding="utf-8")
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

    def _minimal_tree(self, root: Path) -> None:
        """Copy required skeleton from template via lightweight stubs."""
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
        for role in validate_repo.REQUIRED_ROLES:
            for rel in (
                f"team/roles/_base/{role}.md",
                f"team/roles/{role}.md",
                f"agents/{role}/state.md",
            ):
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("# stub\n", encoding="utf-8")
        (root / "team" / "board" / "archive").mkdir(parents=True, exist_ok=True)


class YamlUtilTests(unittest.TestCase):
    def test_load_sources_yaml(self):
        yaml_util = load_module("yaml_util", SCRIPTS / "yaml_util.py")
        text = (TEMPLATE / "data" / "sources.yml").read_text(encoding="utf-8")
        data = yaml_util.load_simple_sources_yaml(text)
        self.assertIn("sources", data)
        self.assertGreaterEqual(len(data["sources"]), 1)
        self.assertEqual(data["sources"][0]["id"], "example-jsonplaceholder")
        self.assertIs(data["sources"][0]["enabled"], False)


class TransformBuildTests(unittest.TestCase):
    def test_transform_and_build_offline(self):
        transform = load_module("transform", SCRIPTS / "transform.py")
        build = load_module("build_dashboard", SCRIPTS / "build_dashboard.py")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data" / "raw").mkdir(parents=True)
            (root / "data" / "processed").mkdir(parents=True)
            (root / "docs" / "data").mkdir(parents=True)
            self.assertEqual(transform.main(["--root", str(root)]), 0)
            self.assertEqual(build.main(["--root", str(root)]), 0)
            dash = (root / "docs" / "data" / "dashboard.json").read_text(encoding="utf-8")
            self.assertIn("last_updated", dash)


if __name__ == "__main__":
    unittest.main()
