#!/usr/bin/env python3
"""Migrate in-repo _artifacts_/ trees into the external agent artifact store."""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from resolve_artifact_path import find_git_root, repo_artifacts_root  # noqa: E402


def merge_tree(source: Path, destination: Path, *, dry_run: bool) -> list[str]:
    actions: list[str] = []
    if not source.is_dir():
        return actions

    for item in sorted(source.rglob("*")):
        relative = item.relative_to(source)
        target = destination / relative
        if item.is_dir():
            if not dry_run and not target.exists():
                target.mkdir(parents=True, exist_ok=True)
                actions.append(f"mkdir {target}")
            continue

        if target.exists():
            actions.append(f"skip existing {target}")
            continue

        actions.append(f"copy {item} -> {target}")
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)

    return actions


def remove_legacy_tree(source: Path, *, dry_run: bool) -> None:
    if not source.is_dir():
        return
    if dry_run:
        print(f"would remove legacy tree: {source}")
        return
    shutil.rmtree(source)


def migrate_legacy_artifacts(
    legacy_root: Path,
    *,
    repo_root: Path | None = None,
    dry_run: bool = False,
    remove_source: bool = False,
) -> int:
    legacy_root = legacy_root.resolve()
    if legacy_root.name != "_artifacts_":
        print(f"error: expected an _artifacts_ directory, got {legacy_root}", file=sys.stderr)
        return 1
    if not legacy_root.is_dir():
        print(f"skip missing: {legacy_root}")
        return 0

    resolved_repo_root = repo_root or find_git_root(legacy_root.parent)
    if resolved_repo_root is None:
        print(f"error: could not find git root for {legacy_root}", file=sys.stderr)
        return 1

    destination = repo_artifacts_root(resolved_repo_root)
    print(f"repo: {resolved_repo_root}")
    print(f"from: {legacy_root}")
    print(f"to:   {destination}")

    actions = merge_tree(legacy_root, destination, dry_run=dry_run)
    if not actions:
        print("nothing to copy")
    else:
        for line in actions:
            print(line)

    if remove_source and actions:
        remove_legacy_tree(legacy_root, dry_run=dry_run)

    return 0


def discover_legacy_roots(search_roots: list[Path]) -> list[Path]:
    found: list[Path] = []
    seen: set[Path] = set()
    for root in search_roots:
        if not root.is_dir():
            continue
        for path in root.rglob("_artifacts_"):
            if not path.is_dir():
                continue
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            found.append(resolved)
    return sorted(found)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Migrate in-repo _artifacts_/ to external store.")
    parser.add_argument(
        "paths",
        nargs="*",
        help="Legacy _artifacts_ directories. When omitted, scan --search-root values.",
    )
    parser.add_argument(
        "--search-root",
        action="append",
        default=[],
        help="Directory to scan recursively for _artifacts/ (repeatable).",
    )
    parser.add_argument("--repo-root", help="Override git repository root for explicit paths.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without copying.")
    parser.add_argument(
        "--remove-source",
        action="store_true",
        help="Delete legacy _artifacts_/ after a successful copy.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    legacy_roots: list[Path]
    if args.paths:
        legacy_roots = [Path(p).expanduser() for p in args.paths]
    elif args.search_root:
        legacy_roots = discover_legacy_roots([Path(p).expanduser() for p in args.search_root])
    else:
        parser.error("provide legacy paths or --search-root")

    if not legacy_roots:
        print("no legacy _artifacts_/ directories found")
        return

    repo_root = Path(args.repo_root).expanduser().resolve() if args.repo_root else None
    exit_code = 0
    for legacy_root in legacy_roots:
        result = migrate_legacy_artifacts(
            legacy_root,
            repo_root=repo_root,
            dry_run=args.dry_run,
            remove_source=args.remove_source,
        )
        if result != 0:
            exit_code = result
        print()
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
