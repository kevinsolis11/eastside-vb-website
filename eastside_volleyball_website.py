#!/usr/bin/env python3
"""
Small helper runner for the project — safe to execute.

This script intentionally keeps behavior minimal: it prints Python
version, current working directory, and whether a virtualenv is
active. It exits with code 0.
"""
import sys
import platform
import os


def main() -> int:
    print("Runner: eastside_volleyball_website.py")
    print("Python:", sys.executable)
    print("Version:", platform.python_version())
    print("CWD:", os.getcwd())
    venv = os.environ.get("VIRTUAL_ENV") or os.environ.get("CONDA_PREFIX")
    print("Virtualenv:", venv or "(none)")
    print("Arguments:", sys.argv[1:])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
