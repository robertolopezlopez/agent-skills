#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
dest_root="${CODEX_HOME:-$HOME/.codex}/skills"
manifest_reader="$repo_root/scripts/skill_manifest.py"

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
  manifest_paths="$("$manifest_reader" list-skill-paths)"
  if [[ "$changed_only" == true ]]; then
    git -C "$repo_root" status --short | while IFS= read -r line; do
      path="${line:3}"
      [[ -n "$path" ]] || continue
      top="${path%%/*}"
      if printf '%s\n' "$manifest_paths" | grep -Fxq "$top"; then
        printf '%s\n' "$repo_root/$top"
      fi
    done | sort -u
  else
    while IFS= read -r skill_path; do
      [[ -n "$skill_path" ]] || continue
      if [[ -d "$repo_root/$skill_path" && -f "$repo_root/$skill_path/SKILL.md" ]]; then
        printf '%s\n' "$repo_root/$skill_path"
      fi
    done <<< "$manifest_paths"
  fi
}

collect_shared_files() {
  while IFS= read -r shared_file; do
    [[ -n "$shared_file" ]] || continue
    printf '%s\n' "$shared_file"
  done < <("$manifest_reader" list-shared-files)
}

copy_shared_file() {
  local relative_path="$1"
  local src="$repo_root/$relative_path"
  local dest="$dest_root/$relative_path"
  [[ -f "$src" ]] || return 0
  run_or_print mkdir -p "$(dirname "$dest")"
  run_or_print cp "$src" "$dest"
  if [[ "$relative_path" == scripts/* ]]; then
    run_or_print chmod +x "$dest"
  fi
}

if [[ ! -x "$manifest_reader" ]]; then
  echo "missing executable manifest reader: $manifest_reader" >&2
  exit 1
fi

run_or_print mkdir -p "$dest_root"

while IFS= read -r shared_file; do
  [[ -n "$shared_file" ]] || continue
  copy_shared_file "$shared_file"
done < <(collect_shared_files)

if [[ "$sync_all" == true || "$changed_only" == true ]]; then
  while IFS= read -r skill_dir; do
    [[ -n "$skill_dir" ]] || continue
    skill_name="$(basename "$skill_dir")"
    run_or_print rm -rf "$dest_root/$skill_name"
    run_or_print cp -R "$skill_dir" "$dest_root/$skill_name"
  done < <(collect_skill_dirs)
fi

if [[ "$delete_missing" == true ]]; then
  manifest_names="$("$manifest_reader" list-skill-names)"
  shopt -s nullglob
  for installed in "$dest_root"/*; do
    [[ -d "$installed" ]] || continue
    skill_name="$(basename "$installed")"
    if ! printf '%s\n' "$manifest_names" | grep -Fxq "$skill_name"; then
      run_or_print rm -rf "$installed"
    fi
  done
fi
