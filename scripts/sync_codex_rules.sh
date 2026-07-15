#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
rules_src="$repo_root/templates/codex/rules"
codex_home="${CODEX_HOME:-$HOME/.codex}"
codex_agents_file="${CODEX_AGENTS_FILE:-$codex_home/AGENTS.md}"
overwrite=0
dry_run=0
only=()

usage() {
  cat <<'EOH'
Usage: sync_codex_rules.sh [options]

Merge Codex always-on rules from templates/codex/rules/*.md into the global
Codex AGENTS.md (default: ~/.codex/AGENTS.md). Each rule is stored in a managed
block so personal guidance outside those blocks is preserved.

Options:
  --overwrite       Refresh managed rule blocks when templates differ (default: skip existing)
  --only NAME       Sync one rule (basename without .md, or full filename)
  --dry-run         Print planned actions only
  -h, --help        Show this help

Environment:
  CODEX_HOME          Codex home directory (default: ~/.codex)
  CODEX_AGENTS_FILE   Full destination path (default: $CODEX_HOME/AGENTS.md)

Examples:
  ./scripts/sync_codex_rules.sh --overwrite
  ./scripts/sync_codex_rules.sh --only literal-code-search
EOH
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --overwrite) overwrite=1; shift ;;
    --dry-run) dry_run=1; shift ;;
    --only)
      [[ $# -ge 2 ]] || { echo "sync_codex_rules: --only requires a name" >&2; exit 2; }
      only+=("$2")
      shift 2
      ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ ! -d "$rules_src" ]]; then
  echo "sync_codex_rules: missing templates directory: $rules_src" >&2
  exit 1
fi

if [[ ! -d "$codex_home" && -z "${CODEX_HOME:-}" && -z "${CODEX_AGENTS_FILE:-}" ]]; then
  echo "sync_codex_rules: skip (~/.codex not found; set CODEX_HOME or CODEX_AGENTS_FILE to override)" >&2
  exit 0
fi

normalize_only_name() {
  local raw=$1
  case "$raw" in
    *.md) printf '%s\n' "$raw" ;;
    *) printf '%s.md\n' "$raw" ;;
  esac
}

should_sync() {
  local base=$1
  if [[ ${#only[@]} -eq 0 ]]; then
    return 0
  fi
  local entry norm
  for entry in "${only[@]}"; do
    norm=$(normalize_only_name "$entry")
    if [[ "$base" == "$norm" ]]; then
      return 0
    fi
  done
  return 1
}

merge_rule() {
  local src=$1
  local name=$2
  python3 - "$codex_agents_file" "$src" "$name" <<'PY'
from pathlib import Path
import os
import stat
import sys
import tempfile

dest = Path(sys.argv[1])
src = Path(sys.argv[2])
name = sys.argv[3]
begin = f"<!-- BEGIN agent-skills rule: {name} -->"
end = f"<!-- END agent-skills rule: {name} -->"
block = f"{begin}\n{src.read_text().rstrip()}\n{end}\n"
text = dest.read_text() if dest.exists() else ""

begin_at = text.find(begin)
end_at = text.find(end)
if (begin_at < 0) != (end_at < 0) or (begin_at >= 0 and end_at < begin_at):
    raise SystemExit(f"sync_codex_rules: malformed managed block for {name} in {dest}")

if begin_at >= 0:
    after = end_at + len(end)
    if after < len(text) and text[after] == "\n":
        after += 1
    updated = text[:begin_at] + block + text[after:]
else:
    separator = "" if not text else ("\n" if text.endswith("\n") else "\n\n")
    updated = text + separator + block

dest.parent.mkdir(parents=True, exist_ok=True)
mode = stat.S_IMODE(dest.stat().st_mode) if dest.exists() else 0o644
fd, tmp_name = tempfile.mkstemp(prefix=f".{dest.name}.", dir=dest.parent)
try:
    with os.fdopen(fd, "w") as handle:
        handle.write(updated)
    os.chmod(tmp_name, mode)
    os.replace(tmp_name, dest)
finally:
    if os.path.exists(tmp_name):
        os.unlink(tmp_name)
PY
}

installed=0
updated=0
skipped=0
matched=0

shopt -s nullglob
for src in "$rules_src"/*.md; do
  base=$(basename "$src")
  should_sync "$base" || continue
  matched=$((matched + 1))
  name=${base%.md}
  begin="<!-- BEGIN agent-skills rule: $name -->"
  exists=0
  if [[ -f "$codex_agents_file" ]] && grep -Fq -- "$begin" "$codex_agents_file"; then
    exists=1
  fi

  if [[ "$exists" -eq 1 && "$overwrite" -eq 0 ]]; then
    echo "skip (managed rule exists): $name in $codex_agents_file"
    skipped=$((skipped + 1))
    continue
  fi

  if [[ "$dry_run" -eq 1 ]]; then
    if [[ "$exists" -eq 1 ]]; then
      echo "would: update managed rule $name in $codex_agents_file"
      updated=$((updated + 1))
    else
      echo "would: install managed rule $name in $codex_agents_file"
      installed=$((installed + 1))
    fi
    continue
  fi

  merge_rule "$src" "$name"
  if [[ "$exists" -eq 1 ]]; then
    echo "updated: $name in $codex_agents_file"
    updated=$((updated + 1))
  else
    echo "installed: $name in $codex_agents_file"
    installed=$((installed + 1))
  fi
done

if [[ "$matched" -eq 0 ]]; then
  echo "sync_codex_rules: no matching templates in $rules_src" >&2
  exit 1
fi

echo "sync_codex_rules: installed=$installed updated=$updated skipped=$skipped dest=$codex_agents_file"
