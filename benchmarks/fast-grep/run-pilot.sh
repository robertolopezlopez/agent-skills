#!/usr/bin/env bash
set -euo pipefail

# Shell phase of the fast-grep benchmark pilot.
# Produces timing + capped outputs under benchmarks/fast-grep/results/run-<timestamp>/

BENCH_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "$BENCH_DIR/../.." && pwd)

usage() {
  cat <<'EOF'
Usage: run-pilot.sh [OPTIONS]

Run the hybrid benchmark shell phase (timing + capped outputs).

Options:
  --out-dir DIR         Output directory (default: results/run-<timestamp>)
  --skip-hyperfine      Imprecise fallback (rejected when precision.hyperfine_required)
  --repo-root DIR       Override repository root
  -h, --help            Show this help

Requires: python3, rg, scripts/literal-search/fast-grep
Optional: hyperfine (recommended)
EOF
}

OUT_DIR=""
SKIP_HYPERFINE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out-dir)
      OUT_DIR=$2
      shift 2
      ;;
    --skip-hyperfine)
      SKIP_HYPERFINE=1
      shift
      ;;
    --repo-root)
      REPO_ROOT=$(cd "$2" && pwd)
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "run-pilot.sh: unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

command -v python3 >/dev/null 2>&1 || {
  echo "run-pilot.sh: python3 is required" >&2
  exit 2
}
command -v rg >/dev/null 2>&1 || {
  echo "run-pilot.sh: rg is required for path A timing parity" >&2
  exit 2
}

args=("$BENCH_DIR/run_pilot.py" "--repo-root" "$REPO_ROOT")
[[ -n "$OUT_DIR" ]] && args+=("--out-dir" "$OUT_DIR")
[[ "$SKIP_HYPERFINE" -eq 1 ]] && args+=("--skip-hyperfine")

echo "run-pilot.sh: repo_root=$REPO_ROOT" >&2
RUN_DIR=$(python3 "${args[@]}")
echo "run-pilot.sh: outputs in $RUN_DIR" >&2

if [[ -x "$BENCH_DIR/estimate-tokens.py" ]]; then
  python3 "$BENCH_DIR/estimate-tokens.py" --run-dir "$RUN_DIR" || true
fi

echo "run-pilot.sh: next — start 3 parallel agents (see prompts/coordinator.md)" >&2
echo "run-pilot.sh: then validate-results.sh and merge-results.sh on $RUN_DIR" >&2
