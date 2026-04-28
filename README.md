# Agent Skills

Custom Codex skills tracked in git.

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
- `skills/core/jira/`: generic Jira and Atlassian issue access and update workflow through the Jira REST API
  See `skills/core/jira/README.md` for setup, auth expectations, and `jira-api` usage.
- `skills/core/multi-spawn-agent/`: reusable template for spawning parallel worker agents with disjoint ownership
- `skills/core/git/`: local Git repository inspection and remote metadata helper
- `skills/core/git-rebase-conflict-resolver/`: rebase and conflict-resolution workflow
- `skills/core/branch-change-reviewer/`: branch review workflow against a target branch

### Guided Experience Service skills

- `skills/private-service/contributor/`: repo workflow skill for private-service
- `skills/private-service/technical-analysis/`: investigation and analysis skill for private-service
- `skills/private-service/parallel-tests/`: run private-service unit and integration tests with 10 workers
- `skills/private-service/mr-comment-analysis/`: private-service overlay that uses `gitlab-mr-comment-analysis` plus repo-specific technical analysis and proposed changes

### Other tracked assets

- `codex-multi-agent-template/`: copy-ready multi-agent starter with `.codex/`, `AGENTS.md`, and prompts
- `git-hooks/post-commit`: copies committed skills into `~/.codex/skills`

The private-service skills are overlays. Use them with the matching generic skills when working in that repository.
Use `jira` for generic Atlassian/Jira access, including site-specific Jira usage when `~/.codex/jira.env` sets `ATLASSIAN_API_BASE_URL=https://example.atlassian.net`.
Likewise, `gitlab-mr-comment-analysis` is an overlay on `gitlab`: use `gitlab` for generic MR fetch and discussion inspection, and `gitlab-mr-comment-analysis` for grouped unresolved-comment analysis and reporting.
Use `codex-multi-agent-template/` when you want fixed lead/developer/reviewer/tester scaffolding. Use `multi-spawn-agent` when you want dynamic worker splits driven by a work definition file.

## Philosophy

This repository aims to provide reusable Codex workflows that are:

- **copy-ready when helpful**: ship runnable templates when users need immediate project scaffolding
- **flexible when needed**: keep skill logic reusable across repositories and task shapes
- **evidence-based**: prefer file paths, commands, and concrete artifacts over vague summaries
- **scoped**: encourage focused changes and avoid unrelated refactors
- **parallel where safe**: use fixed roles or dynamic workers when ownership boundaries are clear

## When To Use What

- Use `codex-multi-agent-template/` when you want a fixed project-level starter with `lead`, `developer`, `reviewer`, and `tester`.
- Use `multi-spawn-agent/` when you want dynamic worker counts, explicit file ownership, or non-standard task splits.
- Use generic skills such as `diagnose`, `github`, `tdd`, `gitlab`, `jira`, and `repository-technical-analysis` for reusable cross-repo workflows.
- Use `git` for local repository state, remotes, and repository identity inspection.
- Use `github` for GitHub issue and pull-request fetch, inspection, and normalization.
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

Bootstrap the shared artifact schema and validator into the installed skills root so installed skill references and bootstrap validation both work correctly:

```bash
mkdir -p ~/.codex/skills ~/.codex/skills/scripts
cp ARTIFACTS.md ~/.codex/skills/ARTIFACTS.md
cp scripts/validate_artifact.py ~/.codex/skills/scripts/validate_artifact.py
chmod +x ~/.codex/skills/scripts/validate_artifact.py
```

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
test -f ~/.codex/skills/ARTIFACTS.md && echo "ok: installed ARTIFACTS.md" || echo "MISSING: ~/.codex/skills/ARTIFACTS.md"
test -f ~/.codex/skills/scripts/validate_artifact.py && echo "ok: installed validator" || echo "MISSING: ~/.codex/skills/scripts/validate_artifact.py"
```

Verify an installed copied skill:

```bash
test -f ~/.codex/skills/multi-spawn-agent/SKILL.md && echo "ok: installed multi-spawn-agent" || echo "MISSING: ~/.codex/skills/multi-spawn-agent/SKILL.md"
```

Verify the post-commit hook is installed:

```bash
test -x .git/hooks/post-commit && echo "ok: post-commit hook" || echo "MISSING: .git/hooks/post-commit"
```

## Behavior

After each commit in this repository, the `post-commit` hook:

- copies `ARTIFACTS.md` to `~/.codex/skills/ARTIFACTS.md`
- copies `scripts/validate_artifact.py` to `~/.codex/skills/scripts/validate_artifact.py`
- reads manifest-declared skill directories from `skills_manifest.yaml`
- removes the matching installed directory in `~/.codex/skills`
- copies the declared skill directory into `~/.codex/skills/<skill-name>`

This keeps this repository as the source of truth while installing real copied directories for Codex discovery.

## Skill Docs

- `skills/core/jira/README.md`: generic Jira setup, auth expectations, base URL behavior, and `jira-api` examples
- `ARTIFACTS.md`: shared schema, naming, and section order for local workflow artifacts

## Local Defaults Files

Use home-local env files for non-secret skill defaults when a skill documents that behavior.

See the relevant skill `README.md` for the supported variables and precedence rules:

- `skills/core/jira/README.md`
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
