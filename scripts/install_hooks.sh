#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
src_dir="$repo_root/git-hooks"
dest_dir="$repo_root/.git/hooks"

usage() {
  cat <<'EOF'
Usage: install_hooks.sh [--copy]

Install repository Git hooks from git-hooks/ into .git/hooks.

Options:
  --copy            Copy hooks instead of creating symlinks.
  -h, --help        Show this help.
EOF
}

mode="symlink"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --copy)
      mode="copy"
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

if [[ ! -d "$dest_dir" ]]; then
  echo "missing Git hooks directory: $dest_dir" >&2
  exit 1
fi

for hook in "$src_dir"/*; do
  [[ -f "$hook" ]] || continue
  hook_name="$(basename "$hook")"
  target="$dest_dir/$hook_name"
  rm -f "$target"
  if [[ "$mode" == "copy" ]]; then
    cp "$hook" "$target"
  else
    ln -s "$hook" "$target"
  fi
  chmod +x "$target"
  echo "installed $hook_name -> $target"
done

