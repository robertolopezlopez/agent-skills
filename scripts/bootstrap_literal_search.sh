#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"

install_cursor_rule=0
install_codex_rule=0
overwrite=0
dry_run=0

usage() {
  cat <<'EOH'
Usage: bootstrap_literal_search.sh [options]

Install optional Cursor or Codex always-on guidance for literal code search from
templates/ in this repository. Policy and helpers sync via scripts/sync_skills.sh to
~/.cursor/skills/ and ~/.codex/skills/ (LITERAL-CODE-SEARCH.md + literal-search/).

Options:
  --cursor-rule    Install templates/cursor/rules/literal-code-search.mdc
  --codex-rule     Merge templates/codex/rules/literal-code-search.md into global AGENTS.md
  --overwrite      Refresh the installed rule when its template differs
  --dry-run        Print planned actions only
  -h, --help       Show this help

Environment:
  CURSOR_RULES_HOME   Cursor rules directory (default: ~/.cursor/rules)
  CODEX_HOME          Codex home directory (default: ~/.codex)
  CODEX_AGENTS_FILE   Codex global instructions file (default: $CODEX_HOME/AGENTS.md)

Examples:
  ./scripts/bootstrap_literal_search.sh --cursor-rule
  ./scripts/bootstrap_literal_search.sh --codex-rule
  ./scripts/sync_skills.sh --all && ./scripts/bootstrap_literal_search.sh --cursor-rule

Both rule variants point to the synced LITERAL-CODE-SEARCH.md workflow.
EOH
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cursor-rule) install_cursor_rule=1; shift ;;
    --codex-rule) install_codex_rule=1; shift ;;
    --overwrite) overwrite=1; shift ;;
    --dry-run) dry_run=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ "$install_cursor_rule" -eq 0 && "$install_codex_rule" -eq 0 ]]; then
  echo "nothing to do (pass --cursor-rule and/or --codex-rule)" >&2
  usage >&2
  exit 2
fi

if [[ "$install_cursor_rule" -eq 1 ]]; then
  sync_rules="$repo_root/scripts/sync_cursor_rules.sh"
  [[ -x "$sync_rules" ]] || { echo "missing helper: $sync_rules" >&2; exit 1; }
  args=(--only literal-code-search)
  [[ "$overwrite" -eq 1 ]] && args+=(--overwrite)
  [[ "$dry_run" -eq 1 ]] && args+=(--dry-run)
  "$sync_rules" "${args[@]}"
fi

if [[ "$install_codex_rule" -eq 1 ]]; then
  sync_rules="$repo_root/scripts/sync_codex_rules.sh"
  [[ -x "$sync_rules" ]] || { echo "missing helper: $sync_rules" >&2; exit 1; }
  args=(--only literal-code-search)
  [[ "$overwrite" -eq 1 ]] && args+=(--overwrite)
  [[ "$dry_run" -eq 1 ]] && args+=(--dry-run)
  "$sync_rules" "${args[@]}"
fi
echo "done."
