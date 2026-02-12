from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ansimon_ai.eval.runner_v0 import load_evalset_v0, run_evalset_v0

def _default_evalset_path(suite: str) -> Path:
    suite = suite.strip().lower()
    if suite in {"smoke", "eval_smoke_v0"}:
        return Path("data/evalsets/v0/eval_smoke_v0.json")
    if suite in {"full", "eval_full_v0"}:
        return Path("data/evalsets/v0/eval_full_v0.json")

    p = Path(suite)
    if p.exists():
        return p

    raise SystemExit(f"unknown suite: {suite}")

def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Run evaluation set v0")
    parser.add_argument(
        "--suite",
        default="full",
        help="smoke|full or path to evalset json (default: full)",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="optional output path (jsonl)",
    )
    args = parser.parse_args(argv)

    evalset_path = _default_evalset_path(args.suite)
    evalset = load_evalset_v0(evalset_path)

    class _MemoryCache(dict):
        def get(self, key):
            return super().get(key)

        def set(self, key, value):
            self[key] = value

    cache = _MemoryCache()

    results = run_evalset_v0(evalset=evalset, cache=cache)

    fail_count = sum(1 for r in results if r.status == "fail")
    warn_count = sum(1 for r in results if r.status == "warn")
    pass_count = sum(1 for r in results if r.status == "pass")

    for r in results:
        usage = r.usage_metrics
        print(
            f"{r.case_id} {r.status.upper()} "
            f"duration_ms={usage.duration_ms} input_chars={usage.input_chars} "
            f"output_chars={usage.output_chars} cache_hit={usage.cache_hit} "
            f"reason_codes={r.reason_codes}"
        )

    print(
        f"\nSummary: pass={pass_count} warn={warn_count} fail={fail_count} "
        f"(suite={evalset.name}, cases={len(results)})"
    )

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            for r in results:
                f.write(json.dumps(r.to_dict(), ensure_ascii=False) + "\n")

    return 1 if fail_count > 0 else 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))