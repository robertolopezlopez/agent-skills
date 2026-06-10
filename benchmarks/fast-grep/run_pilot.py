#!/usr/bin/env python3
"""Shell timing harness for the fast-grep benchmark pilot."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class LiteralTask:
    task_id: str
    description: str
    pattern: str
    path: str
    literal: bool
    ignore_case: bool


def repo_root_from_here() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def load_tasks(tasks_path: Path) -> dict[str, Any]:
    with tasks_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def resolve_path(base: Path, relative: str) -> Path:
    candidate = (base / relative).resolve()
    return candidate


def build_rg_cmd(task: LiteralTask) -> list[str]:
    cmd = ["rg", "--no-heading", "--line-number", "--color=never"]
    if task.ignore_case:
        cmd.append("-i")
    if task.literal:
        cmd.append("-F")
    cmd.extend([task.pattern, task.path])
    return cmd


def build_fast_grep_cmd(script: Path, task: LiteralTask) -> list[str]:
    cmd = [str(script)]
    if task.ignore_case:
        cmd.append("-i")
    if task.literal:
        cmd.append("--literal")
    cmd.extend([task.pattern, task.path])
    return cmd


def cap_lines(text: str, head_limit: int) -> tuple[str, int, bool]:
    lines = text.splitlines()
    total = len(lines)
    if total <= head_limit:
        return text, total, False
    capped = "\n".join(lines[:head_limit])
    if capped:
        capped += "\n"
    return capped, total, True


def run_capture(cmd: list[str], cwd: Path) -> tuple[int, str, float]:
    start = time.perf_counter()
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    output = proc.stdout
    if proc.stderr:
        output = (output or "") + proc.stderr
    return proc.returncode, output or "", elapsed_ms


def parse_hyperfine_stats(
    export_json: Path,
    labels: list[str] | None = None,
) -> dict[str, dict[str, float]]:
    """Return per-command timing stats in milliseconds."""
    if not export_json.is_file():
        return {}
    data = json.loads(export_json.read_text(encoding="utf-8"))
    stats: dict[str, dict[str, float]] = {}
    results = data.get("results", [])
    for index, row in enumerate(results):
        if labels and index < len(labels):
            label = labels[index]
        else:
            label = str(row.get("name", "")).strip() or str(row.get("command", "")).strip()
        if not label:
            continue
        mean_s = float(row["mean"])
        stats[label] = {
            "T_tool_ms_mean": round(mean_s * 1000.0, 3),
            "T_tool_ms_median": round(float(row.get("median", mean_s)) * 1000.0, 3),
            "T_tool_ms_stddev": round(float(row.get("stddev", 0.0)) * 1000.0, 3),
            "T_tool_ms_min": round(float(row.get("min", mean_s)) * 1000.0, 3),
            "T_tool_ms_max": round(float(row.get("max", mean_s)) * 1000.0, 3),
        }
    return stats


def run_hyperfine(
    label_a: str,
    cmd_a: list[str],
    label_b: str,
    cmd_b: list[str],
    cwd: Path,
    min_runs: int,
    warmup: int,
    export_json: Path,
) -> bool:
    if shutil.which("hyperfine") is None:
        return False

    shell_a = " ".join(shlex.quote(part) for part in cmd_a)
    shell_b = " ".join(shlex.quote(part) for part in cmd_b)
    proc = subprocess.run(
        [
            "hyperfine",
            f"--min-runs={min_runs}",
            f"--warmup={warmup}",
            f"--export-json={export_json}",
            "--shell=bash",
            "-n",
            label_a,
            shell_a,
            "-n",
            label_b,
            shell_b,
        ],
        cwd=cwd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0 and proc.stderr:
        print(proc.stderr.strip(), file=sys.stderr)
    return proc.returncode == 0


def literal_tasks_from_config(config: dict[str, Any]) -> list[LiteralTask]:
    tasks: list[LiteralTask] = []
    for task_id, spec in config["literal_tasks"].items():
        tasks.append(
            LiteralTask(
                task_id=task_id,
                description=spec["description"],
                pattern=spec["pattern"],
                path=spec["path"],
                literal=bool(spec.get("literal", True)),
                ignore_case=bool(spec.get("ignore_case", False)),
            )
        )
    return tasks


def write_summary(summary_path: Path, payload: dict[str, Any]) -> None:
    summary_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run fast-grep benchmark pilot (shell phase).")
    parser.add_argument(
        "--tasks",
        type=Path,
        default=Path(__file__).resolve().parent / "pilot-tasks.json",
        help="Task definition JSON (default: pilot-tasks.json beside this script)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory (default: benchmarks/fast-grep/results/run-<timestamp>)",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root (default: auto-detect agent-skills root)",
    )
    parser.add_argument(
        "--skip-hyperfine",
        action="store_true",
        help="Skip hyperfine (imprecise; only when hyperfine cannot be installed)",
    )
    args = parser.parse_args()

    bench_dir = Path(__file__).resolve().parent
    config = load_tasks(args.tasks)
    precision = config.get("precision", {})
    repo_root = args.repo_root or repo_root_from_here()
    if not (repo_root / "skills_manifest.yaml").is_file():
        print(f"run_pilot: repo root does not look like agent-skills: {repo_root}", file=sys.stderr)
        return 2

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_dir = args.out_dir or (bench_dir / "results" / f"run-{stamp}")
    if not out_dir.is_absolute():
        out_dir = (repo_root / out_dir).resolve()
    else:
        out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    head_limit = int(config.get("head_limit", 50))
    min_runs = int(precision.get("hyperfine_min_runs", config.get("hyperfine_min_runs", 10)))
    warmup = int(precision.get("hyperfine_warmup", 2))
    hyperfine_required = bool(precision.get("hyperfine_required", True))
    if hyperfine_required and args.skip_hyperfine:
        print("run_pilot: --skip-hyperfine conflicts with precision.hyperfine_required", file=sys.stderr)
        return 2
    if hyperfine_required and shutil.which("hyperfine") is None:
        print("run_pilot: hyperfine is required (brew install hyperfine)", file=sys.stderr)
        return 2

    fast_grep_script = resolve_path(repo_root, config["paths"]["fast_grep_script"])
    if not fast_grep_script.is_file():
        print(f"run_pilot: fast-grep script not found: {fast_grep_script}", file=sys.stderr)
        return 2

    shutil.copy2(args.tasks, out_dir / "pilot-tasks.json")

    run_meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "repo_profile": config.get("repo_profile", "unknown"),
        "head_limit": head_limit,
        "precision": precision,
        "hyperfine_available": shutil.which("hyperfine") is not None,
        "hyperfine_min_runs": min_runs,
        "hyperfine_warmup": warmup,
        "T_tool_authoritative": {
            "A": "agent Grep tool wall clock around tool call",
            "B": "semantic-search wall clock around tool call",
            "C": "hyperfine mean on fast-grep script",
            "engine_reference": "hyperfine mean on rg command",
        },
        "rg_path": shutil.which("rg"),
        "fast_grep_script": str(fast_grep_script),
        "tasks": [],
    }

    for task in literal_tasks_from_config(config):
        rg_cmd = build_rg_cmd(task)
        fg_cmd = build_fast_grep_cmd(fast_grep_script, task)

        task_entry: dict[str, Any] = {
            "task_id": task.task_id,
            "description": task.description,
            "pattern": task.pattern,
            "path": task.path,
            "rg_cmd": rg_cmd,
            "fast_grep_cmd": fg_cmd,
        }

        for engine, cmd in (("rg", rg_cmd), ("fast-grep", fg_cmd)):
            code, raw_output, elapsed_ms = run_capture(cmd, repo_root)
            capped, total_lines, was_capped = cap_lines(raw_output, head_limit)
            out_file = out_dir / "out" / f"{task.task_id}-{engine}.txt"
            out_file.parent.mkdir(parents=True, exist_ok=True)
            out_file.write_text(capped, encoding="utf-8")

            task_entry[engine] = {
                "exit_code": code,
                "T_tool_ms_single_run": round(elapsed_ms, 2),
                "T_tool_ms_single_run_note": "fallback only — use hyperfine mean when present",
                "hits_returned": total_lines,
                "hits_capped": was_capped,
                "output_file": str(out_file.relative_to(bench_dir)),
            }

        timing_json = out_dir / "timing" / f"{task.task_id}-hyperfine.json"
        timing_json.parent.mkdir(parents=True, exist_ok=True)
        hyperfine_ok = False
        if not args.skip_hyperfine and run_hyperfine(
            "rg",
            rg_cmd,
            "fast-grep",
            fg_cmd,
            repo_root,
            min_runs,
            warmup,
            timing_json,
        ):
            hyperfine_ok = True
            hf = parse_hyperfine_stats(timing_json, ["rg", "fast-grep"])
            task_entry["hyperfine_json"] = str(timing_json.relative_to(bench_dir))
            if "rg" in hf:
                task_entry["rg"]["T_tool_ms"] = hf["rg"]["T_tool_ms_mean"]
                task_entry["rg"]["T_tool_source"] = "hyperfine-mean"
                task_entry["rg"]["hyperfine"] = hf["rg"]
            if "fast-grep" in hf:
                task_entry["fast-grep"]["T_tool_ms"] = hf["fast-grep"]["T_tool_ms_mean"]
                task_entry["fast-grep"]["T_tool_source"] = "hyperfine-mean"
                task_entry["fast-grep"]["hyperfine"] = hf["fast-grep"]
        else:
            task_entry["hyperfine_json"] = None
            if hyperfine_required:
                print(f"run_pilot: hyperfine failed for {task.task_id}", file=sys.stderr)
                return 2

        run_meta["tasks"].append(task_entry)
        rg_ms = task_entry["rg"].get("T_tool_ms", task_entry["rg"]["T_tool_ms_single_run"])
        fg_ms = task_entry["fast-grep"].get("T_tool_ms", task_entry["fast-grep"]["T_tool_ms_single_run"])
        print(
            f"{task.task_id}: rg={rg_ms}ms fast-grep={fg_ms}ms "
            f"hits(rg)={task_entry['rg']['hits_returned']} hyperfine={hyperfine_ok}",
            file=sys.stderr,
        )

    write_summary(out_dir / "timing-summary.json", run_meta)
    print(str(out_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
