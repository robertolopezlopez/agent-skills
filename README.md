# Agent Skills

Custom agent skills tracked in git. They install to **Codex** (`~/.codex/skills`) and **Cursor** (`~/.cursor/skills` for personal agent skills) via `scripts/sync_skills.sh` unless you limit targets with flags or `AGENT_SKILLS_SYNC_TARGETS`.

## Layout

### Core skills

- `skills/core/diagnose/`: focused debugging workflow for concrete bugs, flaky issues, and performance regressions
- `skills/core/github/`: GitHub transport and normalization workflow for issues and pull requests
- `skills/core/github-issue-triage/`: maintainer-facing GitHub issue triage overlay built on top of `github`
- `skills/core/plan-issues/`: planning decomposition skill for turning scoped changes into dependency-aware vertical slices
- `skills/core/tdd/`: generic test-first implementation workflow using small vertical slices and red-green-refactor
- `skills/core/python-fastapi-contributor/`: reusable contributor workflow for Python and FastAPI repositories
- `skills/core/repository-technical-analysis/`: reusable investigation-first workflow for code repositories
- `skills/core/gitlab/`: generic GitLab merge request fetch and discussion-inspection workflow
- `skills/core/gitlab-mr-comment-analysis/`: reusable GitLab merge request comment-analysis workflow for any GitLab repository
- `skills/core/github-pr-comment-analysis/`: reusable GitHub pull request comment-analysis workflow for any GitHub repository (`github` transport)
- `skills/core/jira/`: generic Jira and Atlassian issue access and update workflow through the Jira REST API
  See `skills/core/jira/README.md` for setup, auth expectations, and `jira-api` usage.
- `skills/core/confluence/`: generic Confluence Cloud wiki access and updates through the Confluence REST API
  See `skills/core/confluence/README.md` for `atlassian.env` defaults shared with **`jira`**, auth expectations, and helper usage.
- `skills/core/multi-spawn-agent/`: reusable template for spawning parallel worker agents with disjoint ownership
- `skills/core/git/`: local Git repository inspection and remote metadata helper
- `skills/core/git-rebase-conflict-resolver/`: rebase and conflict-resolution workflow
- `skills/core/branch-change-reviewer/`: branch review workflow against a target branch

### Guided Experience Service skills

- `skills/private-service/contributor/`: repo workflow skill for private-service
- `skills/private-service/technical-analysis/`: investigation and analysis skill for private-service
- `skills/private-service/parallel-tests/`: run private-service unit and integration tests with 10 workers
- `skills/private-service/mr-comment-analysis/`: private-service overlay that uses `gitlab-mr-comment-analysis` plus repo-specific technical analysis and proposed changes

### CLI product skills

Overlays for the **CLI product** source repository (agent- and IDE-agnostic: works with any assistant using these skills). Layer on generic skills the same way guided-experience overlays do.

- `skills/cli/contributor/`: implementation and validation conventions; pnpm, Turbo, and `package.json` script discovery
- `skills/cli/technical-analysis/`: investigation and repro commands for the CLI tree
- `skills/cli/parallel-tests/`: broad suite runs aligned with CI scripts
- `skills/cli/pr-comment-analysis/`: GitHub PR grouped-comment analysis with repo-specific verdicts and proposed changes (`private-pr-comment-analysis`)

### Other tracked assets

- `codex-multi-agent-template/`: copy-ready multi-agent starter with `.codex/`, `AGENTS.md`, and prompts
- `git-hooks/post-commit`: copies committed skills into the configured install roots (default: `~/.codex/skills` and `~/.cursor/skills`)

The private-service and **CLI product** (`skills/cli/`) skills are overlays. Use them with the matching generic skills when working in those repositories.
Use `jira` for generic Atlassian/Jira access, including site-specific Jira usage when **`~/.cursor/atlassian.env`** or **`~/.codex/atlassian.env`** sets `ATLASSIAN_API_BASE_URL=https://example.atlassian.net`.
Use `confluence` for Confluence Cloud wiki access when **`~/.cursor/atlassian.env`** or **`~/.codex/atlassian.env`** sets the same variables (see `skills/core/confluence/README.md`).
Likewise, `gitlab-mr-comment-analysis` is an overlay on `gitlab`: use `gitlab` for generic MR fetch and discussion inspection, and `gitlab-mr-comment-analysis` for grouped unresolved-comment analysis and reporting.
`github-pr-comment-analysis` is the GitHub analogue on top of `github`: use `github` for PR fetch and thread normalization, and `github-pr-comment-analysis` to group unresolved review threads **inside** `review_pr_<number>.md` or `analysis_pr_<number>.md`.
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
- Use generic skills such as `diagnose`, `github`, `tdd`, `gitlab`, `jira`, `confluence`, and `repository-technical-analysis` for reusable cross-repo workflows.
- Use `git` for local repository state, remotes, and repository identity inspection.
- Use `github` for GitHub issue and pull-request fetch, inspection, and normalization.
- Use `github-pr-comment-analysis` for grouped unresolved PR review-thread analysis **inside** `review_pr_<number>.md` or `analysis_pr_<number>.md` after PR context has been fetched or normalized via `github`.
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

Environment overrides: `CODEX_HOME` (Codex base), `CURSOR_AGENT_SKILLS_HOME` (parent of `skills/`, default `~/.cursor`), `AGENT_ARTIFACTS_HOME` (external artifact store root), `AGENT_SKILLS_SYNC_TARGETS` (`codex`, `cursor`, or `codex,cursor` / `all`). Use `./scripts/sync_skills.sh --codex-only` or `--cursor-only` for a single destination.

Optional **install filters** (skip copying whole manifest groups or named skills—excluded directories are removed from each sync target if they were installed earlier):

- `AGENT_SKILLS_EXCLUDE_RELEASE_GROUPS` — comma-separated `release_group` values from `skills_manifest.yaml`. Each value drops **every** skill with that `release_group`. Current manifest values:
  - **`core`** — generic cross-repo skills (e.g. `github`, `gitlab`, `jira`, `repository-technical-analysis`, `tdd`, …).
  - **`cli`** — CLI product overlays (`private-contributor`, `private-technical-analysis`, `private-parallel-tests`, `private-pr-comment-analysis`).
  - **`private-service`** — private-service overlays (`private-service-*`).
  
  Examples: `private-service` only; `private-service,cli` omits both packs. To list groups and member skills after manifest changes, run: `python3 scripts/skill_manifest.py summary-by-group --group-by release_group`.
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

After each commit in this repository, the installed `post-commit` hook runs `scripts/sync_skills.sh --all` with `AGENT_SKILLS_SYNC_TARGETS=codex,cursor`, so **both** Codex and Cursor install roots are updated on every commit. Manual runs can still use `--codex-only`, `--cursor-only`, or a custom `AGENT_SKILLS_SYNC_TARGETS`. Uses `git rev-parse --show-toplevel` so the hook works when `.git/hooks/post-commit` is a symlink.

- copies `ARTIFACTS.md`, `scripts/validate_artifact.py`, and `scripts/atlassian-auth.sh` into each destination skills tree
- reads manifest-declared skill directories from `skills_manifest.yaml`
- replaces each `<skill-name>` directory under both `~/.codex/skills` and `~/.cursor/skills`

This keeps this repository as the source of truth while installing real copied directories for Codex and Cursor agent skill discovery.

Cursor also ships built-in skills under `~/.cursor/skills-cursor/`; this repository only writes your personal manifest skills under `~/.cursor/skills/`.

## Skill Docs

- `skills/core/jira/README.md`: generic Jira setup, auth expectations, base URL behavior, and `jira-api` examples
- `skills/core/confluence/README.md`: Confluence Cloud setup via **`atlassian.env`**, auth expectations, and REST helpers
- `ARTIFACTS.md`: shared schema, naming, and section order for local workflow artifacts

## Local Defaults Files

Use home-local env files for non-secret skill defaults when a skill documents that behavior.

See the relevant skill `README.md` for the supported variables and precedence rules:

- `skills/core/jira/README.md`
- `skills/core/confluence/README.md`
- `skills/private-service/contributor/README.md`
- `skills/private-service/technical-analysis/README.md`
- `skills/private-service/parallel-tests/README.md`
- `skills/private-service/mr-comment-analysis/README.md`

Do not store secrets such as `ATLASSIAN_API_TOKEN` or `IAC_TOKEN` in these files.

## Shared Artifact Schema

Use `ARTIFACTS.md` as the source of truth for local artifact naming, core headings, and content rules shared by Jira, GitLab, and follow-on analysis workflows.

## Artifact Validation

Use `scripts/validate_artifact.py` to validate local workflow artifacts against the shared schema in `ARTIFACTS.md`.

```bash
python3 scripts/validate_artifact.py task_proj-123.md
```
