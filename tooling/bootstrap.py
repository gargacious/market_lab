#!/usr/bin/env python3
"""Plan and inspect workspace setup; install only with an explicit --execute."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

TRACKED_FILES = frozenset({
    ".gitignore", ".gitattributes", ".gitmodules", "AGENTS.md", "README.md", "TASKS.md",
    "tooling/__init__.py", "tooling/bootstrap.py", "tooling/tool-lock.json",
    "tooling/tests/bootstrap_tests.py", "tools/iverilog/bootstrap.py",
    "market-integration", "tools/iverilog-13.0/install.py", "tools/iverilog-13.0/README.txt",
})


def safe_path(root: Path, name: str) -> Path:
    if not isinstance(name, str) or not name or "\\" in name or ":" in name:
        raise ValueError("workspace path must be a plain relative POSIX path")
    relative = PurePosixPath(name)
    if not relative.parts or relative.is_absolute() or any(part in {"..", ".git"} for part in relative.parts):
        raise ValueError("workspace path escapes its owned root")
    path = (root / name).resolve()
    if path != root.resolve() and root.resolve() not in path.parents:
        raise ValueError("workspace path resolves outside its owned root")
    return path


def load_lock(root: Path) -> dict:
    lock = json.loads((root / "tooling/tool-lock.json").read_bytes())
    if lock.get("format") != "market-lab-workspace-bootstrap-v1":
        raise ValueError("unsupported workspace lock")
    integration = lock["integration"]
    if integration["path"] != "market-integration" or not re.fullmatch(r"[0-9a-f]{40}", integration["published_commit"]):
        raise ValueError("invalid integration selection")
    if integration["url"] != "git@bitbucket.org:gargacious/market-integration.git":
        raise ValueError("integration URL differs from the reviewed repository")
    tools = lock["tools"]
    if set(tools) != {"conan", "iverilog"}:
        raise ValueError("unexpected tool selection")
    for name in ("root",):
        safe_path(root, tools["iverilog"][name])
    for name in ("venv", "home"):
        safe_path(root, tools["conan"][name])
    if not re.fullmatch(r"[0-9a-f]{40}", tools["iverilog"]["source_commit"]):
        raise ValueError("Icarus source commit is not exact")
    if tools["iverilog"]["source_url"] != "https://github.com/steveicarus/iverilog.git":
        raise ValueError("Icarus source URL is not the reviewed upstream")
    for tool in tools.values():
        if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)+", tool["version"]):
            raise ValueError("tool version is not exact")
    if any(not re.fullmatch(r"[a-z0-9][a-z0-9+.-]*", package) for package in tools["iverilog"]["build_packages"]):
        raise ValueError("invalid distro build package")
    return lock


def git(root: Path, *args: str) -> str | None:
    result = subprocess.run(
        ["git", "-c", "safe.directory=" + str(root), "-C", str(root), *args],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def python_in(venv: Path) -> Path:
    return venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def tool_status(root: Path, lock: dict) -> dict:
    conan = lock["tools"]["conan"]
    iverilog = lock["tools"]["iverilog"]
    return {
        "conan": {"version": conan["version"], "python_present": python_in(safe_path(root, conan["venv"])).is_file(),
                  "home_present": safe_path(root, conan["home"]).is_dir()},
        "iverilog": {"version": iverilog["version"], "source_commit": iverilog["source_commit"],
                     "compiler_present": (safe_path(root, iverilog["root"]) / "installed/bin/iverilog").is_file(),
                     "runtime_present": (safe_path(root, iverilog["root"]) / "installed/bin/vvp").is_file()},
    }


def status(root: Path, lock: dict) -> dict:
    selected = lock["integration"]
    child = safe_path(root, selected["path"])
    actual_root = git(child, "rev-parse", "--show-toplevel") if child.is_dir() else None
    child_initialized = actual_root is not None and Path(actual_root).resolve() == child.resolve()
    child_head = git(child, "rev-parse", "HEAD") if child_initialized else None
    child_dirty = git(child, "status", "--porcelain=v1", "--untracked-files=all", "--ignore-submodules=all") if child_head else None
    child_links = git(child, "ls-tree", "-r", "HEAD") if child_head else None
    indexed = git(root, "ls-files", "--stage", "--", selected["path"])
    indexed_commit = None
    if indexed:
        fields = indexed.split()
        if len(fields) >= 3 and fields[0] == "160000":
            indexed_commit = fields[1]
    tracked_text = git(root, "ls-files", "-z")
    tracked = set(tracked_text.split("\0")) - {""} if tracked_text is not None else set()
    missing = sorted(name for name in TRACKED_FILES - {selected["path"]} if not (root / name).is_file())
    return {
        "format": "market-lab-workspace-status-v1",
        "root": str(root),
        "parent_head": git(root, "rev-parse", "HEAD"),
        "origin_configured": git(root, "remote", "get-url", "origin") is not None,
        "remote_publication_verified": False,
        "unexpected_tracked_paths": sorted(tracked - TRACKED_FILES),
        "missing_setup_sources": missing,
        "integration": {
            "initialization": "initialized" if child_initialized else ("uninitialized" if child.is_dir() else "absent"),
            "published_commit": selected["published_commit"],
            "indexed_commit": indexed_commit,
            "actual_head": child_head,
            "development_differs_from_published": child_head is not None and child_head != selected["published_commit"],
            "dirty_entry_count": len(child_dirty.splitlines()) if child_dirty else 0,
            "selected_component_submodules": sum(line.startswith("160000 ") for line in (child_links or "").splitlines()),
            "checkout_changed": False,
        },
        "tools": tool_status(root, lock),
        "backup_limits": ["unpublished child refs", "uncommitted source", "ignored evidence and required inputs",
                          "credentials, keys, certificates and profiles", "local environments and caches"],
    }


def plan(root: Path, lock: dict, tool: str) -> list[list[str]]:
    if tool == "conan":
        config = lock["tools"]["conan"]
        venv = safe_path(root, config["venv"])
        return [[sys.executable, "-m", "venv", str(venv)],
                [str(python_in(venv)), "-m", "pip", "install", "conan==" + config["version"]]]
    return [[sys.executable, "-B", str(root / "tools/iverilog/bootstrap.py"), "--root", str(root), "--execute"]]


def conan_environment(root: Path, lock: dict) -> dict[str, str]:
    temporary = str(safe_path(root, "tmp/tool-bootstrap"))
    return {"PIP_CACHE_DIR": str(safe_path(root, "tooling/pip-cache")),
            "CONAN_HOME": str(safe_path(root, lock["tools"]["conan"]["home"])),
            "TMP": temporary, "TEMP": temporary, "TMPDIR": temporary}


def install(root: Path, lock: dict, tool: str, execute: bool) -> dict:
    commands = plan(root, lock, tool)
    selected_environment = conan_environment(root, lock) if tool == "conan" else {}
    if not execute:
        return {"executed": False, "tool": tool, "commands": commands, "environment": selected_environment}
    if tool == "conan":
        venv = safe_path(root, lock["tools"]["conan"]["venv"])
        if venv.exists() and not python_in(venv).is_file():
            raise ValueError("existing tool directory is not a recognized venv; preserve it")
        for path in set(selected_environment.values()):
            Path(path).mkdir(parents=True, exist_ok=True)
        environment = {**os.environ, **selected_environment}
        if not venv.exists():
            subprocess.run(commands[0], check=True, env=environment)
        subprocess.run(commands[1], check=True, env=environment)
    else:
        subprocess.run(commands[0], check=True)
    return {"executed": True, "tool": tool, "environment": selected_environment}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    sub.add_parser("check")
    for name in ("plan", "install"):
        child = sub.add_parser(name)
        child.add_argument("--tool", choices=("conan", "iverilog"), required=True)
        if name == "install":
            child.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    lock = load_lock(root)
    if args.command in {"plan", "install"}:
        result = install(root, lock, args.tool, getattr(args, "execute", False))
    else:
        result = status(root, lock)
        if args.command == "check":
            result["passed"] = not result["unexpected_tracked_paths"] and not result["missing_setup_sources"] and result["integration"]["indexed_commit"] == lock["integration"]["published_commit"]
    print(json.dumps(result, indent=2))
    return 0 if result.get("passed", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
