---
name: splunk-jira
description: Fetch, summarize, create, and update Splunk Jira tickets. Use when the user provides a `splunk.atlassian.net` issue URL or issue key, asks to summarize a Jira ticket, asks to create a Jira ticket, asks to change status, move a ticket into a sprint, assign or edit a ticket, comment on a ticket, asks to override the Jira issue API host and path, or asks to debug Jira access using `ATLASSIAN_API_TOKEN`.
---

# Splunk Jira Ticket Access

Use this skill as a Splunk-specific overlay for `jira`.

When a Splunk Jira issue is not readable through normal browser access, use the generic `jira` skill workflow before concluding the ticket is inaccessible.

## Workflow

1. Extract the issue key from the URL or user request.
2. By default, use `https://splunk.atlassian.net/rest/api/3/issue/`.
3. Accept an optional host + path parameter before the issue key when the user explicitly wants a different Jira site or API base.
4. Follow the generic `jira` skill workflow for auth setup, shared helper refresh, helper execution, field selection, and summarization.
5. When no override is provided, use the Splunk default and fetch:

```text
https://splunk.atlassian.net/rest/api/3/issue/{ISSUE_KEY}
```

6. Request only the fields needed for the task. For summaries, prefer:

```text
summary,status,issuetype,priority,assignee,reporter,created,updated,description,comment,labels
```

7. If the request fails due to sandbox network restrictions, rerun the same helper command with escalated network access.
8. Summarize the issue from the API response, not from the login page.
9. Never issue a direct Jira `curl` command from the skill workflow. All Jira HTTP access must go through `jira-api`.

## Helper Source

The generic helper implementation lives in the `jira` skill at `jira/scripts/jira-api`.
This Splunk overlay keeps a thin compatibility wrapper at `splunk-jira/scripts/jira-api` that defaults `ATLASSIAN_API_BASE_URL` to `https://splunk.atlassian.net` and then delegates to the generic helper.
The generic vendored Atlassian auth helper source lives in the `jira` skill at `jira/scripts/atlassian-auth.sh`.

## Command Pattern

Preferred helper shape after resolving the path relative to this skill directory:

```bash
<resolved-path-to-scripts/jira-api> {ISSUE_KEY}
```

Optional host + path override before the issue key:

```bash
<resolved-path-to-scripts/jira-api> https://splunk.atlassian.net/rest/api/3/issue/ {ISSUE_KEY}
```

Optional fields parameter:

```bash
<resolved-path-to-scripts/jira-api> {ISSUE_KEY} summary,status,priority,assignee
```

Host + path override with explicit fields:

```bash
<resolved-path-to-scripts/jira-api> https://splunk.atlassian.net/rest/api/3/issue/ {ISSUE_KEY} summary,status,priority,assignee
```

## Create Workflow

Use this workflow together with the generic `jira` create workflow.

Keep all Splunk-specific creation logic here.

### Splunk defaults

- Jira site: `https://splunk.atlassian.net`
- Project: `DAT`
- Issue type: usually `Story`
- ProductBacklogArea: `GDI`

### Splunk-specific heuristics

**Title**
- expand abbreviations and produce a clear, concise title
- common abbreviations:
  - `AS` → `Auto-Schematization`
  - `GOB` → `Guided Onboarding`

**Component**
- Auto-schematization, AS, grouping, splitting, CIM, prompts, SPL2, TA → `DM GX AI Schematization BE`
- Guided onboarding, GOB, sources → `DM GX Guided Onboarding BE`
- Platform, auth, workflow, persistence, API, cicd, deployment → `DM GX Platform BE`

**Mission team**
- `DM GX AI Schematization BE` or `DM GX Platform BE` when AS-owned → `GX - Auto Schematization`
- `DM GX Guided Onboarding BE` → `GX - Guided Onboarding`

**Story points**
- Small config change, flag toggle, docs → `1`
- Moderate feature, refactor, new tests → `2`
- Larger feature, multi-file changes, new agent behavior → `3`
- If uncertain, or task scope appears very large, do not provide a default.

**Epic**
- Auto-Schematization work: use an epic under `RDMP-3757`
- Guided Onboarding work: use an epic under `RDMP-3545`

**Sprint**
- default to no sprint (backlog)
- use current sprint only for urgent or already in-progress work

**Assignee**
- default unassigned
- assign to current user only if work is already in progress

### Splunk-specific create steps

1. Follow the generic `jira` create flow for confirmation, auth, create call, optional sprint assignment, and optional transition.
2. Use Splunk Jira field mappings and required custom fields.
3. Create in project `DAT`.
4. Use Splunk-specific component, mission team, epic, sprint, and story point heuristics.

## Update Workflow

Use this workflow together with the generic `jira` update workflow.

Common Splunk Jira developer actions include:

- move a backlog ticket into the current sprint
- transition a ticket to In Progress or another workflow status
- update story points, labels, assignee, epic, or summary
- add implementation notes as a comment

Keep Splunk-specific sprint and field conventions here, and follow the generic `jira` update mechanics for transitions, edits, comments, and sprint assignment calls.

## Notes

- Prefer concise summaries unless the user asks for detail.
- Use this skill together with `jira`: keep the generic Jira workflow there and let this overlay supply Splunk defaults.
- Keep generic Jira creation behavior in `jira` and all Splunk-specific creation rules here.
- Prefer the bundled helper over raw `curl`.
- Resolve `scripts/jira-api` relative to this skill directory and invoke that resolved path directly instead of relying on `PATH` or copies in other directories.
- Accept a host + path override before the issue key, but default to `https://splunk.atlassian.net/rest/api/3/issue/`.
- Never access Jira with a direct assistant-issued `curl`; only run `jira-api`.
- If `ATLASSIAN_API_TOKEN` is already set, do not probe `~/.config/.jira/.credentials` just to verify auth.
- If auth works but the issue is still unavailable, report that the account likely lacks permission to view the ticket.
- Do not expose the raw token in outputs.
