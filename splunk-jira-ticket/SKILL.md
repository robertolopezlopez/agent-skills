---
name: splunk-jira-ticket
description: Fetch and summarize Splunk Jira or Atlassian tickets, especially when a browser URL redirects to login. Use when the user provides a `splunk.atlassian.net` issue URL or issue key, asks to summarize a Jira ticket, asks to override the Jira issue API host and path, or asks to debug Jira access using `ATLASSIAN_API_TOKEN`.
---

# Splunk Jira Ticket Access

When a Splunk Jira issue is not readable through normal browser access, use the Jira REST API before concluding the ticket is inaccessible.

## Workflow

1. Extract the issue key from the URL or user request.
2. Accept an optional host + path parameter before the issue key. Default to `https://splunk.atlassian.net/rest/api/3/issue/`.
3. Use `git config user.email` as the Atlassian username.
4. Use `ATLASSIAN_API_TOKEN` from the environment as the password.
5. Resolve `scripts/jira-api` relative to this skill directory.
6. Resolve `scripts/atlassian-auth.sh` relative to this skill directory.
7. Ensure the shared Atlassian auth helper exists at `${XDG_DATA_HOME:-$HOME/.local/share}/jira/atlassian-auth.sh`.
8. Refresh the shared auth helper from the skill copy before invoking `jira-api`:
   - `mkdir -p "${XDG_DATA_HOME:-$HOME/.local/share}/jira"`
   - `cp {RESOLVED_ATLASSIAN_AUTH_SOURCE} "${XDG_DATA_HOME:-$HOME/.local/share}/jira/atlassian-auth.sh"`
   - if the copy fails due to sandbox restrictions, rerun the copy step with escalated permissions
9. Use the installed shared auth helper from `scripts/jira-api`.
10. If the Jira helper is not executable, run `chmod +x` on the resolved Jira helper path.
11. Invoke the resolved Jira helper path directly:
   - default issue API base: `{RESOLVED_JIRA_API} {ISSUE_KEY}`
   - overridden issue API base: `{RESOLVED_JIRA_API} {HOST_AND_PATH} {ISSUE_KEY}`
12. When the task needs explicit field selection, pass the fields list as the final helper argument.
   - default issue API base: `{RESOLVED_JIRA_API} {ISSUE_KEY} {FIELDS}`
   - overridden issue API base: `{RESOLVED_JIRA_API} {HOST_AND_PATH} {ISSUE_KEY} {FIELDS}`
13. The helper should normalize the default or overridden host + path into an issue API base ending in `/rest/api/3/issue/`, then fetch:

```text
https://splunk.atlassian.net/rest/api/3/issue/{ISSUE_KEY}
```

14. Request only the fields needed for the task. For summaries, prefer:

```text
summary,status,issuetype,priority,assignee,reporter,created,updated,description,comment,labels
```

15. If the request fails due to sandbox network restrictions, rerun the same helper command with escalated network access.
16. Summarize the issue from the API response, not from the login page.
17. Never issue a direct Jira `curl` command from the skill workflow. All Jira HTTP access must go through `jira-api`.

## Helper Source

The canonical helper implementation lives at `scripts/jira-api`, resolved relative to this skill directory.
The vendored Atlassian auth helper source for this skill lives at `scripts/atlassian-auth.sh`, resolved relative to this skill directory.
The installed shared Atlassian auth helper should live at `${XDG_DATA_HOME:-$HOME/.local/share}/jira/atlassian-auth.sh`.

Use the resolved helper path in place for normal skill execution.
Refresh the installed shared auth helper from the vendored skill copy before invoking `jira-api`.
Do not duplicate Atlassian auth logic inline in this file or in `scripts/jira-api`; keep shared auth behavior in `scripts/atlassian-auth.sh` and the installed shared copy.

## Command Pattern

Preferred helper shape after resolving the path relative to this skill directory:

```bash
{RESOLVED_JIRA_API} {ISSUE_KEY}
```

Optional host + path override before the issue key:

```bash
{RESOLVED_JIRA_API} https://splunk.atlassian.net/rest/api/3/issue/ {ISSUE_KEY}
```

Optional fields parameter:

```bash
{RESOLVED_JIRA_API} {ISSUE_KEY} summary,status,priority,assignee
```

Host + path override with explicit fields:

```bash
{RESOLVED_JIRA_API} https://splunk.atlassian.net/rest/api/3/issue/ {ISSUE_KEY} summary,status,priority,assignee
```

## Notes

- Prefer concise summaries unless the user asks for detail.
- Prefer the bundled helper over raw `curl`.
- Resolve `scripts/jira-api` relative to this skill directory and invoke that resolved path directly instead of relying on `PATH` or copies in other directories.
- Accept a host + path override before the issue key, but default to `https://splunk.atlassian.net/rest/api/3/issue/`.
- Never access Jira with a direct assistant-issued `curl`; only run `jira-api`.
- If auth works but the issue is still unavailable, report that the account likely lacks permission to view the ticket.
- Do not expose the raw token in outputs.
