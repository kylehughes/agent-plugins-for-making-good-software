#!/usr/bin/env python3
"""Create the disposable evaluation baseline and its dirty change exactly once."""
import os
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parent
if (root / ".git").exists():
    print("Already bootstrapped; leaving the working tree unchanged.")
    raise SystemExit(0)
env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
           GIT_AUTHOR_NAME="Fixture Author", GIT_AUTHOR_EMAIL="fixture@example.invalid",
           GIT_COMMITTER_NAME="Fixture Author", GIT_COMMITTER_EMAIL="fixture@example.invalid",
           GIT_AUTHOR_DATE="2026-01-01T00:00:00+00:00",
           GIT_COMMITTER_DATE="2026-01-01T00:00:00+00:00")
def git(*args):
    subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgSign=false",
                    *args], cwd=root, env=env, check=True)
git("init", "--initial-branch=main", "--template=")
git("add", "--all")
git("commit", "--no-verify", "-m", "Add cart fixture baseline")
source = root / "Sources/Quantity.swift"
source.write_text(source.read_text().replace('result.append("Item: " + name)', 'let line = "Item: " + name\n            let copy = line\n            result.append(copy)'))
print("Disposable baseline created; inspect git diff HEAD for the owned change.")
