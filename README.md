# Agent Skills

Custom Codex skills tracked in git.

## Layout

- `python-fastapi-contributor/`: reusable contributor workflow for Python and FastAPI repositories
- `repository-technical-analysis/`: reusable investigation-first workflow for code repositories
- `gitlab/`: generic GitLab merge request fetch and discussion-inspection workflow
- `gitlab-mr-comment-analysis/`: reusable GitLab merge request comment-analysis workflow for any GitLab repository
- `jira/`: generic Jira and Atlassian issue access and update workflow through the Jira REST API
  See `jira/README.md` for setup, auth expectations, and `jira-api` usage.
- `private-service-contributor/`: repo workflow skill for private-service
- `private-service-technical-analysis/`: investigation and analysis skill for private-service
- `private-service-parallel-tests/`: run private-service unit and integration tests with 10 workers
- `private-service-mr-comment-analysis/`: private-service overlay that uses `gitlab-mr-comment-analysis` plus repo-specific technical analysis and proposed changes
- `multi-spawn-agent/`: reusable template for spawning parallel worker agents with disjoint ownership
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
- Use generic skills such as `gitlab`, `jira`, and `repository-technical-analysis` for reusable cross-repo workflows.
- Use overlay skills when you need repository-specific commands, conventions, or analysis depth layered on top of a generic workflow.

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
- finds each top-level directory that contains `SKILL.md`
- removes the matching directory in `~/.codex/skills`
- copies the committed skill directory into `~/.codex/skills`

This keeps this repository as the source of truth while installing real copied directories for Codex discovery.

## Skill Docs

- `jira/README.md`: generic Jira setup, auth expectations, base URL behavior, and `jira-api` examples
- `ARTIFACTS.md`: shared schema, naming, and section order for local workflow artifacts

## Local Defaults Files

Use home-local env files for non-secret skill defaults when a skill documents that behavior.

See the relevant skill `README.md` for the supported variables and precedence rules:

- `jira/README.md`
- `private-service-contributor/README.md`
- `private-service-technical-analysis/README.md`
- `private-service-parallel-tests/README.md`
- `private-service-mr-comment-analysis/README.md`

Do not store secrets such as `ATLASSIAN_API_TOKEN` or `IAC_TOKEN` in these files.

## Shared Artifact Schema

Use `ARTIFACTS.md` as the source of truth for local artifact naming, core headings, and content rules shared by Jira, GitLab, and follow-on analysis workflows.

## Artifact Validation

Use `scripts/validate_artifact.py` to validate local workflow artifacts against the shared schema in `ARTIFACTS.md`.

```bash
python3 scripts/validate_artifact.py task_proj-123.md
```
