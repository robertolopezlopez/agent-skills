#!/usr/bin/env bash
set -euo pipefail

# Report runtime config/auth readiness for agent skills. Suggests setup steps; never prints secrets.
#
# Usage:
#   check_skill_config.sh [SKILL ...]
#   check_skill_config.sh jira confluence
#   check_skill_config.sh --all

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
agent_config="$script_dir/agent_config.py"
agent_config_sh="$script_dir/agent-config.sh"

usage() {
  cat <<'EOH'
Usage: check_skill_config.sh [--all | SKILL ...]

Check auth and defaults-file readiness for skills that use host CLIs or bundled
helpers. Print setup steps when config is missing. Never prints tokens.

Examples:
  check_skill_config.sh jira github
  check_skill_config.sh --all
EOH
}

config_home() {
  python3 "$agent_config" --config-home
}

atlassian_env_path() {
  python3 "$agent_config" --atlassian-env
}

circleci_env_path() {
  python3 "$agent_config" --circleci-env
}

env_var_set_in_file() {
  local file=$1
  local var=$2
  [[ -r "$file" ]] || return 1
  local value
  value=$(grep -E "^${var}=" "$file" 2>/dev/null | head -n1 | cut -d= -f2- | tr -d '\r' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
  [[ -n "$value" && "$value" != 'your-api-token' && "$value" != 'your-personal-api-token' ]]
}

has_atlassian_token() {
  if [[ -n "${ATLASSIAN_API_TOKEN:-}" ]]; then
    return 0
  fi
  local cred_file="${ATLASSIAN_API_TOKEN_FILE:-$HOME/.config/.jira/.credentials}"
  if [[ -r "$cred_file" ]]; then
    local line
    line=$(head -n1 "$cred_file" | tr -d '\r')
    [[ -n "$line" ]]
    return
  fi
  local env_file
  env_file=$(atlassian_env_path)
  env_var_set_in_file "$env_file" ATLASSIAN_API_TOKEN
}

has_circleci_token() {
  if [[ -n "${CIRCLE_TOKEN:-}${CIRCLECI_TOKEN:-}" ]]; then
    return 0
  fi
  local env_file
  env_file=$(circleci_env_path)
  env_var_set_in_file "$env_file" CIRCLE_TOKEN || env_var_set_in_file "$env_file" CIRCLECI_TOKEN
}

print_atlassian_setup() {
  local env_file
  env_file=$(atlassian_env_path)
  cat <<EOF
       setup: 1) Resolve path: python3 $agent_config --atlassian-env
       setup: 2) Copy templates/atlassian.env.example from agent-skills to that path (user edits locally)
       setup: 3) Set ATLASSIAN_API_BASE_URL=https://<your-site>.atlassian.net
       setup: 4) Provide ATLASSIAN_API_TOKEN via export, ~/.config/.jira/.credentials (first line), or atlassian.env
       setup: 5) Ensure git config user.email is set (Atlassian username)
       docs:   https://id.atlassian.com/manage-profile/security/api-tokens
EOF
}

print_circleci_setup() {
  local env_file
  env_file=$(circleci_env_path)
  cat <<EOF
       setup: 1) Resolve path: python3 $agent_config --circleci-env
       setup: 2) Copy templates/circleci.env.example from agent-skills to that path when needed
       setup: 3) Export CIRCLE_TOKEN (preferred) or set in circleci.env
       docs:   https://circleci.com/docs/managing-api-tokens/
EOF
}

check_shared_helpers() {
  local home
  home=$(config_home)
  local missing=0
  for helper in atlassian-auth.sh agent-config.sh validate_artifact.py; do
    if [[ -r "$home/skills/scripts/$helper" ]]; then
      printf 'ok   shared helper: %s\n' "$helper"
    else
      printf 'MISSING shared helper: %s\n' "$helper"
      printf '       setup: run ./scripts/sync_skills.sh --all from the agent-skills repository\n'
      missing=$((missing + 1))
    fi
  done
  return "$missing"
}

check_atlassian_config() {
  local label=$1
  local issues=0
  local env_file
  env_file=$(atlassian_env_path)

  if [[ -r "$env_file" ]]; then
    printf 'ok   %s defaults file exists: %s\n' "$label" "$env_file"
  else
    printf 'NEEDS %s defaults file: %s\n' "$label" "$env_file"
    print_atlassian_setup
    issues=$((issues + 1))
  fi

  if [[ -n "${ATLASSIAN_API_BASE_URL:-}" ]] || env_var_set_in_file "$env_file" ATLASSIAN_API_BASE_URL; then
    printf 'ok   ATLASSIAN_API_BASE_URL configured\n'
  else
    printf 'NEEDS ATLASSIAN_API_BASE_URL (export or %s)\n' "$env_file"
    issues=$((issues + 1))
  fi

  if has_atlassian_token; then
    printf 'ok   ATLASSIAN_API_TOKEN source present\n'
  else
    printf 'NEEDS ATLASSIAN_API_TOKEN (export, credentials file, or %s)\n' "$env_file"
    issues=$((issues + 1))
  fi

  if email=$(git config user.email 2>/dev/null) && [[ -n "$email" ]]; then
    printf 'ok   git config user.email set\n'
  else
    printf 'NEEDS git config user.email (Atlassian auth username)\n'
    printf '       setup: git config --global user.email you@example.com\n'
    issues=$((issues + 1))
  fi

  return "$issues"
}

check_circleci_config() {
  local issues=0
  local env_file
  env_file=$(circleci_env_path)

  if [[ -r "$env_file" ]]; then
    printf 'ok   circleci.env exists: %s\n' "$env_file"
  else
    printf 'OPTIONAL circleci.env missing: %s (export CIRCLE_TOKEN is enough)\n' "$env_file"
  fi

  if has_circleci_token; then
    printf 'ok   CIRCLE_TOKEN source present\n'
  else
    printf 'NEEDS CIRCLE_TOKEN or CIRCLECI_TOKEN (export or %s)\n' "$env_file"
    print_circleci_setup
    issues=$((issues + 1))
  fi

  return "$issues"
}

check_gh_auth() {
  if ! command -v gh >/dev/null 2>&1; then
    printf 'SKIP gh auth (gh not installed — run check_skill_prereqs.sh github)\n'
    return 0
  fi
  if gh auth status >/dev/null 2>&1; then
    printf 'ok   gh auth logged in\n'
    return 0
  fi
  printf 'NEEDS gh auth\n'
  printf '       setup: gh auth login\n'
  printf '       docs:   https://cli.github.com/manual/gh_auth_login\n'
  return 1
}

check_glab_auth() {
  if ! command -v glab >/dev/null 2>&1; then
    printf 'SKIP glab auth (glab not installed — run check_skill_prereqs.sh gitlab)\n'
    return 0
  fi
  if glab auth status >/dev/null 2>&1; then
    printf 'ok   glab auth logged in\n'
    return 0
  fi
  printf 'NEEDS glab auth\n'
  printf '       setup: glab auth login\n'
  printf '       docs:   https://gitlab.com/gitlab-org/cli/-/blob/main/README.md\n'
  return 1
}

check_acli_jira_auth() {
  if ! command -v acli >/dev/null 2>&1; then
    printf 'SKIP acli jira auth (acli not installed — run check_skill_prereqs.sh jira)\n'
    return 0
  fi
  if acli jira auth status >/dev/null 2>&1; then
    printf 'ok   acli jira auth logged in\n'
    return 0
  fi
  printf 'NEEDS acli jira auth\n'
  printf '       setup: acli jira auth login --web\n'
  printf '       alt:   echo <token> | acli jira auth login --site SITE.atlassian.net --email YOU@company.com --token\n'
  printf '       docs:  https://developer.atlassian.com/cloud/acli/\n'
  return 1
}

check_jira_config() {
  local issues=0
  check_acli_jira_auth || issues=$((issues + 1))

  local env_file
  env_file=$(atlassian_env_path)
  if [[ -r "$env_file" ]]; then
    printf 'ok   jira defaults file exists: %s\n' "$env_file"
  else
    printf 'OPTIONAL jira defaults file missing: %s (needed for jira-request fallback)\n' "$env_file"
  fi

  if [[ -n "${ATLASSIAN_API_BASE_URL:-}" ]] || env_var_set_in_file "$env_file" ATLASSIAN_API_BASE_URL; then
    printf 'ok   ATLASSIAN_API_BASE_URL configured\n'
  else
    printf 'OPTIONAL ATLASSIAN_API_BASE_URL missing (jira-request fallback)\n'
  fi

  return "$issues"
}

check_group() {
  local group=$1
  local issues=0
  case "$group" in
    shared)
      check_shared_helpers || issues=$((issues + $?))
      ;;
    github)
      check_gh_auth || issues=$((issues + 1))
      ;;
    gitlab|git)
      check_glab_auth || issues=$((issues + 1))
      ;;
    jira)
      check_jira_config || issues=$((issues + $?))
      ;;
    confluence)
      check_atlassian_config "$group" || issues=$((issues + $?))
      ;;
    circleci)
      check_circleci_config || issues=$((issues + $?))
      ;;
    *)
      echo "unknown skill/group: $group" >&2
      return 2
      ;;
  esac
  return "$issues"
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

targets=()
if [[ "${1:-}" == "--all" ]]; then
  targets=(shared github gitlab jira confluence circleci)
elif [[ $# -eq 0 ]]; then
  usage >&2
  exit 2
else
  targets=("$@")
fi

total_issues=0
seen=""
for raw in "${targets[@]}"; do
  group=$raw
  case "$raw" in
    github-pr-comment-analysis|github-issue-triage) group=github ;;
    gitlab-mr-comment-analysis) group=gitlab ;;
    repository-technical-analysis|diagnose) continue ;;
  esac
  case " $seen " in
    *" $group "*) continue ;;
  esac
  seen="$seen $group"
  echo "==> $group"
  check_group "$group" || total_issues=$((total_issues + $?))
done

if [[ "$total_issues" -gt 0 ]]; then
  echo ""
  echo "Config or auth is incomplete. Help the user finish setup before continuing (see AGENTS.md)."
  exit 1
fi

exit 0
