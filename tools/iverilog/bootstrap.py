#!/usr/bin/env python3
"""Build reviewed Icarus source locally; no sudo, global install or implicit run."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    sys.path.insert(0, str(root))
    from tooling.bootstrap import load_lock, safe_path
    config = load_lock(root)["tools"]["iverilog"]
    directory = safe_path(root, config["root"])
    source = safe_path(root, config["root"] + "/source")
    dependencies = safe_path(root, config["root"] + "/build-dependencies")
    extracted = safe_path(root, config["root"] + "/build-dependencies/root")
    installed = safe_path(root, config["root"] + "/installed")
    commands = [
        ["git", "clone", "--depth", "1", "--branch", config["source_tag"], config["source_url"], str(source)],
        ["apt-get", "download", *config["build_packages"]],
        ["sh", "autoconf.sh"],
        ["./configure", "--prefix=" + str(installed)],
        ["make", "-j2"], ["make", "install"],
    ]
    if not args.execute:
        print(json.dumps({"executed": False, "platform": "Debian/Ubuntu Linux", "source_commit": config["source_commit"], "commands": commands}, indent=2))
        return 0
    if not sys.platform.startswith("linux"):
        parser.error("this reviewed local Icarus build supports Debian/Ubuntu Linux only")
    directory.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        subprocess.run(commands[0], check=True)
    actual = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    if actual != config["source_commit"]:
        raise ValueError("Icarus source is not the exact reviewed commit; preserve existing checkout")
    dirty = subprocess.check_output(["git", "-C", str(source), "status", "--porcelain", "--untracked-files=no"], text=True)
    if dirty.strip():
        raise ValueError("Icarus source has tracked changes; preserve them")
    dependencies.mkdir(exist_ok=True)
    subprocess.run(commands[1], cwd=dependencies, check=True)
    archives = sorted(dependencies.glob("*.deb"))
    if not archives:
        raise ValueError("no declared distro build dependencies downloaded")
    for archive in archives:
        subprocess.run(["dpkg-deb", "-x", str(archive), str(extracted)], check=True)
    environment = dict(os.environ)
    environment["PATH"] = str(extracted / "usr/bin") + os.pathsep + environment.get("PATH", "")
    environment["BISON_PKGDATADIR"] = str(extracted / "usr/share/bison")
    environment["M4"] = str(extracted / "usr/bin/m4")
    for command in commands[2:]:
        subprocess.run(command, cwd=source, env=environment, check=True)
    print("PASS: exact-source local Icarus install; no platform qualification claim")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
