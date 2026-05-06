#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
manifest_reader="$repo_root/scripts/skill_manifest.py"
codex_skills_root="${CODEX_HOME:-$HOME/.codex}/skills"
cursor_skills_root="${CURSOR_AGENT_SKILLS_HOME:-$HOME/.cursor}/skills"

usage() {
  cat <<'EOH'
Usage: sync_skills.sh [--all] [--changed] [--dry-run] [--verify] [--delete-missing]
                      [--codex-only | --cursor-only]

Sync manifest-declared skills from this repository into installed skill directories.

Default destinations (override with flags or AGENT_SKILLS_SYNC_TARGETS):
  - Codex:  ${CODEX_HOME:-~/.codex}/skills
  - Cursor: ${CURSOR_AGENT_SKILLS_HOME:-~/.cursor}/skills

Environment:
  CODEX_HOME                  Base for Codex config (default: ~/.codex)
  CURSOR_AGENT_SKILLS_HOME    Parent of skills/ for Cursor (default: ~/.cursor)
  AGENT_SKILLS_SYNC_TARGETS   Codex-and-Cursor sync scope when no target flags:
                              codex | cursor | codex,cursor | all | both
                              (default: codex,cursor)

Options:
  --all             Sync all manifest-declared skills and shared helper files (default).
  --changed         Sync only manifest-declared skills with local changes.
  --dry-run         Print planned sync actions without copying files.
  --verify          Verify that manifest-declared shared files and skills exist in the installed copy after sync.
  --delete-missing  Remove installed copied skills that no longer exist in the manifest.
  --codex-only      Sync only to the Codex skills directory.
  --cursor-only     Sync only to the Cursor agent skills directory.
  -h, --help        Show this help.
EOH
}

sync_all=true
changed_only=false
dry_run=false
verify=false
delete_missing=false
cli_target=""

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
    --verify)
      verify=true
      shift
      ;;
    --delete-missing)
      delete_missing=true
      shift
      ;;
    --codex-only)
      if [[ -n "$cli_target" && "$cli_target" != codex ]]; then
        echo "use only one of --codex-only or --cursor-only" >&2
        exit 2
      fi
      cli_target=codex
      shift
      ;;
    --cursor-only)
      if [[ -n "$cli_target" && "$cli_target" != cursor ]]; then
        echo "use only one of --codex-only or --cursor-only" >&2
        exit 2
      fi
      cli_target=cursor
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

if [[ -n "$cli_target" ]]; then
  target_mode="$cli_target"
else
  case "${AGENT_SKILLS_SYNC_TARGETS:-codex,cursor}" in
    codex)
      target_mode=codex
      ;;
    cursor)
      target_mode=cursor
      ;;
    codex,cursor | all | both)
      target_mode=all
      ;;
    *)
      echo "unknown AGENT_SKILLS_SYNC_TARGETS: ${AGENT_SKILLS_SYNC_TARGETS:-}" >&2
      exit 2
      ;;
  esac
fi

dest_roots=()
if [[ "$target_mode" == all ]]; then
  dest_roots+=("$codex_skills_root" "$cursor_skills_root")
else
  case "$target_mode" in
    codex) dest_roots=("$codex_skills_root") ;;
    cursor) dest_roots=("$cursor_skills_root") ;;
  esac
fi

planned_shared_files=()
planned_skill_names=()
deleted_skill_names=()

run_or_print() {
  if [[ "$dry_run" == true ]]; then
    return 0
  else
    "$@"
  fi
}

collect_skill_entries() {
  "$manifest_reader" list-skill-name-paths
}

collect_shared_files() {
  "$manifest_reader" list-shared-files
}

copy_shared_file() {
  local dest_root="$1"
  local relative_path="$2"
  local src="$repo_root/$relative_path"
  local dest="$dest_root/$relative_path"
  [[ -f "$src" ]] || return 0
  run_or_print mkdir -p "$(dirname "$dest")"
  run_or_print cp "$src" "$dest"
  if [[ "$relative_path" == scripts/* ]]; then
    run_or_print chmod +x "$dest"
  fi
}

sync_to_destination() {
  local dest_root="$1"

  run_or_print mkdir -p "$dest_root"

  while IFS= read -r shared_file; do
    [[ -n "$shared_file" ]] || continue
    copy_shared_file "$dest_root" "$shared_file"
  done < <(collect_shared_files)

  if [[ "$sync_all" == true || "$changed_only" == true ]]; then
    changed_paths=""
    if [[ "$changed_only" == true ]]; then
      changed_paths="$(git -C "$repo_root" status --short | sed 's/^...//' | sed '/^$/d')"
    fi

    while IFS=$'\t' read -r skill_name skill_path; do
      [[ -n "$skill_name" && -n "$skill_path" ]] || continue
      skill_dir="$repo_root/$skill_path"
      [[ -d "$skill_dir" && -f "$skill_dir/SKILL.md" ]] || continue

      if [[ "$changed_only" == true ]]; then
        match=false
        while IFS= read -r changed_path; do
          [[ -n "$changed_path" ]] || continue
          if [[ "$changed_path" == "$skill_path" || "$changed_path" == "$skill_path/"* ]]; then
            match=true
            break
          fi
        done <<< "$changed_paths"
        [[ "$match" == true ]] || continue
      fi

      run_or_print rm -rf "$dest_root/$skill_name"
      run_or_print cp -R "$skill_dir" "$dest_root/$skill_name"
    done < <(collect_skill_entries)
  fi

  if [[ "$delete_missing" == true ]]; then
    manifest_names="$($manifest_reader list-skill-names)"
    shopt -s nullglob
    for installed in "$dest_root"/*; do
      [[ -d "$installed" ]] || continue
      skill_name="$(basename "$installed")"
      # Not manifest skills: dirs required by shared_files (e.g. scripts/ for validate_artifact.py)
      if [[ "$skill_name" == "scripts" ]]; then
        continue
      fi
      if ! printf '%s\n' "$manifest_names" | grep -Fxq "$skill_name"; then
        run_or_print rm -rf "$installed"
        if [[ "$dest_root" == "${dest_roots[0]}" ]]; then
          deleted_skill_names+=("$skill_name")
        fi
      fi
    done
  fi
}

if [[ ! -x "$manifest_reader" ]]; then
  echo "missing executable manifest reader: $manifest_reader" >&2
  exit 1
fi

while IFS= read -r shared_file; do
  [[ -n "$shared_file" ]] || continue
  planned_shared_files+=("$shared_file")
done < <(collect_shared_files)

if [[ "$sync_all" == true || "$changed_only" == true ]]; then
  changed_paths=""
  if [[ "$changed_only" == true ]]; then
    changed_paths="$(git -C "$repo_root" status --short | sed 's/^...//' | sed '/^$/d')"
  fi

  while IFS=$'\t' read -r skill_name skill_path; do
    [[ -n "$skill_name" && -n "$skill_path" ]] || continue
    skill_dir="$repo_root/$skill_path"
    [[ -d "$skill_dir" && -f "$skill_dir/SKILL.md" ]] || continue

    if [[ "$changed_only" == true ]]; then
      match=false
      while IFS= read -r changed_path; do
        [[ -n "$changed_path" ]] || continue
        if [[ "$changed_path" == "$skill_path" || "$changed_path" == "$skill_path/"* ]]; then
          match=true
          break
        fi
      done <<< "$changed_paths"
      [[ "$match" == true ]] || continue
    fi

    planned_skill_names+=("$skill_name")
  done < <(collect_skill_entries)
fi

for dest_root in "${dest_roots[@]}"; do
  sync_to_destination "$dest_root"
done

print_summary() {
  local mode_label="all"
  if [[ "$changed_only" == true ]]; then
    mode_label="changed"
  fi

  if [[ "$dry_run" == true ]]; then
    echo "==> Dry-run sync summary"
  else
    echo "==> Sync summary"
  fi

  echo "mode: $mode_label"
  case "$target_mode" in
    all) echo "targets: codex+cursor" ;;
    codex) echo "targets: codex" ;;
    cursor) echo "targets: cursor" ;;
  esac
  for dest_root in "${dest_roots[@]}"; do
    echo "destination: $dest_root"
  done
  echo "shared files: ${#planned_shared_files[@]}"
  if [[ ${#planned_shared_files[@]} -gt 0 ]]; then
    for shared_file in "${planned_shared_files[@]}"; do
      echo "  - $shared_file"
    done
  fi
  echo "skills: ${#planned_skill_names[@]}"
  if [[ ${#planned_skill_names[@]} -gt 0 ]]; then
    for skill_name in "${planned_skill_names[@]}"; do
      echo "  - $skill_name"
    done
  fi

  if [[ "$verify" == true && "$dry_run" == false ]]; then
    echo "verify: enabled"
  fi

  if [[ "$delete_missing" == true ]]; then
    echo "deleted installed skills (names removed from each target): ${#deleted_skill_names[@]}"
    if [[ ${#deleted_skill_names[@]} -gt 0 ]]; then
      for skill_name in "${deleted_skill_names[@]}"; do
        echo "  - $skill_name"
      done
    fi
  fi
}

verify_install() {
  local dest_root="$1"
  local failures=0
  local verified_sf=0
  local verified_sk=0
  echo "==> Verifying installed copy at $dest_root"

  for shared_file in "${planned_shared_files[@]}"; do
    if [[ ! -f "$dest_root/$shared_file" ]]; then
      echo "missing shared file: $dest_root/$shared_file" >&2
      failures=$((failures + 1))
    else
      verified_sf=$((verified_sf + 1))
    fi
  done

  for skill_name in "${planned_skill_names[@]}"; do
    if [[ ! -f "$dest_root/$skill_name/SKILL.md" ]]; then
      echo "missing installed skill: $dest_root/$skill_name/SKILL.md" >&2
      failures=$((failures + 1))
    else
      verified_sk=$((verified_sk + 1))
    fi
  done

  if [[ "$failures" -gt 0 ]]; then
    echo "verification failed with $failures missing installed item(s)" >&2
    exit 1
  fi
  echo "verification OK for $dest_root (shared files: $verified_sf, skills: $verified_sk)"
}

print_summary

if [[ "$verify" == true ]]; then
  if [[ "$dry_run" == true ]]; then
    echo "cannot verify during dry-run" >&2
    exit 2
  fi
  for dest_root in "${dest_roots[@]}"; do
    verify_install "$dest_root"
  done
fi
