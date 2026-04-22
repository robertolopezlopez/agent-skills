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
                if key in {"path", "status"}:
                    current_skill[key] = value

    return {"shared_files": shared_files, "skills": skills}


def main() -> None:
    parser = argparse.ArgumentParser(description="Read the repo skills manifest.")
    parser.add_argument(
        "command",
        choices={"list-skill-paths", "list-skill-names", "list-shared-files", "summary"},
    )
    parser.add_argument(
        "--manifest",
        default=str(Path(__file__).resolve().parents[1] / "skills_manifest.yaml"),
    )
    args = parser.parse_args()

    manifest = load_manifest(Path(args.manifest))

    if args.command == "list-skill-paths":
      for skill in manifest["skills"]:
          print(skill["path"])
    elif args.command == "list-skill-names":
      for skill in manifest["skills"]:
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


if __name__ == "__main__":
    main()
