#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


FRONTMATTER_NAME_RE = re.compile(r"^name:\s*(.+?)\s*$", re.MULTILINE)
FRONTMATTER_DESCRIPTION_RE = re.compile(r"^description:\s*(.+?)\s*$", re.MULTILINE)
RELATIVE_MD_LINK_RE = re.compile(r"\[[^\]]+\]\((?![a-z]+:|/|#)([^)]+)\)")
INLINE_CODE_SPAN_RE = re.compile(r"`([^`\n]+)`")
KNOWN_PATH_PREFIXES = (
    "./",
    "../",
    "scripts/",
    "templates/",
    "references/",
    "assets/",
)


def load_manifest(path: Path) -> dict[str, object]:
    shared_files: list[str] = []
    skills: list[dict[str, str]] = []
    current_skill: dict[str, str] | None = None
    section: str | None = None

    for raw_line in path.read_text().splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == "shared_files:":
            section = "shared_files"
            current_skill = None
            continue
        if stripped == "skills:":
            section = "skills"
            current_skill = None
            continue
        if section == "shared_files" and stripped.startswith("- "):
            shared_files.append(stripped[2:].strip())
            continue
        if section == "skills":
            if stripped.startswith("- name:"):
                current_skill = {"name": stripped.split(":", 1)[1].strip()}
                skills.append(current_skill)
                continue
            if current_skill is None:
                continue
            if ":" in stripped and not stripped.startswith("- "):
                key, value = stripped.split(":", 1)
                key = key.strip()
                value = value.strip()
                if key in {"path", "status", "type", "repo_scope", "release_group", "owner"}:
                    current_skill[key] = value

    return {"shared_files": shared_files, "skills": skills}


def extract_frontmatter(text: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    return text[4:end]


def extract_body(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    if end == -1:
        return text
    return text[end + 5 :]


def find_primary_heading(body: str) -> str | None:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def validate_skill_dir(
    skill_dir: Path,
    repo_root: Path,
    expected_name: str | None = None,
) -> list[str]:
    errors: list[str] = []
    warnings: list[str] = []
    skill_md = skill_dir / "SKILL.md"

    if not skill_dir.is_dir():
        return [f"{skill_dir}: not a directory"]
    if not skill_md.exists():
        return [f"{skill_dir}: missing SKILL.md"]

    text = skill_md.read_text()
    frontmatter = extract_frontmatter(text)
    body = extract_body(text)

    if frontmatter is None:
        errors.append("missing YAML frontmatter delimited by ---")
        return prefix_errors(skill_dir, errors)

    name_match = FRONTMATTER_NAME_RE.search(frontmatter)
    desc_match = FRONTMATTER_DESCRIPTION_RE.search(frontmatter)

    if not name_match:
        errors.append("missing frontmatter field: name")
    if not desc_match:
        errors.append("missing frontmatter field: description")

    if name_match and expected_name:
        name = name_match.group(1).strip().strip("'\"")
        if name != expected_name:
            errors.append(
                f"frontmatter name mismatch: expected '{expected_name}', found '{name}'"
            )

    if desc_match:
        description = desc_match.group(1).strip().strip("'\"")
        if not description:
            errors.append("frontmatter description must not be empty")

    heading = find_primary_heading(body)
    if heading is None:
        errors.append("missing primary heading starting with '# '")

    if (
        "## Workflow" not in body
        and "## First Read" not in body
        and "## Inputs" not in body
        and "## Input" not in body
    ):
        errors.append(
            "expected at least one operational section: ## Workflow, ## First Read, ## Inputs, or ## Input"
        )

    errors.extend(validate_relative_references(skill_dir, repo_root, text, expected_name))
    warnings.extend(validate_recommended_sections(body))
    return prefix_errors(skill_dir, errors + [f"WARNING: {warning}" for warning in warnings])


def validate_relative_references(
    skill_dir: Path,
    repo_root: Path,
    text: str,
    expected_name: str | None,
) -> list[str]:
    errors: list[str] = []

    linked_paths = set()
    for match in RELATIVE_MD_LINK_RE.finditer(text):
        linked_paths.add(match.group(1).strip())
    for match in INLINE_CODE_SPAN_RE.finditer(text):
        candidate = match.group(1).strip()
        if looks_like_repo_path(candidate):
            linked_paths.add(candidate)

    for raw in sorted(linked_paths):
        normalized = raw.split("#", 1)[0]
        if not normalized:
            continue

        repo_candidate = (skill_dir / normalized).resolve(strict=False)
        if repo_candidate.exists():
            continue

        if expected_name:
            installed_layout_anchor = repo_root / expected_name
            installed_candidate = (installed_layout_anchor / normalized).resolve(strict=False)
            if installed_candidate.exists():
                continue

        if normalized.startswith(".."):
            # Parent-relative references may intentionally point outside this repo,
            # for example to a sibling checked out separately on a developer machine.
            # Validate them when they resolve locally or in installed-layout form,
            # but do not hard-fail when they are external and unavailable in CI.
            continue

        errors.append(f"referenced path does not exist: {normalized}")

    return errors


def prefix_errors(skill_dir: Path, errors: list[str]) -> list[str]:
    return [f"{skill_dir}: {error}" for error in errors]


def validate_recommended_sections(body: str) -> list[str]:
    warnings: list[str] = []
    recommended_groups = [
        ("When to Use", ("## When to Use",)),
        ("When Not to Use", ("## When Not to Use",)),
        ("Validation", ("## Validation",)),
        ("Outputs", ("## Outputs", "## Outputs / Artifacts", "## Output Expectations")),
        ("Companion Skills", ("## Companion Skills",)),
        ("Safety Notes", ("## Safety Notes", "## Constraints", "## General Notes")),
    ]
    for label, variants in recommended_groups:
        if not any(variant in body for variant in variants):
            warnings.append(f"recommended section missing: {label}")
    return warnings


def looks_like_repo_path(candidate: str) -> bool:
    if not candidate or "/" not in candidate:
        return False
    if any(ch in candidate for ch in ("\n", "\r", " ", ">", "<")):
        return False
    if "://" in candidate:
        return False
    return candidate.startswith(KNOWN_PATH_PREFIXES)


def discover_all_skill_dirs(repo_root: Path) -> list[Path]:
    result: list[Path] = []
    for skill_md in sorted(repo_root.rglob("SKILL.md")):
        if any(part.startswith(".") for part in skill_md.relative_to(repo_root).parts):
            continue
        result.append(skill_md.parent)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate manifest-declared skill directories in this repository."
    )
    parser.add_argument(
        "--strict-new",
        action="store_true",
        help="Treat missing recommended sections as hard failures for explicit path targets.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Optional skill directories or SKILL.md files to validate. Defaults to all manifest-declared skills.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    manifest_path = repo_root / "skills_manifest.yaml"
    manifest = load_manifest(manifest_path)
    manifest_entries = manifest["skills"]
    manifest_paths = {Path(skill["path"]) for skill in manifest_entries}
    manifest_names = [skill["name"] for skill in manifest_entries]
    manifest_by_relpath = {Path(skill["path"]): skill for skill in manifest_entries}

    targets: list[Path] = []
    if args.paths:
        for raw in args.paths:
            path = Path(raw).resolve()
            if path.is_file() and path.name == "SKILL.md":
                targets.append(path.parent)
            else:
                targets.append(path)
    else:
        targets = [repo_root / Path(skill["path"]) for skill in manifest_entries]

    total_errors = 0
    total_warnings = 0
    seen_names: dict[str, Path] = {}
    for skill_dir in targets:
        try:
            rel_dir = skill_dir.relative_to(repo_root)
        except ValueError:
            rel_dir = None
        manifest_entry = manifest_by_relpath.get(rel_dir) if rel_dir is not None else None
        expected_name = manifest_entry["name"] if manifest_entry is not None else None

        errors = validate_skill_dir(skill_dir, repo_root, expected_name)
        warning_lines = [line for line in errors if "WARNING:" in line]
        error_lines = [line for line in errors if "WARNING:" not in line]

        if args.strict_new and args.paths:
            error_lines.extend(
                [warning.replace("WARNING: ", "") for warning in warning_lines]
            )
            warning_lines = []

        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            text = skill_md.read_text()
            frontmatter = extract_frontmatter(text)
            if frontmatter is not None:
                name_match = FRONTMATTER_NAME_RE.search(frontmatter)
                if name_match:
                    name = name_match.group(1).strip().strip("'\"")
                    previous = seen_names.get(name)
                    if previous is not None and previous != skill_dir:
                        error_lines.append(
                            f"{skill_dir}: duplicate skill name '{name}' also used by {previous}"
                        )
                    else:
                        seen_names[name] = skill_dir

        if error_lines:
            print(f"{skill_dir}: FAIL")
            for error in error_lines:
                print(f"  - {error}")
            for warning in warning_lines:
                print(f"  - {warning}")
            total_errors += len(error_lines)
            total_warnings += len(warning_lines)
        elif warning_lines:
            print(f"{skill_dir}: WARN")
            for warning in warning_lines:
                print(f"  - {warning}")
            total_warnings += len(warning_lines)
        else:
            print(f"{skill_dir}: OK")

    repo_skill_dirs = {path.relative_to(repo_root) for path in discover_all_skill_dirs(repo_root)}
    for path in sorted(repo_skill_dirs - manifest_paths):
        print(f"{manifest_path}: FAIL")
        print(f"  - {manifest_path}: missing manifest entry for skill path '{path}'")
        total_errors += 1

    for path in sorted(manifest_paths - repo_skill_dirs):
        print(f"{manifest_path}: FAIL")
        print(f"  - {manifest_path}: manifest path does not resolve to a skill directory with SKILL.md: '{path}'")
        total_errors += 1

    if len(set(manifest_names)) != len(manifest_names):
        print(f"{manifest_path}: FAIL")
        print(f"  - {manifest_path}: duplicate skill name entries in manifest")
        total_errors += 1

    for skill in manifest_entries:
        for required_key in ("name", "path", "type", "repo_scope", "release_group"):
            if required_key not in skill or not skill[required_key]:
                print(f"{manifest_path}: FAIL")
                print(
                    f"  - {manifest_path}: manifest entry missing required field '{required_key}'"
                )
                total_errors += 1

    for shared_file in manifest["shared_files"]:
        if not (repo_root / shared_file).exists():
            print(f"{manifest_path}: FAIL")
            print(f"  - {manifest_path}: shared file does not exist: '{shared_file}'")
            total_errors += 1

    if total_warnings:
        print(f"\nWarnings: {total_warnings}")
    raise SystemExit(1 if total_errors else 0)


if __name__ == "__main__":
    main()
