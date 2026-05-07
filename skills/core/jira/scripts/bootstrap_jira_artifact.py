#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any


PRESERVED_SECTION_HEADERS = [
    "## Follow-up Findings",
    "## Improvement Candidates",
]


def parse_preserved_sections(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    text = path.read_text()
    out: dict[str, str] = {}
    headings = [match.group(0) for match in re.finditer(r"^## .+$", text, flags=re.MULTILINE)]
    for header in PRESERVED_SECTION_HEADERS:
        start = text.find(header)
        if start == -1:
            continue
        body_start = start + len(header)
        next_positions: list[int] = []
        for other in headings:
            if other == header:
                continue
            pos = text.find(other, body_start)
            if pos != -1:
                next_positions.append(pos)
        end = min(next_positions) if next_positions else len(text)
        out[header] = text[body_start:end].strip() or "- "
    return out


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


ATLASSIAN_ENV_CANDIDATES: tuple[Path, ...] = (
    Path.home() / ".cursor" / "atlassian.env",
    Path.home() / ".codex" / "atlassian.env",
)


def read_api_base(cli_base: str | None) -> tuple[str | None, Path | None, str]:
    """Return (api_base_or_none, env_file_when_used, source_kind).

    source_kind is one of: cli, env, file, none.
    """
    if cli_base:
        return cli_base.strip(), None, "cli"
    env_inline = (os.environ.get("ATLASSIAN_API_BASE_URL") or "").strip()
    if env_inline:
        return env_inline, None, "env"
    for env_file in ATLASSIAN_ENV_CANDIDATES:
        if not env_file.is_file():
            continue
        for line in env_file.read_text().splitlines():
            if line.startswith("ATLASSIAN_API_BASE_URL="):
                return line.split("=", 1)[1].strip(), env_file, "file"
    return None, None, "none"


def describe_defaults_path(source_kind: str, source_file: Path | None) -> str:
    if source_kind == "cli":
        return "(from --api-base)"
    if source_kind == "env":
        return "(from ATLASSIAN_API_BASE_URL in environment)"
    if source_kind == "file" and source_file is not None:
        return str(source_file)
    return "; ".join(str(p) for p in ATLASSIAN_ENV_CANDIDATES) + " (not found)"


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


def adf_plain_text(node: object) -> str:
    return re.sub(r"\n+", "\n", adf_text(node)).strip()


def comment_entries(fields: dict[str, Any]) -> list[dict[str, str]]:
    comments = (fields.get("comment") or {}).get("comments", [])
    entries: list[dict[str, str]] = []
    for comment in comments:
        author = ((comment.get("author") or {}).get("displayName")) or "Unknown"
        body = adf_plain_text(comment.get("body") or "")
        created = comment.get("created") or ""
        if body:
            entries.append({"author": author, "body": body, "created": created})
    return entries


def summarize_comments(fields: dict[str, Any]) -> str:
    comments = comment_entries(fields)
    if not comments:
        return "- No comments."
    lines = [f"- Comment count: {len(comments)}"]
    recent = comments[-3:]
    lines.append("- Recent actionable comments:")
    for item in recent:
        body = item["body"][:240].strip()
        if len(item["body"]) > 240:
            body += "..."
        lines.append(f"  - {item['author']}: {body}")
    return "\n".join(lines)


def extract_related_references(issue: str, fields: dict[str, Any]) -> list[str]:
    text_parts = [format_description(fields)]
    text_parts.extend(item["body"] for item in comment_entries(fields))
    text_blob = "\n".join(part for part in text_parts if part and part != "No description text available.")

    refs: list[str] = []
    seen: set[str] = set()

    for key in re.findall(r"\b[A-Z][A-Z0-9]+-\d+\b", text_blob):
        if key != issue and key not in seen:
            seen.add(key)
            refs.append(f"- Related issue hint: {key}")

    for url in re.findall(r"https?://\S+", text_blob):
        clean_url = url.rstrip(').,]')
        if clean_url not in seen:
            seen.add(clean_url)
            refs.append(f"- Related link: {clean_url}")
        if len(refs) >= 10:
            break

    if "duplicate" in text_blob.lower() and "- Duplicate-related wording detected in description/comments." not in refs:
        refs.append("- Duplicate-related wording detected in description/comments.")

    return refs


def resolve_validator() -> Path | None:
    candidates = [
        Path(__file__).resolve().parents[2] / 'scripts' / 'validate_artifact.py',
        Path(__file__).resolve().parents[1].parent / 'scripts' / 'validate_artifact.py',
        Path.home() / '.cursor' / 'skills' / 'scripts' / 'validate_artifact.py',
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


def build_content(issue: str, fields: dict, browse_url: str, defaults_path: str, preserved_sections: dict[str, str]) -> str:
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
    comment_summary = summarize_comments(fields)
    related_references = extract_related_references(issue, fields)
    related_references_block = "\n".join(related_references) or "- None found."
    follow_up_findings = preserved_sections.get("## Follow-up Findings", "- ")
    improvement_candidates = preserved_sections.get("## Improvement Candidates", "- ")
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

## Comment Summary
{comment_summary}

## Related References
{related_references_block}

## Follow-up Findings
{follow_up_findings}

## Improvement Candidates
{improvement_candidates}

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
    api_base, api_defaults_file, source_kind = read_api_base(args.api_base)
    browse_url = f"{browse_base_from_api_base(api_base)}/browse/{issue}"
    defaults_path = describe_defaults_path(source_kind, api_defaults_file)
    output = Path(args.output or f"task_{slugify(issue)}.md")
    preserved_sections = parse_preserved_sections(output) if output.exists() else {}

    if output.exists() and not args.overwrite:
        raise SystemExit(f"refusing to overwrite existing file: {output}")

    output.write_text(build_content(issue, fields, browse_url, defaults_path, preserved_sections))
    validate_artifact(output)
    print(output)


if __name__ == "__main__":
    main()
