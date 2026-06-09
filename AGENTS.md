# AGENTS

This repository is the source of truth for agent skills used with Codex and Cursor.

## Skill sync rule

Whenever a manifest-declared skill directory changes or a new skill is created:

1. install or update the matching copied skill under each configured install root (defaults below)
2. keep each installed copy in sync with the repository copy before finishing the task

Default install locations (see `scripts/sync_skills.sh` for overrides):

- Codex: `~/.codex/skills/<skill-name>` (or `$CODEX_HOME/skills/<skill-name>` when `CODEX_HOME` is set)
- Cursor personal agent skills: `~/.cursor/skills/<skill-name>` (or `$CURSOR_AGENT_SKILLS_HOME/skills/<skill-name>` — parent of `skills/` defaults to `~/.cursor`)

Whenever a manifest-declared skill directory is deleted or removed from `skills_manifest.yaml`:

1. remove the matching installed skill from each synced install root listed above

To sync only one stack, use `./scripts/sync_skills.sh --codex-only` or `./scripts/sync_skills.sh --cursor-only`, or set `AGENT_SKILLS_SYNC_TARGETS` to `codex` or `cursor`.

To **omit** manifest skills when installing (e.g. skip all `private-service` overlays), set `AGENT_SKILLS_EXCLUDE_RELEASE_GROUPS` and/or `AGENT_SKILLS_EXCLUDE_SKILL_NAMES` when running `scripts/sync_skills.sh` (see script usage). The hook does not set these by default.

The `git-hooks/post-commit` hook runs `scripts/sync_skills.sh --all` with `AGENT_SKILLS_SYNC_TARGETS=codex,cursor` so each commit refreshes **both** default install roots (update the hook if you need different behavior).

Treat this sync as part of the required workflow for skill changes in this repository.

## Repository constitution

Use this file as the repo-global policy layer. Prefer putting shared rules here instead of repeating them in every skill.

## Installable skill directory contract

Each installable skill directory declared in `skills_manifest.yaml` is expected to be a standalone installed skill.

Required:
- a manifest entry with:
  - stable `name` used for the installed skill name
  - `path` pointing to the repo-local skill directory
- `SKILL.md` at the root of the declared skill directory

Allowed:
- helper scripts
- templates
- references
- assets
- companion docs

Do not assume hidden repo context inside a skill. A copied skill should remain usable after sync into `~/.codex/skills/<skill-name>` and `~/.cursor/skills/<skill-name>` (or the equivalent paths when override env vars are set). Filesystem location inside this repository may differ from installed skill name; the manifest is the source of truth for that mapping.

## SKILL.md minimum contract

Each `SKILL.md` must include:
- YAML frontmatter
- `name`
- `description`
- a primary heading naming the skill
- enough workflow detail to use the skill correctly

Recommended sections:
- Inputs
- Workflow
- Validation
- Outputs or artifacts
- Safety notes
- Companion skills or ordering rules

See `docs/skill-schema.md` for the preferred section order and migration guidance.

## Transport preference

Transport skills (GitHub, GitLab, Jira, Confluence, CircleCI, and similar) use this order unless a skill documents a narrower exception:

1. **Local CLI tools** — `git`, `gh`, `glab`, `circleci`, and other documented host CLIs
2. **Bundled shell helpers** — repository-synced scripts such as `jira-api`, `confluence-api`, and `circleci-request`
3. **MCP** — configured Model Context Protocol servers **last**, when local tools and helpers are missing or insufficient

Do not issue raw assistant `curl` where a skill routes HTTP through helpers. Keep the same normalized output contract regardless of transport path.

## Design rules

- Keep skills modular. Prefer a small focused skill over a large mixed-purpose skill.
- Separate transport/access skills from workflow/analysis skills when practical.
- Put repo-specific behavior in overlay skills instead of polluting general skills.
- Prefer explicit artifact names, file paths, and command examples.
- Prefer helper scripts and checked-in templates over large repeated prose blocks.
- Use relative paths that still make sense after the skill is copied into each install root (`~/.codex/skills/<skill-name>` and `~/.cursor/skills/<skill-name>` by default).

## Validation rule

Before finishing a task that changes any manifest-declared skill directory or shared skill helper:

1. validate the changed skill definitions with the repository skill validator
2. fix validation failures
3. sync the installed copies (default: `~/.codex/skills` and `~/.cursor/skills`; see `scripts/sync_skills.sh`)

If a new common rule appears in multiple skills, move it here unless there is a strong reason not to.

## Runtime config home (Cursor vs Codex)

Skills synced under **`~/.cursor/skills/`** use **`~/.cursor/`** for local defaults files (`atlassian.env`, `circleci.env`, …). Codex installs use **`~/.codex/`**. Bundled helpers detect the runtime from the helper script path; override with **`AGENT_SKILLS_RUNTIME=cursor`** or **`codex`**, or set **`AGENT_CONFIG_HOME`**.

**Agents must not read defaults files directly** — invoke bundled helpers (`jira-api`, `confluence-api`, `circleci-request`, …) or bootstrap scripts, which load the runtime-appropriate file via **`scripts/agent-config.sh`**. Do not probe the other runtime's config home unless the user is debugging cross-runtime setup.

Resolve runtime config paths with **`scripts/agent_config.py`** (synced next to **`scripts/resolve_artifact_path.py`**): **`--atlassian-env`**, **`--config-home`**, **`--runtime`**, **`--defaults-hint atlassian.env`**, **`--api-docs-root`**, or **`--api-docs-dir <slug>`**. Shell equivalent: **`scripts/agent-config.sh`** with the same flags.

## REST API reference cache

When a transport skill needs REST API shape, endpoints, or field semantics:

1. **Read the runtime-local cache first** under **`$AGENT_CONFIG_HOME/api-docs/<service-slug>/`** (Cursor: **`~/.cursor/api-docs/`**; Codex: **`~/.codex/api-docs/`**). Resolve with **`scripts/agent_config.py --api-docs-root`** or **`--api-docs-dir <slug>`** (shell: **`scripts/agent-config.sh`** with the same flags).
2. **On first use** for a service slug, fetch or summarize the official API docs (or the skill's canonical doc URLs), then **write a local copy** into that directory for later sessions. Prefer Markdown index files (`README.md`, endpoint notes) plus optional fetched HTML/PDF/OpenAPI exports when useful.
3. **On later uses**, consult the cached material before re-downloading or re-searching the web. Refresh the cache when the skill, changelog, or user reports an API version change.

Suggested service slugs (transport skills may document narrower names):

| Slug | Typical source |
|------|----------------|
| `jira-rest-v3` | Atlassian Jira Cloud REST API v3 |
| `confluence-rest-v2` | Atlassian Confluence Cloud REST API v2 |
| `github-rest` | GitHub REST API (companion to `gh` / `gh api`) |
| `gitlab-api` | GitLab REST API (companion to `glab api`) |
| `circleci-api-v2` | CircleCI API v2 |

Do not commit cached API docs into this repository; keep them in the runtime config home only. Do not store secrets in the cache tree.

## Artifacts directory phrase

When the user says **"the artifacts directory"** (or similar), resolve **`$ARTIFACTS/<meaningful_id>/`** via **`scripts/resolve_artifact_path.py`** — not in-repo **`_artifacts_/`** unless they explicitly ask. Cross-repo material belongs under **`$GLOBAL/`**. Read existing files in the target folder before creating duplicates.

- **Cursor (optional):** install **`templates/cursor/rules/agent-artifacts-directory.mdc`** with **`./scripts/bootstrap_agent_artifacts.sh --cursor-rule`**
- **Codex:** this section plus **`ARTIFACTS.md`** carry the same contract (Codex has no `.mdc` rules format)
- **One-time store setup:** **`./scripts/bootstrap_agent_artifacts.sh`** creates **`$AGENT_ARTIFACTS_HOME/README.md`** and scaffolds **`$GLOBAL/NEXT_TIME_CHECKS.md`** when missing

## Learn-daily playbook

Portable lessons split by scope (see **`ARTIFACTS.md`**):

- **`$GLOBAL/NEXT_TIME_CHECKS.md`** — cross-repository next-time checks
- **`$GLOBAL/<topic>/`** — cross-repository reference cards (org maps, team ownership, company tooling)
- **`$ARTIFACTS/NEXT_TIME_CHECKS.md`** — lessons specific to the active repository
- **`$ARTIFACTS/<meaningful_id>/`** — ticket-scoped work for the active repository

Legacy in-repo **`_artifacts_/`** paths remain valid for read/extend only.

Resolve paths with **`scripts/resolve_artifact_path.py`** (synced to **`~/.cursor/skills/scripts/`** and **`~/.codex/skills/scripts/`**). Use **`--global-artifacts-root`**, **`--global-next-time-checks`**, or **`--scope global`** for cross-repo paths. Override the store root with **`AGENT_ARTIFACTS_HOME`** when needed.

## Delegation rule

When a skill describes subagent or parallel-agent behavior:
- define ownership clearly
- avoid overlapping write scopes
- keep non-writer roles read-only unless explicitly required
- require concise result reporting with files changed and validation run

## Backward-compatibility rule

Be careful when renaming a skill directory, changing artifact schemas, or changing referenced helper paths. These changes can break installed copies and downstream workflows. Document the change clearly in the edited skill.

## Changelog rule

Use `CHANGELOG.md` for breaking changes and workflow-level repository changes.
Do not treat it as a mirror of every commit; routine wording, cleanup, and implementation-only changes belong in commit history instead.
