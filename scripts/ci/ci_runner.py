#!/usr/bin/env python
from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[2]


def get_python_bin() -> str:
    return os.environ.get("PYTHON_BIN") or sys.executable or "python"


def normalized_env() -> dict[str, str]:
    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH", "")
    prefix = "src"
    if not pythonpath:
        env["PYTHONPATH"] = prefix
    else:
        parts = pythonpath.split(os.pathsep)
        if prefix not in parts:
            env["PYTHONPATH"] = os.pathsep.join([prefix, pythonpath])
    return env


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def format_command(args: Sequence[str]) -> str:
    values = [str(arg) for arg in args]
    if os.name == "nt":
        return subprocess.list2cmdline(values)
    return " ".join(shlex.quote(value) for value in values)


def run_command(args: Sequence[str], *, env: dict[str, str] | None = None) -> None:
    command = [str(arg) for arg in args]
    print(f"+ {format_command(command)}")
    result = subprocess.run(command, cwd=ROOT, env=env, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def run_optional(
    command_name: str, args: Sequence[str], *, env: dict[str, str] | None = None
) -> None:
    if command_exists(command_name):
        run_command(args, env=env)
    else:
        print(f"! skip ({command_name} not installed)")


def config_file_contains(path: Path, token: str) -> bool:
    if not path.exists():
        return False
    return token in path.read_text(encoding="utf-8", errors="replace")


def mypy_configured() -> bool:
    return any(
        [
            (ROOT / "mypy.ini").exists(),
            config_file_contains(ROOT / "pyproject.toml", "[tool.mypy]"),
            config_file_contains(ROOT / "setup.cfg", "[mypy]"),
        ]
    )


def python_script(script_name: str) -> list[str]:
    return [get_python_bin(), str(ROOT / "scripts" / "ci" / script_name)]


def pytest_supports_cov(*, env: dict[str, str]) -> bool:
    result = subprocess.run(
        ["pytest", "--help"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and "--cov" in result.stdout


def pytest_has_marker(marker: str, *, env: dict[str, str]) -> bool:
    result = subprocess.run(
        ["pytest", "--markers"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and marker in result.stdout


def env_flag(name: str) -> bool:
    return os.environ.get(name, "0").strip().lower() in {"1", "true", "yes", "on"}


def split_args(value: str) -> list[str]:
    return [part for part in shlex.split(value) if part]


def first_party_python_targets() -> list[str]:
    configured = os.environ.get("RUFF_TARGETS")
    if configured:
        return split_args(configured)

    candidates = [ROOT / "src", ROOT / "scripts", ROOT / "tests"]
    return [path.name for path in candidates if path.exists()]


def existing_path(paths: Iterable[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def pytest_basetemp(default_name: str) -> Path:
    configured = os.environ.get("PYTEST_BASETEMP")
    if configured:
        path = Path(configured)
        return path if path.is_absolute() else ROOT / path
    return ROOT / ".pytest_tmp" / default_name
