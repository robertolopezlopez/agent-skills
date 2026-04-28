#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
summary_only=false

usage() {
  cat <<'EOH'
Usage: validate_repo.sh [--summary]

Validate manifest-declared skills and root workflow artifacts.

Options:
  --summary    Print a short success summary after validation completes.
  -h, --help   Show this help.
EOH
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --summary)
      summary_only=true
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

echo "==> Validating manifest-declared skills"
python3 "$repo_root/scripts/validate_skill.py"

artifact_paths=()
while IFS= read -r path; do
  [[ -n "$path" ]] && artifact_paths+=("$path")
done < <(
  find "$repo_root" -maxdepth 1 -type f \
    \( -name 'task_*.md' -o -name 'review_mr_*.md' -o -name 'analysis_mr_*.md' -o -name 'work_plan_mr_*.md' -o -name 'mr_*_comment_report.md' \) \
    | sort
)

if [[ ${#artifact_paths[@]} -gt 0 ]]; then
  echo "==> Validating workflow artifacts"
  python3 "$repo_root/scripts/validate_artifact.py" "${artifact_paths[@]}"
else
  echo "==> No matching workflow artifacts found"
fi

if [[ "$summary_only" == true ]]; then
  skill_count="$(python3 "$repo_root/scripts/skill_manifest.py" list-skill-names | wc -l | tr -d ' ')"
  artifact_count="${#artifact_paths[@]}"
  echo "==> Summary: validated ${skill_count} skills and ${artifact_count} root artifact(s)"
  echo "==> Manifest summary"
  python3 "$repo_root/scripts/skill_manifest.py" summary
fi
