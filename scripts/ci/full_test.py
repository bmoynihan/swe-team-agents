#!/usr/bin/env python
from __future__ import annotations

import os

from ci_runner import (
    ROOT,
    command_exists,
    env_flag,
    existing_path,
    normalized_env,
    pytest_basetemp,
    pytest_has_marker,
    pytest_supports_cov,
    python_script,
    run_command,
    split_args,
)


def main() -> None:
    print("== full_test ==")

    env = normalized_env()
    pytest_args = split_args(os.environ.get("PYTEST_ARGS_FULL", "-q"))
    cov_target = os.environ.get("COV_TARGET", "src")

    run_command(python_script("quick_test.py"), env=env)

    if not command_exists("pytest"):
        print("! ERROR: pytest is not installed; cannot run full suite")
        raise SystemExit(1)

    if env_flag("COVERAGE"):
        if pytest_supports_cov(env=env):
            run_command(
                [
                    "pytest",
                    "--basetemp",
                    str(pytest_basetemp("full")),
                    *pytest_args,
                    f"--cov={cov_target}",
                    "--cov-report=term-missing",
                ],
                env=env,
            )
        else:
            print("! WARNING: COVERAGE=1 but pytest-cov not available; running without coverage")
            run_command(
                ["pytest", "--basetemp", str(pytest_basetemp("full")), *pytest_args], env=env
            )
    else:
        run_command(["pytest", "--basetemp", str(pytest_basetemp("full")), *pytest_args], env=env)

    if env_flag("RUN_INTEGRATION"):
        print("== integration_tests ==")
        if pytest_has_marker("integration", env=env):
            run_command(
                [
                    "pytest",
                    "--basetemp",
                    str(pytest_basetemp("integration")),
                    "-q",
                    "-m",
                    "integration",
                ],
                env=env,
            )
        elif (ROOT / "tests" / "integration").exists():
            run_command(
                [
                    "pytest",
                    "--basetemp",
                    str(pytest_basetemp("integration")),
                    "-q",
                    "tests/integration",
                ],
                env=env,
            )
        else:
            print(
                "! WARNING: RUN_INTEGRATION=1 but no integration marker or "
                "tests/integration directory found"
            )

    if env_flag("RUN_E2E"):
        print("== e2e_tests ==")
        runner = existing_path(
            [
                ROOT / "scripts" / "e2e" / "run.ps1",
                ROOT / "scripts" / "e2e.ps1",
                ROOT / "scripts" / "e2e" / "run.sh",
                ROOT / "scripts" / "e2e.sh",
            ]
        )
        if runner is None:
            print("! WARNING: RUN_E2E=1 but no e2e runner found")
        elif runner.suffix.lower() == ".ps1":
            run_command(["pwsh", "-NoLogo", "-NoProfile", "-File", str(runner)], env=env)
        else:
            run_command([str(runner)], env=env)

    print("== full_test: PASS ==")


if __name__ == "__main__":
    main()
