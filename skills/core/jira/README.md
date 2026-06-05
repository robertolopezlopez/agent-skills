# jira

Setup and usage notes for the generic `jira` skill.

## Purpose

This skill lets agents (for example in Codex or Cursor) fetch, summarize, create, and update Jira or Atlassian tickets through the Jira REST API when browser access redirects to login or when API access is more reliable.

Use this skill for generic Jira/Atlassian access.
For a site-specific Jira instance, set `ATLASSIAN_API_BASE_URL=https://example.atlassian.net` in the runtime defaults file (resolve with **`scripts/agent_config.py --atlassian-env`**), or export it before invoking helpers. Helpers detect the runtime from their install path; see **AGENTS.md**.

## Files

- `SKILL.md`: skill definition and workflow
- `README.md`: local setup and helper usage
- `scripts/jira-api`: canonical helper implementation used by the skill
- `scripts/jira-request`: canonical generic request helper for create/update actions
- `scripts/bootstrap_jira_artifact.py`: bootstrap and validate a local `task_<issue>.md` artifact from fetched Jira JSON, including comment summary and related-reference hints

Atlassian authentication lives in the repository manifest **shared_files** helper (`atlassian-auth.sh` next to `validate_artifact.py` under each skills install root). Sync this repository per **AGENTS.md** so that file is present.

## Local Defaults File

Use the runtime defaults file for your install. Resolve the path with **`scripts/agent_config.py --atlassian-env`**. Bundled helpers read URLs and **`ATLASSIAN_API_TOKEN`** from it when not exported; agents should invoke helpers instead of opening the file directly.

Example:

```bash
ATLASSIAN_API_BASE_URL=https://example.atlassian.net
# ATLASSIAN_API_TOKEN=...   # optional; also supported via export or ~/.config/.jira/.credentials
```

Precedence:

1. explicit helper arguments
2. exported environment variables
3. runtime **`atlassian.env`** (loaded by helpers for URLs and token)

See **`templates/atlassian.env.example`** in the agent-skills repository.

## Recommended Setup

Set `ATLASSIAN_API_BASE_URL` to either:

- a site URL such as `https://example.atlassian.net`, or
- an issue API base such as `https://example.atlassian.net/rest/api/3/issue/`

Also set `ATLASSIAN_API_TOKEN` (export, credentials file, or runtime **`atlassian.env`**).

The skill uses:

- `git config user.email` as the Atlassian username
- `ATLASSIAN_API_TOKEN` as the password/token (resolved by **`atlassian-auth.sh`**)

If `ATLASSIAN_API_TOKEN` is not exported, the shared auth helper falls back to:

```text
${ATLASSIAN_API_TOKEN_FILE:-$HOME/.config/.jira/.credentials}
```

then runtime **`atlassian.env`**. It reads the first line of the credentials file as the token. Export is still preferred when available.

The skill uses the bundled `scripts/jira-api` and `scripts/jira-request` helpers directly. They source the shared Atlassian auth helper from the manifest **shared_files** directory next to `validate_artifact.py` under the skills install root (sync per **AGENTS.md** after cloning or updating).

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

Artifact bootstrap helper:

```bash
# Example resolved path:
# ~/.codex/skills/jira/scripts/bootstrap_jira_artifact.py

scripts/bootstrap_jira_artifact.py --issue PROJ-123 --json /tmp/proj-123.json
scripts/bootstrap_jira_artifact.py --issue PROJ-123 --json /tmp/proj-123.json --output task_proj-123.md --overwrite
```

The bootstrap helper validates the generated artifact automatically with `../scripts/validate_artifact.py` or an installed copy at `~/.cursor/skills/scripts/validate_artifact.py` or `~/.codex/skills/scripts/validate_artifact.py`. It also extracts a brief comment summary plus related issue and link hints from the fetched Jira JSON.
If the artifact already exists, it preserves local follow-up sections such as `## Follow-up Findings` and `## Improvement Candidates` while refreshing Jira-derived sections from live issue data.

## Shared Artifact Schema

Jira bootstrap artifacts follow the shared schema in `../ARTIFACTS.md`, including the core section order from `Summary` through `Actionable Context`.

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

```text
Use jira to bootstrap an artifact for PROJ-123
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
