#!/usr/bin/env python3
"""Create local Jira task artifacts from normalized issue JSON."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
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


def filesystem_safe_meaningful_id(issue: str) -> str:
    cleaned = issue.strip()
    safe = re.sub(r'[<>:"/\\|?*\s]+', "-", cleaned)
    safe = re.sub(r"-+", "-", safe).strip("-./")
    return safe or slugify(issue)


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


def load_agent_config():
    infer = Path(__file__)
    candidates = [
        infer.resolve().parents[1] / "agent_config.py",
        runtime_scripts_dir(infer) / "agent_config.py",
    ]
    for path in candidates:
        if not path.is_file():
            continue
        spec = importlib.util.spec_from_file_location("agent_config", path)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    raise SystemExit("agent_config.py not found; sync shared scripts from agent-skills")


def resolve_resolver_script() -> Path | None:
    infer = Path(__file__)
    candidates = [
        infer.resolve().parents[1] / "resolve_artifact_path.py",
        runtime_scripts_dir(infer) / "resolve_artifact_path.py",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def resolve_validator() -> Path | None:
    infer = Path(__file__)
    candidates = [
        infer.resolve().parents[1] / "validate_artifact.py",
        runtime_scripts_dir(infer) / "validate_artifact.py",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def resolve_jira_context_script() -> Path | None:
    infer = Path(__file__)
    candidates = [
        infer.resolve().parent / "jira_context.py",
        runtime_scripts_dir(infer) / "jira" / "jira_context.py",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def find_repo_root() -> Path:
    current = Path.cwd().resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists():
            return candidate
    return current


def resolve_default_output_path(meaningful_id: str, basename: str) -> Path:
    resolver = resolve_resolver_script()
    if resolver is None:
        return Path("_artifacts_") / meaningful_id / basename
    repo_root = find_repo_root()
    result = subprocess.run(
        [
            "python3",
            str(resolver),
            "--repo-root",
            str(repo_root),
            "--meaningful-id",
            meaningful_id,
            "--basename",
            basename,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip())


def resolve_existing_output_path(meaningful_id: str, basename: str) -> Path | None:
    resolver = resolve_resolver_script()
    if resolver is None:
        legacy = Path("_artifacts_") / meaningful_id / basename
        return legacy if legacy.is_file() else None
    repo_root = find_repo_root()
    result = subprocess.run(
        [
            "python3",
            str(resolver),
            "--repo-root",
            str(repo_root),
            "--find-existing",
            "--meaningful-id",
            meaningful_id,
            "--basename",
            basename,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip())


def default_output_path(issue: str) -> Path:
    meaningful_id = filesystem_safe_meaningful_id(issue)
    return resolve_default_output_path(meaningful_id, f"task_{slugify(issue)}.md")


def read_api_base(cli_base: str | None) -> tuple[str | None, Path | None, str]:
    ac = load_agent_config()
    if cli_base:
        return cli_base.strip(), None, "cli"
    env_inline = (os.environ.get("ATLASSIAN_API_BASE_URL") or "").strip()
    if env_inline:
        return env_inline, None, "env"
    env_file = ac.env_file_path("atlassian.env", Path(__file__))
    if env_file.is_file():
        for line in env_file.read_text().splitlines():
            if line.startswith("ATLASSIAN_API_BASE_URL="):
                return line.split("=", 1)[1].strip(), env_file, "file"
    return None, None, "none"


def describe_defaults_path(source_kind: str, source_file: Path | None) -> str:
    ac = load_agent_config()
    if source_kind == "cli":
        return "(from --api-base)"
    if source_kind == "env":
        return "(from ATLASSIAN_API_BASE_URL in environment)"
    if source_kind == "file" and source_file is not None:
        return str(source_file)
    return str(ac.env_file_path("atlassian.env", Path(__file__))) + " (not found)"


def browse_base_from_api_base(api_base: str | None) -> str:
    if not api_base:
        return "https://example.atlassian.net"
    return api_base.split("/rest/api/3/issue", 1)[0].rstrip("/") or "https://example.atlassian.net"


def extract_issue_and_fields(obj: dict[str, Any], fallback_issue: str) -> tuple[str, dict[str, Any], str]:
    issue = str(obj.get("issue_key") or obj.get("key") or fallback_issue).upper()
    fields = obj.get("fields") if isinstance(obj.get("fields"), dict) else {}
    browse_url = str(obj.get("url") or "")
    if not browse_url:
        api_base, _, _ = read_api_base(None)
        browse_url = f"{browse_base_from_api_base(api_base)}/browse/{issue}"
    return issue, fields, browse_url


def fetch_issue_json(issue_key: str) -> dict[str, Any]:
    fetcher = resolve_jira_context_script()
    if fetcher is None:
        raise SystemExit("jira_context.py not found; sync scripts/jira/ from agent-skills")
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        subprocess.run(
            ["python3", str(fetcher), issue_key, "--output", str(tmp_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(tmp_path.read_text())
    except subprocess.CalledProcessError as exc:
        message = (exc.stderr or exc.stdout or "jira-fetch failed").strip()
        raise SystemExit(message) from exc
    finally:
        tmp_path.unlink(missing_ok=True)


def format_description(fields: dict[str, Any], normalized_description: str = "") -> str:
    if normalized_description:
        description = normalized_description
    else:
        description = re.sub(r"\n+", "\n", adf_text(fields.get("description") or "")).strip()
    if not description:
        return "No description text available."
    if len(description) > 1200:
        return description[:1200] + "..."
    return description


def adf_plain_text(node: object) -> str:
    return re.sub(r"\n+", "\n", adf_text(node)).strip()


def comment_entries(fields: dict[str, Any], normalized_comments: list[dict[str, str]] | None = None) -> list[dict[str, str]]:
    if normalized_comments:
        return normalized_comments
    comments = (fields.get("comment") or {}).get("comments", [])
    entries: list[dict[str, str]] = []
    for comment in comments:
        author = ((comment.get("author") or {}).get("displayName")) or "Unknown"
        body = adf_plain_text(comment.get("body") or "")
        created = comment.get("created") or ""
        if body:
            entries.append({"author": author, "body": body, "created": created})
    return entries


def summarize_comments(fields: dict[str, Any], normalized_comments: list[dict[str, str]] | None = None) -> str:
    comments = comment_entries(fields, normalized_comments)
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


def extract_related_references(issue: str, fields: dict[str, Any], normalized_comments: list[dict[str, str]] | None = None) -> list[str]:
    text_parts = [format_description(fields)]
    text_parts.extend(item["body"] for item in comment_entries(fields, normalized_comments))
    text_blob = "\n".join(part for part in text_parts if part and part != "No description text available.")

    refs: list[str] = []
    seen: set[str] = set()

    for key in re.findall(r"\b[A-Z][A-Z0-9]+-\d+\b", text_blob):
        if key != issue and key not in seen:
            seen.add(key)
            refs.append(f"- Related issue hint: {key}")

    for url in re.findall(r"https?://\S+", text_blob):
        clean_url = url.rstrip(").,]")
        if clean_url not in seen:
            seen.add(clean_url)
            refs.append(f"- Related link: {clean_url}")
        if len(refs) >= 10:
            break

    if "duplicate" in text_blob.lower() and "- Duplicate-related wording detected in description/comments." not in refs:
        refs.append("- Duplicate-related wording detected in description/comments.")

    return refs


def validate_artifact(output: Path) -> None:
    validator = resolve_validator()
    if validator is None:
        raise SystemExit("artifact written but validator not found: expected scripts/validate_artifact.py")
    subprocess.run(["python3", str(validator), str(output)], check=True)


def build_content(
    issue: str,
    fields: dict[str, Any],
    browse_url: str,
    defaults_path: str,
    preserved_sections: dict[str, str],
    *,
    transport: str = "",
    normalized_description: str = "",
    normalized_comments: list[dict[str, str]] | None = None,
) -> str:
    summary = fields.get("summary", "")
    status = (fields.get("status") or {}).get("name", "")
    issue_type = (fields.get("issuetype") or {}).get("name", "")
    priority = (fields.get("priority") or {}).get("name", "Unknown")
    assignee = ((fields.get("assignee") or {}).get("displayName") if fields.get("assignee") else "Unassigned")
    reporter = ((fields.get("reporter") or {}).get("displayName") if fields.get("reporter") else "Unknown")
    created = fields.get("created", "")
    updated = fields.get("updated", "")
    labels = ", ".join(fields.get("labels") or []) or "none"
    comment_count = len(comment_entries(fields, normalized_comments))
    description = format_description(fields, normalized_description)
    comment_summary = summarize_comments(fields, normalized_comments)
    related_references = extract_related_references(issue, fields, normalized_comments)
    related_references_block = "\n".join(related_references) or "- None found."
    follow_up_findings = preserved_sections.get("## Follow-up Findings", "- ")
    improvement_candidates = preserved_sections.get("## Improvement Candidates", "- ")
    transport_line = f"- Transport: {transport}\n" if transport else ""
    return f"""# Task

## Summary
{issue}: {summary}

## Type
jira

## Repository


## Context Links
- {browse_url}

## Selected Skills
- JIRA-ACCESS.md

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
{transport_line}
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
    parser.add_argument("--json", help="Path to fetched Jira issue JSON (REST or normalized)")
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="Fetch live issue JSON via jira-fetch/jira_context.py before bootstrapping.",
    )
    parser.add_argument("--output", help="Output Markdown path")
    parser.add_argument("--api-base", help="Optional Jira API base or site URL")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if args.fetch and args.json:
        raise SystemExit("--fetch and --json are mutually exclusive")

    if args.fetch:
        obj = fetch_issue_json(args.issue)
    elif args.json:
        obj = json.loads(Path(args.json).read_text())
    else:
        raise SystemExit("provide --json or --fetch")

    issue, fields, browse_url = extract_issue_and_fields(obj, args.issue)
    normalized_description = str(obj.get("description") or "")
    normalized_comments = obj.get("comments") if isinstance(obj.get("comments"), list) else None
    transport = str(obj.get("transport") or "")
    api_base, api_defaults_file, source_kind = read_api_base(args.api_base)
    if not browse_url:
        browse_url = f"{browse_base_from_api_base(api_base)}/browse/{issue}"
    defaults_path = describe_defaults_path(source_kind, api_defaults_file)
    output = Path(args.output) if args.output else default_output_path(issue)
    existing = resolve_existing_output_path(
        filesystem_safe_meaningful_id(issue),
        f"task_{slugify(issue)}.md",
    )
    preserved_source = existing if existing is not None else output
    preserved_sections = parse_preserved_sections(preserved_source) if preserved_source.exists() else {}

    if output.exists() and not args.overwrite:
        raise SystemExit(f"refusing to overwrite existing file: {output}")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        build_content(
            issue,
            fields,
            browse_url,
            defaults_path,
            preserved_sections,
            transport=transport,
            normalized_description=normalized_description,
            normalized_comments=normalized_comments,
        )
    )
    validate_artifact(output)
    print(output)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or exc.stdout or b"").decode() if isinstance(exc.stderr, bytes) else (exc.stderr or exc.stdout or "")
        raise SystemExit(stderr.strip() or f"subprocess failed with exit code {exc.returncode}") from exc
