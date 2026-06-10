#!/usr/bin/env python3
"""Validate benchmark artifacts against precision requirements."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


REQUIRED_AGENT_ROWS = {
    "A": {"L1", "L3", "L7"},
    "B": {"S1", "S2", "S3"},
    "C": {"L1", "L3", "L7"},
    "D": {"L1", "L3", "L7"},
}

REQUIRED_FIELDS = [
    "run_id",
    "path",
    "suite",
    "tool_engine",
    "T_tool_ms",
    "T_tool_source",
    "T_turn_ms",
    "tok_total",
    "tok_source",
    "hits_returned",
    "correct_top1",
]

T_TOOL_SOURCE = {
    "A": {"agent-grep-timed"},
    "B": {"semantic-search-timed"},
    "C": {"hyperfine-mean"},
    "D": {"hyperfine-mean"},
}

TOK_SOURCES = {"cursor-usage", "agent-usage"}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate fast-grep benchmark results.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=None,
        help="Directory with agent CSV files",
    )
    args = parser.parse_args()

    bench_dir = Path(__file__).resolve().parent
    results_dir = args.results_dir or (bench_dir / "results")
    errors: list[str] = []

    tasks_path = args.run_dir / "pilot-tasks.json"
    if tasks_path.is_file():
        config = json.loads(tasks_path.read_text(encoding="utf-8"))
        precision = config.get("precision", {})
        agent_tasks = precision.get("agent_tasks", REQUIRED_AGENT_ROWS)
        hyperfine_required = bool(precision.get("hyperfine_required", True))
    else:
        agent_tasks = REQUIRED_AGENT_ROWS
        hyperfine_required = True

    timing_path = args.run_dir / "timing-summary.json"
    if not timing_path.is_file():
        errors.append(f"missing timing-summary.json in {args.run_dir}")
    else:
        timing = json.loads(timing_path.read_text(encoding="utf-8"))
        for task in timing.get("tasks", []):
            tid = task["task_id"]
            if hyperfine_required and not task.get("hyperfine_json"):
                errors.append(f"missing hyperfine json for task {tid}")
            for engine in ("rg", "fast-grep", "preferred-host"):
                if hyperfine_required and "T_tool_ms" not in task.get(engine, {}):
                    errors.append(f"missing hyperfine T_tool_ms for {tid}/{engine}")

    agents = {
        "A": results_dir / "agent-a-results.csv",
        "B": results_dir / "agent-b-results.csv",
        "C": results_dir / "agent-c-results.csv",
        "D": results_dir / "agent-d-results.csv",
    }

    for label, csv_path in agents.items():
        rows = read_csv(csv_path)
        expected = set(agent_tasks.get(label, REQUIRED_AGENT_ROWS[label]))
        found = {row.get("suite", "").strip() for row in rows if row.get("suite")}
        missing_tasks = expected - found
        if missing_tasks:
            errors.append(f"agent {label}: missing suites {sorted(missing_tasks)}")
        if not rows and expected:
            errors.append(f"agent {label}: no rows in {csv_path}")

        for row in rows:
            suite = row.get("suite", "")
            if suite not in expected:
                continue
            for field in REQUIRED_FIELDS:
                if not str(row.get(field, "")).strip():
                    errors.append(f"agent {label} {suite}: missing {field}")
            tok_source = row.get("tok_source", "")
            if tok_source not in TOK_SOURCES:
                errors.append(
                    f"agent {label} {suite}: tok_source must be agent-usage or cursor-usage "
                    f"(got {tok_source!r})"
                )
            t_source = row.get("T_tool_source", "")
            allowed = T_TOOL_SOURCE[label]
            if t_source not in allowed:
                errors.append(
                    f"agent {label} {suite}: T_tool_source must be one of {sorted(allowed)} "
                    f"(got {t_source!r})"
                )
            if label == "C" and row.get("tok_skill", "").strip() and suite != "L1":
                # warn only — allow non-zero but note
                pass

    if errors:
        print("validate-results: FAILED", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print("validate-results: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
