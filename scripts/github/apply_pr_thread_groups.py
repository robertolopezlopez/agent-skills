#!/usr/bin/env python3
"""Upsert ## Grouped unresolved comments from gh_context.py --full JSON into a PR artifact."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


GROUPED_HEADER = "## Grouped unresolved comments"


def runtime_scripts_dir(infer_from: Path) -> Path:
    parts = infer_from.resolve().parts
    for idx, part in enumerate(parts):
        if part in {".cursor", ".codex"} and idx + 1 < len(parts) and parts[idx + 1] == "skills":
            return Path.home() / part / "skills" / "scripts"
    if (Path.home() / ".cursor" / "skills").is_dir():
        return Path.home() / ".cursor" / "skills" / "scripts"
    if (Path.home() / ".codex" / "skills").is_dir():
        return Path.home() / ".codex" / "skills" / "scripts"
    return Path.home() / ".cursor" / "skills" / "scripts"


def resolve_script(name: str, subdir: str | None = None) -> Path | None:
    infer = Path(__file__)
    candidates = []
    if subdir:
        candidates.append(infer.resolve().parent / name)
        candidates.append(runtime_scripts_dir(infer) / subdir / name)
    else:
        candidates.append(infer.resolve().parents[1] / name)
        candidates.append(runtime_scripts_dir(infer) / name)
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def validate_artifact(path: Path) -> None:
    validator = resolve_script("validate_artifact.py")
    if validator is None:
        raise SystemExit("artifact written but validator not found")
    subprocess.run(["python3", str(validator), str(path)], check=True)


def short_title(body: str, *, max_len: int = 60) -> str:
    text = " ".join((body or "").strip().split())
    if not text:
        return "Review thread"
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def thread_anchor(thread: dict[str, Any]) -> str:
    comments = thread.get("comments") or []
    if comments:
        url = comments[0].get("url") or ""
        if url:
            return url
    return thread.get("thread_id") or ""


def issue_label(index: int) -> str:
    return f"issue_{index:02d}"


def render_issue_block(index: int, thread: dict[str, Any], pr: dict[str, Any]) -> str:
    comments = thread.get("comments") or []
    first = comments[0] if comments else {}
    title = short_title(first.get("body") or "")
    anchor = thread_anchor(thread)
    path = first.get("path") or ""
    line = first.get("line")
    location = f"{path}:{line}" if path and line is not None else path or "unknown location"
    authors = ", ".join(
        sorted({str(c.get("author") or "").strip() for c in comments if c.get("author")})
    ) or "unknown"
    body_lines = []
    for comment in comments:
        author = comment.get("author") or "unknown"
        body = (comment.get("body") or "").strip()
        url = comment.get("url") or ""
        body_lines.append(f"- [{author}]({url}): {body}" if url else f"- {author}: {body}")
    comment_block = "\n".join(body_lines) or "- "
    canonical = pr.get("canonical_url") or ""
    return f"""### {issue_label(index)} — {title}

- PR: {canonical}
- Thread anchor: {anchor}
- Location: `{location}`
- Authors: {authors}
- Reply/waiting status: unresolved (live refresh)
- Grouped comment summary:
{comment_block}
- Technical analysis: pending (pair with repository-technical-analysis when code-aware)
- Verdict: unresolved review thread
- Proposed changes: pending
- Recommended next action: inspect `{location}` and respond on-thread
- Confidence: high (transport refresh)
- Open questions: none from transport layer
"""


def build_grouped_section(pr: dict[str, Any]) -> str:
    threads = [thread for thread in (pr.get("review_threads") or []) if not thread.get("is_resolved")]
    unresolved = pr.get("unresolved_review_thread_count")
    total = pr.get("review_thread_count")
    pr_number = pr.get("pr_number") or pr.get("object_number") or "?"
    header = [
        GROUPED_HEADER,
        "",
        f"Live refresh via `gh-fetch pr {pr_number} --full`.",
        f"Unresolved review threads: {len(threads)}"
        + (f" (reported {unresolved}/{total})" if unresolved is not None and total is not None else "")
        + ".",
        "",
    ]
    if not threads:
        header.extend(["No unresolved review threads in the last `--full` fetch.", ""])
        return "\n".join(header)

    blocks = [render_issue_block(index, thread, pr) for index, thread in enumerate(threads, start=1)]
    return "\n".join(header + blocks) + "\n"


def strip_grouped_section(text: str) -> str:
    start = text.find(GROUPED_HEADER)
    if start == -1:
        return text.rstrip() + "\n"
    return text[:start].rstrip() + "\n"


def load_pr_json(args: argparse.Namespace) -> dict[str, Any]:
    if args.fetch:
        if not args.pr or not args.owner or not args.repo:
            raise SystemExit("--fetch requires --pr, --owner, and --repo")
        gh_context = resolve_script("gh_context.py", "github")
        if gh_context is None:
            raise SystemExit("gh_context.py not found")
        result = subprocess.run(
            [
                "python3",
                str(gh_context),
                "pr",
                str(args.pr),
                "--owner",
                args.owner,
                "--repo",
                args.repo,
                "--full",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(result.stdout)
        if args.save_json:
            Path(args.save_json).write_text(result.stdout)
        return payload
    if not args.json:
        raise SystemExit("provide --json or --fetch with --pr --owner --repo")
    return json.loads(Path(args.json).read_text())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upsert grouped unresolved PR review threads into the main PR artifact."
    )
    parser.add_argument("--json", help="Path to gh_context.py --full JSON.")
    parser.add_argument("--fetch", action="store_true", help="Fetch live --full JSON before grouping.")
    parser.add_argument("--save-json", help="When using --fetch, also write JSON to this path.")
    parser.add_argument("--pr", help="Pull request number for --fetch.")
    parser.add_argument("--owner", help="Repository owner for --fetch.")
    parser.add_argument("--repo", help="Repository name for --fetch.")
    parser.add_argument("--artifact", required=True, help="review_pr_<n>.md or analysis_pr_<n>.md path.")
    args = parser.parse_args()

    pr = load_pr_json(args)
    if pr.get("fetch_depth") != "full":
        raise SystemExit("PR JSON must come from gh_context.py --full (review_threads required)")

    artifact = Path(args.artifact)
    if not artifact.is_file():
        raise SystemExit(f"artifact not found: {artifact}")

    grouped = build_grouped_section(pr)
    text = strip_grouped_section(artifact.read_text()) + "\n" + grouped
    artifact.write_text(text)
    validate_artifact(artifact)
    print(artifact)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or exc.stdout or "").strip()
        raise SystemExit(stderr or f"subprocess failed with exit code {exc.returncode}") from exc
