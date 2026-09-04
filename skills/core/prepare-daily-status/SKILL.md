---
name: prepare-daily-status
description: Maintain the latest `TEAM_STATUS_DIR` workday entry until explicitly asked to carry it over, then produce share-ready status updates from stated/session evidence.
---

# Prepare Daily Status

Maintain one concise workday status entry until the user explicitly asks to carry it over.

## When to Use

- Prepare or update a standup, daily status, team sync, or EOD report
- Record session outcomes for colleagues
- Carry the latest workday entry into the current local date

## When Not to Use

- Personal journaling or agent lessons; use `learn-daily`
- Sending a message to Slack or email
- Rewriting historical status without an explicit request

## Inputs

- Status facts from the current session or user-provided text
- Optional date or timezone override
- Explicit `carry over` request to start the current local-date entry
- Optional explicit output directory, which overrides `.env` configuration

## Configuration

Read `prepare-daily-status.env` from the active runtime config home:

- `$AGENT_CONFIG_HOME/prepare-daily-status.env` when `AGENT_CONFIG_HOME` is set
- `~/.codex/prepare-daily-status.env` under Codex
- `~/.cursor/prepare-daily-status.env` under Cursor

Accept only this setting:

```dotenv
TEAM_STATUS_DIR=$HOME/Documents/team-status/
```

Expand `$HOME` or `~` in the value without executing the file. If the file or
setting is missing, use `$HOME/Documents/team-status/`. An explicit user path
wins over both. Copy `assets/prepare-daily-status.env.example` to the runtime
config home when the user wants a persistent override; never commit the
customized runtime file.

## Workflow

1. Resolve the status directory using this precedence: explicit user path,
   runtime `.env`, default `$HOME/Documents/team-status/`; create it when missing.
2. Select the target: explicit date first; on explicit `carry over`, current local date; otherwise the latest existing `YYYY-MM-DD.md`, falling back to current local date when none exists.
3. Read the target file. For `carry over`, create the current-date file when absent and copy `In progress`, `In review`, `Blocked / risks`, `Next`, `Needs help / decisions`, and relevant `Links` from the latest entry; do not carry completed bullets or modify the source file.
4. If the target is absent, create this stable scaffold:

   ```markdown
   # Team status — YYYY-MM-DD

   ## YYYY-MM-DD (updates)

   ### Done since last log

   ### In progress

   ### In review

   ### Blocked / risks

   ### Next

   ### Needs help / decisions

   ### Links
   ```

5. Keep exactly one `## YYYY-MM-DD (updates)` section. If a legacy file uses
   same-day `## HH:MM` sections, merge them into the scaffold and remove
   duplicate empty boilerplate.
6. Merge new facts:
   - Append each new `Done since last log` bullet after existing bullets; never
     insert it at the top. Keep local `HH:MM` at the start:
     `- **11:15** — CLI-1667 hotfix done, finished.`
   - Keep active work under `In progress` and submitted work under `In review`.
   - Update blockers, next steps, decisions, and links only from stated facts.
   - Keep every bullet to one short fact or action. Leave empty subsections empty.
   - Avoid duplicate bullets and multiple same-day status sections.
7. Return the consolidated status section for review or sharing.

## Validation

- Without `carry over` or an explicit date, the latest existing workday file is updated and no new dated file is created.
- `carry over` targets the current local date, preserves the source, and carries only unfinished work and relevant links.
- File date, title, and updates heading match the selected target date.
- All seven subsection names remain exact and appear once.
- No same-day `## HH:MM` sibling sections remain.
- Every logged fact is supported by this session or explicit user input.
- New `Done since last log` bullets appear after existing bullets.

## Outputs / Artifacts

- Updated selected `<status-directory>/YYYY-MM-DD.md`
- Consolidated status shown on screen

## Companion Skills

- `learn-daily` only for reusable agent lessons; do not mix those into team
  status.

## Safety Notes

- Never log tokens, passwords, customer secrets, or sensitive internal data.
- Update only the selected entry; `carry over` never deletes or rewrites its source.
- If no concrete outcome exists, record `No concrete engineering outcomes
  captured this session` instead of inventing work.
- Ignore unknown `.env` keys and never execute `.env` contents as shell code.
- Request filesystem approval when the runtime cannot write the resolved
  directory.
