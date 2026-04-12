#!/usr/bin/env python3
import argparse
import json


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    args = ap.parse_args()

    # Simulate a deterministic workload
    with open(args.input, "r", encoding="utf-8") as f:
        obj = json.load(f)

    # Do some repeatable CPU work (still tiny)
    s = 0
    for item in obj.get("items", []):
        s += int(item.get("value", 0))

    # Keep stdout quiet for harness; real benchmarks can print if you remove DEVNULL in harness.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


