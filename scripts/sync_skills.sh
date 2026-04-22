#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
dest_root="${CODEX_HOME:-$HOME/.codex}/skills"

usage() {
  cat <<'EOF'
Usage: sync_skills.sh [--all] [--changed] [--dry-run] [--delete-missing]

Sync top-level skill directories from this repository into ~/.codex/skills.

Options:
  --all             Sync all top-level skills and shared helper files (default).
  --changed         Sync only top-level skills with local changes.
  --dry-run         Print planned sync actions without copying files.
  --delete-missing  Remove installed copied skills that no longer exist in the repo.
  -h, --help        Show this help.
EOF
}

sync_all=true
changed_only=false
dry_run=false
delete_missing=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all)
      sync_all=true
      changed_only=false
      shift
      ;;
    --changed)
      changed_only=true
      sync_all=false
      shift
      ;;
    --dry-run)
      dry_run=true
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

run_or_print() {
  if [[ "$dry_run" == true ]]; then
    printf '[dry-run] '
    printf '%q ' "$@"
    printf '\n'
  else
    "$@"
  fi
}

collect_skill_dirs() {
  if [[ "$changed_only" == true ]]; then
    git -C "$repo_root" status --short | while IFS= read -r line; do
      path="${line:3}"
      [[ -n "$path" ]] || continue
      top="${path%%/*}"
      if [[ -f "$repo_root/$top/SKILL.md" ]]; then
        printf '%s\n' "$repo_root/$top"
      fi
    done | sort -u
  else
    for skill_dir in "$repo_root"/*; do
      if [[ -d "$skill_dir" && -f "$skill_dir/SKILL.md" ]]; then
        printf '%s\n' "$skill_dir"
      fi
    done | sort
  fi
}

run_or_print mkdir -p "$dest_root" "$dest_root/scripts"

if [[ -f "$repo_root/ARTIFACTS.md" ]]; then
  run_or_print cp "$repo_root/ARTIFACTS.md" "$dest_root/ARTIFACTS.md"
fi

for helper in validate_artifact.py; do
  if [[ -f "$repo_root/scripts/$helper" ]]; then
    run_or_print cp "$repo_root/scripts/$helper" "$dest_root/scripts/$helper"
    run_or_print chmod +x "$dest_root/scripts/$helper"
  fi
done

if [[ "$sync_all" == true || "$changed_only" == true ]]; then
  while IFS= read -r skill_dir; do
    [[ -n "$skill_dir" ]] || continue
    skill_name="$(basename "$skill_dir")"
    run_or_print rm -rf "$dest_root/$skill_name"
    run_or_print cp -R "$skill_dir" "$dest_root/$skill_name"
  done < <(collect_skill_dirs)
fi

if [[ "$delete_missing" == true ]]; then
  shopt -s nullglob
  for installed in "$dest_root"/*; do
    [[ -d "$installed" ]] || continue
    skill_name="$(basename "$installed")"
    if [[ ! -f "$repo_root/$skill_name/SKILL.md" ]]; then
      run_or_print rm -rf "$installed"
    fi
  done
fi
