# jira

Setup and usage notes for the generic `jira` skill.

## Purpose

This skill lets Codex fetch, summarize, create, and update Jira or Atlassian tickets through the Jira REST API when browser access redirects to login or when API access is more reliable.

Use this skill for generic Jira/Atlassian access.
For Splunk Jira, set `ATLASSIAN_API_BASE_URL=https://splunk.atlassian.net` in `~/.codex/jira.env` or export it in the environment before invoking the helpers.

## Files

- `SKILL.md`: Codex skill definition and workflow
- `README.md`: local setup and helper usage
- `scripts/jira-api`: canonical helper implementation used by the skill
- `scripts/jira-request`: canonical generic request helper for create/update actions
- `scripts/atlassian-auth.sh`: vendored Atlassian auth helper source used to bootstrap the shared installed copy

## Local Defaults File

Use `~/.codex/jira.env` for non-secret local defaults for this skill.

Example:

```bash
ATLASSIAN_API_BASE_URL=https://splunk.atlassian.net
```

Precedence:

1. explicit helper arguments
2. exported environment variables
3. `~/.codex/jira.env`

Do not store `ATLASSIAN_API_TOKEN` in this file.

## Recommended Setup

Set `ATLASSIAN_API_BASE_URL` to either:

- a site URL such as `https://example.atlassian.net`, or
- an issue API base such as `https://example.atlassian.net/rest/api/3/issue/`

Also set `ATLASSIAN_API_TOKEN`.

The skill uses:

- `git config user.email` as the Atlassian username
- `ATLASSIAN_API_TOKEN` as the password/token

If `ATLASSIAN_API_TOKEN` is not exported, the shared auth helper can fall back to:

```text
${ATLASSIAN_API_TOKEN_FILE:-$HOME/.config/.jira/.credentials}
```

It reads the first line as the token. The environment variable is still preferred.

The skill uses the bundled `scripts/jira-api` and `scripts/jira-request` helpers directly.
Before running the Jira helper, the skill refreshes shared Atlassian auth logic under:

```text
${XDG_DATA_HOME:-$HOME/.local/share}/jira/atlassian-auth.sh
```

## Helper usage

The helper accepts either:

- `jira-api ISSUE_KEY [FIELDS]`, using `ATLASSIAN_API_BASE_URL`, or
- `jira-api ISSUE_API_BASE ISSUE_KEY [FIELDS]`, overriding the base for one call

The helper normalizes either a site URL such as:

```text
https://example.atlassian.net
```

or an issue API base such as:

```text
https://example.atlassian.net/rest/api/3/issue/
```

into an issue API base ending in `/rest/api/3/issue/`.

Examples:

```bash
# Example resolved path:
# ~/.codex/skills/jira/scripts/jira-api

# Use ATLASSIAN_API_BASE_URL from the environment
scripts/jira-api PROJ-123

# Request only a few fields
scripts/jira-api PROJ-123 summary,status,priority,assignee

# Override the Jira site/API base for one call
scripts/jira-api https://example.atlassian.net/rest/api/3/issue/ PROJ-123

# Override the base and request selected fields
scripts/jira-api https://example.atlassian.net/rest/api/3/issue/ PROJ-123 summary,status,priority,assignee
```

The generic request helper accepts either:

- `jira-request METHOD PATH [JSON_BODY_FILE]`, using `ATLASSIAN_API_BASE_URL`, or
- `jira-request SITE_BASE METHOD PATH [JSON_BODY_FILE]`, overriding the base for one call

Examples:

```bash
# Example resolved path:
# ~/.codex/skills/jira/scripts/jira-request

# Create or update using ATLASSIAN_API_BASE_URL
scripts/jira-request POST /rest/api/3/issue /tmp/create-issue.json

# Change issue status
scripts/jira-request POST /rest/api/3/issue/PROJ-123/transitions /tmp/transition.json

# Move a ticket into a sprint
scripts/jira-request POST /rest/agile/1.0/sprint/456/issue /tmp/sprint-issues.json

# Add a comment using an explicit site override
scripts/jira-request https://example.atlassian.net POST /rest/api/3/issue/PROJ-123/comment /tmp/comment.json
```

## Codex usage examples

Example prompts:

```text
Summarize Jira ticket PROJ-123
```

```text
Fetch https://example.atlassian.net/browse/PROJ-123 and summarize it
```

```text
Use jira to fetch PROJ-123 with fields summary,status,priority,assignee
```

```text
Debug Jira access for PROJ-123 using ATLASSIAN_API_TOKEN
```

## Generic create workflow

Use `jira` for the generic parts of ticket creation and update:

- auth
- base URL handling
- confirmation-before-create
- generic REST creation pattern
- optional sprint assignment
- optional post-create transition
- generic issue edits
- generic comments
- generic transition and sprint move mechanics

Project-specific defaults layered on top of `jira` may add:

- project defaults
- field mappings
- custom fields
- component/team heuristics
- epic/sprint conventions

### Generic create API shape

Create issue:

```text
POST {ATLASSIAN_SITE_URL}/rest/api/3/issue
```

Optional sprint assignment:

```text
POST {ATLASSIAN_SITE_URL}/rest/agile/1.0/sprint/{sprintId}/issue
Body: {"issues": ["PROJ-123"]}
```

Generic transition:

```text
POST {ATLASSIAN_SITE_URL}/rest/api/3/issue/{ISSUE_KEY}/transitions
```

Generic issue edit:

```text
PUT {ATLASSIAN_SITE_URL}/rest/api/3/issue/{ISSUE_KEY}
```

Generic comment:

```text
POST {ATLASSIAN_SITE_URL}/rest/api/3/issue/{ISSUE_KEY}/comment
```

### Codex create examples

```text
Create a Jira ticket for adding retries to a flaky API integration, infer sensible defaults, and ask me to confirm before creating it
```

```text
Use jira to create a ticket in this Atlassian site and keep the description in ADF format
```

```text
Use jira to move PROJ-123 from backlog into the current sprint
```

```text
Use jira to change PROJ-123 to In Progress after showing me the available transitions
```

```text
Use jira to add a comment to PROJ-123 summarizing the implementation plan
```

## Notes

- The helper requires either an explicit issue API host/path override or `ATLASSIAN_API_BASE_URL`.
- For summaries, prefer requesting only needed fields, commonly:

```text
summary,status,issuetype,priority,assignee,reporter,created,updated,description,comment,labels
```

- Codex should never issue a direct Jira `curl` request itself; Jira access must go through `jira-api`.
