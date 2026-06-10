#!/usr/bin/env python3
"""Append Path D (preferred-host / direct rg) timing to an existing run directory.

Re-runs hyperfine on each task's rg_cmd and merges results as preferred-host.
Documents supplement provenance in timing-summary.json.
"""

from __future__ import annotations

import argparse
import json
import shlex
import shutil
import subprocess
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

# Reuse helpers from run_pilot when executed from repo.
BENCH_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BENCH_DIR))
from run_pilot import (  # noqa: E402
    cap_lines,
    parse_hyperfine_stats,
    resolve_preferred_host,
    run_capture,
    run_hyperfine,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Append preferred-host (Path D) rg timing to an existing benchmark run."
    )
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument(
        "--derive-from-existing-rg",
        action="store_true",
        help="Copy existing rg hyperfine stats instead of re-running (same session only).",
    )
    parser.add_argument("--skip-hyperfine", action="store_true")
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    summary_path = run_dir / "timing-summary.json"
    if not summary_path.is_file():
        print(f"append_preferred_host: missing {summary_path}", file=sys.stderr)
        return 2

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    repo_root = Path(summary["repo_root"]).resolve()
    bench_dir = BENCH_DIR
    head_limit = int(summary.get("head_limit", 50))
    min_runs = int(summary.get("hyperfine_min_runs", 10))
    warmup = int(summary.get("hyperfine_warmup", 2))

    prefs_script = repo_root / "scripts/literal-search/fast-grep-prefs.sh"
    tool_id, binary, env_path = resolve_preferred_host(prefs_script)

    summary["preferred_host"] = {
        "tool_id": tool_id,
        "binary": binary,
        "fast_grep_env": env_path,
        "policy": "LITERAL-CODE-SEARCH.md — read fast-grep.env then host CLI directly",
    }
    summary.setdefault("T_tool_authoritative", {})["D"] = (
        "hyperfine mean on preferred host CLI (fast-grep.env policy)"
    )
    summary["path_d_supplement"] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "method": "derive-from-existing-rg" if args.derive_from_existing_rg else "hyperfine-rg-rerun",
        "note": (
            "preferred-host appended to prior run; compare fast-grep (same session) "
            "vs preferred-host (supplement) for wrapper overhead only."
        ),
    }

    precision = summary.get("precision", {})
    agent_tasks = precision.setdefault("agent_tasks", {})
    agent_tasks.setdefault("D", ["L1", "L3", "L7"])

    for task in summary.get("tasks", []):
        if "rg_cmd" not in task:
            print(f"append_preferred_host: task {task.get('task_id')} missing rg_cmd", file=sys.stderr)
            return 2

        rg_cmd = task["rg_cmd"]
        task["preferred_host_cmd"] = list(rg_cmd)
        task["preferred_tool_id"] = tool_id
        task["preferred_binary"] = binary

        if args.derive_from_existing_rg:
            ph = deepcopy(task["rg"])
            ph["T_tool_source"] = "hyperfine-mean-derived-from-rg"
            ph["note"] = "Path D equivalent to rg when preferred=ripgrep; copied from same-session rg row"
            task["preferred-host"] = ph
            rel = task["rg"]["output_file"]
            src = bench_dir / rel
            dest_rel = rel.replace("-rg.txt", "-preferred-host.txt")
            dest = bench_dir / dest_rel
            if src.is_file():
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
                task["preferred-host"]["output_file"] = dest_rel
            continue

        code, raw_output, elapsed_ms = run_capture(rg_cmd, repo_root)
        capped, total_lines, was_capped = cap_lines(raw_output, head_limit)
        rel_out = f"results/{run_dir.name}/out/{task['task_id']}-preferred-host.txt"
        out_file = bench_dir / rel_out
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(capped, encoding="utf-8")

        ph_entry: dict = {
            "exit_code": code,
            "T_tool_ms_single_run": round(elapsed_ms, 2),
            "T_tool_ms_single_run_note": "fallback only — use hyperfine mean when present",
            "hits_returned": total_lines,
            "hits_capped": was_capped,
            "output_file": rel_out,
            "T_tool_source": "hyperfine-mean-supplement",
        }
        task["preferred-host"] = ph_entry

        if not args.skip_hyperfine:
            timing_json = run_dir / "timing" / f"{task['task_id']}-preferred-host-hyperfine.json"
            timing_json.parent.mkdir(parents=True, exist_ok=True)
            if run_hyperfine(
                [("preferred-host", rg_cmd)],
                repo_root,
                min_runs,
                warmup,
                timing_json,
            ):
                hf = parse_hyperfine_stats(timing_json, ["preferred-host"])
                if "preferred-host" in hf:
                    ph_entry["T_tool_ms"] = hf["preferred-host"]["T_tool_ms_mean"]
                    ph_entry["hyperfine"] = hf["preferred-host"]
                    ph_entry["hyperfine_json"] = str(
                        Path("results") / run_dir.name / "timing" / timing_json.name
                    )
            else:
                print(
                    f"append_preferred_host: hyperfine failed for {task['task_id']}",
                    file=sys.stderr,
                )
                return 2

        print(
            f"{task['task_id']}: preferred-host="
            f"{ph_entry.get('T_tool_ms', ph_entry['T_tool_ms_single_run'])}ms "
            f"(fast-grep same session={task['fast-grep'].get('T_tool_ms', '?')}ms)",
            file=sys.stderr,
        )

    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
