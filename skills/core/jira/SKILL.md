---
name: jira
description: Fetch, summarize, create, and update Jira or Atlassian issues. Use when the user provides an Atlassian issue URL or issue key, asks to summarize a Jira ticket, asks to create a Jira ticket, asks to change status, move a ticket into a sprint, assign or edit a ticket, comment on a ticket, asks to override the Jira issue API host and path, or asks to debug Jira access using `ATLASSIAN_API_TOKEN`. Prefer Jira or Atlassian MCP when available, with bundled helper fallback.
---

# Jira Ticket Access

When a Jira issue is not readable through normal browser access, prefer Jira or Atlassian MCP when available, otherwise use the bundled Jira REST helper workflow before concluding the ticket is inaccessible.

## When to Use

Use this skill when the user wants to:

- fetch or summarize a Jira or Atlassian issue
- create a Jira ticket
- transition or update a Jira ticket
- move a ticket into a sprint
- assign, edit, or comment on a ticket
- bootstrap a local task artifact from Jira
- debug Jira helper access or Jira auth defaults

## When Not to Use

Do not use this skill when:

- the task is GitLab MR access or Git repository context
- the task is only local artifact analysis and no live Jira access is needed
- a repository-specific overlay should own project-local Jira conventions after issue data has already been fetched

## Inputs

Accept, depending on the requested action:

- an issue key such as `PROJ-123`
- an Atlassian issue URL
- an optional host or base-path override for fallback helper use
- a requested field set
- free-form task context for create or update flows

## Workflow

1. Extract the issue key from the URL or user request.
2. Accept an optional host + path parameter before the issue key.
3. Prefer Jira or Atlassian MCP for read and write operations when a suitable MCP server is configured in the session.
4. For fallback helpers, invoke `jira-api` or `jira-request` directly. They resolve defaults in this order: exported `ATLASSIAN_API_BASE_URL`, then the runtime defaults file (see **Local Defaults File**). **Do not read defaults files with the editor/Read tool** unless the user explicitly asked to debug helper resolution.
5. Use `git config user.email` as the Atlassian username for fallback helper auth.
6. Use `ATLASSIAN_API_TOKEN` for fallback helper auth. Resolution order (handled by **`atlassian-auth.sh`** — agents do not need to `source` the defaults file):
   - exported **`ATLASSIAN_API_TOKEN`**
   - first line of **`${ATLASSIAN_API_TOKEN_FILE:-$HOME/.config/.jira/.credentials}`**
   - **`ATLASSIAN_API_TOKEN`** in runtime **`atlassian.env`** (resolve with **`scripts/agent_config.py --atlassian-env`**)
7. Resolve `scripts/jira-api` and `scripts/jira-request` relative to this skill directory for fallback helper use.
8. Ensure manifest **shared_files** from this repository have been synced into the active skills install root so the Atlassian auth helper expected by `jira-api` and `jira-request` exists under that root `scripts/` directory next to `validate_artifact.py` when missing (follow **AGENTS.md** sync rules). The helpers locate and source that file automatically.
9. If a Jira helper is not executable, run `chmod +x` on the resolved helper path.
10. If MCP is unavailable or insufficient, invoke the resolved Jira helper path directly:
   - env-configured base: `<resolved-path-to-scripts/jira-api> {ISSUE_KEY}`
   - overridden issue API base: `<resolved-path-to-scripts/jira-api> {HOST_AND_PATH} {ISSUE_KEY}`
11. When the task needs explicit field selection in fallback helper mode, pass the fields list as the final helper argument.
   - env-configured base: `<resolved-path-to-scripts/jira-api> {ISSUE_KEY} {FIELDS}`
   - overridden issue API base: `<resolved-path-to-scripts/jira-api> {HOST_AND_PATH} {ISSUE_KEY} {FIELDS}`
12. The fallback helper should normalize either:
   - a site URL like `https://example.atlassian.net`, or
   - an issue API base ending in `/rest/api/3/issue/`
13. Request only the fields needed for the task. For summaries, prefer:

```text
summary,status,issuetype,priority,assignee,reporter,created,updated,description,comment,labels
```

14. If the fallback helper request fails due to sandbox network restrictions, rerun the same helper command with escalated network access.
15. Summarize the issue from MCP output when available, otherwise from the fallback API response, not from the login page.
16. For non-read actions, prefer MCP first. If MCP is unavailable or insufficient, invoke the resolved request helper path directly:
   - env-configured base: `<resolved-path-to-scripts/jira-request> METHOD /rest/api/3/... [JSON_BODY_FILE]`
   - overridden site base: `<resolved-path-to-scripts/jira-request> https://example.atlassian.net METHOD /rest/api/3/... [JSON_BODY_FILE]`
17. When the user asks to bootstrap an artifact from a Jira issue, save the fetched issue JSON from MCP when possible, otherwise from the fallback helper, to a temporary local file and run `scripts/bootstrap_jira_artifact.py`.
18. Never issue a direct Jira `curl` command from the skill workflow. All Jira HTTP access must go through Jira or Atlassian MCP when available, otherwise through `jira-api` or `jira-request`.

## Validation

- Prefer Jira or Atlassian MCP first when available.
- Keep fallback helper execution routed through `jira-api` or `jira-request`, never direct `curl`.
- Resolve auth and base URL defaults before invoking fallback helpers.
- Keep the same normalized issue and artifact contract regardless of transport.

## Transport Preference

Preferred order:

1. Jira or Atlassian MCP for issue reads, comments, transitions, edits, and creation
2. `jira-api` for fallback issue reads
3. `jira-request` for fallback write operations

Use the same normalized issue summary and artifact contract regardless of transport so companion skills or follow-on work do not depend on how Jira was accessed.

## Helper Source

The canonical helper implementation lives at `scripts/jira-api`, resolved relative to this skill directory.
The canonical generic request helper implementation lives at `scripts/jira-request`, resolved relative to this skill directory.
The canonical artifact bootstrap helper implementation lives at `scripts/bootstrap_jira_artifact.py`, resolved relative to this skill directory.
Atlassian authentication and runtime config resolution are shared with the Confluence skill through repository manifest **shared_files** helpers (`atlassian-auth.sh`, `agent-config.sh` under each skills install root `scripts/` directory). Do not duplicate that logic inline in this file or in `scripts/jira-api` or `scripts/jira-request`.

## Local Defaults File

Bundled helpers load defaults from **one** runtime config home (see **AGENTS.md**). Resolve the active file with **`scripts/agent_config.py --atlassian-env`** (or **`scripts/agent-config.sh --atlassian-env`**).

Override detection with **`AGENT_SKILLS_RUNTIME=cursor`** or **`codex`**, or set **`AGENT_CONFIG_HOME`**.

Preferred usage:

```bash
ATLASSIAN_API_BASE_URL=https://example.atlassian.net
```

Rules:

- treat explicit helper arguments as highest priority
- treat exported environment variables as higher priority than defaults files
- let **`jira-api`** / **`jira-request`** read the runtime defaults file for URLs and token; agents must not open the file unless debugging config resolution
- **`ATLASSIAN_API_TOKEN`** may live in **`atlassian.env`** when not exported; prefer export or the credentials file when your environment already provides them

## Fallback Command Pattern

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

Artifact bootstrap helper (default output under `$ARTIFACTS/<issue-key>/`):

```bash
<resolved-path-to-scripts/bootstrap_jira_artifact.py> --issue PROJ-123 --json /tmp/proj-123.json
```

Default path when `--output` is omitted:

```text
$ARTIFACTS/PROJ-123/task_proj-123.md
```

Artifact bootstrap helper with explicit output (user or repo rules override the default directory):

```bash
<resolved-path-to-scripts/bootstrap_jira_artifact.py> --issue PROJ-123 --json /tmp/proj-123.json --output $ARTIFACTS/PROJ-123/task_proj-123.md --overwrite
```

## Artifact Bootstrap Workflow

Use this workflow when the user asks to bootstrap an artifact, create a task file from a Jira issue, or fill a local `task_<issue>.md` file from Jira.

Prefer new artifacts under `$ARTIFACTS/<meaningful_id>/` at the repository root (see repo `ARTIFACTS.md`). For Jira bootstrap, `meaningful_id` defaults to the issue key (filesystem-safe), e.g. `$ARTIFACTS/PROJ-123/task_proj-123.md`. Honor explicit user `--output` paths or repo `AGENTS.md` overrides.

1. Fetch the issue with Jira or Atlassian MCP when available, otherwise with `jira-api`, requesting the summary fields set:

```text
summary,status,issuetype,priority,assignee,reporter,created,updated,description,comment,labels
```

2. Save the fetched JSON to a temporary local file.
3. Run `scripts/bootstrap_jira_artifact.py` with the issue key and JSON path.
4. Let the bootstrap helper extract comment summary and related-reference hints from the fetched Jira JSON.
5. If a local artifact already exists at the resolved output path (default `$ARTIFACTS/<issue-key>/task_<issue>.md`, or an explicit `--output`), preserve durable local sections such as `Follow-up Findings`, `Improvement Candidates`, `Implementation Notes`, `Similar Prior Issues`, `Resolved Unknowns`, `Next Best Step`, or `Common Ticket Pattern` while refreshing Jira-sourced sections from live data.
6. Let the bootstrap helper validate the generated artifact against the shared schema.
7. Write the artifact using the shared section order documented in `../ARTIFACTS.md`.
8. Report the local artifact path and the most actionable next step.
9. Do not modify Jira itself during artifact bootstrap.

## Outputs / Artifacts

This skill should return the most useful normalized Jira result for the task, such as:

- issue summary and key fields
- available transitions
- update outcome
- created ticket key and URL
- helper or auth diagnosis

When artifact bootstrap is requested, this skill may also write:

- `$ARTIFACTS/<issue-key>/task_<issue>.md` by default (e.g. `$ARTIFACTS/PROJ-123/task_proj-123.md`)
- an explicit `--output` path when the user or repo rules override the default

## Create Workflow

Use this workflow when the user asks to create a Jira ticket, issue, story, or task.

### Input contract

This workflow accepts one free-form task/context string supplied at invocation time.

Treat the text in `<skill_input>` as TASK_CONTEXT.
If no `<skill_input>` is present, use the user's most recent request as TASK_CONTEXT.

### Prerequisites

Reuse the same generic Jira auth and base URL conventions for fallback helper use:

- use `git config user.email` as the Atlassian username
- bundled helpers resolve **`ATLASSIAN_API_TOKEN`** from the environment, credentials file, then runtime **`atlassian.env`** — no manual `source` required

### Generic creation flow

1. Infer sensible draft values from TASK_CONTEXT.
2. Present the inferred values to the user for confirmation.
3. Do not create the ticket until the user confirms.
4. Build an Atlassian Document Format (ADF) description payload when Jira description content is needed.
5. Prefer creating the ticket with Jira or Atlassian MCP. If MCP is unavailable or insufficient, create it via Jira REST API:

```text
POST {ATLASSIAN_SITE_URL}/rest/api/3/issue
```

6. Authenticate with the shared Atlassian auth helper conventions when using fallback helpers.
7. If the project uses Agile sprint assignment, assign the created ticket in a separate call, preferably through MCP and otherwise via fallback helper:

```text
POST {ATLASSIAN_SITE_URL}/rest/agile/1.0/sprint/{sprintId}/issue
```

8. If the workflow requires it, transition the ticket after creation in a separate call, preferably through MCP and otherwise via fallback helper.
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

1. Fetch the current issue first when the change depends on current fields or status, preferably through MCP and otherwise via fallback helper.
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

7. In fallback mode, prefer concise JSON payload files and call the generic request helper instead of direct `curl`.

### Notes for overlays

Project-specific overlay skills should keep local ownership of:

- project defaults
- issue type defaults
- project defaults for status, sprint, or field conventions

## Companion Skills

Use this skill as the Jira transport and normalization layer.

Common pairings:

- repository-specific overlay skills for project-local issue conventions
- local task artifacts such as `$ARTIFACTS/<issue-key>/task_<issue>.md` for downstream implementation or analysis

## Safety Notes

- Never issue direct Jira `curl` commands from this skill.
- Keep shared Atlassian auth behavior in the vendored helper scripts instead of duplicating it inline.
- Do not modify Jira during artifact bootstrap.
- custom field mappings
- component/team heuristics
- epic and sprint conventions
- any product-specific workflow rules

Keep those details out of the generic `jira` skill.

## Artifact-Aware Self-Improving Behavior

When rerunning work for the same Jira issue or refreshing a bootstrapped artifact (default `$ARTIFACTS/<issue-key>/task_<issue>.md`):

- read the existing local artifact first when it exists
- preserve durable learned sections such as `## Implementation Notes`, `## Similar Prior Issues`, `## Resolved Unknowns`, `## Next Best Step`, and `## Common Ticket Pattern` when they still match the current issue and local evidence
- refresh Jira-sourced facts from the live Jira response before reusing them
- keep durable learned sections concise, actionable, and tied to the issue family or component rather than generic advice
- promote repeated confirmed issue-family observations into short heuristics, preferably phrased like `tickets in component X usually need Y before coding`
- demote, mark stale, or remove heuristics contradicted by refreshed issue data or local investigation

## Notes

- Prefer concise summaries unless the user asks for detail.
- Prefer Jira or Atlassian MCP when available, otherwise prefer the bundled helper over raw `curl`.
- Resolve `scripts/jira-api` and `scripts/jira-request` relative to this skill directory and invoke those resolved paths directly instead of relying on `PATH` or copies in other directories.
- Accept a host + path override before the issue key.
- When no override is provided for fallback helper use, bundled helpers resolve `ATLASSIAN_API_BASE_URL` from the environment, then the runtime **`atlassian.env`** file.
- Do not probe the other runtime's config home (Cursor vs Codex) unless the user is debugging cross-runtime setup.
- Never access Jira with a direct assistant-issued `curl`; use Jira or Atlassian MCP when available, otherwise only run `jira-api` or `jira-request`.
- If `ATLASSIAN_API_TOKEN` is already exported, helpers do not read the credentials file or **`atlassian.env`** for the token.
- If auth works but the issue is still unavailable, report that the account likely lacks permission to view the ticket.
- Do not expose the raw token in outputs.
