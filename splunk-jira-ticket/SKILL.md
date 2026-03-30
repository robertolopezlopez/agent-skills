---
name: splunk-jira-ticket
description: Fetch and summarize Splunk Jira or Atlassian tickets, especially when a browser URL redirects to login. Use when the user provides a `splunk.atlassian.net` issue URL or issue key, asks to summarize a Jira ticket, or asks to debug Jira access using `ATLASSIAN_API_TOKEN`.
---

# Splunk Jira Ticket Access

When a Splunk Jira issue is not readable through normal browser access, use the Jira REST API before concluding the ticket is inaccessible.

## Workflow

1. Extract the issue key from the URL or user request.
2. Use `git config user.email` as the Atlassian username.
3. Use `ATLASSIAN_API_TOKEN` from the environment as the password.
4. Fetch the issue from:

```text
https://splunk.atlassian.net/rest/api/3/issue/{ISSUE_KEY}
```

5. Request only the fields needed for the task. For summaries, prefer:

```text
summary,status,issuetype,priority,assignee,reporter,created,updated,description,comment,labels
```

6. If the request fails due to sandbox network restrictions, rerun the command with escalated network access.
7. Summarize the issue from the API response, not from the login page.

## Command Pattern

Use `curl` with basic auth:

```bash
curl -sS -u "$(git config user.email):$ATLASSIAN_API_TOKEN" \
  -H 'Accept: application/json' \
  "https://splunk.atlassian.net/rest/api/3/issue/{ISSUE_KEY}?fields=summary,status,issuetype,priority,assignee,reporter,created,updated,description,comment,labels"
```

## Notes

- Prefer concise summaries unless the user asks for detail.
- If auth works but the issue is still unavailable, report that the account likely lacks permission to view the ticket.
- Do not expose the raw token in outputs.
