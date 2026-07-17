#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
home=$tmp/home

for runtime in codex cursor; do
  mkdir -p "$home/.$runtime/skills/scripts"
  cp "$repo_root/scripts/agent_config.py" "$home/.$runtime/skills/scripts/"
  cp "$repo_root/scripts/agent-config.sh" "$home/.$runtime/skills/scripts/"
done

clean_env() {
  env -u AGENT_CONFIG_HOME -u AGENT_SKILLS_RUNTIME \
    -u CODEX_THREAD_ID -u CODEX_CI HOME="$home" "$@"
}

assert_eq() {
  [[ "$1" == "$2" ]] || {
    printf 'expected %s, got %s\n' "$2" "$1" >&2
    exit 1
  }
}

for runtime in codex cursor; do
  expected=$home/.$runtime/circleci.env
  assert_eq "$(clean_env python3 "$home/.$runtime/skills/scripts/agent_config.py" --circleci-env)" "$expected"
  assert_eq "$(clean_env "$home/.$runtime/skills/scripts/agent-config.sh" --circleci-env)" "$expected"
done

assert_eq "$(clean_env env CODEX_THREAD_ID=test python3 "$repo_root/scripts/agent_config.py" --circleci-env)" "$home/.codex/circleci.env"
assert_eq "$(clean_env env CODEX_CI=1 "$repo_root/scripts/agent-config.sh" --circleci-env)" "$home/.codex/circleci.env"
assert_eq "$(clean_env env CODEX_THREAD_ID=test AGENT_SKILLS_RUNTIME=cursor python3 "$repo_root/scripts/agent_config.py" --circleci-env)" "$home/.cursor/circleci.env"

echo 'ok: agent config runtime resolution'
