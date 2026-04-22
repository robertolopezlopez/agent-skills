# AGENTS

This repository is the source of truth for Codex skills.

## Skill sync rule

Whenever a top-level skill directory changes or a new skill is created:

1. install or update the matching copied skill in `~/.codex/skills/<skill-name>`
2. keep the installed copy in sync with the repository copy before finishing the task

Whenever a top-level skill directory is deleted:

1. remove the matching installed skill from `~/.codex/skills/<skill-name>`

Treat this sync as part of the required workflow for skill changes in this repository.

## Repository constitution

Use this file as the repo-global policy layer. Prefer putting shared rules here instead of repeating them in every skill.

## Top-level skill directory contract

Each top-level skill directory is expected to be a standalone installed skill.

Required:
- a top-level directory name that becomes the installed skill name
- `SKILL.md` at the root of that directory

Allowed:
- helper scripts
- templates
- references
- assets
- companion docs

Do not assume hidden repo context inside a skill. A copied skill should remain usable after sync into `~/.codex/skills/<skill-name>`.

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

## Design rules

- Keep skills modular. Prefer a small focused skill over a large mixed-purpose skill.
- Separate transport/access skills from workflow/analysis skills when practical.
- Put repo-specific behavior in overlay skills instead of polluting general skills.
- Prefer explicit artifact names, file paths, and command examples.
- Prefer helper scripts and checked-in templates over large repeated prose blocks.
- Use relative paths that still make sense after the skill is copied into `~/.codex/skills/<skill-name>`.

## Validation rule

Before finishing a task that changes any top-level skill directory or shared skill helper:

1. validate the changed skill definitions with the repository skill validator
2. fix validation failures
3. sync the installed copy in `~/.codex/skills`

If a new common rule appears in multiple skills, move it here unless there is a strong reason not to.

## Delegation rule

When a skill describes subagent or parallel-agent behavior:
- define ownership clearly
- avoid overlapping write scopes
- keep non-writer roles read-only unless explicitly required
- require concise result reporting with files changed and validation run

## Backward-compatibility rule

Be careful when renaming a skill directory, changing artifact schemas, or changing referenced helper paths. These changes can break installed copies and downstream workflows. Document the change clearly in the edited skill.
