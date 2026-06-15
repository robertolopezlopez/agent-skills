#!/bin/sh
# Shared agent runtime config home resolution (Cursor vs Codex).
#
# Usage:
#   # shellcheck source=/dev/null
#   . "/path/to/scripts/agent-config.sh"
#   agent_config_init "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
#   agent_config_read_var ATLASSIAN_API_BASE_URL atlassian.env
#
# CLI (when executed directly):
#   scripts/agent-config.sh --config-home
#   scripts/agent-config.sh --atlassian-env
#   scripts/agent-config.sh --circleci-env
#   scripts/agent-config.sh --fast-grep-env
#   scripts/agent-config.sh --skills-root
#   scripts/agent-config.sh --literal-search-dir
#   scripts/agent-config.sh --literal-search-policy
#   scripts/agent-config.sh --runtime
#   scripts/agent-config.sh --defaults-hint atlassian.env
#   scripts/agent-config.sh --api-docs-root
#   scripts/agent-config.sh --api-docs-dir jira-rest-v3
#
# Exports after agent_config_init:
#   AGENT_CONFIG_RUNTIME   cursor | codex
#   AGENT_CONFIG_HOME      ~/.cursor or ~/.codex (or AGENT_CONFIG_HOME override)

AGENT_CONFIG_RUNTIME=""
AGENT_CONFIG_HOME=""

agent_config_default_runtime() {
  if [ -d "${HOME}/.cursor" ]; then
    AGENT_CONFIG_RUNTIME=cursor
    return 0
  fi
  AGENT_CONFIG_RUNTIME=codex
}

agent_config_init() {
  call_dir=${1:-}

  if [ -n "${AGENT_CONFIG_HOME:-}" ]; then
    case "${AGENT_SKILLS_RUNTIME:-}" in
      cursor|codex)
        AGENT_CONFIG_RUNTIME=$AGENT_SKILLS_RUNTIME
        ;;
      *)
        case "$AGENT_CONFIG_HOME" in
          */.codex) AGENT_CONFIG_RUNTIME=codex ;;
          *) AGENT_CONFIG_RUNTIME=cursor ;;
        esac
        ;;
    esac
    export AGENT_CONFIG_RUNTIME AGENT_CONFIG_HOME
    return 0
  fi

  case "${AGENT_SKILLS_RUNTIME:-}" in
    cursor|codex)
      AGENT_CONFIG_RUNTIME=$AGENT_SKILLS_RUNTIME
      ;;
    *)
      if [ -n "$call_dir" ]; then
        case "$call_dir" in
          */.cursor/skills/*|*/.cursor/skills)
            AGENT_CONFIG_RUNTIME=cursor
            ;;
          */.codex/skills/*|*/.codex/skills)
            AGENT_CONFIG_RUNTIME=codex
            ;;
          *)
            agent_config_default_runtime
            ;;
        esac
      else
        agent_config_default_runtime
      fi
      ;;
  esac

  case "$AGENT_CONFIG_RUNTIME" in
    codex) AGENT_CONFIG_HOME=$HOME/.codex ;;
    *) AGENT_CONFIG_RUNTIME=cursor; AGENT_CONFIG_HOME=$HOME/.cursor ;;
  esac

  export AGENT_CONFIG_RUNTIME AGENT_CONFIG_HOME
}

agent_config_env_path() {
  filename=$1
  if [ -z "$AGENT_CONFIG_HOME" ]; then
    agent_config_init
  fi
  printf '%s/%s\n' "$AGENT_CONFIG_HOME" "$filename"
}

agent_config_read_var() {
  var_name=$1
  env_filename=$2
  env_file=$(agent_config_env_path "$env_filename")
  [ -r "$env_file" ] || return 1
  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in
      \#*) ;;
      "${var_name}"=*)
        printf '%s\n' "${line#${var_name}=}"
        return 0
        ;;
    esac
  done < "$env_file"
  return 1
}

agent_config_defaults_hint() {
  env_filename=$1
  if [ -z "$AGENT_CONFIG_HOME" ]; then
    agent_config_init
  fi
  printf '%s/%s (runtime: %s)\n' "$AGENT_CONFIG_HOME" "$env_filename" "$AGENT_CONFIG_RUNTIME"
}

agent_config_api_docs_root() {
  if [ -z "$AGENT_CONFIG_HOME" ]; then
    agent_config_init
  fi
  printf '%s/api-docs\n' "$AGENT_CONFIG_HOME"
}

agent_config_skills_root() {
  if [ -z "$AGENT_CONFIG_HOME" ]; then
    agent_config_init
  fi
  printf '%s/skills\n' "$AGENT_CONFIG_HOME"
}

agent_config_literal_search_dir() {
  if [ -z "$AGENT_CONFIG_HOME" ]; then
    agent_config_init
  fi
  printf '%s/skills/scripts/literal-search\n' "$AGENT_CONFIG_HOME"
}

agent_config_literal_search_policy() {
  if [ -z "$AGENT_CONFIG_HOME" ]; then
    agent_config_init
  fi
  printf '%s/skills/LITERAL-CODE-SEARCH.md\n' "$AGENT_CONFIG_HOME"
}

agent_config_git_scripts_dir() {
  if [ -z "$AGENT_CONFIG_HOME" ]; then
    agent_config_init
  fi
  printf '%s/skills/scripts/git\n' "$AGENT_CONFIG_HOME"
}

agent_config_git_access_policy() {
  if [ -z "$AGENT_CONFIG_HOME" ]; then
    agent_config_init
  fi
  printf '%s/skills/GIT-ACCESS.md\n' "$AGENT_CONFIG_HOME"
}

agent_config_github_scripts_dir() {
  if [ -z "$AGENT_CONFIG_HOME" ]; then
    agent_config_init
  fi
  printf '%s/skills/scripts/github\n' "$AGENT_CONFIG_HOME"
}

agent_config_github_access_policy() {
  if [ -z "$AGENT_CONFIG_HOME" ]; then
    agent_config_init
  fi
  printf '%s/skills/GITHUB-ACCESS.md\n' "$AGENT_CONFIG_HOME"
}

agent_config_jira_scripts_dir() {
  if [ -z "$AGENT_CONFIG_HOME" ]; then
    agent_config_init
  fi
  printf '%s/skills/scripts/jira\n' "$AGENT_CONFIG_HOME"
}

agent_config_jira_access_policy() {
  if [ -z "$AGENT_CONFIG_HOME" ]; then
    agent_config_init
  fi
  printf '%s/skills/JIRA-ACCESS.md\n' "$AGENT_CONFIG_HOME"
}

agent_config_api_docs_dir() {
  slug=$1
  if [ -z "$slug" ]; then
    echo "agent-config.sh: missing api-docs slug" >&2
    return 2
  fi
  if [ -z "$AGENT_CONFIG_HOME" ]; then
    agent_config_init
  fi
  sanitized=$(printf '%s' "$slug" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9._-]+/-/g; s/-+/-/g; s/^-|-$//g')
  [ -n "$sanitized" ] || sanitized=unknown
  printf '%s/api-docs/%s\n' "$AGENT_CONFIG_HOME" "$sanitized"
}

if [ "${0##*/}" = "agent-config.sh" ] && [ -n "${1:-}" ]; then
  case "$1" in
    --config-home)
      agent_config_init "${2:-}"
      printf '%s\n' "$AGENT_CONFIG_HOME"
      exit 0
      ;;
    --atlassian-env)
      agent_config_init "${2:-}"
      agent_config_env_path atlassian.env
      exit 0
      ;;
    --circleci-env)
      agent_config_init "${2:-}"
      agent_config_env_path circleci.env
      exit 0
      ;;
    --fast-grep-env)
      agent_config_init "${2:-}"
      agent_config_env_path fast-grep.env
      exit 0
      ;;
    --skills-root)
      agent_config_init "${2:-}"
      agent_config_skills_root
      exit 0
      ;;
    --literal-search-dir)
      agent_config_init "${2:-}"
      agent_config_literal_search_dir
      exit 0
      ;;
    --literal-search-policy)
      agent_config_init "${2:-}"
      agent_config_literal_search_policy
      exit 0
      ;;
    --github-scripts-dir)
      agent_config_init "${2:-}"
      agent_config_github_scripts_dir
      exit 0
      ;;
    --git-scripts-dir)
      agent_config_init "${2:-}"
      agent_config_git_scripts_dir
      exit 0
      ;;
    --git-access-policy)
      agent_config_init "${2:-}"
      agent_config_git_access_policy
      exit 0
      ;;
    --github-access-policy)
      agent_config_init "${2:-}"
      agent_config_github_access_policy
      exit 0
      ;;
    --jira-scripts-dir)
      agent_config_init "${2:-}"
      agent_config_jira_scripts_dir
      exit 0
      ;;
    --jira-access-policy)
      agent_config_init "${2:-}"
      agent_config_jira_access_policy
      exit 0
      ;;
    --runtime)
      agent_config_init "${2:-}"
      printf '%s\n' "$AGENT_CONFIG_RUNTIME"
      exit 0
      ;;
    --defaults-hint)
      if [ -z "${2:-}" ]; then
        echo "usage: agent-config.sh --defaults-hint FILENAME" >&2
        exit 2
      fi
      agent_config_init "${3:-}"
      agent_config_defaults_hint "$2"
      exit 0
      ;;
    --api-docs-root)
      agent_config_init "${2:-}"
      agent_config_api_docs_root
      exit 0
      ;;
    --api-docs-dir)
      if [ -z "${2:-}" ]; then
        echo "usage: agent-config.sh --api-docs-dir SLUG" >&2
        exit 2
      fi
      agent_config_init "${3:-}"
      agent_config_api_docs_dir "$2"
      exit 0
      ;;
    *)
      echo "usage: agent-config.sh --config-home | --atlassian-env | --circleci-env | --fast-grep-env | --skills-root | --literal-search-dir | --literal-search-policy | --github-access-policy | --github-scripts-dir | --jira-access-policy | --jira-scripts-dir | --git-access-policy | --git-scripts-dir | --runtime | --defaults-hint FILENAME | --api-docs-root | --api-docs-dir SLUG" >&2
      exit 2
      ;;
  esac
fi
