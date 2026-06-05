#!/bin/sh
# Shared agent runtime config home resolution (Cursor vs Codex).
#
# Usage:
#   # shellcheck source=/dev/null
#   . "/path/to/scripts/agent-config.sh"
#   agent_config_init "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
#   agent_config_read_var ATLASSIAN_API_BASE_URL atlassian.env
#
# Exports after agent_config_init:
#   AGENT_CONFIG_RUNTIME   cursor | codex
#   AGENT_CONFIG_HOME      ~/.cursor or ~/.codex

AGENT_CONFIG_RUNTIME=""
AGENT_CONFIG_HOME=""

agent_config_default_runtime() {
  if [ -d "${HOME}/.cursor/skills" ]; then
    AGENT_CONFIG_RUNTIME=cursor
    return 0
  fi
  if [ -d "${HOME}/.codex/skills" ]; then
    AGENT_CONFIG_RUNTIME=codex
    return 0
  fi
  AGENT_CONFIG_RUNTIME=cursor
}

agent_config_init() {
  call_dir=${1:-}

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
