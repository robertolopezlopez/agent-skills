---
name: circleci
description: Fetch and inspect CircleCI Cloud pipelines, workflows, and jobs through the CircleCI API v2. Use when Codex or Cursor agents need CircleCI context and the user provides a pipeline ID, workflow ID, job number, CircleCI project slug, or app URL, asks to list recent pipelines, inspect run status, read job logs metadata, trigger or continue pipelines via API, or debug CircleCI API access using CIRCLE_TOKEN. Prefer a CircleCI MCP server when available, with the bundled circleci-request helper as fallback transport.
---

# CircleCI API Access

Use this skill when CI state lives in CircleCI and you need structured fetch or safe API operations before downstream diagnosis or reporting.

This skill is the transport layer for CircleCI API v2 identity, reads, and writes that fit the generic helper pattern. Keep repository or failure analysis in companion skills.

After sync from this repository (see **AGENTS.md**), the installable copy lives at **`~/.codex/skills/circleci`** or **`$CODEX_HOME/skills/circleci`** for Codex, and **`~/.cursor/skills/circleci`** or **`$CURSOR_AGENT_SKILLS_HOME/skills/circleci`** for Cursor. Resolve `scripts/circleci-request` relative to whichever root is active for the session—behavior is the same in both.

## When to Use

Use this skill when the user wants to:

- list or inspect pipelines for a project
- fetch pipeline, workflow, or job details by id
- inspect job artifacts or test metadata pointers exposed by the API
- trigger or continue a pipeline when API access is explicitly requested
- debug token or base URL issues against CircleCI Cloud (or a custom API root)

## When Not to Use

Do not use this skill when:

- the task is only local Git inspection; use `git`
- the task is CI on GitHub Actions, GitLab CI, Jenkins, or another provider
- the user only wants code-level debugging with no CircleCI API access; use `diagnose` or `repository-technical-analysis` after you have local evidence
- the task is primarily GitHub issue or PR discussion; use `github`

## Inputs

Accept, depending on the request:

- a **project slug** in the form `vcs/org/repo` (for GitHub OAuth projects, commonly `gh/<org>/<repo>`). GitLab and GitHub App projects may use `circleci/<org-id>/<project-id>` as described in the [CircleCI API v2 documentation](https://circleci.com/docs/api/v2/).
- a **pipeline id** (UUID) or **pipeline number** when the user or URL references it
- a **workflow id** (UUID)
- a **job number** (integer) with enough context to resolve the owning project or pipeline when required by the endpoint
- a CircleCI web URL from which to extract ids (path segments or query parameters)
- optional **`CIRCLECI_API_BASE_URL`** for dedicated server or non-default API roots (defaults to CircleCI Cloud `https://circleci.com/api/v2`)

If the project slug is missing but the repo is a GitHub project on CircleCI, derive candidates from Git remotes after using the `git` skill, for example:

- remote `git@github.com:myorg/myrepo.git` or `https://github.com/myorg/myrepo` maps to project slug `gh/myorg/myrepo`

Confirm ambiguous slugs with the user when multiple remotes or organizations could apply.

## First Read

- Read the repository `AGENTS.md` before running commands when working from a checkout.
- Prefer a **CircleCI MCP server** when one is configured and exposes the needed resources.
- Fall back to `scripts/circleci-request` relative to this skill directory for API v2 calls when MCP is unavailable or insufficient.
- Use the `git` skill when local remote resolution is needed to infer `gh/<org>/<repo>`.

## Workflow

1. Prefer CircleCI MCP for reads and writes when it can satisfy the request.
2. Resolve the API base URL in this order:
   - explicit argument passed to `scripts/circleci-request`
   - exported `CIRCLECI_API_BASE_URL`
   - first readable defaults file (**`~/.cursor/circleci.env`**, then **`~/.codex/circleci.env`**) for `CIRCLECI_API_BASE_URL`
   - default `https://circleci.com/api/v2` for CircleCI Cloud
3. Resolve the API token in this order:
   - exported `CIRCLE_TOKEN` (matches CircleCI docs examples)
   - exported `CIRCLECI_TOKEN`
   - first match in **`~/.cursor/circleci.env`**, then **`~/.codex/circleci.env`**, for `CIRCLE_TOKEN` or `CIRCLECI_TOKEN`
4. Resolve `scripts/circleci-request` relative to this skill directory for fallback calls.
5. If the helper is not executable, run `chmod +x` on the resolved helper path.
6. Call the smallest endpoint set needed (pipeline list, then pipeline detail, then workflows or jobs).
7. If the fallback request fails because outbound HTTPS is blocked (for example in a restricted agent sandbox), rerun the same helper from an environment that allows TLS to `circleci.com` or to your configured API host.
8. Normalize results for downstream skills: project slug, pipeline id and number, workflow ids, job numbers, states, and relevant URLs from API fields.
9. Never issue a raw `curl` to CircleCI from this skill workflow. When MCP is not used, route HTTP through `scripts/circleci-request`.

## Validation

- Prefer CircleCI MCP first when available.
- Keep HTTP access behind `scripts/circleci-request`, not ad hoc `curl`.
- Stop when authenticated API access fails and report missing or invalid token clearly.
- Do not expose tokens in logs, skill output, or committed files.

## Transport Preference

Preferred order:

1. CircleCI MCP for structured reads and supported writes
2. `scripts/circleci-request` for arbitrary [API v2](https://circleci.com/docs/api/v2/) requests the helper can reach with `Circle-Token` authentication

## Helper Source

The generic request helper lives at `scripts/circleci-request`, resolved relative to this skill directory (the synced skill root, not the agent-skills git checkout path, when the agent loads the installed copy).

## Local Defaults File

If **`~/.cursor/circleci.env`** or **`~/.codex/circleci.env`** exists, read the first match for each variable in that order before invoking the fallback helper when environment variables are not set. Prefer **`~/.cursor/circleci.env`** for Cursor-oriented setups; **`~/.codex/circleci.env`** remains the right place for Codex-heavy environments when you want defaults separate from Cursor.

Preferred usage (non-secret base URL only in file; token optional if you already export it):

```bash
CIRCLECI_API_BASE_URL=https://circleci.com/api/v2
```

Dedicated server example:

```bash
CIRCLECI_API_BASE_URL=https://circleci.example.com/api/v2
```

Rules:

- treat explicit helper arguments as highest priority
- treat exported environment variables as higher priority than defaults files
- prefer keeping `CIRCLE_TOKEN` or `CIRCLECI_TOKEN` in the environment instead of long-lived tokens in defaults files when possible

## Fallback Command Pattern

Ensure `CIRCLE_TOKEN` or `CIRCLECI_TOKEN` is set for the shell unless the token is supplied via defaults files.

List recent pipelines for a project (slug segments must be URL-encoded when used in the path; encode `/` as `%2F`):

```bash
<resolved-path-to-scripts/circleci-request> GET /project/gh%2Fmyorg%2Fmyrepo/pipeline
```

Fetch one pipeline by id:

```bash
<resolved-path-to-scripts/circleci-request> GET /pipeline/00000000-0000-0000-0000-000000000000
```

Fetch workflows for a pipeline:

```bash
<resolved-path-to-scripts/circleci-request> GET /pipeline/00000000-0000-0000-0000-000000000000/workflow
```

POST body from a file (for example trigger or continue pipeline payloads from the API docs):

```bash
<resolved-path-to-scripts/circleci-request> POST /project/gh%2Fmyorg%2Fmyrepo/pipeline /tmp/trigger-pipeline.json
```

Explicit API root before method:

```bash
<resolved-path-to-scripts/circleci-request> https://circleci.com/api/v2 GET /me
```

## Outputs / Artifacts

Return normalized results for the task, such as:

- project slug and API root used
- pipeline ids, numbers, states, and VCS revision metadata when present
- workflow ids and statuses
- job names, numbers, and statuses
- concise error or auth diagnosis without leaking secrets

This skill does not need to write a local artifact by default.

## Companion Skills

Use this skill as the CircleCI transport layer.

Common pairings:

- `git` to infer `gh/<org>/<repo>` from remotes
- `repository-technical-analysis` or `diagnose` when CI failures lead into codebase investigation

## Safety Notes

- Confirm before triggering pipelines, rerunning workflows, or canceling jobs; default bias is read-only unless the user asked for the write.
- Treat cancel, approve, and context secret operations as high impact.
- Do not paste API tokens into tickets, transcripts, or commits.
