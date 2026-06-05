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
#   scripts/agent-config.sh --runtime
#   scripts/agent-config.sh --defaults-hint atlassian.env
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
    *)
      echo "usage: agent-config.sh --config-home | --atlassian-env | --runtime | --defaults-hint FILENAME" >&2
      exit 2
      ;;
  esac
fi
