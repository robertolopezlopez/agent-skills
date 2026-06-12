#!/usr/bin/env python3
"""Shared runtime config home resolution for Python skill helpers."""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path


API_DOCS_SEGMENT = "api-docs"


def detect_runtime(infer_from: Path | None = None) -> str:
    override = (os.environ.get("AGENT_SKILLS_RUNTIME") or "").strip().lower()
    if override in {"cursor", "codex"}:
        return override

    if infer_from is not None:
        parts = infer_from.resolve().parts
        for idx, part in enumerate(parts):
            if part in {".cursor", ".codex"} and idx + 1 < len(parts) and parts[idx + 1] == "skills":
                return "cursor" if part == ".cursor" else "codex"

    if (Path.home() / ".cursor").is_dir():
        return "cursor"
    return "codex"


def config_home(runtime: str | None = None, infer_from: Path | None = None) -> Path:
    override = (os.environ.get("AGENT_CONFIG_HOME") or "").strip()
    if override:
        return Path(override).expanduser()
    resolved = runtime or detect_runtime(infer_from)
    return Path.home() / (".cursor" if resolved == "cursor" else ".codex")


def env_file_path(basename: str, infer_from: Path | None = None) -> Path:
    return config_home(infer_from=infer_from) / basename


def sanitize_api_docs_slug(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9._-]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "unknown"


def api_docs_root(infer_from: Path | None = None) -> Path:
    return config_home(infer_from=infer_from) / API_DOCS_SEGMENT


def api_docs_dir(slug: str, infer_from: Path | None = None) -> Path:
    return api_docs_root(infer_from=infer_from) / sanitize_api_docs_slug(slug)


def skills_root(infer_from: Path | None = None) -> Path:
    return config_home(infer_from=infer_from) / "skills"


def literal_search_dir(infer_from: Path | None = None) -> Path:
    return skills_root(infer_from=infer_from) / "scripts" / "literal-search"


def literal_search_policy(infer_from: Path | None = None) -> Path:
    return skills_root(infer_from=infer_from) / "LITERAL-CODE-SEARCH.md"


def git_scripts_dir(infer_from: Path | None = None) -> Path:
    return skills_root(infer_from=infer_from) / "scripts" / "git"


def git_access_policy(infer_from: Path | None = None) -> Path:
    return skills_root(infer_from=infer_from) / "GIT-ACCESS.md"


def github_scripts_dir(infer_from: Path | None = None) -> Path:
    return skills_root(infer_from=infer_from) / "scripts" / "github"


def github_access_policy(infer_from: Path | None = None) -> Path:
    return skills_root(infer_from=infer_from) / "GITHUB-ACCESS.md"


def defaults_hint(basename: str, infer_from: Path | None = None) -> str:
    runtime = detect_runtime(infer_from)
    path = config_home(runtime=runtime, infer_from=infer_from) / basename
    return f"{path} (runtime: {runtime})"


def read_env_var(name: str, basename: str, infer_from: Path | None = None) -> str | None:
    path = env_file_path(basename, infer_from=infer_from)
    if not path.is_file():
        return None
    prefix = f"{name}="
    for line in path.read_text().splitlines():
        if line.startswith("#") or not line.startswith(prefix):
            continue
        value = line.split("=", 1)[1].strip()
        if value:
            return value
    return None


def resolve_installed_script(name: str, infer_from: Path | None = None) -> Path | None:
    infer_from = infer_from or Path(__file__)
    candidates = [
        infer_from.resolve().parents[4] / "scripts" / name,
        config_home(infer_from=infer_from) / "skills" / "scripts" / name,
    ]
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if resolved.is_file():
            return resolved
    return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Resolve agent runtime config paths (Cursor vs Codex)."
    )
    parser.add_argument(
        "--infer-from",
        help="Path to infer runtime from (for example a synced skill helper script).",
    )
    parser.add_argument(
        "--runtime",
        action="store_true",
        help="Print the active runtime (cursor or codex).",
    )
    parser.add_argument(
        "--config-home",
        action="store_true",
        help="Print the active config home (~/.cursor or ~/.codex, or AGENT_CONFIG_HOME).",
    )
    parser.add_argument(
        "--atlassian-env",
        action="store_true",
        help="Print the resolved atlassian.env path for the active runtime.",
    )
    parser.add_argument(
        "--circleci-env",
        action="store_true",
        help="Print the resolved circleci.env path for the active runtime.",
    )
    parser.add_argument(
        "--fast-grep-env",
        action="store_true",
        help="Print the resolved fast-grep.env path for the active runtime.",
    )
    parser.add_argument(
        "--skills-root",
        action="store_true",
        help="Print the synced skills install root for the active runtime.",
    )
    parser.add_argument(
        "--literal-search-dir",
        action="store_true",
        help="Print the synced literal-search helpers directory.",
    )
    parser.add_argument(
        "--literal-search-policy",
        action="store_true",
        help="Print the synced LITERAL-CODE-SEARCH.md path.",
    )
    parser.add_argument(
        "--git-scripts-dir",
        action="store_true",
        help="Print the synced Git repository identity helper scripts directory.",
    )
    parser.add_argument(
        "--git-access-policy",
        action="store_true",
        help="Print the synced GIT-ACCESS.md path.",
    )
    parser.add_argument(
        "--github-scripts-dir",
        action="store_true",
        help="Print the synced GitHub helper scripts directory.",
    )
    parser.add_argument(
        "--github-access-policy",
        action="store_true",
        help="Print the synced GITHUB-ACCESS.md path.",
    )
    parser.add_argument(
        "--defaults-hint",
        metavar="FILENAME",
        help="Print a human-readable defaults-file hint (for example atlassian.env).",
    )
    parser.add_argument(
        "--api-docs-root",
        action="store_true",
        help="Print the runtime-local API reference cache root (~/.cursor/api-docs or ~/.codex/api-docs).",
    )
    parser.add_argument(
        "--api-docs-dir",
        metavar="SLUG",
        help="Print the cache directory for a service slug (for example jira-rest-v3).",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    infer_from = Path(args.infer_from).expanduser() if args.infer_from else None

    flags = [
        args.runtime,
        args.config_home,
        args.atlassian_env,
        args.circleci_env,
        args.fast_grep_env,
        args.skills_root,
        args.literal_search_dir,
        args.literal_search_policy,
        args.github_access_policy,
        args.github_scripts_dir,
        args.git_access_policy,
        args.git_scripts_dir,
        bool(args.defaults_hint),
        args.api_docs_root,
        bool(args.api_docs_dir),
    ]
    if sum(int(flag) for flag in flags) != 1:
        parser.error(
            "specify exactly one of --runtime, --config-home, --atlassian-env, "
            "--defaults-hint, --circleci-env, --fast-grep-env, --skills-root, "
            "--literal-search-dir, --literal-search-policy, --github-access-policy, --github-scripts-dir, "
            "--git-access-policy, --git-scripts-dir, --api-docs-root, or --api-docs-dir"
        )

    if args.runtime:
        print(detect_runtime(infer_from))
        return
    if args.config_home:
        print(config_home(infer_from=infer_from))
        return
    if args.atlassian_env:
        print(env_file_path("atlassian.env", infer_from=infer_from))
        return
    if args.circleci_env:
        print(env_file_path("circleci.env", infer_from=infer_from))
        return
    if args.fast_grep_env:
        print(env_file_path("fast-grep.env", infer_from=infer_from))
        return
    if args.skills_root:
        print(skills_root(infer_from=infer_from))
        return
    if args.literal_search_dir:
        print(literal_search_dir(infer_from=infer_from))
        return
    if args.literal_search_policy:
        print(literal_search_policy(infer_from=infer_from))
        return
    if args.github_access_policy:
        print(github_access_policy(infer_from=infer_from))
        return
    if args.github_scripts_dir:
        print(github_scripts_dir(infer_from=infer_from))
        return
    if args.git_access_policy:
        print(git_access_policy(infer_from=infer_from))
        return
    if args.git_scripts_dir:
        print(git_scripts_dir(infer_from=infer_from))
        return
    if args.api_docs_root:
        print(api_docs_root(infer_from=infer_from))
        return
    if args.api_docs_dir:
        print(api_docs_dir(args.api_docs_dir, infer_from=infer_from))
        return
    print(defaults_hint(args.defaults_hint, infer_from=infer_from))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:  # pragma: no cover - CLI guardrail
        print(f"agent_config: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
