#!/usr/bin/env python3
"""Create a local markdown artifact from normalized GitHub PR JSON."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
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
        infer.resolve().parents[1] / "validate_artifact.py",
        runtime_scripts_dir(infer) / "validate_artifact.py",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


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


def resolve_gh_context_script() -> Path | None:
    infer = Path(__file__)
    candidates = [
        infer.resolve().parent / "gh_context.py",
        runtime_scripts_dir(infer) / "github" / "gh_context.py",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def validate_artifact(output: Path) -> None:
    validator = resolve_validator()
    if validator is None:
        raise SystemExit("artifact written but validator not found: expected scripts/validate_artifact.py")
    subprocess.run(["python3", str(validator), str(output)], check=True)


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


def find_repo_root() -> Path:
    current = Path.cwd().resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists():
            return candidate
    return current


def default_output_path(number: str, artifact_type: str) -> Path:
    prefix = "review" if artifact_type == "review" else "analysis"
    meaningful_id = f"pr-{number}"
    basename = f"{prefix}_pr_{number}.md"
    return resolve_default_output_path(meaningful_id, basename)


def repository_text(pr: dict[str, Any]) -> str:
    owner = pr.get("repository_owner") or ""
    repo = pr.get("repository_name") or ""
    if owner and repo:
        return f"{owner}/{repo}"
    return ""


def fetch_pr_json(number: str, owner: str | None, repo: str | None) -> dict[str, Any]:
    fetcher = resolve_gh_context_script()
    if fetcher is None:
        raise SystemExit("gh_context.py not found under scripts/github/")
    command = ["python3", str(fetcher), "pr", number]
    if owner:
        command.extend(["--owner", owner])
    if repo:
        command.extend(["--repo", repo])
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
        cwd=find_repo_root(),
    )
    return json.loads(result.stdout)


def build_content(
    pr: dict[str, Any],
    artifact_type: str,
    defaults_files: list[str],
    preserved_sections: dict[str, str],
) -> str:
    number = str(pr.get("pr_number") or pr.get("object_number") or "")
    title = pr.get("title") or ""
    canonical_url = pr.get("canonical_url") or ""
    project = repository_text(pr)
    labels = as_list(pr.get("labels"))
    author = pr.get("author") or ""
    state = pr.get("state") or ""
    source_branch = pr.get("source_branch") or ""
    target_branch = pr.get("target_branch") or ""
    description = (pr.get("body") or "").strip()
    draft = pr.get("draft")
    review_count = len(pr.get("reviews") or [])
    review_comment_count = len(pr.get("review_comments") or [])

    labels_text = ", ".join(labels) or "none"
    defaults_block = "\n".join(f"- {x}" for x in defaults_files) or "- "
    description_block = description if description else ""

    actionable_lines = [
        f"- Review PR {number} against `{target_branch}` from `{source_branch}`.",
        "- Read unresolved review threads before proposing changes or replies.",
        "- Validate claimed behavior against the actual diff and affected files.",
    ]
    if draft:
        actionable_lines.insert(0, "- PR is draft; confirm whether feedback should focus on readiness blockers or early review.")
    actionable_block = "\n".join(actionable_lines)
    follow_up_findings = preserved_sections.get("## Follow-up Findings", "- ")
    improvement_candidates = preserved_sections.get("## Improvement Candidates", "- ")

    return f"""# Task

## Summary
PR {number}: {title}

## Type
{artifact_type}

## Repository
{project}

## Context Links
- {canonical_url}

## Selected Skills
- GITHUB-ACCESS.md
- github-pr-comment-analysis

## Defaults Files
{defaults_block}

## Assumptions
- PR metadata may need **`gh-fetch pr <PR> --full`** for unresolved review-thread grouping.
- Artifact bootstrap is local only and does not modify GitHub.

## Initial Plan
1. Read the PR overview and changed files.
2. Fetch and inspect unresolved review threads if review comments matter.
3. Summarize actionable next steps or hand off to github-pr-comment-analysis.

## Validation Plan
- Confirm the PR target branch, scope, and review state before deeper analysis.
- Run repository-specific validation only after follow-on implementation or review work begins.

## Open Questions
- Are unresolved review threads present and actionable?
- Is this PR for review, summary, or implementation follow-up?

## GitHub Details
- PR Number: {number}
- Title: {title}
- State: {state}
- Author: {author}
- Source Branch: {source_branch}
- Target Branch: {target_branch}
- Draft: {bool_text(draft)}
- Labels: {labels_text}
- Review Count: {review_count}
- Review Comment Count: {review_comment_count}

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
    parser = argparse.ArgumentParser(description="Create a local markdown artifact from GitHub PR JSON.")
    parser.add_argument("--json", help="Path to normalized GitHub PR JSON from gh-fetch / gh_context.py.")
    parser.add_argument("--pr", help="Pull request number override or sole input with --fetch.")
    parser.add_argument("--owner", help="Repository owner when using --fetch.")
    parser.add_argument("--repo", help="Repository name when using --fetch.")
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="Fetch live PR JSON via gh-fetch/gh_context.py before bootstrapping.",
    )
    parser.add_argument(
        "--output",
        help=(
            "Output markdown path. Defaults to $ARTIFACTS/pr-<PR>/review_pr_<PR>.md "
            "or $ARTIFACTS/pr-<PR>/analysis_pr_<PR>.md (external store; see ARTIFACTS.md)."
        ),
    )
    parser.add_argument("--type", choices=["review", "analysis"], default="review", help="Artifact type.")
    parser.add_argument("--defaults-file", action="append", default=[], help="Defaults files recorded in the artifact.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output if it exists.")
    args = parser.parse_args()

    if args.fetch:
        if not args.pr:
            raise SystemExit("--fetch requires --pr")
        pr = fetch_pr_json(args.pr, args.owner, args.repo)
    elif args.json:
        pr = json.loads(Path(args.json).read_text())
        if args.pr:
            pr["pr_number"] = args.pr
            pr["object_number"] = args.pr
    else:
        raise SystemExit("provide --json or --fetch with --pr")

    number = str(pr.get("pr_number") or pr.get("object_number") or args.pr or "").strip()
    if not number:
        raise SystemExit("missing PR number in JSON and no --pr override provided")

    output = Path(args.output) if args.output else default_output_path(number, args.type)
    prefix = "review" if args.type == "review" else "analysis"
    existing = resolve_existing_output_path(f"pr-{number}", f"{prefix}_pr_{number}.md")
    preserved_source = existing if existing is not None else output
    preserved_sections = parse_preserved_sections(preserved_source) if preserved_source.exists() else {}
    if output.exists() and not args.overwrite:
        raise SystemExit(f"refusing to overwrite existing file: {output}")

    content = build_content(
        pr=pr,
        artifact_type=args.type,
        defaults_files=args.defaults_file,
        preserved_sections=preserved_sections,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content)
    validate_artifact(output)
    print(output)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or exc.stdout or b"").decode() if isinstance(exc.stderr, bytes) else (exc.stderr or exc.stdout or "")
        raise SystemExit(stderr.strip() or f"subprocess failed with exit code {exc.returncode}") from exc
