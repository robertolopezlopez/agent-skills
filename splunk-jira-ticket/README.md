# splunk-jira-ticket

Setup and usage notes for the `splunk-jira-ticket` skill.

## Purpose

This skill lets Codex fetch and summarize Splunk Jira tickets through the Jira REST API when a browser URL redirects to Atlassian login. It can also take an optional issue API host + path override before the issue key.

## Files

- `SKILL.md`: Codex skill definition and workflow
- `README.md`: local setup and helper usage
- `scripts/jira-api`: canonical helper implementation used by the skill

## Recommended Setup

The skill uses the bundled `scripts/jira-api` helper directly.

### 1. Auth config

Set the Jira base URL and token.

For skill/runtime use, resolve `scripts/jira-api` relative to the skill directory and invoke that resolved path.

```text
<skill-dir>/scripts/jira-api ...
```

If you want a standalone convenience command outside the skill directory, you can optionally copy it into `~/.local/bin`.

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

### 2. Helper usage

The bundled helper is `scripts/jira-api`.
For normal skill use, no extra install step is required.

If needed, make sure it is executable:

```bash
chmod +x scripts/jira-api
```

If you want to install a standalone copy:

```bash
cp scripts/jira-api ~/.local/bin/jira-api
chmod +x ~/.local/bin/jira-api
```

### 3. Usage

Examples:

```bash
scripts/jira-api DAT-2921
scripts/jira-api DAT-2921 summary,status,priority,assignee
scripts/jira-api https://splunk.atlassian.net/rest/api/3/issue/ DAT-2921
scripts/jira-api https://splunk.atlassian.net/rest/api/3/issue/ DAT-2921 summary,status,priority,assignee
```

## Codex Approval Model

For Codex, prefer invoking the bundled helper by its resolved path relative to the skill directory so the skill does not depend on `PATH` or shell-specific behavior.

If you want shorter interactive commands for manual use, copy the helper into `~/.local/bin` and add that directory to your shell `PATH`.

If your approval system supports persistent command prefixes, allow the helper command using the narrowest stable prefix available in your environment, for example:

```text
["<skill-dir>/scripts/jira-api"]
```

Codex should never issue a direct Jira `curl` request itself; Jira access must go through `jira-api`.
