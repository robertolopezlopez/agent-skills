# splunk-jira-ticket

Setup and usage notes for the `splunk-jira-ticket` skill.

## Purpose

This skill lets Codex fetch and summarize Splunk Jira tickets through the Jira REST API when a browser URL redirects to Atlassian login. It can also take an optional issue API host + path override before the issue key.

## Files

- `SKILL.md`: Codex skill definition and workflow
- `README.md`: local setup and helper usage
- `scripts/jira-api`: canonical helper implementation used by the skill
- `scripts/atlassian-auth.sh`: vendored Atlassian auth helper source used to bootstrap the shared installed copy

## Recommended Setup

The skill uses the bundled `scripts/jira-api` helper directly.
Before running the Jira helper, the skill refreshes shared Atlassian auth logic under:

```text
${XDG_DATA_HOME:-$HOME/.local/share}/jira/atlassian-auth.sh
```

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
For normal skill use, the skill refreshes the shared auth helper automatically from `scripts/atlassian-auth.sh` before invoking `scripts/jira-api`.

### 2a. Shared auth helper install

If you want to pre-install or refresh the shared Atlassian auth helper yourself:

```bash
mkdir -p "${XDG_DATA_HOME:-$HOME/.local/share}/jira"
cp scripts/atlassian-auth.sh "${XDG_DATA_HOME:-$HOME/.local/share}/jira/atlassian-auth.sh"
```

The shared auth helper is sourced by scripts, so it does not need to be executable.

Future Atlassian-related skills should reuse this shared auth helper instead of duplicating auth checks.

If needed, make sure it is executable:

```bash
chmod +x scripts/jira-api
```

If you want to install a standalone copy:

```bash
cp scripts/jira-api ~/.local/bin/jira-api
chmod +x ~/.local/bin/jira-api
```

If you use a standalone `jira-api` copy outside the skill directory, make sure the shared auth helper is also present at:

```text
${XDG_DATA_HOME:-$HOME/.local/share}/jira/atlassian-auth.sh
```

### 3. Usage

The following examples assume you are running commands from the skill directory. Otherwise, replace `scripts/jira-api` with the resolved path to the helper.

Examples:

```bash
scripts/jira-api DAT-2921
scripts/jira-api DAT-2921 summary,status,priority,assignee
scripts/jira-api https://splunk.atlassian.net/rest/api/3/issue/ DAT-2921
scripts/jira-api https://splunk.atlassian.net/rest/api/3/issue/ DAT-2921 summary,status,priority,assignee
```

## Codex Approval Model

For Codex, prefer invoking the bundled helper by its resolved path relative to the skill directory so the skill does not depend on `PATH` or shell-specific behavior.
For shared auth behavior, prefer a stable path under `${XDG_DATA_HOME:-$HOME/.local/share}/jira/`.

If you want shorter interactive commands for manual use, copy the helper into `~/.local/bin` and add that directory to your shell `PATH`.

If your approval system supports persistent command prefixes, allow the helper command using the narrowest stable prefix available in your environment, for example:

```text
["<skill-dir>/scripts/jira-api"]
```

Codex should never issue a direct Jira `curl` request itself; Jira access must go through `jira-api`.
