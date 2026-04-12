#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / ".github" / "skills" / "autoagent-loop" / "scripts" / "autoagent_loop.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("repo_autoagent_loop", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = _load_module()
    return module.main()


if __name__ == "__main__":
    raise SystemExit(main())
