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
