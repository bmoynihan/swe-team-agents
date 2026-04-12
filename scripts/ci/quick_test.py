#!/usr/bin/env python
from __future__ import annotations

import os

from ci_runner import (
    ROOT,
    command_exists,
    first_party_python_targets,
    get_python_bin,
    mypy_configured,
    normalized_env,
    pytest_basetemp,
    python_script,
    run_command,
    run_optional,
)


def main() -> None:
    print("== quick_test ==")

    env = normalized_env()
    pytest_mark_expr = os.environ.get(
        "PYTEST_MARK_EXPR", "not slow and not integration and not e2e"
    )
    python_bin = get_python_bin()
    python_targets = first_party_python_targets()
    mypy_targets = [
        target
        for target in python_targets
        if any((ROOT / target).rglob("*.py")) or any((ROOT / target).rglob("*.pyi"))
    ]

    run_command([python_bin, "-m", "compileall", "-q", "."], env=env)

    path_guard = ROOT / "scripts" / "ci" / "check_agent_paths.py"
    if path_guard.exists():
        run_command(python_script("check_agent_paths.py"), env=env)
    else:
        print("! skip (scripts/ci/check_agent_paths.py not found)")

    agent_guard = ROOT / "scripts" / "ci" / "check_agent_system.py"
    if agent_guard.exists():
        run_command([python_bin, str(agent_guard)], env=env)
    else:
        print("! skip (scripts/ci/check_agent_system.py not found)")

    run_optional("ruff", ["ruff", "format", "--check", *python_targets], env=env)
    run_optional("ruff", ["ruff", "check", *python_targets], env=env)

    if command_exists("mypy"):
        if mypy_configured():
            if mypy_targets:
                run_command(["mypy", *mypy_targets], env=env)
            else:
                print("! skip (no Python source files found for mypy targets)")
        else:
            print("! skip (mypy installed but no config detected)")
    else:
        print("! skip (mypy not installed)")

    if command_exists("pytest"):
        run_command(
            [
                "pytest",
                "--basetemp",
                str(pytest_basetemp("quick")),
                "-q",
                "-m",
                pytest_mark_expr,
            ],
            env=env,
        )
    else:
        print("! skip (pytest not installed)")

    print("== quick_test: PASS ==")


if __name__ == "__main__":
    main()
