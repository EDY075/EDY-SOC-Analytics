"""Fail CI when generation changes tracked files or creates untracked files."""

from __future__ import annotations

import subprocess
import sys


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def main() -> int:
    # Keep diagnostics printable on Windows runners whose inherited console
    # encoding cannot represent report labels such as the event → alert chain.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

    diff = git("diff", "--exit-code", "--", ".")
    status = git("status", "--porcelain=v1", "--untracked-files=all")

    if diff.returncode not in {0, 1}:
        print(diff.stderr or diff.stdout)
        return diff.returncode
    if status.returncode != 0:
        print(status.stderr or status.stdout)
        return status.returncode

    if diff.returncode == 1 or status.stdout.strip():
        print("The reproducible validation left the Git worktree dirty.")
        if diff.stdout:
            print(diff.stdout)
        if status.stdout:
            print(status.stdout)
        return 1

    print("Tracked and untracked Git inventory is clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
