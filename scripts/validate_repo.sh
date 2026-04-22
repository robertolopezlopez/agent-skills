#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"

echo "==> Validating top-level skills"
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

