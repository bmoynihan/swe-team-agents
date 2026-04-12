# Bench Harness (language-agnostic)

This folder contains a small, deterministic benchmark harness that can run *any* command and emit JSON results.

## Conventions
- Benchmarks should be deterministic (use fixtures under `bench/fixtures/`).
- Avoid network calls. Prefer hermetic inputs.
- Use warmups to stabilize JIT/GC/caches when applicable.

## Quick start (single benchmark)
```bash
python3 bench/harness/bench.py \
  --name example-parse \
  --warmup 3 \
  --runs 10 \
  --fixture bench/fixtures/example/input.json \
  -- \
  python3 bench/benchmarks/example/target.py --input "$BENCH_FIXTURE"
```

