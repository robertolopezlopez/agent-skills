#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

cat > "$tmp/gh" <<'EOF'
#!/usr/bin/env bash
[[ "${1:-} ${2:-}" == "auth status" ]] && exit 1
exit 2
EOF
chmod +x "$tmp/gh"

if output=$(PATH="$tmp:$PATH" "$repo_root/scripts/check_skill_config.sh" github 2>&1); then
  echo 'expected failed auth check' >&2
  exit 1
fi

grep -q '^UNVERIFIED gh auth$' <<<"$output"
grep -q 'run gh auth login only if that retry confirms' <<<"$output"
! grep -q '^NEEDS gh auth$' <<<"$output"

echo 'ok: failed gh status does not claim missing auth'
