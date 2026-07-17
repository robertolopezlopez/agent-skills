---
name: prepare-daily-status
description: Maintain a consolidated daily team status log under configurable `TEAM_STATUS_DIR` and return a share-ready update. Load the directory from the runtime `prepare-daily-status.env` file, defaulting to `$HOME/Documents/team-status/`. Use when the user mentions standup, daily status, team sync, EOD, progress for colleagues, or asks to log, prepare, append, or update team status. Use only session evidence or work the user explicitly states.
---

# Prepare Daily Status

Maintain one concise team-status file per local calendar day.

## When to Use

- Prepare or update a standup, daily status, team sync, or EOD report
- Record session outcomes for colleagues

## When Not to Use

- Personal journaling or agent lessons; use `learn-daily`
- Sending a message to Slack or email
- Rewriting historical status without an explicit request

## Inputs

- Status facts from the current session or user-provided text
- Optional date or timezone override; otherwise use local date and time
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
   runtime `.env`, default `$HOME/Documents/team-status/`. Resolve local date
   and time, then use `<status-directory>/YYYY-MM-DD.md`; create the directory
   when missing.
2. Read today’s file before editing it.
3. If absent, create this stable scaffold:

   ```markdown
   # Team status — YYYY-MM-DD

   ## YYYY-MM-DD (updates)

   ### Done since last log
   None.

   ### In progress
   None.

   ### In review
   None.

   ### Blocked / risks
   None.

   ### Next
   None.

   ### Needs help / decisions
   None.

   ### Links
   None.
   ```

4. Keep exactly one `## YYYY-MM-DD (updates)` section. If a legacy file uses
   same-day `## HH:MM` sections, merge them into the scaffold and remove
   duplicate empty boilerplate.
5. Merge new facts:
   - Append each new `Done since last log` bullet after existing bullets; never
     insert it at the top. Keep local `HH:MM` at the start:
     `- **11:15** — CLI-1667 hotfix done, finished.`
   - Keep active work under `In progress` and submitted work under `In review`.
   - Update blockers, next steps, decisions, and links only from stated facts.
   - Remove `None.` when adding content; restore it when a subsection becomes
     empty.
   - Avoid duplicate bullets and multiple same-day status sections.
6. Return the consolidated status section for review or sharing.

## Validation

- File date, title, and updates heading use the selected local date.
- All seven subsection names remain exact and appear once.
- No same-day `## HH:MM` sibling sections remain.
- Every logged fact is supported by this session or explicit user input.
- New `Done since last log` bullets appear after existing bullets.

## Outputs / Artifacts

- Updated `<status-directory>/YYYY-MM-DD.md`
- Consolidated status shown on screen

## Companion Skills

- `learn-daily` only for reusable agent lessons; do not mix those into team
  status.

## Safety Notes

- Never log tokens, passwords, customer secrets, or sensitive internal data.
- Do not delete or rewrite earlier days unless the user explicitly asks.
- If no concrete outcome exists, record `No concrete engineering outcomes
  captured this session` instead of inventing work.
- Ignore unknown `.env` keys and never execute `.env` contents as shell code.
- Request filesystem approval when the runtime cannot write the resolved
  directory.
