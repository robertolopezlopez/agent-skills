# Agent Skills

Custom agent skills tracked in git. They install to **Codex** (`~/.codex/skills`) and **Cursor** (`~/.cursor/skills` for personal agent skills) via `scripts/sync_skills.sh` unless you limit targets with flags or `AGENT_SKILLS_SYNC_TARGETS`.

## Layout

### Core skills

- `skills/core/diagnose/`: focused debugging workflow for concrete bugs, flaky issues, and performance regressions
- `skills/core/github-issue-triage/`: maintainer-facing GitHub issue triage overlay on **`GITHUB-ACCESS.md`**
- `skills/core/plan-issues/`: planning decomposition skill for turning scoped changes into dependency-aware vertical slices
- `skills/core/tdd/`: generic test-first implementation workflow using small vertical slices and red-green-refactor
- `skills/core/python-fastapi-contributor/`: reusable contributor workflow for Python and FastAPI repositories
- `skills/core/repository-technical-analysis/`: reusable investigation-first workflow for code repositories
- `skills/core/gitlab/`: generic GitLab merge request fetch and discussion-inspection workflow
- `skills/core/gitlab-mr-comment-analysis/`: reusable GitLab merge request comment-analysis workflow for any GitLab repository
- `skills/core/github-pr-comment-analysis/`: reusable GitHub pull request comment-analysis workflow (**`GITHUB-ACCESS.md`** + `gh` transport)
- **`JIRA-ACCESS.md`** + **`acli`** for Jira Cloud issue access (resolve policy with **`scripts/agent_config.py --jira-access-policy`**; helpers: **`--jira-scripts-dir`**)
- `skills/core/confluence/`: Confluence Cloud access through authenticated `acli`, Basic-auth REST helper fallback, then MCP
  See `skills/core/confluence/SKILL.md` for transport order and `references/commands.md` for exact commands.
- `skills/core/multi-spawn-agent/`: reusable template for spawning parallel worker agents with disjoint ownership
- `skills/core/prepare-daily-status/`: consolidated local standup and team-status logging
- `skills/core/git-rebase-conflict-resolver/`: rebase and conflict-resolution workflow
- `skills/core/branch-change-reviewer/`: branch review workflow against a target branch

### Guided Experience Service skills

- `skills/guided-experience-service/contributor/`: repo workflow skill for guided-experience-service
- `skills/guided-experience-service/technical-analysis/`: investigation and analysis skill for guided-experience-service
- `skills/guided-experience-service/parallel-tests/`: run guided-experience-service unit and integration tests with 10 workers
- `skills/guided-experience-service/mr-comment-analysis/`: guided-experience-service overlay that uses `gitlab-mr-comment-analysis` plus repo-specific technical analysis and proposed changes

### CLI product skills

Overlays for the **CLI product** source repository (agent- and IDE-agnostic: works with any assistant using these skills). Layer on generic skills the same way guided-experience overlays do.

- `skills/cli/contributor/`: implementation and validation conventions; pnpm, Turbo, and `package.json` script discovery
- `skills/cli/cli-caretaker/`: daily CLI Ask and support-triage workflow
- `skills/cli/branch-change-reviewer/`: read-only branch review overlay combining CLI technical analysis with terse Caveman findings
- `skills/cli/technical-analysis/`: investigation and repro commands for the CLI tree
- `skills/cli/parallel-tests/`: broad suite runs aligned with CI scripts
- `skills/cli/pr-comment-analysis/`: GitHub PR grouped-comment analysis with repo-specific verdicts and proposed changes (`cli-pr-comment-analysis`)

### Other tracked assets

- `codex-multi-agent-template/`: copy-ready multi-agent starter with `.codex/`, `AGENTS.md`, and prompts
- `git-hooks/post-commit`: copies committed skills into the configured install roots, refreshes Cursor rules under `~/.cursor/rules/`, and refreshes managed Codex rule blocks in `~/.codex/AGENTS.md`

The guided-experience-service and **CLI product** (`skills/cli/`) skills are overlays. Use them with the matching generic skills when working in those repositories.
Use **`JIRA-ACCESS.md`** + **`acli`** for Jira Cloud issue access (resolve policy with **`scripts/agent_config.py --jira-access-policy`**).
Use `confluence` for Confluence Cloud wiki access; prefer `acli confluence auth`, then Basic-auth REST helpers, then MCP.
Likewise, `gitlab-mr-comment-analysis` is an overlay on `gitlab`: use `gitlab` for generic MR fetch and discussion inspection, and `gitlab-mr-comment-analysis` for grouped unresolved-comment analysis and reporting.
`github-pr-comment-analysis` is the GitHub analogue: fetch per synced **`GITHUB-ACCESS.md`** (`gh` / `gh api`), then use **`github-pr-comment-analysis`** to group unresolved review threads **inside** `review_pr_<number>.md` or `analysis_pr_<number>.md`.
Use `codex-multi-agent-template/` when you want fixed lead/developer/reviewer/tester scaffolding. Use `multi-spawn-agent` when you want dynamic worker splits driven by a work definition file.

## Philosophy

This repository aims to provide reusable agent workflows (Codex and Cursor) that are:

- **copy-ready when helpful**: ship runnable templates when users need immediate project scaffolding
- **flexible when needed**: keep skill logic reusable across repositories and task shapes
- **evidence-based**: prefer file paths, commands, and concrete artifacts over vague summaries
- **scoped**: encourage focused changes and avoid unrelated refactors
- **parallel where safe**: use fixed roles or dynamic workers when ownership boundaries are clear

## When To Use What

- Use `codex-multi-agent-template/` when you want a fixed project-level starter with `lead`, `developer`, `reviewer`, and `tester`.
- Use `multi-spawn-agent/` when you want dynamic worker counts, explicit file ownership, or non-standard task splits.
- Use generic skills such as `diagnose`, `tdd`, `gitlab`, **`JIRA-ACCESS.md`**, `confluence`, and `repository-technical-analysis` for reusable cross-repo workflows.
- Use synced **`GITHUB-ACCESS.md`** + **`gh`** for GitHub issue and pull-request fetch, inspection, and normalization (`agent_config.py --github-access-policy`).
- Use synced **`GIT-ACCESS.md`** for local repository state, remotes, and repository identity inspection (`agent_config.py --git-access-policy`).
- Use `github-pr-comment-analysis` for grouped unresolved PR review-thread analysis **inside** `review_pr_<number>.md` or `analysis_pr_<number>.md` after PR context has been fetched per **`GITHUB-ACCESS.md`**.
- Use `github-issue-triage` for maintainer-facing GitHub issue classification, missing-info detection, and next-state recommendation after issue context has been fetched.
- Use `repository-technical-analysis` or `diagnose` when GitHub issue triage requires technical evidence before a confident next-state recommendation.
- Use `diagnose` for tight debugging loops with a concrete failing behavior, repro, or regression signal.
- Use `plan-issues` when the scope is already understood and you want to break the work into dependency-aware vertical slices.
- Use `tdd` when the target behavior is already understood and you want to implement or fix it through a test-first red-green-refactor loop.
- Use `multi-spawn-agent` after `plan-issues` when the breakdown is ready for delegated parallel execution.
- Use `repository-technical-analysis` for broader investigation, triage, root-cause framing, and artifact-driven analysis.
- Use `repository-technical-analysis` plus `diagnose` when a broad investigation narrows into a concrete bug that needs disciplined debugging.
- Use `diagnose` plus `tdd` when a concrete bug has been isolated and the fix should be driven by a regression test first.
- Use `plan-issues` plus `tdd` when scoped work should be executed slice-by-slice through a test-first loop.
- Use overlay skills when you need repository-specific commands, conventions, or analysis depth layered on top of a generic workflow.

## Default Multi-Agent Roles

| Role | Access | Responsibility |
|------|--------|----------------|
| `lead` | read-only | Explore the repo, write the design, coordinate work, approve the plan, produce the final summary |
| `developer` | write | Implement the approved design and run validation |
| `reviewer` | read-only | Review correctness, regressions, security, and missing tests |
| `tester` | read-only | Validate coverage, CI readiness, and edge cases |

Only the `developer` writes files in the fixed multi-agent template.

## Standard Workflow Phases

The fixed multi-agent template follows this default flow:

1. `lead` explores the repo and writes the design
2. `reviewer` and `tester` review the design in parallel
3. `lead` approves the final plan
4. `developer` implements the approved design
5. `reviewer` and `tester` audit the implementation in parallel
6. `lead` summarizes what changed, how it was validated, and any remaining risks

Not every task needs all 4 roles. Use `multi-spawn-agent/` instead when a narrower or non-standard split is a better fit.

## Quick Start

For the fastest fixed-role setup in a target project:

```bash
cp -r codex-multi-agent-template/.codex/ my-project/.codex/
cp codex-multi-agent-template/AGENTS.md my-project/
cp -r codex-multi-agent-template/prompts/ my-project/.codex-prompts/  # optional

cd my-project
test -f AGENTS.md && echo "ok: AGENTS.md" || echo "MISSING: AGENTS.md"
test -f .codex/config.toml && echo "ok: config.toml" || echo "MISSING: config.toml"
ls .codex/agents/*.toml
```

Then start Codex in that project and use `prompts/standard-multi-agent-prompt.txt`.

For longer tasks, use `prompts/status-dump.txt` to keep a short shared progress snapshot with current status, evidence, blockers, and next step.

Example status snapshot:

```text
Task: add repo-specific worker split template
Progress: lead done, design approved, developer in progress, reviewer pending, tester pending
Evidence: changed README.md, multi-spawn-agent/SKILL.md
Blockers: none
Next step: developer finishes docs update, then reviewer and tester audit
```

## Install

Copy the tracked hook into the local git hooks directory:

```bash
cp git-hooks/post-commit .git/hooks/post-commit
chmod +x .git/hooks/post-commit
```

Bootstrap the shared artifact schema, path resolver, and validator into each installed skills root so installed skill references and bootstrap validation both work correctly. The usual approach is to run `./scripts/sync_skills.sh --all` from this repository (defaults to both Codex and Cursor); or copy files manually:

```bash
mkdir -p ~/.codex/skills ~/.codex/skills/scripts ~/.cursor/skills ~/.cursor/skills/scripts
cp ARTIFACTS.md ~/.codex/skills/ARTIFACTS.md
cp scripts/resolve_artifact_path.py ~/.codex/skills/scripts/resolve_artifact_path.py
cp scripts/validate_artifact.py ~/.codex/skills/scripts/validate_artifact.py
chmod +x ~/.codex/skills/scripts/resolve_artifact_path.py ~/.codex/skills/scripts/validate_artifact.py
cp ARTIFACTS.md ~/.cursor/skills/ARTIFACTS.md
cp scripts/resolve_artifact_path.py ~/.cursor/skills/scripts/resolve_artifact_path.py
cp scripts/validate_artifact.py ~/.cursor/skills/scripts/validate_artifact.py
chmod +x ~/.cursor/skills/scripts/resolve_artifact_path.py ~/.cursor/skills/scripts/validate_artifact.py
```

Durable workflow artifacts default outside project checkouts under **`$AGENT_ARTIFACTS_HOME/<repo-key>/`** (see **`ARTIFACTS.md`**). Override with **`AGENT_ARTIFACTS_HOME`** when needed.

**One-time machine bootstrap** (after syncing skills):

```bash
./scripts/bootstrap_agent_artifacts.sh --cursor-rule   # Cursor: store README + optional phrase rule
./scripts/bootstrap_agent_artifacts.sh --codex-rule    # Codex: store README + managed global AGENTS.md rule
./scripts/bootstrap_agent_artifacts.sh                   # Codex-only or shared store without Cursor rule
AGENT_ARTIFACTS_HOME=~/Documents/agent-artifacts ./scripts/bootstrap_agent_artifacts.sh   # shared default store
```

Creates **`$AGENT_ARTIFACTS_HOME/README.md`**, scaffolds **`$GLOBAL/NEXT_TIME_CHECKS.md`**, and optionally installs the Cursor rule or its managed Codex `AGENTS.md` equivalent. Idempotent unless **`--overwrite`**.

Environment overrides: `CODEX_HOME` (Codex base), `CURSOR_AGENT_SKILLS_HOME` (parent of `skills/`, default `~/.cursor`), `AGENT_ARTIFACTS_HOME` (external artifact store root), `AGENT_SKILLS_SYNC_TARGETS` (`codex`, `cursor`, or `codex,cursor` / `all`). Use `./scripts/sync_skills.sh --codex-only` or `--cursor-only` for a single destination.

Optional **install filters** (skip copying whole manifest groups or named skills—excluded directories are removed from each sync target if they were installed earlier):

- `AGENT_SKILLS_EXCLUDE_RELEASE_GROUPS` — comma-separated `release_group` values from `skills_manifest.yaml`. Each value drops **every** skill with that `release_group`. Current manifest values:
  - **`core`** — generic cross-repo skills (e.g. **`GITHUB-ACCESS.md`**, **`JIRA-ACCESS.md`**, `gitlab`, `repository-technical-analysis`, `tdd`, …).
  - **`cli`** — CLI product overlays (`cli-contributor`, `cli-technical-analysis`, `cli-parallel-tests`, `cli-pr-comment-analysis`).
  - **`guided-experience-service`** — guided-experience-service overlays (`guided-experience-service-*`).
  
  Examples: `guided-experience-service` only; `guided-experience-service,cli` omits both packs. To list groups and member skills after manifest changes, run: `python3 scripts/skill_manifest.py summary-by-group --group-by release_group`.
- `AGENT_SKILLS_EXCLUDE_SKILL_NAMES` — comma-separated exact manifest `name` entries.

The `post-commit` hook does not set these; export them in your environment or wrap `sync_skills.sh` if you want narrower installs by default. See `scripts/sync_skills.sh` usage for details.

## Multi-Agent Starter Template

To bootstrap a target project with a fixed Codex multi-agent setup:

```bash
cp -r codex-multi-agent-template/.codex/ my-project/.codex/
cp codex-multi-agent-template/AGENTS.md my-project/
cp -r codex-multi-agent-template/prompts/ my-project/.codex-prompts/  # optional
```

Verify the copied files:

```bash
cd my-project
test -f AGENTS.md && echo "ok: AGENTS.md" || echo "MISSING: AGENTS.md"
test -f .codex/config.toml && echo "ok: config.toml" || echo "MISSING: config.toml"
ls .codex/agents/*.toml
```

Why this layout:

- `AGENTS.md` carries shared workflow rules for the whole project
- `.codex/config.toml` registers the roles and multi-agent settings
- `.codex/agents/*.toml` keeps role-specific model and sandbox config close to execution
- `prompts/` provides paste-ready kickoff and status-tracking helpers

For per-role configuration details and template-specific notes, see `codex-multi-agent-template/README.md`.

For larger tasks, the lead can break work into milestones so review and validation can start on completed slices before the entire implementation is finished.

## CLI tools

Host CLIs and bundled helpers used by skills in this repository. **Required** means a skill group fails its prereq check when the tool is missing. **Optional** improves speed or convenience but has fallbacks. **Target repo** tools live in the repository you are working on, not in agent-skills itself.

Agents should run **`check_skill_prereqs.sh`** before relying on a transport or search skill, and **`check_skill_config.sh`** for auth and defaults files. Both scripts print **OS-appropriate** install suggestions (`brew`, `apt`, `dnf`, `pacman`, …) — ask before installing; do not install packages unless the user explicitly asks (see `AGENTS.md`).

### Audit commands

After syncing skills (`./scripts/sync_skills.sh --all`):

```bash
# All skill groups tracked by this repo
./scripts/check_skill_prereqs.sh --all

# One group or skill alias
./scripts/check_skill_prereqs.sh github jira literal-search gmail

# Auth and runtime defaults (after CLIs are on PATH)
./scripts/check_skill_config.sh --all
```

Synced copies: `~/.cursor/skills/scripts/check_skill_prereqs.sh` and `~/.codex/skills/scripts/check_skill_prereqs.sh` (same for `check_skill_config.sh`).

### Runtime helpers (this repo)

| Tool | Role |
|------|------|
| **bash** | Run synced `*.sh` helpers directly — do not prefix with `python3` |
| **python3** | Run synced `*.py` helpers (`agent_config.py`, `resolve_artifact_path.py`, `validate_artifact.py`, …) |
| **git** | Repository identity, diffs, rebases (`GIT-ACCESS.md`, `git-rebase-conflict-resolver`, `branch-change-reviewer`) |

### Transport and access

| Tool | Required | Used by | Auth / config |
|------|----------|---------|----------------|
| **gh** | yes | `GITHUB-ACCESS.md`, `github-pr-comment-analysis`, `github-issue-triage` | `gh auth login` — `check_skill_config.sh github` |
| **glab** | yes | `gitlab`, `gitlab-mr-comment-analysis` | `glab auth login` — `check_skill_config.sh gitlab` |
| **acli** | yes | `JIRA-ACCESS.md`, `confluence` | `acli jira auth login` / `acli confluence auth login` |
| **jq** | optional | Jira, Confluence, investigation JSON filtering | — |
| **circleci** | yes | `circleci` skill | `CIRCLE_TOKEN` / `circleci.env` — `check_skill_config.sh circleci` |

Confluence prefers authenticated **`acli confluence`**, then bundled **`confluence-api`** / **`confluence-request`** Basic-auth helpers, then MCP. See `skills/core/confluence/SKILL.md`.

### Gmail (`GMAIL-ACCESS.md`)

| Tool | Required | Notes |
|------|----------|-------|
| **notmuch** | one of notmuch **or** himalaya | Offline Maildir search; pair with **mbsync** / **isync** to sync mail first |
| **himalaya** | one of notmuch **or** himalaya | Live IMAP CLI; OAuth builds may need `cargo install` with `oauth2,keyring` (see `scripts/gmail/README.md`) |
| **mbsync** | optional | IMAP sync for notmuch workflows |

### Investigation and literal search (`repository-technical-analysis`)

`repository-technical-analysis` and **`LITERAL-CODE-SEARCH.md`** prefer host literal search before the agent Grep tool.

| Tool | Required | Search tier |
|------|----------|-------------|
| **rg** (ripgrep) | recommended | Fastest — preferred when on `PATH` |
| **ugrep** | optional | Fast alternative |
| **ag** (The Silver Searcher) | optional | Moderate |
| **ack** | optional | Moderate |
| **git** + **git grep** | fallback | Scoped search when faster tools are missing |
| **grep** | fallback | POSIX slowest host tier |
| **jq** | optional | JSON filtering during investigation — `check_skill_prereqs.sh investigate` |

Configure preference in **`~/.cursor/fast-grep.env`** or **`~/.codex/fast-grep.env`** (`agent_config.py --fast-grep-env`). Policy: **`agent_config.py --literal-search-policy`**.

### Parallel test skills

| Tool | Required | Used by |
|------|----------|---------|
| **parallel** (GNU parallel) | optional | `cli-parallel-tests`, `guided-experience-service-parallel-tests` — speeds disjoint suite splits; sequential fallback when absent |

### Target-repository tools (not checked by `--all`)

Install and run these **in the repository under investigation**. Use overlay skills for exact commands.

| Stack | Typical CLIs | Overlay skills |
|-------|----------------|----------------|
| **CLI product** | **pnpm**, **node**, repo `package.json` scripts | `cli-contributor`, `cli-technical-analysis`, `cli-parallel-tests` |
| **guided-experience-service** | **uv**, **make**, **pytest** (via `uv run`) | `guided-experience-service-contributor`, `guided-experience-service-technical-analysis` |
| **Python / FastAPI** (generic) | **pytest**, repo lint/format targets | `python-fastapi-contributor` + `repository-technical-analysis` |

Contributor and **tdd** skills have no transport auth — run **`check_skill_prereqs.sh`** in the target repo for project-specific test runners.

### MCP (last resort)

Skills prefer **local CLI → bundled helpers → MCP**. Configure MCP servers (for example Slack, Snyk, Google Gmail) only when host tools are missing or insufficient after prereq checks. Gmail: see **`GMAIL-ACCESS.md`** — no community Gmail MCP repos.

## Verify Local Setup

Verify the shared installed assets:

```bash
test -f ~/.codex/skills/ARTIFACTS.md && echo "ok: installed ARTIFACTS.md (codex)" || echo "MISSING: ~/.codex/skills/ARTIFACTS.md"
test -f ~/.cursor/skills/ARTIFACTS.md && echo "ok: installed ARTIFACTS.md (cursor)" || echo "MISSING: ~/.cursor/skills/ARTIFACTS.md"
test -f ~/.codex/skills/scripts/resolve_artifact_path.py && echo "ok: installed resolver (codex)" || echo "MISSING: ~/.codex/skills/scripts/resolve_artifact_path.py"
test -f ~/.cursor/skills/scripts/resolve_artifact_path.py && echo "ok: installed resolver (cursor)" || echo "MISSING: ~/.cursor/skills/scripts/resolve_artifact_path.py"
test -f ~/.codex/skills/scripts/validate_artifact.py && echo "ok: installed validator (codex)" || echo "MISSING: ~/.codex/skills/scripts/validate_artifact.py"
test -f ~/.cursor/skills/scripts/validate_artifact.py && echo "ok: installed validator (cursor)" || echo "MISSING: ~/.cursor/skills/scripts/validate_artifact.py"
```

Verify an installed copied skill:

```bash
test -f ~/.codex/skills/multi-spawn-agent/SKILL.md && echo "ok: installed multi-spawn-agent (codex)" || echo "MISSING"
test -f ~/.cursor/skills/multi-spawn-agent/SKILL.md && echo "ok: installed multi-spawn-agent (cursor)" || echo "MISSING"
```

Verify the post-commit hook is installed:

```bash
test -x .git/hooks/post-commit && echo "ok: post-commit hook" || echo "MISSING: .git/hooks/post-commit"
```

## Behavior

After each commit in this repository, the installed `post-commit` hook runs `scripts/sync_skills.sh --all` with `AGENT_SKILLS_SYNC_TARGETS=codex,cursor`, then refreshes Cursor and Codex rules. Cursor templates copy from `templates/cursor/rules/*.mdc` to `~/.cursor/rules/`; Codex templates from `templates/codex/rules/*.md` are merged into individually marked blocks in `~/.codex/AGENTS.md`, preserving personal content outside those blocks. Manual runs can still use `--codex-only`, `--cursor-only`, `scripts/sync_cursor_rules.sh`, or `scripts/sync_codex_rules.sh`. Uses `git rev-parse --show-toplevel` so the hook works when `.git/hooks/post-commit` is a symlink.

- copies `ARTIFACTS.md`, `scripts/validate_artifact.py`, and `scripts/atlassian-auth.sh` into each destination skills tree
- reads manifest-declared skill directories from `skills_manifest.yaml`
- replaces each `<skill-name>` directory under both `~/.codex/skills` and `~/.cursor/skills`

This keeps this repository as the source of truth while installing real copied directories for Codex and Cursor agent skill discovery.

Cursor also ships built-in skills under `~/.cursor/skills-cursor/`; this repository only writes your personal manifest skills under `~/.cursor/skills/`.

## Skill Docs

- **`JIRA-ACCESS.md`**: Jira Cloud transport, **`acli`**, synced **`scripts/jira/`** helpers, auth, and bootstrap (see `docs/jira-access-migration.md`)
- `skills/core/confluence/SKILL.md`: Confluence Cloud transport order and auth expectations
- `ARTIFACTS.md`: shared schema, naming, and section order for local workflow artifacts

## Local Defaults Files

Use home-local env files for non-secret skill defaults when a skill documents that behavior.

See the relevant skill reference or policy doc for supported variables and precedence rules:

- **`JIRA-ACCESS.md`** + `templates/atlassian.env.example` (Jira)
- `skills/core/confluence/references/commands.md`
- `skills/guided-experience-service/contributor/README.md`
- `skills/guided-experience-service/technical-analysis/README.md`
- `skills/guided-experience-service/parallel-tests/README.md`
- `skills/guided-experience-service/mr-comment-analysis/README.md`

Do not store secrets such as `ATLASSIAN_API_TOKEN` or `IAC_TOKEN` in these files.

## Shared Artifact Schema

Use `ARTIFACTS.md` as the source of truth for local artifact naming, core headings, and content rules shared by Jira, GitLab, and follow-on analysis workflows.

## Artifact Validation

Use `scripts/validate_artifact.py` to validate local workflow artifacts against the shared schema in `ARTIFACTS.md`.

```bash
python3 scripts/validate_artifact.py task_proj-123.md
```
