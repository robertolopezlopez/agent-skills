# Confluence command reference

Read only when exact command or configuration details are needed.

## Local CLI

```bash
twg help describe "confluence content update"
twg confluence content get <CONTENT_ID>
twg confluence content update <CONTENT_ID> [options]
acli confluence auth status
acli confluence auth login
acli confluence page view --id <PAGE_ID> --body-format storage --json
```

Use TWG first. Continue to authenticated ACLI, then helpers, only when the
preceding transport is unavailable or does not support the operation.

## Bundled helpers

These are the Basic-auth fallback after TWG and ACLI.

Resolve both helpers relative to the installed `confluence` skill:

```text
confluence-api [CONFLUENCE_API_ROOT] PAGE_ID [QUERY_WITHOUT_QUESTION_MARK]
confluence-request [CONFLUENCE_API_ROOT] METHOD PATH [JSON_BODY_FILE]
```

Examples:

```bash
<confluence-api> <PAGE_ID>
<confluence-api> <PAGE_ID> body-format=storage
<confluence-request> GET /pages/<PAGE_ID>
<confluence-request> GET /spaces
<confluence-request> POST /pages /tmp/create-page.json
<confluence-request> PUT /pages/<PAGE_ID> /tmp/update-page.json
```

## Runtime configuration

Helpers resolve values in this order:

1. explicit API-root argument
2. exported `ATLASSIAN_CONFLUENCE_API_BASE_URL`, then `ATLASSIAN_API_BASE_URL`
3. active runtime `atlassian.env`

`ATLASSIAN_CONFLUENCE_API_BASE_URL` is the full `/wiki/rest/api/v2` root. For a site URL in `ATLASSIAN_API_BASE_URL`, helpers append that suffix. Auth uses `git config user.email` plus `ATLASSIAN_API_TOKEN`, the configured token file, or runtime defaults through shared `atlassian-auth.sh`.

Resolve the defaults path with `agent_config.py --atlassian-env`; let helpers read it.

## Create/update

Use `twg confluence content create|update`; inspect live help first. For fallback
REST updates, fetch the current version, build the smallest JSON payload, call
`confluence-request`, and report the returned page ID and URL.

Consult the runtime `confluence-rest-v2` cache for payload fields rather than guessing.

Use Confluence/Atlassian MCP only when TWG, ACLI, and these helpers cannot
perform the operation.
