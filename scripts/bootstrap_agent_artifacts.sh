#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
resolver="$repo_root/scripts/resolve_artifact_path.py"

install_cursor_rule=0
install_codex_rule=0
install_store_readme=1
scaffold_global_playbook=1
overwrite=0
dry_run=0

usage() {
  cat <<'EOH'
Usage: bootstrap_agent_artifacts.sh [options]

Bootstrap the external agent-artifacts store and optional Cursor/Codex rules
from templates/ in this repository. Idempotent by default (skip existing files).

Options:
  --cursor-rule          Install templates/cursor/rules/agent-artifacts-directory.mdc
  --codex-rule           Merge templates/codex/rules/agent-artifacts-directory.md into global AGENTS.md
  --no-store-readme      Skip $AGENT_ARTIFACTS_HOME/README.md
  --no-global-playbook   Skip $AGENT_ARTIFACTS_HOME/_global/NEXT_TIME_CHECKS.md scaffold
  --overwrite            Replace README and refresh installed rules when templates differ
  --dry-run              Print planned actions only
  -h, --help             Show this help

Environment:
  AGENT_ARTIFACTS_HOME   Override artifact store root (same as resolve_artifact_path.py)
  CURSOR_RULES_HOME      Cursor rules directory (default: ~/.cursor/rules)
  CODEX_HOME             Codex home directory (default: ~/.codex)
  CODEX_AGENTS_FILE      Codex global instructions file (default: $CODEX_HOME/AGENTS.md)

Examples:
  ./scripts/bootstrap_agent_artifacts.sh --cursor-rule
  ./scripts/bootstrap_agent_artifacts.sh --codex-rule
  AGENT_ARTIFACTS_HOME=~/Documents/agent-artifacts ./scripts/bootstrap_agent_artifacts.sh
EOH
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cursor-rule) install_cursor_rule=1; shift ;;
    --codex-rule) install_codex_rule=1; shift ;;
    --no-store-readme) install_store_readme=0; shift ;;
    --no-global-playbook) scaffold_global_playbook=0; shift ;;
    --overwrite) overwrite=1; shift ;;
    --dry-run) dry_run=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ ! -x "$resolver" ]]; then
  echo "missing resolver: $resolver" >&2
  exit 1
fi

artifacts_home="$(python3 "$resolver" --artifacts-home)"
global_root="$(python3 "$resolver" --global-artifacts-root)"
global_playbook="$(python3 "$resolver" --global-next-time-checks)"

readme_template="$repo_root/templates/agent-artifacts/README.md"
playbook_template="$repo_root/templates/agent-artifacts/NEXT_TIME_CHECKS.global.scaffold.md"

run_or_echo() {
  if [[ "$dry_run" -eq 1 ]]; then
    printf 'would: %s\n' "$*"
  else
    "$@"
  fi
}

install_file() {
  local src=$1
  local dest=$2
  local label=$3

  if [[ ! -f "$src" ]]; then
    echo "missing template: $src" >&2
    exit 1
  fi

  if [[ -f "$dest" && "$overwrite" -eq 0 ]]; then
    echo "skip ($label exists): $dest"
    return 0
  fi

  run_or_echo mkdir -p "$(dirname "$dest")"
  if [[ "$dry_run" -eq 1 ]]; then
    if [[ -f "$dest" && "$overwrite" -eq 1 ]]; then
      printf 'would: overwrite %s from %s\n' "$dest" "$src"
    else
      printf 'would: install %s -> %s\n' "$src" "$dest"
    fi
  else
    cp "$src" "$dest"
    echo "installed ($label): $dest"
  fi
}

echo "artifact store: $artifacts_home"

run_or_echo mkdir -p "$global_root"

if [[ "$install_store_readme" -eq 1 ]]; then
  install_file "$readme_template" "$artifacts_home/README.md" "store README"
fi

if [[ "$scaffold_global_playbook" -eq 1 ]]; then
  install_file "$playbook_template" "$global_playbook" "global NEXT_TIME_CHECKS"
fi

if [[ "$install_cursor_rule" -eq 1 ]]; then
  sync_rules="$repo_root/scripts/sync_cursor_rules.sh"
  if [[ ! -x "$sync_rules" ]]; then
    echo "missing helper: $sync_rules" >&2
    exit 1
  fi
  rule_args=(--only agent-artifacts-directory)
  [[ "$overwrite" -eq 1 ]] && rule_args+=(--overwrite)
  [[ "$dry_run" -eq 1 ]] && rule_args+=(--dry-run)
  "$sync_rules" "${rule_args[@]}"
fi

if [[ "$install_codex_rule" -eq 1 ]]; then
  sync_rules="$repo_root/scripts/sync_codex_rules.sh"
  if [[ ! -x "$sync_rules" ]]; then
    echo "missing helper: $sync_rules" >&2
    exit 1
  fi
  rule_args=(--only agent-artifacts-directory)
  [[ "$overwrite" -eq 1 ]] && rule_args+=(--overwrite)
  [[ "$dry_run" -eq 1 ]] && rule_args+=(--dry-run)
  "$sync_rules" "${rule_args[@]}"
fi

echo "done."
