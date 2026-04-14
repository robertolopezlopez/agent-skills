#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def as_list(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(x) for x in value if str(x).strip()]
    return [str(value)]


def bool_text(value: Any) -> str:
    return "yes" if bool(value) else "no"


def repository_text(mr: dict[str, Any]) -> str:
    path = (mr.get("references") or {}).get("full") or ""
    if "!" in path:
        path = path.split("!", 1)[0]
    if path:
        return path
    web_url = mr.get("web_url") or ""
    marker = "/-/merge_requests/"
    if marker in web_url:
        before = web_url.split(marker, 1)[0]
        parts = before.split("//", 1)
        if len(parts) == 2 and "/" in parts[1]:
            return parts[1].split("/", 1)[1]
    return str(mr.get("target_project_id") or "")


def build_content(mr: dict[str, Any], artifact_type: str, defaults_files: list[str]) -> str:
    iid = mr.get("iid", "")
    title = mr.get("title") or ""
    web_url = mr.get("web_url") or ""
    project = repository_text(mr)
    labels = as_list(mr.get("labels"))
    author = (mr.get("author") or {}).get("name") or ""
    state = mr.get("state") or ""
    source_branch = mr.get("source_branch") or ""
    target_branch = mr.get("target_branch") or ""
    description = (mr.get("description") or "").strip()
    draft = mr.get("draft")
    if draft is None:
        draft = mr.get("work_in_progress")

    labels_text = ", ".join(labels)
    defaults_block = "\n".join(f"- {x}" for x in defaults_files) or "- "
    description_block = description if description else ""

    actionable_lines = [
        f"- Review MR {iid} against `{target_branch}` from `{source_branch}`.",
        "- Read unresolved discussions before proposing changes or replies.",
        "- Validate claimed behavior against the actual diff and affected files.",
    ]
    if draft:
        actionable_lines.insert(0, "- MR is draft; confirm whether feedback should focus on readiness blockers or early review.")
    actionable_block = "\n".join(actionable_lines)

    return f"""# Task

## Summary
MR {iid}: {title}

## Type
{artifact_type}

## Repository
{project}

## Context Links
- {web_url}

## Selected Skills
- gitlab

## Defaults Files
{defaults_block}

## Assumptions
- MR metadata may need follow-up discussion fetch for unresolved review threads.
- Artifact bootstrap is local only and does not modify GitLab.

## Initial Plan
1. Read the MR overview and changed files.
2. Fetch and inspect unresolved discussions if review comments matter.
3. Summarize actionable next steps or hand off to a companion skill.

## Validation Plan
- Confirm the MR target branch, scope, and discussion state before deeper analysis.
- Run repository-specific validation only after follow-on implementation or review work begins.

## Open Questions
- Are unresolved discussions present and actionable?
- Is this MR for review, summary, or implementation follow-up?

## GitLab Details
- MR IID: {iid}
- Title: {title}
- State: {state}
- Author: {author}
- Source Branch: {source_branch}
- Target Branch: {target_branch}
- Draft: {bool_text(draft)}
- Labels: {labels_text}

## Description
{description_block}

## Actionable Context
{actionable_block}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a local markdown artifact from GitLab MR JSON.")
    parser.add_argument("--json", required=True, help="Path to GitLab MR JSON fetched via glab api.")
    parser.add_argument("--mr", help="Merge request IID override.")
    parser.add_argument("--output", help="Output markdown path. Defaults to review_mr_<iid>.md or analysis_mr_<iid>.md.")
    parser.add_argument("--type", choices=["review", "analysis"], default="review", help="Artifact type.")
    parser.add_argument("--defaults-file", action="append", default=[], help="Defaults files recorded in the artifact.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output if it exists.")
    args = parser.parse_args()

    mr = json.loads(Path(args.json).read_text())
    if args.mr:
        mr["iid"] = args.mr

    iid = str(mr.get("iid") or "").strip()
    if not iid:
        raise SystemExit("missing MR IID in JSON and no --mr override provided")

    prefix = "review" if args.type == "review" else "analysis"
    output = Path(args.output or f"{prefix}_mr_{iid}.md")
    if output.exists() and not args.overwrite:
        raise SystemExit(f"refusing to overwrite existing file: {output}")

    content = build_content(mr=mr, artifact_type=args.type, defaults_files=args.defaults_file)
    output.write_text(content)
    print(output)


if __name__ == "__main__":
    main()
