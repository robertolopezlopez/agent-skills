#!/bin/sh
set -eu

# Shared Atlassian auth/env helper for reusable scripts.
#
# Intended usage from another script:
#
#   # shellcheck source=/dev/null
#   . "/path/to/atlassian-auth.sh"
#   atlassian_require_auth
#   curl -u "$ATLASSIAN_AUTH_USERPASS" ...
#
# Exports on success:
#   ATLASSIAN_AUTH_EMAIL
#   ATLASSIAN_AUTH_TOKEN
#   ATLASSIAN_AUTH_USERPASS
#
# Token resolution order:
#   1. ATLASSIAN_API_TOKEN in the environment
#   2. first line of ATLASSIAN_API_TOKEN_FILE (default ~/.config/.jira/.credentials)
#   3. ATLASSIAN_API_TOKEN in runtime atlassian.env (resolved via agent-config.sh)

atlassian_auth_fail() {
  echo "$*" >&2
  exit 1
}

atlassian_token_file() {
  printf '%s\n' "${ATLASSIAN_API_TOKEN_FILE:-$HOME/.config/.jira/.credentials}"
}

atlassian_load_config_helper() {
  _d=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ -n "$_d" ]; do
    if [ -r "$_d/scripts/agent-config.sh" ]; then
      # shellcheck source=/dev/null
      . "$_d/scripts/agent-config.sh"
      if [ -z "${AGENT_CONFIG_HOME:-}" ]; then
        agent_config_init "$_d"
      fi
      return 0
    fi
    [ "$_d" = "/" ] && break
    _d=$(dirname "$_d")
  done
  return 1
}

atlassian_git_email() {
  if ! email=$(git config user.email 2>/dev/null); then
    atlassian_auth_fail "git config user.email is not set"
  fi

  if [ -z "$email" ]; then
    atlassian_auth_fail "git config user.email is not set"
  fi

  ATLASSIAN_AUTH_EMAIL=$email
  export ATLASSIAN_AUTH_EMAIL
}

atlassian_api_token() {
  token=${ATLASSIAN_API_TOKEN:-}
  token_file=$(atlassian_token_file)

  if [ -z "$token" ]; then
    if [ -r "$token_file" ]; then
      token=$(head -n 1 "$token_file" | tr -d '\r')
    fi
  fi

  if [ -z "$token" ]; then
    if atlassian_load_config_helper; then
      if token_from_env=$(agent_config_read_var ATLASSIAN_API_TOKEN atlassian.env); then
        token=$token_from_env
      fi
    fi
  fi

  if [ -z "$token" ]; then
    defaults_hint=
    if atlassian_load_config_helper; then
      defaults_hint=$(agent_config_defaults_hint atlassian.env)
    else
      defaults_hint="runtime atlassian.env (resolve with scripts/agent_config.py --atlassian-env)"
    fi
    atlassian_auth_fail "ATLASSIAN_API_TOKEN must be set, or present in $defaults_hint, or first line of $token_file"
  fi

  ATLASSIAN_AUTH_TOKEN=$token
  export ATLASSIAN_AUTH_TOKEN
}

atlassian_require_auth() {
  atlassian_git_email
  atlassian_api_token
  ATLASSIAN_AUTH_USERPASS=$ATLASSIAN_AUTH_EMAIL:$ATLASSIAN_AUTH_TOKEN
  export ATLASSIAN_AUTH_USERPASS
}

atlassian_require_auth_vars() {
  atlassian_require_auth
}
