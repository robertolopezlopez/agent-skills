#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
dest_root="${CODEX_HOME:-$HOME/.codex}/skills"

usage() {
  cat <<'EOF'
Usage: sync_skills.sh [--all] [--delete-missing]

Sync top-level skill directories from this repository into ~/.codex/skills.

Options:
  --all             Sync all top-level skills and shared helper files (default).
  --delete-missing  Remove installed copied skills that no longer exist in the repo.
  -h, --help        Show this help.
EOF
}

sync_all=true
delete_missing=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all)
      sync_all=true
      shift
      ;;
    --delete-missing)
      delete_missing=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

mkdir -p "$dest_root" "$dest_root/scripts"

if [[ -f "$repo_root/ARTIFACTS.md" ]]; then
  cp "$repo_root/ARTIFACTS.md" "$dest_root/ARTIFACTS.md"
fi

for helper in validate_artifact.py; do
  if [[ -f "$repo_root/scripts/$helper" ]]; then
    cp "$repo_root/scripts/$helper" "$dest_root/scripts/$helper"
    chmod +x "$dest_root/scripts/$helper"
  fi
done

if [[ "$sync_all" == true ]]; then
  for skill_dir in "$repo_root"/*; do
    if [[ -d "$skill_dir" && -f "$skill_dir/SKILL.md" ]]; then
      skill_name="$(basename "$skill_dir")"
      rm -rf "$dest_root/$skill_name"
      cp -R "$skill_dir" "$dest_root/$skill_name"
    fi
  done
fi

if [[ "$delete_missing" == true ]]; then
  shopt -s nullglob
  for installed in "$dest_root"/*; do
    [[ -d "$installed" ]] || continue
    skill_name="$(basename "$installed")"
    if [[ ! -f "$repo_root/$skill_name/SKILL.md" ]]; then
      rm -rf "$installed"
    fi
  done
fi

