---
name: circleci
description: Fetch and inspect CircleCI Cloud pipelines, workflows, and jobs through the CircleCI API v2. Use when Codex or Cursor agents need CircleCI context and the user provides a pipeline ID, workflow ID, job number, CircleCI project slug, or app URL, asks to list recent pipelines, inspect run status, read job logs metadata, trigger or continue pipelines via API, or debug CircleCI API access using CIRCLE_TOKEN. Prefer the `circleci` CLI and bundled `circleci-request` helper, then CircleCI MCP when local tools are insufficient.
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

- the task is only local Git inspection; use synced **`GIT-ACCESS.md`**
- the task is CI on GitHub Actions, GitLab CI, Jenkins, or another provider
- the user only wants code-level debugging with no CircleCI API access; use `diagnose` or `repository-technical-analysis` after you have local evidence
- the task is primarily GitHub issue or PR discussion; use **`GITHUB-ACCESS.md`** + `gh`

## Inputs

Accept, depending on the request:

- a **project slug** in the form `vcs/org/repo` (for GitHub OAuth projects, commonly `gh/<org>/<repo>`). GitLab and GitHub App projects may use `circleci/<org-id>/<project-id>` as described in the [CircleCI API v2 documentation](https://circleci.com/docs/api/v2/).
- a **pipeline id** (UUID) or **pipeline number** when the user or URL references it
- a **workflow id** (UUID)
- a **job number** (integer) with enough context to resolve the owning project or pipeline when required by the endpoint
- a CircleCI web URL from which to extract ids (path segments or query parameters)
- optional **`CIRCLECI_API_BASE_URL`** for dedicated server or non-default API roots (defaults to CircleCI Cloud `https://circleci.com/api/v2`)

If the project slug is missing but the repo is a GitHub project on CircleCI, derive candidates from Git remotes after synced **`GIT-ACCESS.md`** + **`git-repo-identity`**, for example:

- remote `git@github.com:myorg/myrepo.git` or `https://github.com/myorg/myrepo` maps to project slug `gh/myorg/myrepo`

Confirm ambiguous slugs with the user when multiple remotes or organizations could apply.

## First Read

- Read the repository `AGENTS.md` before running commands when working from a checkout.
- Use synced **`GIT-ACCESS.md`** + **`git-repo-identity`** when local remote resolution is needed to infer `gh/<org>/<repo>`.
- Prefer the `circleci` CLI when it can satisfy the request (for example local job execution or follow).
- Prefer `scripts/circleci-request` relative to this skill directory for API v2 calls.
- Use CircleCI MCP only when local tools are missing or insufficient.

## Workflow

1. Use the `circleci` CLI when it can satisfy the request.
2. Invoke `scripts/circleci-request` for API v2 calls. It resolves the API base URL and token from exported env vars, then the runtime **`circleci.env`** file (see **Local Defaults File**). **Do not read defaults files with the editor/Read tool** unless the user explicitly asked to debug helper resolution.
3. Resolve `scripts/circleci-request` relative to this skill directory.
4. If the helper is not executable, run `chmod +x` on the resolved helper path.
5. Call the smallest endpoint set needed (pipeline list, then pipeline detail, then workflows or jobs).
6. If the helper request fails because outbound HTTPS is blocked (for example in a restricted agent sandbox), rerun the same helper from an environment that allows TLS to `circleci.com` or to your configured API host.
7. Use CircleCI MCP only when local tools are missing or insufficient.
8. Normalize results for downstream skills: project slug, pipeline id and number, workflow ids, job numbers, states, and relevant URLs from API fields.
9. Never issue a raw `curl` to CircleCI from this skill workflow. Route HTTP through `scripts/circleci-request`, then MCP when helpers are insufficient.

## Validation

- Run **`scripts/check_skill_prereqs.sh circleci`** and **`scripts/check_skill_config.sh circleci`**. **Help the user** install `circleci` when needed and configure **`CIRCLE_TOKEN`** (export and/or **`circleci.env`** from **`templates/circleci.env.example`**) before API calls fail.
- Prefer local `circleci` CLI and `circleci-request` before CircleCI MCP.
- Keep HTTP access behind `scripts/circleci-request`, not ad hoc `curl`.
- Stop when authenticated API access fails and report missing or invalid token clearly.
- Do not expose tokens in logs, skill output, or committed files.

## Transport Preference

Preferred order:

1. synced **`GIT-ACCESS.md`** + **`git-repo-identity`** when project slug inference from remotes is needed
2. `circleci` CLI when it can satisfy the request
3. `scripts/circleci-request` for arbitrary [API v2](https://circleci.com/docs/api/v2/) requests the helper can reach with `Circle-Token` authentication
4. CircleCI MCP when local tools are missing or insufficient

## API reference cache

Resolve **`$AGENT_CONFIG_HOME/api-docs/circleci-api-v2/`** with **`scripts/agent_config.py --api-docs-dir circleci-api-v2`**.

1. Read the cached `README.md` and endpoint notes when present.
2. On first use (or when stale), fetch or summarize [CircleCI API v2](https://circleci.com/docs/api/v2/) docs into that directory — especially pipeline, workflow, and job endpoints used by `circleci-request`.
3. On later uses, consult the cache before re-downloading docs.

See **AGENTS.md** (REST API reference cache).

## Helper Source

The generic request helper lives at `scripts/circleci-request`, resolved relative to this skill directory (the synced skill root, not the agent-skills git checkout path, when the agent loads the installed copy).

## Local Defaults File

Bundled helpers load defaults from **one** runtime config home (see **AGENTS.md**). Resolve with **`scripts/agent_config.py --circleci-env`** (shell: **`scripts/agent-config.sh --circleci-env`**).

Override detection with **`AGENT_SKILLS_RUNTIME=cursor`** or **`codex`**. Let **`circleci-request`** read the file; agents must not open it unless debugging config resolution. Scaffold from **`templates/circleci.env.example`** when helping the user set up config.

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

## Shell Helper Commands

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

- synced **`GIT-ACCESS.md`** + **`git-repo-identity`** to infer `gh/<org>/<repo>` from remotes
- `repository-technical-analysis` or `diagnose` when CI failures lead into codebase investigation

## Safety Notes

- Confirm before triggering pipelines, rerunning workflows, or canceling jobs; default bias is read-only unless the user asked for the write.
- Treat cancel, approve, and context secret operations as high impact.
- Do not paste API tokens into tickets, transcripts, or commits.
