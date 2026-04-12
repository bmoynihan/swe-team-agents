#!/usr/bin/env sh
set -eu

# BENCH_FIXTURE is set by the harness when --fixture is provided (or by benchmark.json fixture).
: "${BENCH_FIXTURE:?BENCH_FIXTURE is required}"

python3 target.py --input "$BENCH_FIXTURE"

