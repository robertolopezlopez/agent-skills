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


def validate_skill_dir(skill_dir: Path) -> list[str]:
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

    if name_match:
        name = name_match.group(1).strip().strip("'\"")
        if name != skill_dir.name:
            errors.append(
                f"frontmatter name mismatch: expected '{skill_dir.name}', found '{name}'"
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

    errors.extend(validate_relative_references(skill_dir, text))
    warnings.extend(validate_recommended_sections(body))
    return prefix_errors(skill_dir, errors + [f"WARNING: {warning}" for warning in warnings])


def validate_relative_references(skill_dir: Path, text: str) -> list[str]:
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
        if not normalized or normalized.startswith(".."):
            continue
        candidate = skill_dir / normalized
        if not candidate.exists():
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


def discover_top_level_skill_dirs(repo_root: Path) -> list[Path]:
    result: list[Path] = []
    for child in sorted(repo_root.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith("."):
            continue
        if (child / "SKILL.md").exists():
            result.append(child)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate top-level skill directories in this repository."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Optional skill directories or SKILL.md files to validate. Defaults to all top-level skills.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]

    targets: list[Path] = []
    if args.paths:
        for raw in args.paths:
            path = Path(raw).resolve()
            if path.is_file() and path.name == "SKILL.md":
                targets.append(path.parent)
            else:
                targets.append(path)
    else:
        targets = discover_top_level_skill_dirs(repo_root)

    total_errors = 0
    total_warnings = 0
    seen_names: dict[str, Path] = {}
    for skill_dir in targets:
        errors = validate_skill_dir(skill_dir)
        warning_lines = [line for line in errors if "WARNING:" in line]
        error_lines = [line for line in errors if "WARNING:" not in line]

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

    if total_warnings:
        print(f"\nWarnings: {total_warnings}")
    raise SystemExit(1 if total_errors else 0)


if __name__ == "__main__":
    main()
