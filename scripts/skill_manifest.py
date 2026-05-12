#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


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


def parse_csv_set(raw: str) -> set[str]:
    parts = [p.strip() for p in raw.replace("\n", ",").split(",")]
    return {p for p in parts if p}


def should_install_skill(
    skill: dict[str, str],
    exclude_release_groups: set[str],
    exclude_skill_names: set[str],
) -> bool:
    if skill["name"] in exclude_skill_names:
        return False
    rg = (skill.get("release_group") or "").strip()
    if rg and rg in exclude_release_groups:
        return False
    return True


def filter_installable_skills(
    manifest: dict[str, object],
    exclude_release_groups: set[str],
    exclude_skill_names: set[str],
) -> list[dict[str, str]]:
    skills = manifest["skills"]
    assert isinstance(skills, list)
    return [
        s
        for s in skills
        if should_install_skill(s, exclude_release_groups, exclude_skill_names)
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Read the repo skills manifest.")
    parser.add_argument(
        "command",
        choices={
            "list-skill-paths",
            "list-skill-names",
            "list-skill-name-paths",
            "list-excluded-skill-names",
            "list-shared-files",
            "summary",
            "summary-by-group",
        },
    )
    parser.add_argument(
        "--group-by",
        choices={"release_group", "repo_scope", "type"},
        default="release_group",
    )
    parser.add_argument(
        "--manifest",
        default=str(Path(__file__).resolve().parents[1] / "skills_manifest.yaml"),
    )
    parser.add_argument(
        "--exclude-release-groups",
        default="",
        help=(
            "Comma-separated release_group values to omit from install-oriented listings "
            "(list-skill-* and list-excluded-skill-names)."
        ),
    )
    parser.add_argument(
        "--exclude-skill-names",
        default="",
        help=(
            "Comma-separated skill names to omit from install-oriented listings "
            "(list-skill-* and list-excluded-skill-names)."
        ),
    )
    args = parser.parse_args()

    manifest = load_manifest(Path(args.manifest))
    exclude_groups = parse_csv_set(args.exclude_release_groups)
    exclude_names = parse_csv_set(args.exclude_skill_names)
    installable = filter_installable_skills(manifest, exclude_groups, exclude_names)

    if args.command == "list-skill-paths":
        for skill in installable:
            print(skill["path"])
    elif args.command == "list-skill-names":
        for skill in installable:
            print(skill["name"])
    elif args.command == "list-skill-name-paths":
        for skill in installable:
            print(f"{skill['name']}\t{skill['path']}")
    elif args.command == "list-excluded-skill-names":
        skills = manifest["skills"]
        assert isinstance(skills, list)
        for skill in skills:
            if not should_install_skill(skill, exclude_groups, exclude_names):
                print(skill["name"])
    elif args.command == "list-shared-files":
        for shared_file in manifest["shared_files"]:
            print(shared_file)
    elif args.command == "summary":
        skills = manifest["skills"]
        stable = [skill for skill in skills if skill.get("status") == "stable"]
        experimental = [skill for skill in skills if skill.get("status") == "experimental"]
        print(f"skills: {len(skills)}")
        print(f"stable: {len(stable)}")
        print(f"experimental: {len(experimental)}")
        print(f"shared_files: {len(manifest['shared_files'])}")
    elif args.command == "summary-by-group":
        groups: dict[str, list[dict[str, str]]] = {}
        for skill in manifest["skills"]:
            key = skill.get(args.group_by, "unknown")
            groups.setdefault(key, []).append(skill)
        for key in sorted(groups):
            print(f"{args.group_by}: {key} ({len(groups[key])})")
            for skill in sorted(groups[key], key=lambda s: s["name"]):
                print(f"  - {skill['name']}")


if __name__ == "__main__":
    main()
