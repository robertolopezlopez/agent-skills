# splunk-jira

Setup and usage notes for the `splunk-jira` skill.

## Purpose

This skill lets Codex fetch, summarize, create, and update Splunk Jira tickets through the Jira REST API. It is a Splunk-specific overlay on top of the generic `jira` skill.

## Files

- `SKILL.md`: Codex skill definition and workflow
- `README.md`: local setup and helper usage
- `scripts/jira-api`: thin compatibility wrapper that defaults to Splunk and delegates to the generic `jira` helper
- `scripts/jira-request`: thin compatibility wrapper that defaults to Splunk and delegates to the generic `jira` request helper

## Recommended Setup

The skill uses the bundled `scripts/jira-api` wrapper directly.
That wrapper delegates to the generic `jira` skill helper.
Before running the Jira helper, the generic `jira` workflow refreshes shared Atlassian auth logic under:

```text
${XDG_DATA_HOME:-$HOME/.local/share}/jira/atlassian-auth.sh
```

### 1. Auth config

Set the Jira base URL and token.

For skill/runtime use, resolve `scripts/jira-api` or `scripts/jira-request` relative to the skill directory and invoke that resolved path.

```text
<skill-dir>/scripts/jira-api ...
<skill-dir>/scripts/jira-request ...
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

If `ATLASSIAN_API_TOKEN` is not exported, the generic shared auth helper can fall back to:

```text
${ATLASSIAN_API_TOKEN_FILE:-$HOME/.config/.jira/.credentials}
```

It reads the first line as the token. The environment variable is still preferred.

### 2. Helper usage

The bundled wrappers are `scripts/jira-api` and `scripts/jira-request`.
For normal skill use, use the generic `jira` skill workflow to refresh the shared auth helper before invoking them.

If needed, make sure it is executable:

```bash
chmod +x scripts/jira-api
chmod +x scripts/jira-request
```

### 3. Usage

The following examples assume you are running commands from the skill directory. Otherwise, replace `scripts/jira-api` with the resolved path to the helper.

Examples:

```bash
# Example resolved path:
# ~/.codex/skills/splunk-jira/scripts/jira-api

# Use Splunk Jira as the default base
scripts/jira-api DAT-2921

# Request only a few fields
scripts/jira-api DAT-2921 summary,status,priority,assignee

# Override the Jira site/API base for one call
scripts/jira-api https://splunk.atlassian.net/rest/api/3/issue/ DAT-2921

# Override the base and request selected fields
scripts/jira-api https://splunk.atlassian.net/rest/api/3/issue/ DAT-2921 summary,status,priority,assignee
```

For update and create actions, use the request wrapper.

Examples:

```bash
# Example resolved path:
# ~/.codex/skills/splunk-jira/scripts/jira-request

# Move a ticket into a sprint
scripts/jira-request POST /rest/agile/1.0/sprint/456/issue /tmp/sprint-issues.json

# Change ticket status
scripts/jira-request POST /rest/api/3/issue/DAT-2921/transitions /tmp/transition.json

# Add a comment
scripts/jira-request POST /rest/api/3/issue/DAT-2921/comment /tmp/comment.json
```

## Codex usage examples

Example prompts:

```text
Summarize Splunk Jira ticket DAT-2921
```

```text
Fetch https://splunk.atlassian.net/browse/DAT-2921 and summarize it
```

```text
Use splunk-jira to fetch DAT-2921 with fields summary,status,priority,assignee
```

```text
Debug Splunk Jira access for DAT-2921 using ATLASSIAN_API_TOKEN
```

## Create ticket workflow

Use the generic `jira` skill for creation mechanics and this skill for Splunk defaults.

### Splunk defaults

- Jira site: `https://splunk.atlassian.net`
- Project: `DAT`
- Issue type: usually `Story`
- ProductBacklogArea: `GDI`

### Splunk field reference

Use `POST https://splunk.atlassian.net/rest/api/3/issue` with:

| Field | API field | Notes |
|---|---|---|
| Project | `project.key` | Always `"DAT"` |
| Type | `issuetype.name` | Usually `"Story"` |
| Summary | `summary` | Title string |
| Description | `description` | Atlassian Document Format (ADF) JSON |
| Component | `components[].name` | Splunk Jira component |
| ProductBacklogArea | `customfield_14900.value` | Always `"GDI"` |
| Mission Team | `customfield_14901.value` | Required |
| Story Points | `customfield_10081` | Numeric |
| Parent (Epic) | `parent.key` | Epic key |
| Assignee | `assignee.accountId` | Resolve account ID first if needed |

### Splunk epic guidance

- Auto-Schematization work: use an epic under `RDMP-3757`
- Guided Onboarding work: use an epic under `RDMP-3545`

To list available epics, query:

```text
parent = RDMP-XXXX ORDER BY key ASC
```

via the Jira search API.

### Splunk sprint assignment

Sprints are managed via Agile API:

```text
POST https://splunk.atlassian.net/rest/agile/1.0/sprint/{sprintId}/issue
Body: {"issues": ["DAT-XXXX"]}
```

Find the current active sprint by reading `customfield_11301` from an existing ticket on the same board.

### Codex create examples

```text
Create a Splunk Jira for adding retries to the workflow service when model calls time out
```

```text
Use splunk-jira to draft a DAT story for Guided Onboarding source validation improvements
```

```text
Create a Splunk Jira ticket for this work, suggest component/team/points/epic/sprint, and ask me to confirm before creating it
```

## Update ticket workflow

Use the generic `jira` update mechanics and this skill's Splunk defaults for common developer actions such as:

- move a backlog ticket into the current sprint
- transition a ticket to In Progress
- update story points, assignee, labels, summary, or epic
- add a comment

### Codex update examples

```text
Use splunk-jira to move DAT-2921 into the current sprint
```

```text
Use splunk-jira to change DAT-2921 to In Progress after showing me the available transitions
```

```text
Use splunk-jira to add a comment to DAT-2921 with today's implementation update
```

```text
Use splunk-jira to update DAT-2921 story points to 3 and assign it to me
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
