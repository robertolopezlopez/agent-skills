---
name: splunk-jira-ticket
description: Fetch and summarize Splunk Jira or Atlassian tickets, especially when a browser URL redirects to login. Use when the user provides a `splunk.atlassian.net` issue URL or issue key, asks to summarize a Jira ticket, asks to override the Jira issue API host and path, or asks to debug Jira access using `ATLASSIAN_API_TOKEN`.
---

# Splunk Jira Ticket Access

When a Splunk Jira issue is not readable through normal browser access, use the Jira REST API before concluding the ticket is inaccessible.

## Workflow

1. Extract the issue key from the URL or user request.
2. Accept an optional host + path parameter before the issue key. Default to `https://splunk.atlassian.net/rest/api/3/issue/`.
3. Use `git config user.email` as the Atlassian username.
4. Use `ATLASSIAN_API_TOKEN` from the environment as the password.
5. Check whether `~/.local/bin/jira-api` exists.
6. If it does not exist:
   - create `~/.local/bin` with `mkdir -p ~/.local/bin`
   - copy `scripts/jira-api` from this skill into `~/.local/bin/jira-api`
   - run `chmod +x ~/.local/bin/jira-api`
   - if file creation or chmod fails due to sandbox restrictions, rerun those commands with escalated permissions
7. Infer the user's interactive shell from `$SHELL`, not from session metadata or assumptions.
   - Resolve the shell name from `basename "$SHELL"` when available.
   - Treat `fish` as fish syntax.
   - Treat `bash`, `zsh`, `sh`, `dash`, and `ksh` as sh-compatible syntax.
   - If `$SHELL` is empty or unrecognized, do not guess; prefer invoking `~/.local/bin/jira-api` directly.
8. Check whether `PATH` contains `$HOME/.local/bin`.
9. If it does not, add `$HOME/.local/bin` to `PATH` for the current command flow before invoking the helper, using the syntax that matches `$SHELL`:
   - for sh-compatible shells: `export PATH="$HOME/.local/bin:$PATH"`
   - for fish: `set -gx PATH $HOME/.local/bin $PATH`
   - for unknown shells: skip PATH mutation and invoke `~/.local/bin/jira-api` directly
10. Build the helper command with `jira-api` when `~/.local/bin` is on `PATH`; otherwise call `~/.local/bin/jira-api` directly.
    - default issue API base: `jira-api {ISSUE_KEY}`
    - overridden issue API base: `jira-api {HOST_AND_PATH} {ISSUE_KEY}`
11. When the task needs explicit field selection, pass the fields list as the final helper argument.
    - default issue API base: `jira-api {ISSUE_KEY} {FIELDS}`
    - overridden issue API base: `jira-api {HOST_AND_PATH} {ISSUE_KEY} {FIELDS}`
12. The helper should normalize the default or overridden host + path into an issue API base ending in `/rest/api/3/issue/`, then fetch:

```text
https://splunk.atlassian.net/rest/api/3/issue/{ISSUE_KEY}
```

13. Request only the fields needed for the task. For summaries, prefer:

```text
summary,status,issuetype,priority,assignee,reporter,created,updated,description,comment,labels
```

14. If the request fails due to sandbox network restrictions, rerun the same `jira-api` helper command with escalated network access.
15. Summarize the issue from the API response, not from the login page.
16. Never issue a direct Jira `curl` command from the skill workflow. All Jira HTTP access must go through `jira-api`.

## Helper Bootstrap

If `~/.local/bin/jira-api` is missing, copy `scripts/jira-api` from this skill. The helper script should contain:

```sh
#!/bin/sh
set -eu

if [ "$#" -lt 1 ] || [ "$#" -gt 3 ]; then
  echo "usage: jira-api [ISSUE_API_BASE] ISSUE_KEY [FIELDS]" >&2
  exit 2
fi

normalize_issue_api_base() {
  case "$1" in
    */rest/api/3/issue)
      printf '%s/\n' "$1"
      ;;
    */rest/api/3/issue/)
      printf '%s\n' "$1"
      ;;
    http://*|https://*)
      printf '%s/rest/api/3/issue/\n' "${1%/}"
      ;;
    *)
      printf '%s\n' "$1"
      ;;
  esac
}

default_base=$(normalize_issue_api_base "${ATLASSIAN_API_BASE_URL:-https://splunk.atlassian.net/rest/api/3/issue/}")
fields_default=summary,status,issuetype,priority,assignee,reporter,created,updated,description,comment,labels

case "$#" in
  1)
    issue_api_base=$default_base
    issue_key=$1
    fields=$fields_default
    ;;
  2)
    case "$1" in
      http://*|https://*)
        issue_api_base=$(normalize_issue_api_base "$1")
        issue_key=$2
        fields=$fields_default
        ;;
      *)
        issue_api_base=$default_base
        issue_key=$1
        fields=$2
        ;;
    esac
    ;;
  3)
    issue_api_base=$(normalize_issue_api_base "$1")
    issue_key=$2
    fields=$3
    ;;
esac

token=${ATLASSIAN_API_TOKEN:-}

if ! email=$(git config user.email); then
  echo "git config user.email is not set" >&2
  exit 1
fi

if [ -z "$email" ] || [ -z "$token" ]; then
  echo "git config user.email and ATLASSIAN_API_TOKEN must be set" >&2
  exit 1
fi

exec curl -sS \
  -u "$email:$token" \
  -H 'Accept: application/json' \
  "${issue_api_base}${issue_key}?fields=$fields"
```

## Command Pattern

Preferred wrapper shape:

```bash
jira-api {ISSUE_KEY}
```

Optional host + path override before the issue key:

```bash
jira-api https://splunk.atlassian.net/rest/api/3/issue/ {ISSUE_KEY}
```

Optional fields parameter:

```bash
jira-api {ISSUE_KEY} summary,status,priority,assignee
```

Host + path override with explicit fields:

```bash
jira-api https://splunk.atlassian.net/rest/api/3/issue/ {ISSUE_KEY} summary,status,priority,assignee
```

## Notes

- Prefer concise summaries unless the user asks for detail.
- Prefer the helper flow over raw `curl`; create the helper first when it is missing.
- Infer shell behavior from `$SHELL`, not from session metadata or assumptions about the user's shell.
- Ensure `$HOME/.local/bin` is on `PATH` before preferring `jira-api` over `~/.local/bin/jira-api`, using syntax that matches `$SHELL`.
- When shell detection is unclear, avoid shell-specific PATH edits and call `~/.local/bin/jira-api` directly.
- Accept a host + path override before the issue key, but default to `https://splunk.atlassian.net/rest/api/3/issue/`.
- Never access Jira with a direct assistant-issued `curl`; only run `jira-api`.
- If auth works but the issue is still unavailable, report that the account likely lacks permission to view the ticket.
- Do not expose the raw token in outputs.
