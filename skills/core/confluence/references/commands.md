# Confluence command reference

Read only when exact command or configuration details are needed.

## Local CLI

```bash
acli confluence auth status
acli confluence page view --id <PAGE_ID> --body-format storage --json
```

## Bundled helpers

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

1. Resolve title, space, parent, and body format.
2. For updates, fetch the current page and version first.
3. Build the smallest REST v2 JSON payload.
4. Confirm when the target or overwrite is consequential.
5. Call `confluence-request`; report returned page ID and canonical wiki URL.

Consult the runtime `confluence-rest-v2` cache for payload fields rather than guessing.
