---
name: jira
description: Fetch, summarize, create, and update Jira or Atlassian issues through the Jira REST API. Use when the user provides an Atlassian issue URL or issue key, asks to summarize a Jira ticket, asks to create a Jira ticket, asks to change status, move a ticket into a sprint, assign or edit a ticket, comment on a ticket, asks to override the Jira issue API host and path, or asks to debug Jira access using `ATLASSIAN_API_TOKEN`.
---

# Jira Ticket Access

When a Jira issue is not readable through normal browser access, use the Jira REST API before concluding the ticket is inaccessible.

## Workflow

1. Extract the issue key from the URL or user request.
2. Accept an optional host + path parameter before the issue key.
3. If no host + path override is provided, resolve defaults in this order: exported environment variable, `~/.codex/jira.env`, then any built-in helper fallback.
   - Prefer `ATLASSIAN_API_BASE_URL` from the exported environment when present.
   - Otherwise, if `~/.codex/jira.env` exists, read it for default non-secret Jira settings before invoking the helper.
   - `ATLASSIAN_API_BASE_URL` in `~/.codex/jira.env` may be a site URL like `https://example.atlassian.net`.
   - `ATLASSIAN_API_BASE_URL` in `~/.codex/jira.env` may already be an issue API base like `https://example.atlassian.net/rest/api/3/issue/`.
4. Use `git config user.email` as the Atlassian username.
5. Use `ATLASSIAN_API_TOKEN` from the environment as the password.
   - If it is unset, the shared auth helper may fall back to `${ATLASSIAN_API_TOKEN_FILE:-$HOME/.config/.jira/.credentials}` and read the first line as the token.
   - Prefer the environment variable when available.
6. Resolve `scripts/jira-api` and `scripts/jira-request` relative to this skill directory.
7. Resolve `scripts/atlassian-auth.sh` relative to this skill directory.
8. Ensure the shared Atlassian auth helper exists at `${XDG_DATA_HOME:-$HOME/.local/share}/jira/atlassian-auth.sh`.
9. Refresh the shared auth helper from the skill copy before invoking `jira-api` or `jira-request`:
   - `mkdir -p "${XDG_DATA_HOME:-$HOME/.local/share}/jira"`
   - `cp <resolved-path-to-scripts/atlassian-auth.sh> "${XDG_DATA_HOME:-$HOME/.local/share}/jira/atlassian-auth.sh"`
   - if the copy fails due to sandbox restrictions, rerun the copy step with escalated permissions
10. Use the installed shared auth helper from `scripts/jira-api` and `scripts/jira-request`.
11. If a Jira helper is not executable, run `chmod +x` on the resolved helper path.
12. Invoke the resolved Jira helper path directly:
   - env-configured base: `<resolved-path-to-scripts/jira-api> {ISSUE_KEY}`
   - overridden issue API base: `<resolved-path-to-scripts/jira-api> {HOST_AND_PATH} {ISSUE_KEY}`
13. When the task needs explicit field selection, pass the fields list as the final helper argument.
   - env-configured base: `<resolved-path-to-scripts/jira-api> {ISSUE_KEY} {FIELDS}`
   - overridden issue API base: `<resolved-path-to-scripts/jira-api> {HOST_AND_PATH} {ISSUE_KEY} {FIELDS}`
14. The helper should normalize either:
   - a site URL like `https://example.atlassian.net`, or
   - an issue API base ending in `/rest/api/3/issue/`
15. Request only the fields needed for the task. For summaries, prefer:

```text
summary,status,issuetype,priority,assignee,reporter,created,updated,description,comment,labels
```

16. If the request fails due to sandbox network restrictions, rerun the same helper command with escalated network access.
17. Summarize the issue from the API response, not from the login page.
18. For non-read actions, invoke the resolved request helper path directly:
   - env-configured base: `<resolved-path-to-scripts/jira-request> METHOD /rest/api/3/... [JSON_BODY_FILE]`
   - overridden site base: `<resolved-path-to-scripts/jira-request> https://example.atlassian.net METHOD /rest/api/3/... [JSON_BODY_FILE]`
19. Never issue a direct Jira `curl` command from the skill workflow. All Jira HTTP access must go through `jira-api` or `jira-request`.

## Helper Source

The canonical helper implementation lives at `scripts/jira-api`, resolved relative to this skill directory.
The canonical generic request helper implementation lives at `scripts/jira-request`, resolved relative to this skill directory.
The vendored Atlassian auth helper source for this skill lives at `scripts/atlassian-auth.sh`, resolved relative to this skill directory.
The installed shared Atlassian auth helper should live at `${XDG_DATA_HOME:-$HOME/.local/share}/jira/atlassian-auth.sh`.

Use the resolved helper path in place for normal skill execution.
Refresh the installed shared auth helper from the vendored skill copy before invoking `jira-api`.
Use `~/.codex/jira.env` for non-secret defaults such as `ATLASSIAN_API_BASE_URL`; keep tokens out of that file unless the local environment explicitly requires it.
Do not duplicate Atlassian auth logic inline in this file or in `scripts/jira-api` or `scripts/jira-request`; keep shared auth behavior in `scripts/atlassian-auth.sh` and the installed shared copy.

## Local Defaults File

If `~/.codex/jira.env` exists, read it before invoking the Jira helpers to supply default non-secret settings.

Preferred usage:

```bash
ATLASSIAN_API_BASE_URL=https://splunk.atlassian.net
```

Rules:

- treat explicit helper arguments as highest priority
- treat exported environment variables as higher priority than `~/.codex/jira.env`
- use `~/.codex/jira.env` for defaults, not for required per-request overrides
- prefer keeping `ATLASSIAN_API_TOKEN` in the environment or existing credentials flow instead of storing it in `~/.codex/jira.env`

## Command Pattern

Preferred helper shape after resolving the path relative to this skill directory:

```bash
<resolved-path-to-scripts/jira-api> {ISSUE_KEY}
```

Optional host + path override before the issue key:

```bash
<resolved-path-to-scripts/jira-api> https://example.atlassian.net/rest/api/3/issue/ {ISSUE_KEY}
```

Optional fields parameter:

```bash
<resolved-path-to-scripts/jira-api> {ISSUE_KEY} summary,status,priority,assignee
```

Host + path override with explicit fields:

```bash
<resolved-path-to-scripts/jira-api> https://example.atlassian.net/rest/api/3/issue/ {ISSUE_KEY} summary,status,priority,assignee
```

Generic request helper:

```bash
<resolved-path-to-scripts/jira-request> POST /rest/api/3/issue /tmp/create-issue.json
```

Generic request helper with explicit site override:

```bash
<resolved-path-to-scripts/jira-request> https://example.atlassian.net POST /rest/api/3/issue /tmp/create-issue.json
```

## Create Workflow

Use this workflow when the user asks to create a Jira ticket, issue, story, or task.

### Input contract

This workflow accepts one free-form task/context string supplied at invocation time.

Treat the text in `<skill_input>` as TASK_CONTEXT.
If no `<skill_input>` is present, use the user's most recent request as TASK_CONTEXT.

### Prerequisites

Reuse the same generic Jira auth and base URL conventions:

- use `git config user.email` as the Atlassian username
- use `ATLASSIAN_API_TOKEN` from the environment as the password
- if it is unset, the shared auth helper may fall back to `${ATLASSIAN_API_TOKEN_FILE:-$HOME/.config/.jira/.credentials}` and read the first line as the token
- read `~/.codex/jira.env` for default non-secret Jira settings when present
- use `ATLASSIAN_API_BASE_URL` from the exported environment first, then from `~/.codex/jira.env`, unless an explicit override is provided

### Generic creation flow

1. Infer sensible draft values from TASK_CONTEXT.
2. Present the inferred values to the user for confirmation.
3. Do not create the ticket until the user confirms.
4. Build an Atlassian Document Format (ADF) description payload when Jira description content is needed.
5. Create the ticket via Jira REST API:

```text
POST {ATLASSIAN_SITE_URL}/rest/api/3/issue
```

6. Authenticate with the shared Atlassian auth helper conventions.
7. If the project uses Agile sprint assignment, assign the created ticket in a separate call:

```text
POST {ATLASSIAN_SITE_URL}/rest/agile/1.0/sprint/{sprintId}/issue
```

8. If the workflow requires it, transition the ticket after creation in a separate call.
9. Report back the ticket key and URL.

## Update Workflow

Use this workflow when the user asks to change or manage an existing Jira ticket.

### Common developer actions

- transition status
- move a backlog ticket into the current sprint
- assign or reassign a ticket
- update priority, story points, summary, description, labels, or other editable fields
- add a comment

### Generic update flow

1. Fetch the current issue first when the change depends on current fields or status.
2. For status changes, list available transitions first:

```text
GET /rest/api/3/issue/{ISSUE_KEY}/transitions
```

3. After the user confirms the intended transition, transition the issue:

```text
POST /rest/api/3/issue/{ISSUE_KEY}/transitions
```

4. For sprint moves, use the Agile API:

```text
POST /rest/agile/1.0/sprint/{sprintId}/issue
```

5. For field edits, use:

```text
PUT /rest/api/3/issue/{ISSUE_KEY}
```

6. For comments, use:

```text
POST /rest/api/3/issue/{ISSUE_KEY}/comment
```

7. Prefer concise JSON payload files and call the generic request helper instead of direct `curl`.

### Notes for overlays

Project-specific overlay skills should keep local ownership of:

- project defaults
- issue type defaults
- custom field mappings
- component/team heuristics
- epic and sprint conventions
- any product-specific workflow rules

Keep those details out of the generic `jira` skill.

## Notes

- Prefer concise summaries unless the user asks for detail.
- Prefer the bundled helper over raw `curl`.
- Resolve `scripts/jira-api` and `scripts/jira-request` relative to this skill directory and invoke those resolved paths directly instead of relying on `PATH` or copies in other directories.
- Accept a host + path override before the issue key.
- When no override is provided, prefer exported `ATLASSIAN_API_BASE_URL`, then `~/.codex/jira.env`, to identify the Jira site.
- Use `~/.codex/jira.env` for defaults like `ATLASSIAN_API_BASE_URL=https://splunk.atlassian.net`.
- Never access Jira with a direct assistant-issued `curl`; only run `jira-api` or `jira-request`.
- If `ATLASSIAN_API_TOKEN` is already set, do not probe `~/.config/.jira/.credentials` just to verify auth.
- If auth works but the issue is still unavailable, report that the account likely lacks permission to view the ticket.
- Do not expose the raw token in outputs.
