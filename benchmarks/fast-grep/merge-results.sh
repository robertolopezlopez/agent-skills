#!/usr/bin/env bash
set -euo pipefail

BENCH_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

if [[ $# -lt 1 ]]; then
  echo "Usage: merge-results.sh <run-dir> [results-dir]" >&2
  exit 2
fi

args=("$BENCH_DIR/merge-results.py" "--run-dir" "$1")
[[ $# -ge 2 ]] && args+=("--results-dir" "$2")

python3 "${args[@]}"
