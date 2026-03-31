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

  if [ -z "$token" ]; then
    atlassian_auth_fail "ATLASSIAN_API_TOKEN must be set"
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
