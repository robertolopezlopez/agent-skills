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

atlassian_auth_fail() {
  echo "$*" >&2
  exit 1
}

atlassian_token_file() {
  printf '%s\n' "${ATLASSIAN_API_TOKEN_FILE:-$HOME/.config/.jira/.credentials}"
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
    atlassian_auth_fail "ATLASSIAN_API_TOKEN must be set or first line of $token_file must contain a token"
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
