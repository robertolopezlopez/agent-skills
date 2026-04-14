#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


def adf_text(node: object) -> str:
    if isinstance(node, dict):
        parts: list[str] = []
        node_type = node.get("type")
        if node_type == "text":
            parts.append(str(node.get("text", "")))
        for child in node.get("content", []) or []:
            parts.append(adf_text(child))
        if node_type in {"paragraph", "heading", "bulletList", "orderedList", "listItem"}:
            parts.append("\n")
        return "".join(parts)
    if isinstance(node, list):
        return "".join(adf_text(item) for item in node)
    return ""


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "jira-task"


def read_api_base(cli_base: str | None) -> str | None:
    if cli_base:
        return cli_base
    env_file = Path.home() / ".codex/jira.env"
    if not env_file.exists():
        return None
    for line in env_file.read_text().splitlines():
        if line.startswith("ATLASSIAN_API_BASE_URL="):
            return line.split("=", 1)[1].strip()
    return None


def browse_base_from_api_base(api_base: str | None) -> str:
    if not api_base:
        return "https://example.atlassian.net"
    return api_base.split("/rest/api/3/issue", 1)[0].rstrip("/") or "https://example.atlassian.net"


def format_description(fields: dict) -> str:
    description = re.sub(r"\n+", "\n", adf_text(fields.get("description") or "")).strip()
    if not description:
        return "No description text available."
    if len(description) > 1200:
        return description[:1200] + "..."
    return description


def resolve_validator() -> Path | None:
    candidates = [
        Path(__file__).resolve().parents[2] / 'scripts' / 'validate_artifact.py',
        Path(__file__).resolve().parents[1].parent / 'scripts' / 'validate_artifact.py',
        Path.home() / '.codex' / 'skills' / 'scripts' / 'validate_artifact.py',
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def validate_artifact(output: Path) -> None:
    validator = resolve_validator()
    if validator is None:
        raise SystemExit('artifact written but validator not found: expected scripts/validate_artifact.py')
    subprocess.run(['python3', str(validator), str(output)], check=True)


def build_content(issue: str, fields: dict, browse_url: str, defaults_path: str) -> str:
    summary = fields.get("summary", "")
    status = (fields.get("status") or {}).get("name", "")
    issue_type = (fields.get("issuetype") or {}).get("name", "")
    priority = (fields.get("priority") or {}).get("name", "Unknown")
    assignee = ((fields.get("assignee") or {}).get("displayName") if fields.get("assignee") else "Unassigned")
    reporter = ((fields.get("reporter") or {}).get("displayName") if fields.get("reporter") else "Unknown")
    created = fields.get("created", "")
    updated = fields.get("updated", "")
    labels = ", ".join(fields.get("labels") or []) or "none"
    comment_count = len((fields.get("comment") or {}).get("comments", []))
    description = format_description(fields)
    return f"""# Task

## Summary
{issue}: {summary}

## Type
jira

## Repository


## Context Links
- {browse_url}

## Selected Skills
- jira

## Defaults Files
- {defaults_path}

## Assumptions
- Ticket status is {status}.
- Best next step depends on whether user wants summary only or follow-up engineering work.

## Initial Plan
1. Use Jira issue details as source of truth for ticket context.
2. Determine whether ticket implies new work or only historical reference.
3. If follow-up work exists, create or refine an implementation or investigation plan from this context.

## Validation Plan
- No code validation yet; this artifact only captures Jira context.

## Open Questions
- Is this ticket historical context only?
- Is there a related repository, merge request, or follow-up Jira ticket?
- Does user want summary, follow-up implementation, or investigation?

## Jira Details
- Key: {issue}
- Summary: {summary}
- Status: {status}
- Issue Type: {issue_type}
- Priority: {priority}
- Assignee: {assignee}
- Reporter: {reporter}
- Created: {created}
- Updated: {updated}
- Labels: {labels}
- Comment Count: {comment_count}

## Description
{description}

## Actionable Context
- Start from Jira issue details above.
- Review description and comments for concrete requested work, debugging clues, or follow-up links.
- If ticket lacks implementation detail, locate related repo, pipeline, or successor ticket before starting engineering work.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue", required=True, help="Jira issue key, e.g. DAT-1234")
    parser.add_argument("--json", required=True, help="Path to fetched Jira issue JSON")
    parser.add_argument("--output", help="Output Markdown path")
    parser.add_argument("--api-base", help="Optional Jira API base or site URL")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    obj = json.loads(Path(args.json).read_text())
    issue = obj.get("key") or args.issue
    fields = obj.get("fields", {})
    api_base = read_api_base(args.api_base)
    browse_url = f"{browse_base_from_api_base(api_base)}/browse/{issue}"
    defaults_path = str(Path.home() / ".codex/jira.env")
    output = Path(args.output or f"task_{slugify(issue)}.md")

    if output.exists() and not args.overwrite:
        raise SystemExit(f"refusing to overwrite existing file: {output}")

    output.write_text(build_content(issue, fields, browse_url, defaults_path))
    validate_artifact(output)
    print(output)


if __name__ == "__main__":
    main()
