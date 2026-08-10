# CircleCI command reference

Read only when exact command or configuration details are needed.

## Helper

Resolve `scripts/circleci-request` relative to the installed `circleci` skill. Syntax:

```text
circleci-request [CIRCLECI_API_ROOT] METHOD PATH [JSON_BODY_FILE]
```

Run calls directly—no pipeline, command substitution, `&&`, or `;` around the helper.

```bash
<helper> GET /project/gh%2Fmyorg%2Fmyrepo/pipeline
<helper> GET /pipeline/<pipeline-uuid>
<helper> GET /pipeline/<pipeline-uuid>/workflow
<helper> GET /workflow/<workflow-uuid>
<helper> GET /workflow/<workflow-uuid>/job
<helper> POST /workflow/<workflow-uuid>/cancel
<helper> POST /workflow/<workflow-uuid>/rerun /tmp/rerun.json
<helper> https://circleci.com/api/v1.1 GET /project/gh/org/repo/<job-number>
```

Encode `/` as `%2F` inside API v2 project slugs.

## Runtime configuration

The helper resolves API root and token from exported variables, then the active runtime `circleci.env`:

- `CIRCLECI_API_BASE_URL` (default `https://circleci.com/api/v2`)
- `CIRCLE_TOKEN`, then `CIRCLECI_TOKEN`

Resolve the file with `agent_config.py --circleci-env`. Let the helper read it; do not open it unless the user explicitly asks to debug configuration. Explicit API-root arguments override environment/defaults.

## Common endpoint progression

Use only the required chain:

1. project pipelines
2. pipeline details
3. pipeline workflows
4. workflow jobs
5. v1.1 job detail only when v2 fields are insufficient

For pagination, follow `next_page_token` with the endpoint's documented page-token query. Consult the runtime `circleci-api-v2` cache before inventing fields or payloads.
