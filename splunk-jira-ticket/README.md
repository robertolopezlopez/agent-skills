# splunk-jira-ticket

Setup and usage notes for the `splunk-jira-ticket` skill.

## Purpose

This skill lets Codex fetch and summarize Splunk Jira tickets through the Jira REST API when a browser URL redirects to Atlassian login.

## Files

- `SKILL.md`: Codex skill definition and workflow
- `README.md`: local setup for shell auth and helper command

## Recommended Setup

Use a small wrapper command so Codex can request a narrow persistent approval like `["jira-api"]` instead of trying to auto-approve a raw `curl` command that contains shell expansion.

### 1. Shell auth config

Set the Jira base URL and token, and make sure `~/.local/bin` is on `PATH`.

#### Fish

Create `~/.config/fish/conf.d/jira.fish`:

```fish
set -gx ATLASSIAN_API_BASE_URL https://splunk.atlassian.net
set -gx ATLASSIAN_API_TOKEN '...'

if test -d $HOME/.local/bin
    contains -- $HOME/.local/bin $PATH
    or set -gx PATH $HOME/.local/bin $PATH
end
```

Reload with:

```fish
source ~/.config/fish/conf.d/jira.fish
```

#### Bash

Add this to `~/.bashrc`:

```bash
export ATLASSIAN_API_BASE_URL=https://splunk.atlassian.net
export ATLASSIAN_API_TOKEN='...'

case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *) export PATH="$HOME/.local/bin:$PATH" ;;
esac
```

Reload with:

```bash
source ~/.bashrc
```

#### Zsh

Add this to `~/.zshrc`:

```zsh
export ATLASSIAN_API_BASE_URL=https://splunk.atlassian.net
export ATLASSIAN_API_TOKEN='...'

case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *) export PATH="$HOME/.local/bin:$PATH" ;;
esac
```

Reload with:

```zsh
source ~/.zshrc
```

### 2. Helper command

Create `~/.local/bin/jira-api`:

```sh
#!/bin/sh
set -eu

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "usage: jira-api ISSUE_KEY [FIELDS]" >&2
  exit 2
fi

issue_key=$1
fields=${2:-summary,status,issuetype,priority,assignee,reporter,created,updated,description,comment,labels}
base_url=${ATLASSIAN_API_BASE_URL:-https://splunk.atlassian.net}
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
  "$base_url/rest/api/3/issue/$issue_key?fields=$fields"
```

Then make it executable:

```bash
chmod +x ~/.local/bin/jira-api
```

### 3. Usage

Examples:

```bash
jira-api DAT-2921
jira-api DAT-2921 summary,status,priority,assignee
```

## Codex Approval Model

The point of `jira-api` is to give Codex a stable, narrow command prefix. After the helper exists, allow the command with a persistent prefix rule for:

```text
["jira-api"]
```

That is safer and more compatible with Codex approvals than trying to persist approval for a raw `curl` command with `$(...)`, env vars, or wildcards.
