#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
sync_script="$repo_root/scripts/sync_codex_rules.sh"
tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/sync-codex-rules.XXXXXX")"
trap 'rm -rf "$tmp_dir"' EXIT

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

assert_contains() {
  local path=$1
  local expected=$2
  grep -Fq -- "$expected" "$path" || fail "$path does not contain: $expected"
}

assert_not_contains() {
  local path=$1
  local unexpected=$2
  if [[ -f "$path" ]] && grep -Fq -- "$unexpected" "$path"; then
    fail "$path unexpectedly contains: $unexpected"
  fi
}

codex_home="$tmp_dir/codex"
mkdir -p "$codex_home"
printf '# Personal Codex guidance\n\nKeep this text.\n' > "$codex_home/AGENTS.md"

CODEX_HOME="$codex_home" "$sync_script"
assert_contains "$codex_home/AGENTS.md" '# Personal Codex guidance'
assert_contains "$codex_home/AGENTS.md" '<!-- BEGIN agent-skills rule: agent-artifacts-directory -->'
assert_contains "$codex_home/AGENTS.md" '<!-- BEGIN agent-skills rule: literal-code-search -->'
first_install="$(cat "$codex_home/AGENTS.md")"

CODEX_HOME="$codex_home" "$sync_script"
[[ "$(cat "$codex_home/AGENTS.md")" == "$first_install" ]] || fail 'default rerun changed managed rules'

python3 - "$codex_home/AGENTS.md" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text()
path.write_text(text.replace("# Literal code search", "# Locally modified rule", 1))
PY
CODEX_HOME="$codex_home" "$sync_script" --overwrite
assert_contains "$codex_home/AGENTS.md" '# Literal code search'
assert_not_contains "$codex_home/AGENTS.md" '# Locally modified rule'
assert_contains "$codex_home/AGENTS.md" 'Keep this text.'

only_home="$tmp_dir/only"
mkdir -p "$only_home"
CODEX_HOME="$only_home" "$sync_script" --only literal-code-search
assert_contains "$only_home/AGENTS.md" '<!-- BEGIN agent-skills rule: literal-code-search -->'
assert_not_contains "$only_home/AGENTS.md" '<!-- BEGIN agent-skills rule: agent-artifacts-directory -->'

dry_home="$tmp_dir/dry"
mkdir -p "$dry_home"
dry_output="$(CODEX_HOME="$dry_home" "$sync_script" --dry-run)"
[[ "$dry_output" == *'would: install'* ]] || fail 'dry run did not describe installation'
[[ ! -e "$dry_home/AGENTS.md" ]] || fail 'dry run created AGENTS.md'

echo 'ok: sync_codex_rules'
