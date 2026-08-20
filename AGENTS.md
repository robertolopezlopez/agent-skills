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

To **omit** manifest skills when installing (e.g. skip all `guided-experience-service` overlays), set `AGENT_SKILLS_EXCLUDE_RELEASE_GROUPS` and/or `AGENT_SKILLS_EXCLUDE_SKILL_NAMES` when running `scripts/sync_skills.sh` (see script usage). The hook does not set these by default.

The `git-hooks/post-commit` hook runs `scripts/sync_skills.sh --all` with `AGENT_SKILLS_SYNC_TARGETS=codex,cursor`, `scripts/sync_cursor_rules.sh --overwrite`, and `scripts/sync_codex_rules.sh --overwrite` so each commit refreshes **both** default install roots, **Cursor always-on rules** from `templates/cursor/rules/`, and managed **Codex global `AGENTS.md` rules** from `templates/codex/rules/` (update the hook if you need different behavior).

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

1. **Local CLI tools** — authenticated official or documented CLIs such as `git`, `gh`, `glab`, `acli`, `circleci`, and `twg` when its workflow applies
2. **Bundled shell helpers** — repository-synced scripts such as `jira-api`, `confluence-api`, and `circleci-request`; use `ATLASSIAN_API_TOKEN` only here as Basic-auth fallback
3. **MCP** — configured Model Context Protocol servers **last**, when local tools and helpers are missing or insufficient

Do not issue raw assistant `curl` where a skill routes HTTP through helpers. Keep the same normalized output contract regardless of transport path.

## Missing CLI tools — ask before fallback

When a skill needs a host CLI, check availability first (`command -v <tool>` or **`scripts/check_skill_prereqs.sh <skill>`** after sync). The helper detects **`uname -s`** and available package managers (`brew`, `apt-get`, `dnf`, `pacman`, …) and prints **OS-appropriate** install suggestions.

If the tool is **missing** and a **safe, standard** install path exists:

1. **Ask the user** to install it. Give the command that matches **their OS**, not only macOS Homebrew. Prefer the **`suggest (...)`** line from **`check_skill_prereqs.sh`** when it matches the user's platform; otherwise pick the closest standard package-manager command or official vendor doc link the skill lists.
2. **Do not install** packages yourself unless the user explicitly asks you to run the install command.
3. **OS guidance (examples — verify against helper output):**
   - **macOS** — Homebrew when `brew` is available (`brew install gh`, `brew install glab`, …)
   - **Debian/Ubuntu** — `apt` when available (`sudo apt install gh`, `sudo apt install jq`, …)
   - **Fedora/RHEL** — `dnf` when available (`sudo dnf install gh`, …)
   - **Arch** — `pacman` when available (`sudo pacman -S github-cli`, …)
   - **Other / unsupported distro** — official vendor install URL from the skill or helper `vendor:` line
4. Treat **bundled repo scripts** (synced helpers under the skills install root) as already available — do not ask to install those.
5. Only after the user declines, install is blocked, or auth setup is still required, continue with the next transport layer per **Transport preference** (helpers, then MCP last) and say which tool was skipped.

Unsafe or non-standard installs (random `curl | bash`, unknown taps, sudo-heavy scripts) require explicit user approval — default to asking, not doing.

## Literal code search

Routine literal search uses synced **`LITERAL-CODE-SEARCH.md`** and helpers under **`$AGENT_CONFIG_HOME/skills/scripts/literal-search/`** (Cursor: **`~/.cursor/skills/…`**; Codex: **`~/.codex/skills/…`**). Resolve paths with **`scripts/agent_config.py`** (or **`scripts/agent-config.sh`**).

```text
Read fast-grep.env (when set) → host rg/ag/… → agent Grep tool (last literal resort)
First time only: discover → ask install or fast-grep-prefs.sh use/decline → write fast-grep.env
SemanticSearch — behavioral queries only
```

| Task | Resolver / command |
|------|------------------|
| Policy doc | `agent_config.py --literal-search-policy` |
| Helper scripts | `agent_config.py --literal-search-dir` |
| Prefs file | `agent_config.py --fast-grep-env` |
| Prereqs | `check_skill_prereqs.sh literal-search` (under synced `skills/scripts/`) |

- **Cursor (optional):** install **`templates/cursor/rules/literal-code-search.mdc`** with **`./scripts/bootstrap_literal_search.sh --cursor-rule`**
- **Codex / other agents:** rely on synced **`LITERAL-CODE-SEARCH.md`** and investigation skills (no `.mdc` rule)

**OS portability:** literal search follows **Missing CLI tools — ask before fallback** above. Run **`check_skill_prereqs.sh literal-search`** or **`fast-grep-resolve --missing`** (`os=` + **`install_cmd`**). Never assume Homebrew; ask before installing; do not install unless the user explicitly requests it.

In IDE runtimes with Shell available, read **`fast-grep.env`** and use host CLI or **`fast-grep`** before the agent Grep tool. **`repository-technical-analysis`** step 3 owns investigation search workflow.

## GitHub access

Routine GitHub issue and PR fetch uses synced **`GITHUB-ACCESS.md`** at **`$AGENT_CONFIG_HOME/skills/`** (resolve: **`agent_config.py --github-access-policy`**).

```text
GIT-ACCESS.md (repo identity) → gh → gh api → GitHub MCP (last)
Prereqs: check_skill_prereqs.sh github  |  Auth: check_skill_config.sh github → gh auth login
```

| Task | Resolver / command |
|------|------------------|
| Policy doc | `agent_config.py --github-access-policy` |
| **Helper scripts** | `agent_config.py --github-scripts-dir` |
| API doc cache | `agent_config.py --api-docs-dir github-rest` |
| Prereqs | `check_skill_prereqs.sh github` (alias: `github-access`) |
| Auth | `check_skill_config.sh github` |

Workflow skills (**`github-pr-comment-analysis`**, **`github-issue-triage`**, repo overlays) consume normalized context from this policy — they do not duplicate **`gh`** fetch logic.

## Jira access

Routine Jira Cloud issue fetch and update uses synced **`JIRA-ACCESS.md`** at **`$AGENT_CONFIG_HOME/skills/`** (resolve: **`agent_config.py --jira-access-policy`**).

```text
acli jira workitem … → jira-request → jira-api → Jira MCP (last)
Prereqs: check_skill_prereqs.sh jira  |  Auth: check_skill_config.sh jira → acli jira auth login
```

| Task | Resolver / command |
|------|------------------|
| Policy doc | `agent_config.py --jira-access-policy` |
| **Helper scripts** (Phase B) | `agent_config.py --jira-scripts-dir` |
| Atlassian defaults | `agent_config.py --atlassian-env` |
| API doc cache | `agent_config.py --api-docs-dir jira-rest-v3` |
| Prereqs | `check_skill_prereqs.sh jira` (alias: `jira-access`) |
| Auth | `check_skill_config.sh jira` |

The installable **`jira`** skill was removed in Phase C. Workflow skills (**`plan-issues`**, overlays) consume normalized context from this policy — they do not duplicate **`acli`** fetch logic.

Bundled **`jira-api`** / **`jira-request`** use Basic auth (`email:ATLASSIAN_API_TOKEN`). The email must match the token owner; prefer **`acli`** when `git config user.email` differs from the Atlassian account.

## Runtime tool and helper configuration

Host CLIs and bundled helpers often need **auth or defaults files** under **`$AGENT_CONFIG_HOME`** (Cursor: **`~/.cursor/`**; Codex: **`~/.codex/`**). After install checks, run **`scripts/check_skill_config.sh <skill>`** (synced shared file).

**Helper invocation:** run synced **`*.sh`** helpers directly (bash — **do not** prefix with `python3`). Use **`python3`** only for **`*.py`** helpers (`agent_config.py`, `resolve_artifact_path.py`, …).

When config is **missing or incomplete**:

1. **Help the user finish setup** before falling back to MCP or giving up. Give the resolved file path (`agent_config.py --atlassian-env`, `--circleci-env`, …), the variables needed, and vendor doc links for tokens.
2. Use **`templates/*.env.example`** from this repository as scaffolds. Offer to copy the template to the resolved runtime path **only when the user agrees**; let them paste secrets locally.
3. **CLI auth** — guide `gh auth login`, `glab auth login`, and similar when `check_skill_config.sh` reports `NEEDS … auth`.
4. **Bundled helpers** — if shared scripts are missing from **`$AGENT_CONFIG_HOME/skills/scripts/`**, run **`./scripts/sync_skills.sh --all`** from the agent-skills repo (or ask the user to).
5. **Do not read defaults files with the Read tool** to extract tokens unless the user explicitly asked to debug config. Use helper errors and **`check_skill_config.sh`** instead.
6. **Do not commit secrets** to this repository, artifacts, or chat. Prefer export, official credential files, or runtime `*.env` the user controls.
7. After setup, re-run **`check_skill_config.sh`** or a minimal probe (`gh auth status`, `acli jira auth status`, `acli jira workitem view KEY --json`) before continuing the skill workflow.

| Skill / helper | Config / auth |
|----------------|---------------|
| Jira (`JIRA-ACCESS.md`) | **`acli jira auth login`** — see **`JIRA-ACCESS.md`**; optional **`atlassian.env`** for **`jira-request`** fallback |
| `confluence` | **`acli confluence auth login`** first; fallback **`atlassian.env`** — `ATLASSIAN_API_BASE_URL`, `ATLASSIAN_API_TOKEN` (or export / `~/.config/.jira/.credentials`), `git config user.email` |
| `circleci` | **`CIRCLE_TOKEN`** export and/or **`circleci.env`** |
| GitHub (`GITHUB-ACCESS.md`) | **`gh auth login`** — see **`GITHUB-ACCESS.md`** |
| `gitlab`, `git --fetch-id` | **`glab auth login`** |

## Git repository identity

Local remote identity resolution uses synced **`GIT-ACCESS.md`** at **`$AGENT_CONFIG_HOME/skills/`** (resolve: **`agent_config.py --git-access-policy`**).

```text
git CLI + git-repo-identity helper → glab api (--fetch-id) when GitLab numeric ID needed
Prereqs: check_skill_prereqs.sh git-access  |  GitLab ID: check_skill_prereqs.sh gitlab
```

| Task | Resolver / command |
|------|------------------|
| Policy doc | `agent_config.py --git-access-policy` |
| **Helper scripts** | `agent_config.py --git-scripts-dir` |
| Prereqs (git binary) | `check_skill_prereqs.sh git-access` |
| GitLab ID fetch | `check_skill_prereqs.sh gitlab` + `check_skill_config.sh gitlab` |

The installable **`git`** skill was removed in Phase C. **`gitlab`**, **`circleci`**, and **`GITHUB-ACCESS.md`** consume identity from this policy.

Templates: **`templates/atlassian.env.example`**, **`templates/circleci.env.example`**.

## Contributor design principles

Contributor skills (`python-fastapi-contributor`, `cli-contributor`, repo overlays, …) treat **testability** as a primary objective:

- **Dependency injection** — pass collaborators (HTTP clients, clocks, stores, config) via constructors, parameters, or framework hooks (`Depends`, factory args). Avoid reaching for module singletons inside business logic.
- **No hidden globals** — avoid module-level mutable state, import-time side effects, and ambient `process.env` / `os.environ` reads deep in logic. Centralize config at the composition root and inject it.
- **Test seams** — prefer fakes/stubs over broad mocks; new behavior should be provable with a narrow unit or integration test without network, disk, or real time unless the task explicitly needs them.
- **Refactor for injection** — when touching code that uses globals or hard-coded deps, narrow the change but move toward injectable dependencies when the cost is small.
- **`tdd`** owns the red-green-refactor loop; contributor skills own testable structure (DI, no globals).

Repo overlays add language- and stack-specific patterns; this block is the shared default.

## Design rules

- Prefer the smallest implementation and instruction footprint that preserves behavior, safety, compatibility, and validation. Reuse local CLIs, repository helpers, and standard-library features before adding prose, wrappers, dependencies, or remote tool calls.
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

Resolve runtime config paths with **`scripts/agent_config.py`** (synced next to **`scripts/resolve_artifact_path.py`**): **`--atlassian-env`**, **`--circleci-env`**, **`--fast-grep-env`**, **`--skills-root`**, **`--literal-search-dir`**, **`--literal-search-policy`**, **`--github-access-policy`**, **`--gitlab-scripts-dir`**, **`--jira-access-policy`**, **`--config-home`**, **`--runtime`**, **`--defaults-hint atlassian.env`**, **`--api-docs-root`**, or **`--api-docs-dir <slug>`**. Shell equivalent: **`scripts/agent-config.sh`** with the same flags.

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

When the user says **"the artifacts directory"** (or similar), resolve **`$ARTIFACTS/<meaningful_id>/`** via **`scripts/resolve_artifact_path.py`** — not in-repo **`_artifacts_/`** unless they explicitly ask. General technical-analysis reference belongs under **`$KNOWLEDGE/`** (store root). Cross-repo org material belongs under **`$GLOBAL/`**. Read existing files in the target folder before creating duplicates.

- **Cursor (optional):** install **`templates/cursor/rules/agent-artifacts-directory.mdc`** with **`./scripts/bootstrap_agent_artifacts.sh --cursor-rule`**
- **Codex:** this section plus **`ARTIFACTS.md`** carry the same contract (Codex has no `.mdc` rules format)
- **One-time store setup:** **`./scripts/bootstrap_agent_artifacts.sh`** creates **`$AGENT_ARTIFACTS_HOME/README.md`** and scaffolds **`$GLOBAL/NEXT_TIME_CHECKS.md`** when missing

## Learn-daily playbook

Portable lessons split by scope (see **`ARTIFACTS.md`**):

- **`$GLOBAL/NEXT_TIME_CHECKS.md`** — cross-repository next-time checks
- **`$GLOBAL/<topic>/`** — cross-repository reference cards (org maps, team ownership, company tooling)
- **`$KNOWLEDGE/`** — general technical-analysis reference (store root; not under `<repo-key>/`)
- **`$ARTIFACTS/NEXT_TIME_CHECKS.md`** — lessons specific to the active repository
- **`$ARTIFACTS/<meaningful_id>/`** — ticket-scoped work for the active repository

Legacy in-repo **`_artifacts_/`** paths remain valid for read/extend only.

Resolve paths with **`scripts/resolve_artifact_path.py`** (synced to **`~/.cursor/skills/scripts/`** and **`~/.codex/skills/scripts/`**). Use **`--global-artifacts-root`**, **`--knowledge-artifacts-root`**, **`--global-next-time-checks`**, **`--scope global`**, or **`--scope knowledge`** for cross-repo and general-knowledge paths. Override the store root with **`AGENT_ARTIFACTS_HOME`** when needed.

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
