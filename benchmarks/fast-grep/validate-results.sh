#!/usr/bin/env bash
set -euo pipefail

BENCH_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

if [[ $# -lt 1 ]]; then
  echo "Usage: validate-results.sh <run-dir> [results-dir]" >&2
  exit 2
fi

args=("$BENCH_DIR/validate-results.py" "--run-dir" "$1")
[[ $# -ge 2 ]] && args+=("--results-dir" "$2")

python3 "${args[@]}"
