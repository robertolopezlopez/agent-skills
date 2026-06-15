# Jira access (canonical policy)

Portable Jira Cloud issue fetch and update for **any repository**, **any OS**, and **any agent runtime** (Cursor, Codex, and similar). Policy syncs to **`$AGENT_CONFIG_HOME/skills/JIRA-ACCESS.md`**. Resolve with **`scripts/agent_config.py --jira-access-policy`**.

Workflow skills (`plan-issues`, overlays) consume normalized issue context produced here; they do not duplicate transport logic.

## Transport order

```text
1. acli jira workitem … — fetch, search, create, edit, transition, comment
2. jira-request           — REST v3 + agile escape hatch (sprint move, ADF edge cases)
3. jira-api               — read fallback when acli unavailable (Basic auth + token)
4. Jira / Atlassian MCP   — last resort when local tools missing or insufficient
```

Follow **Transport preference** and **Missing CLI tools — ask before fallback** in **`AGENTS.md`**.

**Auth note:** **`acli`** uses its own session (OAuth or API token login). Bundled **`jira-api`** / **`jira-request`** use **`email:ATLASSIAN_API_TOKEN`** Basic auth. The email must match the Atlassian account that owns the token (often **not** `git config user.email`). Prefer **`acli`** when emails differ.

## Prerequisites

Before fetching or updating issues:

```bash
scripts/check_skill_prereqs.sh jira      # acli install (OS-appropriate suggest lines)
scripts/check_skill_config.sh jira       # acli jira auth status
```

Alias: **`check_skill_prereqs.sh jira-access`** → same **`jira`** group.

If **`acli`** is missing, **ask the user** to install using the OS-appropriate **`suggest (...)`** line — do not install unless asked. If auth is missing, guide:

```bash
acli jira auth login --web
# or API token:
echo "<token>" | acli jira auth login --site "mysite.atlassian.net" --email "you@company.com" --token
```

Before MCP fallback, re-run **`acli jira auth status`**.

Site URL for helpers: resolve **`ATLASSIAN_API_BASE_URL`** from runtime **`atlassian.env`** (`agent_config.py --atlassian-env`). **`acli`** stores site in its auth profile after login.

## Path resolution

| What | Resolver |
|------|----------|
| Policy doc (this file) | `agent_config.py --jira-access-policy` |
| **Helper scripts** (Phase B) | `agent_config.py --jira-scripts-dir` |
| Atlassian defaults | `agent_config.py --atlassian-env` |
| Skills scripts root | `agent_config.py --skills-root` |
| API doc cache | `agent_config.py --api-docs-dir jira-rest-v3` |
| Prereqs | `check_skill_prereqs.sh jira` |
| Auth / config | `check_skill_config.sh jira` |

Until Phase B lands, bootstrap helpers remain under the installable **`jira`** skill directory (`skills/core/jira/scripts/` when working from the agent-skills repo).

## Inputs

Accept, depending on the task:

- issue key such as `PROJ-123`
- Atlassian issue URL containing the key
- JQL for search (`plan-issues`, bulk reads)
- free-form context for create/update flows (confirm with user before writes)

Extract the issue key from URLs before invoking commands.

## Normalized context contract

Downstream workflow skills expect stable field names whether data came from **`acli`**, **`jira-request`**, or MCP:

| Field | Description |
|-------|-------------|
| `issue_key` | e.g. `CLI-1474` |
| `url` | Browse URL |
| `summary` | Issue summary |
| `status` | Status name |
| `issuetype` | Type name when relevant |
| `assignee` / `reporter` | Display or email when relevant |
| `description` | Plain text or ADF source when fetched |
| `comments` | Comment list when requested |
| `transitions` | Available transitions when requested |
| `labels` | When relevant |
| `transport` | `acli`, `jira-request`, or `jira-api` |

Phase B adds **`jira-fetch`** / **`jira_context.py`** to emit this contract as JSON (mirrors **`gh-fetch`**).

## Workflow

1. Parse issue key or URL from the user request.
2. Reuse normalized context from an earlier fetch in the same session when still valid.
3. Run **`acli jira workitem view`** / **`search`** for reads; use **`comment list`** when comments are needed.
4. For writes (create, edit, transition, comment), use **`acli jira workitem …`** when the command covers the operation.
5. Escalate to **`jira-request`** for agile sprint assignment (`POST /rest/agile/1.0/sprint/{id}/issue`), ADF-heavy payloads, or site-specific REST not exposed by **`acli`**.
6. Use **`jira-api`** only as a read fallback when **`acli`** is missing or insufficient.
7. Use Jira or Atlassian MCP only after prereq/config checks fail.
8. **Confirm with the user** before create, transition, or comment on production issues unless they explicitly requested the write.

## Local commands (`acli`)

View issue (JSON):

```bash
acli jira workitem view PROJ-123 --json --fields summary,status,issuetype,assignee,comment
```

Search (JQL):

```bash
acli jira workitem search --jql 'project = CLI AND status = "In Review"' --json --fields key,summary,status
```

Comment:

```bash
acli jira workitem comment create --key PROJ-123 --body "Your comment" --json
acli jira workitem comment list --key PROJ-123 --json
```

Create (confirm fields first):

```bash
acli jira workitem create --summary "Title" --project PROJ --type Task --json
```

Edit / assign:

```bash
acli jira workitem edit --key PROJ-123 --summary "Updated" --assignee user@company.com --json
```

Transition:

```bash
acli jira workitem transition --key PROJ-123 --status "Done" --json
```

Sprint listing (assignment usually needs **`jira-request`**):

```bash
acli jira board list-sprints --board <boardId> --json
```

## REST escape hatch (`jira-request`)

Resolve helper from installable **`jira`** skill scripts (Phase B: **`scripts/jira/jira-request`**):

```bash
JSDIR=skills/core/jira/scripts   # repo path; use --jira-scripts-dir after Phase B
"$JSDIR/jira-request" GET /rest/api/3/issue/PROJ-123
"$JSDIR/jira-request" POST /rest/api/3/issue/PROJ-123/transitions /tmp/transition.json
"$JSDIR/jira-request" POST /rest/agile/1.0/sprint/SPRINT_ID/issue /tmp/sprint-body.json
```

Requires valid **`email:ATLASSIAN_API_TOKEN`** pair (see **Auth note** above).

## Artifact bootstrap

Default layout: **`$ARTIFACTS/<issue-key>/task_<issue>.md`** (see **`ARTIFACTS.md`**).

```bash
# Today: fetch JSON with acli, save, bootstrap
acli jira workitem view PROJ-123 --json --fields summary,status,description,comment > /tmp/proj-123.json
python3 skills/core/jira/scripts/bootstrap_jira_artifact.py --issue PROJ-123 --json /tmp/proj-123.json

# Phase B: bootstrap_jira_artifact.py --fetch --issue PROJ-123
```

Preserves **`Follow-up Findings`** and **`Improvement Candidates`** when re-bootstrapping an existing artifact.

## API reference cache

1. Read **`$AGENT_CONFIG_HOME/api-docs/jira-rest-v3/`** first (`agent_config.py --api-docs-dir jira-rest-v3`).
2. On first use or when stale, summarize [Jira Cloud REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/) into that directory.
3. Prefer cached endpoint notes before re-downloading.

## Workflow skill pairings

| Task | Skill / doc |
|------|-------------|
| Break down work / vertical slices | **`plan-issues`** |
| Investigation after fetch | **`repository-technical-analysis`** |
| Concrete bug repro | **`diagnose`** |
| Test-first fix | **`tdd`** |
| Wiki context | **`confluence`** (separate policy; Phase A pending) |

Transport stays in **this policy**; planning and code analysis stay in workflow skills.

## Safety

- Do not mix transport with planning or implementation policy here.
- Stop when authenticated Jira access fails — do not guess from partial data.
- Treat **writes** as user-confirmed unless the user explicitly requested them in the current task.
- Do not duplicate fetch logic inside workflow skills — refresh live state via **`acli`** / **`jira-request`** per this doc, then hand off.
