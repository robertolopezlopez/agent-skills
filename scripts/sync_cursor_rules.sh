#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
rules_src="$repo_root/templates/cursor/rules"
cursor_rules_dir="${CURSOR_RULES_HOME:-$HOME/.cursor/rules}"
overwrite=0
dry_run=0
only=()

usage() {
  cat <<'EOH'
Usage: sync_cursor_rules.sh [options]

Copy Cursor always-on rules from templates/cursor/rules/*.mdc into the local
Cursor rules directory (default: ~/.cursor/rules).

Options:
  --overwrite       Replace installed rules when templates differ (default: skip existing)
  --only NAME       Sync one rule (basename without .mdc, or full filename)
  --dry-run         Print planned actions only
  -h, --help        Show this help

Environment:
  CURSOR_RULES_HOME   Cursor rules directory (default: ~/.cursor/rules)

Examples:
  ./scripts/sync_cursor_rules.sh --overwrite          # post-commit / refresh all
  ./scripts/sync_cursor_rules.sh --only literal-code-search
EOH
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --overwrite) overwrite=1; shift ;;
    --dry-run) dry_run=1; shift ;;
    --only)
      [[ $# -ge 2 ]] || { echo "sync_cursor_rules: --only requires a name" >&2; exit 2; }
      only+=("$2")
      shift 2
      ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ ! -d "$rules_src" ]]; then
  echo "sync_cursor_rules: missing templates directory: $rules_src" >&2
  exit 1
fi

if [[ ! -d "${HOME}/.cursor" && -z "${CURSOR_RULES_HOME:-}" ]]; then
  echo "sync_cursor_rules: skip (~/.cursor not found; set CURSOR_RULES_HOME to override)" >&2
  exit 0
fi

run_or_echo() {
  if [[ "$dry_run" -eq 1 ]]; then
    printf 'would: %s\n' "$*"
  else
    "$@"
  fi
}

normalize_only_name() {
  local raw=$1
  case "$raw" in
    *.mdc) printf '%s\n' "$raw" ;;
    *) printf '%s.mdc\n' "$raw" ;;
  esac
}

should_sync() {
  local base=$1
  if [[ ${#only[@]} -eq 0 ]]; then
    return 0
  fi
  local entry want norm
  for entry in "${only[@]}"; do
    norm=$(normalize_only_name "$entry")
    if [[ "$base" == "$norm" ]]; then
      return 0
    fi
  done
  return 1
}

installed=0
skipped=0

shopt -s nullglob
for src in "$rules_src"/*.mdc; do
  base=$(basename "$src")
  should_sync "$base" || continue
  dest="$cursor_rules_dir/$base"

  if [[ -f "$dest" && "$overwrite" -eq 0 ]]; then
    echo "skip (exists): $dest"
    skipped=$((skipped + 1))
    continue
  fi

  if [[ "$dry_run" -eq 1 ]]; then
    if [[ -f "$dest" && "$overwrite" -eq 1 ]]; then
      printf 'would: overwrite %s from %s\n' "$dest" "$src"
    else
      printf 'would: install %s -> %s\n' "$src" "$dest"
    fi
  else
    run_or_echo mkdir -p "$cursor_rules_dir"
    cp "$src" "$dest"
    if [[ -f "$dest" && "$overwrite" -eq 1 ]]; then
      echo "updated: $dest"
    else
      echo "installed: $dest"
    fi
  fi
  installed=$((installed + 1))
done

if [[ "$installed" -eq 0 && "$skipped" -eq 0 ]]; then
  echo "sync_cursor_rules: no matching templates in $rules_src" >&2
  exit 1
fi

echo "sync_cursor_rules: installed/updated=$installed skipped=$skipped dest=$cursor_rules_dir"
