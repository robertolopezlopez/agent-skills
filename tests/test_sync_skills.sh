#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

installed="$tmp_dir/codex/skills/python-fastapi-contributor"
marker="$tmp_dir/copy-started"
mkdir -p "$installed" "$tmp_dir/bin"
printf '%s\n' 'previous skill' > "$installed/SKILL.md"
printf '%s\n' 'stale' > "$installed/stale.txt"

real_cp="$(command -v cp)"
cat > "$tmp_dir/bin/cp" <<'EOF'
#!/usr/bin/env bash
for arg in "$@"; do
  if [[ "$arg" == */skills/core/python-fastapi-contributor* ]]; then
    : > "$SYNC_TEST_MARKER"
    sleep 1
    break
  fi
done
exec "$SYNC_TEST_REAL_CP" "$@"
EOF
chmod +x "$tmp_dir/bin/cp"

PATH="$tmp_dir/bin:$PATH" \
  CODEX_HOME="$tmp_dir/codex" \
  AGENT_SKILLS_SYNC_TARGETS=codex \
  SYNC_TEST_MARKER="$marker" \
  SYNC_TEST_REAL_CP="$real_cp" \
  "$repo_root/scripts/sync_skills.sh" --all > "$tmp_dir/sync.out" 2>&1 &
sync_pid=$!

for _ in {1..200}; do
  [[ -e "$marker" ]] && break
  if ! kill -0 "$sync_pid" 2>/dev/null; then
    wait "$sync_pid" || true
    cat "$tmp_dir/sync.out"
    echo "sync exited before copying test skill" >&2
    exit 1
  fi
  sleep 0.01
done

if [[ ! -f "$installed/SKILL.md" ]]; then
  wait "$sync_pid"
  echo "installed SKILL.md disappeared during sync" >&2
  exit 1
fi

wait "$sync_pid"
cmp -s "$repo_root/skills/core/python-fastapi-contributor/SKILL.md" "$installed/SKILL.md"
[[ ! -e "$installed/stale.txt" ]]
echo "sync preserves installed SKILL.md"
