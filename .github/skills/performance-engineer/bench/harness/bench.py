#!/usr/bin/env python3
"""
Language-agnostic benchmark harness.

- Runs any command multiple times (warmups + measured runs)
- Passes fixture path via BENCH_FIXTURE env var
- Emits a single JSON result per benchmark run

Examples:
    python3 bench/harness/bench.py --name foo --warmup 3 --runs 10 \
        --fixture bench/fixtures/x.json -- mycmd --arg 1
  python3 bench/harness/bench.py --suite bench/benchmarks --default-warmup 3 --default-runs 10
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


def _now_ns() -> int:
    return time.perf_counter_ns()


def _percentile(sorted_vals: Sequence[float], p: float) -> float:
    # p in [0, 100]
    if not sorted_vals:
        return float("nan")
    if p <= 0:
        return float(sorted_vals[0])
    if p >= 100:
        return float(sorted_vals[-1])
    k = (len(sorted_vals) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return float(sorted_vals[f])
    d0 = sorted_vals[f] * (c - k)
    d1 = sorted_vals[c] * (k - f)
    return float(d0 + d1)


def _env_fingerprint() -> Dict[str, Any]:
    return {
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "cwd": os.getcwd(),
        "cpu_count": os.cpu_count(),
    }


def _try_max_rss_kb() -> Optional[int]:
    # Best-effort on Unix. None on Windows.
    try:
        import resource  # type: ignore

        usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        # Linux: ru_maxrss is KB; macOS: bytes. Normalize to KB.
        maxrss = int(usage.ru_maxrss)
        if sys.platform == "darwin":
            maxrss = max(0, maxrss // 1024)
        return maxrss
    except Exception:
        return None


def _run_once(cmd: List[str], env: Dict[str, str], cwd: Optional[str]) -> Tuple[int, int]:
    """
    Returns: (returncode, elapsed_ns)
    """
    start = _now_ns()
    p = subprocess.run(
        cmd,
        env=env,
        cwd=cwd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    end = _now_ns()
    return p.returncode, end - start


@dataclass
class BenchmarkDef:
    name: str
    command: List[str]
    cwd: Optional[str] = None
    env: Dict[str, str] = None  # type: ignore
    fixture: Optional[str] = None
    warmup: int = 3
    runs: int = 10


def _load_benchmark_json(path: Path, default_warmup: int, default_runs: int) -> BenchmarkDef:
    data = json.loads(path.read_text(encoding="utf-8"))

    if "name" not in data:
        raise ValueError(f"{path}: missing required field 'name'")
    if "command" not in data:
        raise ValueError(f"{path}: missing required field 'command'")

    name = str(data["name"])

    cmd_raw = data["command"]
    if isinstance(cmd_raw, str):
        # Allow string command, but run via shell is discouraged; we keep it explicit:
        # Convert to ["bash","-lc", cmd] if bash exists, else ["sh","-lc", cmd]
        shell = "bash" if shutil.which("bash") else "sh"
        command = [shell, "-lc", cmd_raw]
    elif isinstance(cmd_raw, list) and all(isinstance(x, str) for x in cmd_raw):
        command = list(cmd_raw)
    else:
        raise ValueError(f"{path}: 'command' must be a string or list[str]")

    cwd = str(data["cwd"]) if "cwd" in data else str(path.parent)

    env = {}
    if isinstance(data.get("env"), dict):
        env = {str(k): str(v) for k, v in data["env"].items()}

    fixture = None
    if "fixture" in data and data["fixture"] is not None:
        fixture = str(data["fixture"])
        # Make fixture relative to the benchmark.json directory if it is relative
        if not os.path.isabs(fixture):
            fixture = str((path.parent / fixture).resolve())

    warmup = int(data.get("warmup", default_warmup))
    runs = int(data.get("runs", default_runs))

    return BenchmarkDef(
        name=name,
        command=command,
        cwd=cwd,
        env=env,
        fixture=fixture,
        warmup=warmup,
        runs=runs,
    )


def _benchmark(defn: BenchmarkDef) -> Dict[str, Any]:
    env = os.environ.copy()
    env.update(defn.env or {})

    if defn.fixture:
        env["BENCH_FIXTURE"] = defn.fixture

    # Warmups
    warmup_codes: List[int] = []
    for _ in range(max(0, defn.warmup)):
        rc, _elapsed = _run_once(defn.command, env=env, cwd=defn.cwd)
        warmup_codes.append(rc)

    # Measured runs
    samples_ns: List[int] = []
    run_codes: List[int] = []
    for _ in range(max(1, defn.runs)):
        rc, elapsed = _run_once(defn.command, env=env, cwd=defn.cwd)
        run_codes.append(rc)
        samples_ns.append(int(elapsed))

    max_rss_kb = _try_max_rss_kb()

    # Stats
    samples_ms = [s / 1_000_000.0 for s in samples_ns]
    sorted_ms = sorted(samples_ms)

    mean_ms = statistics.mean(samples_ms) if samples_ms else float("nan")
    median_ms = statistics.median(samples_ms) if samples_ms else float("nan")
    stdev_ms = statistics.pstdev(samples_ms) if len(samples_ms) > 1 else 0.0
    p95_ms = _percentile(sorted_ms, 95.0)
    p99_ms = _percentile(sorted_ms, 99.0)

    status = "ok"
    if any(rc != 0 for rc in run_codes):
        status = "command_failed"
    elif any(rc != 0 for rc in warmup_codes):
        status = "warmup_failed"

    return {
        "type": "BenchmarkResult",
        "name": defn.name,
        "status": status,
        "command": defn.command,
        "cwd": defn.cwd,
        "fixture": defn.fixture,
        "warmup": defn.warmup,
        "runs": defn.runs,
        "env": {
            "BENCH_FIXTURE": defn.fixture if defn.fixture else None,
        },
        "environment": _env_fingerprint(),
        "samples": {
            "elapsed_ns": samples_ns,
            "elapsed_ms": samples_ms,
        },
        "summary": {
            "mean_ms": mean_ms,
            "median_ms": median_ms,
            "stdev_ms": stdev_ms,
            "p95_ms": p95_ms,
            "p99_ms": p99_ms,
            "min_ms": float(sorted_ms[0]) if sorted_ms else float("nan"),
            "max_ms": float(sorted_ms[-1]) if sorted_ms else float("nan"),
            "max_rss_kb": max_rss_kb,
            "returncodes": {
                "warmup": warmup_codes,
                "runs": run_codes,
            },
        },
    }


def _iter_benchmark_json_files(suite_dir: Path) -> List[Path]:
    return sorted(p for p in suite_dir.rglob("benchmark.json") if p.is_file())


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", help="benchmark name (single-command mode)")
    ap.add_argument("--warmup", type=int, default=3, help="warmup runs (single-command mode)")
    ap.add_argument("--runs", type=int, default=10, help="measured runs (single-command mode)")
    ap.add_argument("--fixture", help="fixture path (single-command mode)")
    ap.add_argument("--cwd", help="working directory (single-command mode)")
    ap.add_argument("--out", help="also write JSON output to this path")
    ap.add_argument(
        "--suite", help="run all benchmarks under this directory (finds **/benchmark.json)"
    )
    ap.add_argument(
        "--default-warmup",
        type=int,
        default=3,
        help="default warmup for suite entries missing warmup",
    )
    ap.add_argument(
        "--default-runs", type=int, default=10, help="default runs for suite entries missing runs"
    )

    ap.add_argument("--", dest="sep", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument(
        "command", nargs=argparse.REMAINDER, help="command to run (single-command mode)"
    )

    args = ap.parse_args(argv)

    results: List[Dict[str, Any]] = []

    if args.suite:
        suite_dir = Path(args.suite).resolve()
        files = _iter_benchmark_json_files(suite_dir)
        if not files:
            print(
                json.dumps(
                    {
                        "type": "BenchmarkSuiteResult",
                        "status": "no_benchmarks_found",
                        "suite": str(suite_dir),
                        "message": "No benchmark.json files found under suite directory.",
                    },
                    indent=2,
                )
            )
            return 2

        for f in files:
            try:
                bd = _load_benchmark_json(f, args.default_warmup, args.default_runs)
                results.append(_benchmark(bd))
            except Exception as e:
                results.append(
                    {
                        "type": "BenchmarkResult",
                        "name": str(f),
                        "status": "definition_error",
                        "error": str(e),
                    }
                )

        suite_result = {
            "type": "BenchmarkSuiteResult",
            "status": "ok" if all(r.get("status") == "ok" for r in results) else "has_failures",
            "suite": str(suite_dir),
            "benchmarks": results,
        }

        out_json = json.dumps(suite_result, indent=2)
        print(out_json)
        if args.out:
            Path(args.out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.out).write_text(out_json + "\n", encoding="utf-8")
        return 0 if suite_result["status"] == "ok" else 3

    # Single-command mode
    if not args.name:
        ap.error("single-command mode requires --name (or use --suite)")
    if not args.command:
        ap.error("single-command mode requires a command after '--'")

    bd = BenchmarkDef(
        name=args.name,
        command=list(args.command),
        cwd=args.cwd,
        env={},
        fixture=str(Path(args.fixture).resolve()) if args.fixture else None,
        warmup=int(args.warmup),
        runs=int(args.runs),
    )

    result = _benchmark(bd)
    out_json = json.dumps(result, indent=2)
    print(out_json)

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(out_json + "\n", encoding="utf-8")

    return 0 if result.get("status") == "ok" else 4


if __name__ == "__main__":
    raise SystemExit(main())


