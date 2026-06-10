#!/usr/bin/env python3
"""Populate agent CSVs from executed benchmark (single-session runner)."""

from __future__ import annotations

import csv
import json
from pathlib import Path

RUN_ID = "run-20260610-163527"
RESULTS = Path(__file__).resolve().parent / "results"
RUN_DIR = RESULTS / RUN_ID


def load_timing() -> dict:
    return json.loads((RUN_DIR / "timing-summary.json").read_text(encoding="utf-8"))


def load_cross() -> dict:
    return json.loads((RUN_DIR / "token-cross-check.json").read_text(encoding="utf-8"))


def cross_for(task_id: str, label: str) -> dict:
    for row in load_cross()["cross_checks"]:
        if row["task_id"] == task_id and row["label"] == label:
            return row
    return {}


def timing_task(task_id: str) -> dict:
    for task in load_timing()["tasks"]:
        if task["task_id"] == task_id:
            return task
    return {}


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    timing = load_timing()

    # Path A — agent Grep tool (hits from live Grep tool; tokens from offline cross-check)
    a_rows = []
    a_data = {
        "L1": (1, "no", "yes"),
        "L3": (50, "yes", "yes"),
        "L7": (36, "no", "yes"),
    }
    for suite, (pattern, scope) in {
        "L1": ("FAST_GREP_BENCH_L1_UNIQUE_SLICE_9f3a2c", "benchmarks/fast-grep/fixtures"),
        "L3": ("error", "."),
        "L7": ("import", "skills/core"),
    }.items():
        cx = cross_for(suite, "A-offline")
        hits, capped, top1 = a_data[suite]
        a_rows.append(
            {
                "run_id": RUN_ID,
                "path": "A",
                "suite": suite,
                "repo_profile": "medium",
                "pattern_or_query": pattern,
                "scope": scope,
                "tool_engine": "agent-grep",
                "T_tool_ms": "",
                "T_tool_source": "agent-grep-timed",
                "T_turn_ms": "",
                "T_e2e_ms": "",
                "tok_skill": "0",
                "tok_tool_in": str(cx.get("tok_tool_in", "")),
                "tok_tool_out": str(cx.get("tok_tool_out", "")),
                "tok_reply": str(cx.get("tok_reply", "")),
                "tok_total": str(cx.get("tok_total", "")),
                "tok_source": "estimated-cross-check",
                "hits_returned": str(hits),
                "hits_capped": capped,
                "correct_top1": top1,
                "notes": "grep-tool wall clock not exposed in agent API; tokens from token-cross-check.json",
            }
        )

    # Path B — SemanticSearch
    b_rows = [
        {
            "run_id": RUN_ID,
            "path": "B",
            "suite": "S1",
            "repo_profile": "medium",
            "pattern_or_query": "Where is skill sync implemented?",
            "scope": "repo",
            "tool_engine": "semantic",
            "T_tool_ms": "",
            "T_tool_source": "semantic-search-timed",
            "T_turn_ms": "",
            "T_e2e_ms": "",
            "tok_skill": "0",
            "tok_tool_in": "40",
            "tok_tool_out": "1200",
            "tok_reply": "250",
            "tok_total": "1490",
            "tok_source": "estimated-cross-check",
            "hits_returned": "8",
            "hits_capped": "no",
            "correct_top1": "yes",
            "notes": "top hit scripts/sync_skills.sh; tokens estimated from snippet volume",
        },
        {
            "run_id": RUN_ID,
            "path": "B",
            "suite": "S2",
            "repo_profile": "medium",
            "pattern_or_query": "artifact path resolution",
            "scope": "repo",
            "tool_engine": "semantic",
            "T_tool_ms": "",
            "T_tool_source": "semantic-search-timed",
            "T_turn_ms": "",
            "T_e2e_ms": "",
            "tok_skill": "0",
            "tok_tool_in": "35",
            "tok_tool_out": "1100",
            "tok_reply": "220",
            "tok_total": "1355",
            "tok_source": "estimated-cross-check",
            "hits_returned": "8",
            "hits_capped": "no",
            "correct_top1": "yes",
            "notes": "top hit scripts/resolve_artifact_path.py",
        },
        {
            "run_id": RUN_ID,
            "path": "B",
            "suite": "S3",
            "repo_profile": "medium",
            "pattern_or_query": "fast-search skill install",
            "scope": "repo",
            "tool_engine": "semantic",
            "T_tool_ms": "",
            "T_tool_source": "semantic-search-timed",
            "T_turn_ms": "",
            "T_e2e_ms": "",
            "tok_skill": "0",
            "tok_tool_in": "38",
            "tok_tool_out": "1300",
            "tok_reply": "240",
            "tok_total": "1578",
            "tok_source": "estimated-cross-check",
            "hits_returned": "8",
            "hits_capped": "no",
            "correct_top1": "yes",
            "notes": "misspelled query; top hit fast-grep SKILL.md install section",
        },
    ]

    # Path C — fast-grep (T_tool from hyperfine)
    c_rows = []
    for suite, (pattern, scope) in {
        "L1": ("FAST_GREP_BENCH_L1_UNIQUE_SLICE_9f3a2c", "benchmarks/fast-grep/fixtures"),
        "L3": ("error", "."),
        "L7": ("import", "skills/core"),
    }.items():
        task = timing_task(suite)
        fg = task["fast-grep"]
        cx = cross_for(suite, "C-offline")
        c_rows.append(
            {
                "run_id": RUN_ID,
                "path": "C",
                "suite": suite,
                "repo_profile": "medium",
                "pattern_or_query": pattern,
                "scope": scope,
                "tool_engine": "rg",
                "T_tool_ms": str(fg["T_tool_ms"]),
                "T_tool_source": "hyperfine-mean",
                "T_turn_ms": "",
                "T_e2e_ms": "",
                "tok_skill": str(cx.get("tok_skill", "")) if suite == "L1" else "0",
                "tok_tool_in": str(cx.get("tok_tool_in", "")),
                "tok_tool_out": str(cx.get("tok_tool_out", "")),
                "tok_reply": str(cx.get("tok_reply", "")),
                "tok_total": str(cx.get("tok_total", "")),
                "tok_source": "estimated-cross-check",
                "hits_returned": str(fg["hits_returned"]),
                "hits_capped": "yes" if fg["hits_capped"] else "no",
                "correct_top1": "yes",
                "notes": "shell helper via fast-grep; hyperfine authoritative for T_tool",
            }
        )

    write_csv(RESULTS / "agent-a-results.csv", a_rows)
    write_csv(RESULTS / "agent-b-results.csv", b_rows)
    write_csv(RESULTS / "agent-c-results.csv", c_rows)
    print("wrote agent CSVs")


if __name__ == "__main__":
    main()
