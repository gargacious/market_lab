#!/usr/bin/env python3
"""Focused source-only bootstrap fixtures; no tool install or network."""
from __future__ import annotations
import argparse
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

SOURCE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SOURCE))
from tooling import bootstrap

SCRATCH: Path


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-c", "safe.directory=" + str(root), "-C", str(root), *args],
        text=True, stderr=subprocess.PIPE,
    ).strip()


class BootstrapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "workspace"
        self.root.mkdir()
        for name in bootstrap.TRACKED_FILES - {"market-integration"}:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE / name, target)

    def init_git(self, root: Path) -> None:
        git(root, "init", "-b", "codex/test")
        git(root, "config", "user.name", "Workspace Fixture")
        git(root, "config", "user.email", "workspace-fixture@example.invalid")

    def test_relocatable_pinned_plans(self) -> None:
        lock = bootstrap.load_lock(self.root)
        plan = bootstrap.plan(self.root, lock, "conan")
        self.assertEqual(plan[1][-1], "conan==2.31.2")
        self.assertIn(str(self.root), plan[0][-1])
        self.assertEqual(lock["tools"]["iverilog"]["source_commit"], "dfeee909ed9f20b4870dd93423156c0170c0e1ff")
        self.assertFalse((self.root / "tooling/conan-2.31.2").exists())

    def test_paths_reject_escape_and_git(self) -> None:
        for value in (".", "../escape", "/absolute", "C:/escape", ".git/config", "tools/../../escape", "tools\\escape"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                bootstrap.safe_path(self.root, value)

    def test_plan_never_executes_or_creates_environment(self) -> None:
        lock = bootstrap.load_lock(self.root)
        before = sorted(str(path.relative_to(self.root)) for path in self.root.rglob("*"))
        with mock.patch.object(bootstrap.subprocess, "run", side_effect=AssertionError("unexpected execution")):
            for tool in ("conan", "iverilog"):
                self.assertFalse(bootstrap.install(self.root, lock, tool, False)["executed"])
        self.assertEqual(before, sorted(str(path.relative_to(self.root)) for path in self.root.rglob("*")))

    def test_existing_foreign_environment_is_preserved(self) -> None:
        lock = bootstrap.load_lock(self.root)
        venv = bootstrap.safe_path(self.root, lock["tools"]["conan"]["venv"])
        venv.mkdir()
        marker = venv / "uncommitted-marker"
        marker.write_bytes(b"preserve")
        with mock.patch.object(bootstrap.subprocess, "run", side_effect=AssertionError("unexpected execution")):
            with self.assertRaisesRegex(ValueError, "preserve"):
                bootstrap.install(self.root, lock, "conan", True)
        self.assertEqual(marker.read_bytes(), b"preserve")

    def test_status_preserves_development_child_and_git_directory(self) -> None:
        child = self.root / "market-integration"
        child.mkdir()
        self.init_git(child)
        (child / "source.txt").write_text("published", encoding="utf-8")
        git(child, "add", "source.txt")
        git(child, "commit", "-m", "fixture published")
        published = git(child, "rev-parse", "HEAD")
        (child / "source.txt").write_text("development", encoding="utf-8")
        git(child, "commit", "-am", "fixture development")
        development = git(child, "rev-parse", "HEAD")
        (child / "source.txt").write_text("uncommitted", encoding="utf-8")
        lock = bootstrap.load_lock(self.root)
        lock["integration"]["published_commit"] = published
        (self.root / "tooling/tool-lock.json").write_text(json.dumps(lock), encoding="utf-8")
        self.init_git(self.root)
        git(self.root, "add", *sorted(bootstrap.TRACKED_FILES - {"market-integration"}))
        git(self.root, "update-index", "--add", "--cacheinfo", "160000," + published + ",market-integration")
        git(self.root, "commit", "-m", "fixture workspace")
        git_directory = (child / ".git").resolve()
        result = bootstrap.status(self.root, lock)
        self.assertEqual(result["integration"]["indexed_commit"], published)
        self.assertEqual(result["integration"]["actual_head"], development)
        self.assertTrue(result["integration"]["development_differs_from_published"])
        self.assertGreater(result["integration"]["dirty_entry_count"], 0)
        self.assertEqual(git(child, "rev-parse", "HEAD"), development)
        self.assertEqual((child / ".git").resolve(), git_directory)
        self.assertTrue((child / ".git").is_dir())
        self.assertEqual((child / "source.txt").read_text(), "uncommitted")

    def test_allowlist_ignores_generated_and_detects_foreign_tracked_path(self) -> None:
        self.init_git(self.root)
        for name in ("artifacts/report.json", "tmp/output", "worktrees/copy/file",
                     "tooling/conan-home/cache/file", "tools/iverilog-13.0/installed/bin/iverilog",
                     "private-profile", "tools/iverilog-13.0/source/generated-file"):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"fixture")
            git(self.root, "check-ignore", "--", name)
        for name in ("tools/iverilog-13.0/install.py", "tools/iverilog-13.0/README.txt"):
            result = subprocess.run(["git", "-c", "safe.directory=" + str(self.root), "-C", str(self.root), "check-ignore", "-q", "--", name], check=False)
            self.assertEqual(result.returncode, 1)
        (self.root / "foreign.txt").write_bytes(b"fixture")
        git(self.root, "add", "-f", "foreign.txt")
        result = bootstrap.status(self.root, bootstrap.load_lock(self.root))
        self.assertEqual(result["unexpected_tracked_paths"], ["foreign.txt"])

    def test_icarus_default_plan_never_installs(self) -> None:
        result = subprocess.run(
            [sys.executable, "-B", str(self.root / "tools/iverilog/bootstrap.py"), "--root", str(self.root)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True,
        )
        observed = json.loads(result.stdout)
        self.assertFalse(observed["executed"])
        self.assertEqual(observed["source_commit"], "dfeee909ed9f20b4870dd93423156c0170c0e1ff")
        self.assertFalse((self.root / "tools/iverilog-13.0/installed").exists())
        self.assertFalse((self.root / "tools/iverilog-13.0/source").exists())

    def test_icarus_wrong_existing_source_never_builds(self) -> None:
        path = self.root / "tools/iverilog/bootstrap.py"
        spec = importlib.util.spec_from_file_location("workspace_iverilog_fixture", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        (self.root / "tools/iverilog-13.0/source").mkdir(parents=True)
        with mock.patch.object(sys, "argv", [str(path), "--root", str(self.root), "--execute"]),              mock.patch.object(sys, "platform", "linux"),              mock.patch.object(module.subprocess, "check_output", return_value="0" * 40),              mock.patch.object(module.subprocess, "run", side_effect=AssertionError("unexpected build")):
            with self.assertRaisesRegex(ValueError, "exact reviewed commit"):
                module.main()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scratch", type=Path, required=True)
    args, remaining = parser.parse_known_args()
    SCRATCH = args.scratch.resolve()
    SCRATCH.mkdir(parents=True, exist_ok=True)
    unittest.main(argv=[sys.argv[0], *remaining])
