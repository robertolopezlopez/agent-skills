#!/usr/bin/env python3
"""Merge precision benchmark artifacts into REPORT.md."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read_agent_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sum_tok(rows: list[dict[str, str]]) -> int:
    total = 0
    for row in rows:
        if row.get("tok_source") not in ("cursor-usage", "agent-usage", "estimated-cross-check"):
            continue
        try:
            total += int(str(row.get("tok_total", "")).strip())
        except ValueError:
            continue
    return total


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge benchmark run artifacts.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, default=None)
    args = parser.parse_args()

    bench_dir = Path(__file__).resolve().parent
    results_dir = args.results_dir or (bench_dir / "results")

    timing_path = args.run_dir / "timing-summary.json"
    cross_path = args.run_dir / "token-cross-check.json"
    timing = json.loads(timing_path.read_text(encoding="utf-8")) if timing_path.is_file() else {}
    cross = json.loads(cross_path.read_text(encoding="utf-8")) if cross_path.is_file() else {}

    agents = {
        "A": read_agent_csv(results_dir / "agent-a-results.csv"),
        "B": read_agent_csv(results_dir / "agent-b-results.csv"),
        "C": read_agent_csv(results_dir / "agent-c-results.csv"),
    }

    report = {
        "run_dir": str(args.run_dir),
        "methodology": "precision-first per METRICS.md",
        "timing_summary": timing,
        "token_cross_check": cross,
        "agent_results": agents,
        "authoritative_totals": {
            "tok_total_A_cursor_usage": sum_tok(agents["A"]),
            "tok_total_B_cursor_usage": sum_tok(agents["B"]),
            "tok_total_C_cursor_usage": sum_tok(agents["C"]),
        },
    }

    out_json = args.run_dir / "merged-report.json"
    out_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# fast-grep benchmark report (precision-first)",
        "",
        f"Run directory: `{args.run_dir}`",
        "",
        "Authoritative sources: see `METRICS.md`.",
        "",
        "## T_tool — engine reference (hyperfine mean, ms)",
        "",
        "| Task | rg mean | rg σ | fast-grep mean | fast-grep σ | rg hits |",
        "|------|---------|------|----------------|-------------|---------|",
    ]

    for task in timing.get("tasks", []):
        rg = task.get("rg", {})
        fg = task.get("fast-grep", {})
        rg_hf = rg.get("hyperfine", {})
        fg_hf = fg.get("hyperfine", {})
        lines.append(
            f"| {task['task_id']} | {rg.get('T_tool_ms', '')} | {rg_hf.get('T_tool_ms_stddev', '')} | "
            f"{fg.get('T_tool_ms', '')} | {fg_hf.get('T_tool_ms_stddev', '')} | "
            f"{rg.get('hits_returned', '')} |"
        )

    lines.extend(
        [
            "",
            "## T_tool / T_turn / tokens — agent paths (authoritative)",
            "",
            f"- **A** agent Grep `tok_total`: **{report['authoritative_totals']['tok_total_A_cursor_usage']}**",
            f"- **B** semantic `tok_total` (cursor-usage): **{report['authoritative_totals']['tok_total_B_cursor_usage']}**",
            f"- **C** fast-grep `tok_total` (cursor-usage): **{report['authoritative_totals']['tok_total_C_cursor_usage']}**",
            "",
        ]
    )

    if cross:
        lines.append("## Token cross-check (offline vs agent)")
        lines.append("")
        for row in cross.get("cross_checks", []):
            if row.get("agent_tok_total") is None:
                continue
            lines.append(
                f"- {row['task_id']} {row['label']}: agent={row['agent_tok_total']} "
                f"offline={row['offline_tok_total']} delta={row['delta_agent_minus_offline']}"
            )
        lines.append("")

    for label, rows in (("A", agents["A"]), ("B", agents["B"]), ("C", agents["C"])):
        lines.append(f"## Agent {label} ({len(rows)} rows)")
        lines.append("")
        if not rows:
            lines.append("_No rows — run the agent prompt._")
        else:
            header = list(rows[0].keys())
            lines.append("| " + " | ".join(header) + " |")
            lines.append("| " + " | ".join("---" for _ in header) + " |")
            for row in rows:
                lines.append("| " + " | ".join(row.get(h, "") for h in header) + " |")
        lines.append("")

    out_md = args.run_dir / "REPORT.md"
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
