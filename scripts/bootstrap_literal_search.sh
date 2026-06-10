#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"

install_cursor_rule=0
overwrite=0
dry_run=0

usage() {
  cat <<'EOH'
Usage: bootstrap_literal_search.sh [options]

Install optional Cursor always-on rule for literal code search from templates/
in this repository. Policy and helpers sync via scripts/sync_skills.sh to
~/.cursor/skills/ and ~/.codex/skills/ (LITERAL-CODE-SEARCH.md + literal-search/).

Options:
  --cursor-rule    Install templates/cursor/rules/literal-code-search.mdc
  --overwrite      Replace Cursor rule when template differs
  --dry-run        Print planned actions only
  -h, --help       Show this help

Environment:
  CURSOR_RULES_HOME   Cursor rules directory (default: ~/.cursor/rules)

Examples:
  ./scripts/bootstrap_literal_search.sh --cursor-rule
  ./scripts/sync_skills.sh --all && ./scripts/bootstrap_literal_search.sh --cursor-rule

Codex and other agents: rely on synced LITERAL-CODE-SEARCH.md and investigation
skills (no .mdc rule). Run sync_skills.sh for both targets when using Codex.
EOH
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cursor-rule) install_cursor_rule=1; shift ;;
    --overwrite) overwrite=1; shift ;;
    --dry-run) dry_run=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

sync_rules="$repo_root/scripts/sync_cursor_rules.sh"

if [[ "$install_cursor_rule" -eq 0 ]]; then
  echo "nothing to do (pass --cursor-rule)" >&2
  usage >&2
  exit 2
fi

if [[ ! -x "$sync_rules" ]]; then
  echo "missing helper: $sync_rules" >&2
  exit 1
fi

args=(--only literal-code-search)
[[ "$overwrite" -eq 1 ]] && args+=(--overwrite)
[[ "$dry_run" -eq 1 ]] && args+=(--dry-run)
"$sync_rules" "${args[@]}"
echo "done."
