#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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


def resolve_validator() -> Path | None:
    infer = Path(__file__)
    candidates = [
        infer.resolve().parents[4] / "scripts" / "validate_artifact.py",
        runtime_scripts_dir(infer) / "validate_artifact.py",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def validate_artifact(output: Path) -> None:
    validator = resolve_validator()
    if validator is None:
        raise SystemExit('artifact written but validator not found: expected scripts/validate_artifact.py')
    subprocess.run(['python3', str(validator), str(output)], check=True)


def resolve_resolver_script() -> Path | None:
    infer = Path(__file__)
    candidates = [
        infer.resolve().parents[4] / "scripts" / "resolve_artifact_path.py",
        runtime_scripts_dir(infer) / "resolve_artifact_path.py",
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


def default_output_path(iid: str, artifact_type: str) -> Path:
    prefix = "review" if artifact_type == "review" else "analysis"
    meaningful_id = f"mr-{iid}"
    basename = f"{prefix}_mr_{iid}.md"
    return resolve_default_output_path(meaningful_id, basename)


def build_content(mr: dict[str, Any], artifact_type: str, defaults_files: list[str], preserved_sections: dict[str, str]) -> str:
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
    follow_up_findings = preserved_sections.get("## Follow-up Findings", "- ")
    improvement_candidates = preserved_sections.get("## Improvement Candidates", "- ")

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

## Follow-up Findings
{follow_up_findings}

## Improvement Candidates
{improvement_candidates}

## Actionable Context
{actionable_block}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a local markdown artifact from GitLab MR JSON.")
    parser.add_argument("--json", required=True, help="Path to GitLab MR JSON fetched via glab api.")
    parser.add_argument("--mr", help="Merge request IID override.")
    parser.add_argument(
        "--output",
        help=(
            "Output markdown path. Defaults to $ARTIFACTS/mr-<iid>/review_mr_<iid>.md "
            "or $ARTIFACTS/mr-<iid>/analysis_mr_<iid>.md (external store; see ARTIFACTS.md)."
        ),
    )
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

    output = Path(args.output) if args.output else default_output_path(iid, args.type)
    prefix = "review" if args.type == "review" else "analysis"
    existing = resolve_existing_output_path(f"mr-{iid}", f"{prefix}_mr_{iid}.md")
    preserved_source = existing if existing is not None else output
    preserved_sections = parse_preserved_sections(preserved_source) if preserved_source.exists() else {}
    if output.exists() and not args.overwrite:
        raise SystemExit(f"refusing to overwrite existing file: {output}")

    content = build_content(mr=mr, artifact_type=args.type, defaults_files=args.defaults_file, preserved_sections=preserved_sections)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content)
    validate_artifact(output)
    print(output)


if __name__ == "__main__":
    main()
