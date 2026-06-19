#!/usr/bin/env python3
"""Resolve agent workflow artifact paths outside project git checkouts.

Default layout::

    $AGENT_ARTIFACTS_HOME/_global/NEXT_TIME_CHECKS.md
    $AGENT_ARTIFACTS_HOME/_global/<meaningful_id>/<basename>.md
    $AGENT_ARTIFACTS_HOME/knowledge/<basename>.md
    $AGENT_ARTIFACTS_HOME/<repo-key>/NEXT_TIME_CHECKS.md
    $AGENT_ARTIFACTS_HOME/<repo-key>/<meaningful_id>/<basename>.md

See ARTIFACTS.md in the skills install root for precedence and legacy in-repo paths.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from parse_remote_url import RemoteUrlParseError, parse_remote_url, tail_path_segments


GLOBAL_SEGMENT = "_global"
KNOWLEDGE_SEGMENT = "knowledge"


def artifacts_home() -> Path:
    override = (os.environ.get("AGENT_ARTIFACTS_HOME") or "").strip()
    if override:
        return Path(override).expanduser()
    cursor_home = Path.home() / ".cursor" / "agent-artifacts"
    codex_home = Path.home() / ".codex" / "agent-artifacts"
    if (Path.home() / ".cursor").is_dir():
        return cursor_home
    return codex_home


def sanitize_component(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9._-]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "unknown"


def repo_key_from_remote(url: str) -> str | None:
    try:
        host, project_path = parse_remote_url(url)
    except RemoteUrlParseError:
        return None
    tail = tail_path_segments(project_path, 2)
    if not tail:
        return None
    org, repo = tail
    host_slug = sanitize_component(host)
    return f"{host_slug}-{sanitize_component(org)}-{sanitize_component(repo)}"


def find_git_root(start: Path) -> Path | None:
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists():
            return candidate
    return None


def repo_key(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            parsed = repo_key_from_remote(result.stdout.strip())
            if parsed:
                return parsed
    except OSError:
        pass
    return sanitize_component(repo_root.name)


def global_artifacts_root() -> Path:
    return artifacts_home() / GLOBAL_SEGMENT


def knowledge_artifacts_root() -> Path:
    return artifacts_home() / KNOWLEDGE_SEGMENT


def repo_artifacts_root(repo_root: Path) -> Path:
    return artifacts_home() / repo_key(repo_root)


def artifact_path(repo_root: Path, meaningful_id: str, basename: str) -> Path:
    return repo_artifacts_root(repo_root) / meaningful_id / basename


def global_artifact_path(meaningful_id: str, basename: str) -> Path:
    return global_artifacts_root() / meaningful_id / basename


def knowledge_artifact_path(basename: str) -> Path:
    return knowledge_artifacts_root() / basename


def next_time_checks_path(repo_root: Path) -> Path:
    return repo_artifacts_root(repo_root) / "NEXT_TIME_CHECKS.md"


def global_next_time_checks_path() -> Path:
    return global_artifacts_root() / "NEXT_TIME_CHECKS.md"


def legacy_artifact_path(repo_root: Path, meaningful_id: str, basename: str) -> Path:
    return repo_root / "_artifacts_" / meaningful_id / basename


def find_existing_knowledge_artifact(repo_root: Path, basename: str) -> Path | None:
    candidates = [
        knowledge_artifact_path(basename),
        repo_artifacts_root(repo_root) / KNOWLEDGE_SEGMENT / basename,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def find_existing_artifact(repo_root: Path, meaningful_id: str, basename: str) -> Path | None:
    candidates = [
        artifact_path(repo_root, meaningful_id, basename),
        legacy_artifact_path(repo_root, meaningful_id, basename),
        repo_root / basename,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def resolve_repo_root(explicit: str | None) -> Path:
    if explicit:
        root = Path(explicit).expanduser().resolve()
        if not root.is_dir():
            raise SystemExit(f"repo root is not a directory: {root}")
        return root
    git_root = find_git_root(Path.cwd())
    return git_root or Path.cwd().resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Resolve external agent artifact paths.")
    parser.add_argument(
        "--repo-root",
        help="Git repository root (default: git root of cwd, else cwd).",
    )
    parser.add_argument("--meaningful-id", help="Ticket/session folder name.")
    parser.add_argument("--basename", help="Artifact filename, e.g. review_mr_123.md.")
    parser.add_argument(
        "--next-time-checks",
        action="store_true",
        help="Print NEXT_TIME_CHECKS.md path for the repository.",
    )
    parser.add_argument(
        "--global-next-time-checks",
        action="store_true",
        help="Print cross-repo NEXT_TIME_CHECKS.md path ($GLOBAL/).",
    )
    parser.add_argument(
        "--repo-artifacts-root",
        action="store_true",
        help="Print the external artifact store root ($ARTIFACTS) for the repository.",
    )
    parser.add_argument(
        "--global-artifacts-root",
        action="store_true",
        help="Print the cross-repo artifact store root ($GLOBAL/).",
    )
    parser.add_argument(
        "--knowledge-artifacts-root",
        action="store_true",
        help="Print the general-knowledge artifact store root ($KNOWLEDGE/).",
    )
    parser.add_argument(
        "--scope",
        choices=("repo", "global", "knowledge"),
        default="repo",
        help="Artifact scope when resolving --meaningful-id/--basename (default: repo).",
    )
    parser.add_argument(
        "--artifacts-home",
        action="store_true",
        help="Print AGENT_ARTIFACTS_HOME (before repo-key suffix).",
    )
    parser.add_argument(
        "--repo-key",
        action="store_true",
        help="Print the repo-key segment for the repository.",
    )
    parser.add_argument(
        "--find-existing",
        action="store_true",
        help="Print the first existing artifact among external, legacy in-repo, or repo root.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    repo_root = resolve_repo_root(args.repo_root)

    if args.artifacts_home:
        print(artifacts_home())
        return
    if args.repo_key:
        print(repo_key(repo_root))
        return
    if args.global_artifacts_root:
        print(global_artifacts_root())
        return
    if args.knowledge_artifacts_root:
        print(knowledge_artifacts_root())
        return
    if args.repo_artifacts_root:
        print(repo_artifacts_root(repo_root))
        return
    if args.global_next_time_checks:
        print(global_next_time_checks_path())
        return
    if args.next_time_checks:
        print(next_time_checks_path(repo_root))
        return

    if not args.basename:
        parser.error("--basename is required unless using a root-only flag")
    if args.scope != "knowledge" and not args.meaningful_id:
        parser.error("--meaningful-id is required unless --scope knowledge or using a root-only flag")

    if args.scope == "knowledge":
        if args.find_existing:
            existing = find_existing_knowledge_artifact(repo_root, args.basename)
            if existing is None:
                raise SystemExit(1)
            print(existing)
            return
        print(knowledge_artifact_path(args.basename))
        return

    if args.scope == "global":
        if args.find_existing:
            candidate = global_artifact_path(args.meaningful_id, args.basename)
            if not candidate.is_file():
                raise SystemExit(1)
            print(candidate)
            return
        print(global_artifact_path(args.meaningful_id, args.basename))
        return

    if args.find_existing:
        existing = find_existing_artifact(repo_root, args.meaningful_id, args.basename)
        if existing is None:
            raise SystemExit(1)
        print(existing)
        return

    print(artifact_path(repo_root, args.meaningful_id, args.basename))


if __name__ == "__main__":
    try:
        main()
    except SystemExit as exc:
        raise
    except Exception as exc:  # pragma: no cover - CLI guardrail
        print(f"resolve_artifact_path: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
