#!/usr/bin/env python3
"""Offline token cross-check — not authoritative (see METRICS.md)."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def estimate_tokens(text: str) -> int:
    stripped = text.strip()
    if not stripped:
        return 0
    return max(1, len(stripped) // 4)


def estimate_turn(
    pattern: str,
    scope: str,
    output_text: str,
    *,
    include_skill: bool,
    skill_tokens: int,
) -> dict[str, int]:
    user_prompt = f"Search for literal pattern {pattern!r} under {scope!r} (cap 50 lines)."
    tool_in = json.dumps({"pattern": pattern, "path": scope, "head_limit": 50}, separators=(",", ":"))
    reply = f"Found {len(output_text.splitlines())} lines (capped at 50)."

    tok_skill = skill_tokens if include_skill else 0
    tok_tool_in = estimate_tokens(user_prompt) + estimate_tokens(tool_in)
    tok_tool_out = estimate_tokens(output_text)
    tok_reply = estimate_tokens(reply)
    tok_total = tok_skill + tok_tool_in + tok_tool_out + tok_reply
    return {
        "tok_skill": tok_skill,
        "tok_tool_in": tok_tool_in,
        "tok_tool_out": tok_tool_out,
        "tok_reply": tok_reply,
        "tok_total": tok_total,
    }


def read_agent_totals(results_dir: Path, path_label: str, suites: set[str]) -> dict[str, int]:
    mapping = {
        "A": "agent-a-results.csv",
        "C": "agent-c-results.csv",
        "D": "agent-d-results.csv",
    }
    csv_path = results_dir / mapping[path_label]
    if not csv_path.is_file():
        return {}
    totals: dict[str, int] = {}
    with csv_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            suite = row.get("suite", "")
            if suite not in suites:
                continue
            try:
                totals[suite] = int(str(row.get("tok_total", "")).strip())
            except ValueError:
                continue
    return totals


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Cross-check offline token estimates against shell outputs."
    )
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, default=None)
    parser.add_argument("--skill-tokens", type=int, default=2700)
    args = parser.parse_args()

    summary_path = args.run_dir / "timing-summary.json"
    if not summary_path.is_file():
        raise SystemExit(f"timing-summary.json not found in {args.run_dir}")

    bench_dir = Path(__file__).resolve().parent
    results_dir = args.results_dir or (bench_dir / "results")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    cross_checks: list[dict[str, object]] = []

    agent_a = read_agent_totals(results_dir, "A", {"L1", "L3", "L7"})
    agent_c = read_agent_totals(results_dir, "C", {"L1", "L3", "L7"})
    agent_d = read_agent_totals(results_dir, "D", {"L1", "L3", "L7"})

    offline_specs = (
        ("rg", "A-offline", "A", False),
        ("preferred-host", "D-offline", "D", False),
        ("fast-grep", "C-offline", "C", True),
    )

    for task in summary.get("tasks", []):
        task_id = task["task_id"]
        pattern = task["pattern"]
        scope = task["path"]
        for path_key, label, agent_key, include_skill in offline_specs:
            rel = task[path_key]["output_file"]
            out_file = bench_dir / rel
            text = out_file.read_text(encoding="utf-8") if out_file.is_file() else ""
            est = estimate_turn(
                pattern,
                scope,
                text,
                include_skill=include_skill,
                skill_tokens=args.skill_tokens,
            )
            agent_map = {"A": agent_a, "C": agent_c, "D": agent_d}[agent_key]
            agent_total = agent_map.get(task_id)
            delta = None
            if agent_total is not None:
                delta = agent_total - est["tok_total"]
            cross_checks.append(
                {
                    "task_id": task_id,
                    "label": label,
                    "offline_tok_total": est["tok_total"],
                    "agent_tok_total": agent_total,
                    "delta_agent_minus_offline": delta,
                    "note": "delta is sanity check only; agent cursor-usage is authoritative",
                    **est,
                }
            )

    payload = {
        "run_dir": str(args.run_dir),
        "authoritative_token_source": "cursor-usage in agent CSV files",
        "purpose": "cross_check_only",
        "cross_checks": cross_checks,
    }

    out_path = args.run_dir / "token-cross-check.json"
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
