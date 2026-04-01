# AGENTS

## Skill sync rule

This repository is the source of truth for skills.

Whenever a top-level skill directory changes or a new skill is created:

1. install or update the matching copied skill in `~/.codex/skills/<skill-name>`
2. keep the installed copy in sync with the repository copy before finishing the task

Whenever a top-level skill directory is deleted:

1. remove the matching installed skill from `~/.codex/skills/<skill-name>`

Treat this sync as part of the required workflow for skill changes in this repository.
