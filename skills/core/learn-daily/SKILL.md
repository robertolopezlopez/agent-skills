---
name: learn-daily
description: >-
  Streamline repeatable daily agent habits (learn daily): session start (repo guidance + consolidated
  next-time checks), disciplined artifact placement under $ARTIFACTS/<meaningful_id>/ (repo-scoped)
  or $GLOBAL/<meaningful_id>/ (cross-repo knowledge), and session end capture into
  $GLOBAL/NEXT_TIME_CHECKS.md and/or $ARTIFACTS/NEXT_TIME_CHECKS.md. Use when starting or closing focused work in a codebase, when the user asks for a daily
  routine, or to avoid re-learning the same friction every session.
---

# Learn Daily

Use this skill in **any repository root** where Cursor or Codex runs multi-step work and you want light structure without a heavy template.

It does **not** fetch GitHub, GitLab, Jira, or CI; it only shapes **local** habits and paths.

## When to Use

Use this skill when:

- the user asks for a **daily rhythm**, **learn daily**, **start/end checklist**, or fewer manual steps across sessions
- kicking off a session and you should **load durable repo guidance** before coding or analyzing
- winding down a session and should **capture reusable lessons** without opening five files ad hoc
- aligning with repo conventions in shipped `ARTIFACTS.md` (`$ARTIFACTS/` layout and basenames)
- the user asks to **bootstrap** `$ARTIFACTS/NEXT_TIME_CHECKS.md` (first-time setup steps 1–2 below)

## When Not to Use

Do not use this skill when:

- the task is purely transport or API access (**`GITHUB-ACCESS.md`**, **`JIRA-ACCESS.md`**, `gitlab`, …)
- the user only wants deep investigation or implementation (use `repository-technical-analysis`, overlays, or `tdd`)
- the user has explicitly opted out of the external artifact store and legacy in-repo paths

## Inputs

Accept:

- optional **meaningful_id** for the current thread (issue key, `pr-<n>`, `mr-<iid>`, branch slug—per `ARTIFACTS.md` precedence and repo `AGENTS.md`)
- optional path override if the team keeps next-time checks elsewhere (prefer pointing `AGENTS.md` at the canonical file instead)

Resolve paths per **`ARTIFACTS.md`**:

- **`$GLOBAL/`** — **`$AGENT_ARTIFACTS_HOME/_global/`** (cross-repo knowledge)
- **`$ARTIFACTS/`** — **`$AGENT_ARTIFACTS_HOME/<repo-key>/`** (active repository)

Use **`scripts/resolve_artifact_path.py`** when you need absolute paths (`--global-artifacts-root`, `--global-next-time-checks`, `--scope global`, or repo-scoped flags).

### Scope routing

| Write here | When |
| --- | --- |
| **`$GLOBAL/<topic>/`** | Org structure, team ownership, company tooling, facts true in any checkout |
| **`$GLOBAL/NEXT_TIME_CHECKS.md`** | Recurring lessons that apply across repositories |
| **`$ARTIFACTS/<meaningful_id>/`** | Ticket, PR, MR, branch review, or repo-specific investigation |
| **`$ARTIFACTS/NEXT_TIME_CHECKS.md`** | Recurring lessons **only** for the active repository |

If a repo-scoped bullet would help in every checkout, **promote** it to **`$GLOBAL/NEXT_TIME_CHECKS.md`** and remove the duplicate from the repo file.

## First Read

Before substantive work:

1. Read **`AGENTS.md`** when present (and `README` / contributor docs if `AGENTS.md` defers to them).
2. Read **`ARTIFACTS.md`** in the active skills install root when artifact naming or section order matters (synced copy next to skills; repo may also carry a link or mirror).
3. If **`$GLOBAL/NEXT_TIME_CHECKS.md`** exists, read it and skim section headers relevant to today’s task.
4. If **`$ARTIFACTS/NEXT_TIME_CHECKS.md`** exists, read it and skim section headers relevant to today’s task. If only a legacy in-repo **`_artifacts_/NEXT_TIME_CHECKS.md`** exists, read that instead.
5. When the task involves org-wide facts (team ownership, internal URLs, auth defaults), check **`$GLOBAL/<topic>/`** before re-researching.
6. If the user already has a ticket-scoped artifact under **`$ARTIFACTS/<meaningful_id>/`** (or legacy in-repo **`_artifacts_/…`**), open it before duplicating context.

## Workflow

### Bootstrap `$ARTIFACTS/NEXT_TIME_CHECKS.md` (once per repo)

Run when the user wants the playbook but it is missing, or **`AGENTS.md`** does not point agents at it:

0. **Bootstrap the external store (once per machine)** — from the agent-skills repository run **`./scripts/bootstrap_agent_artifacts.sh`** (add **`--cursor-rule`** on Cursor for the "artifacts directory" phrase). Creates **`$AGENT_ARTIFACTS_HOME/README.md`** and **`$GLOBAL/NEXT_TIME_CHECKS.md`** when absent. Set **`AGENT_ARTIFACTS_HOME`** first when Cursor and Codex should share one store.
1. **Create the playbook file** — Resolve **`$ARTIFACTS/`** for the active repository (see **`ARTIFACTS.md`**). Create **`$ARTIFACTS/NEXT_TIME_CHECKS.md`**. Start with stable scaffold only:
   - `# Next-time checks`
   - `## How to use` — one short paragraph: agents read at **session start** (with **Learn Daily**); humans **prune** stale bullets periodically; bullets stay **compressed** and carry a **`(source: …)`** tag (ticket, PR path, etc.).
   - Optional empty `## Patterns` or similar section headers where the repo expects grouping (subsystem, tooling, CI).
2. **Register the canonical path for agents** — If **`AGENTS.md`** exists in the **project** repository, add **one unmistakable sentence** naming the external **`$ARTIFACTS/NEXT_TIME_CHECKS.md`** path (or how to resolve it via **`AGENT_ARTIFACTS_HOME`**) as where portable next-time lessons live. Avoid duplicating the whole playbook inline in the project repo.

Do **not** create new durable playbooks under in-repo **`_artifacts_/`** unless the user explicitly opts in; that location is legacy and vulnerable to **`git clean`**.

### After bootstrap (remaining steps checklist)

Treat these as hygiene after 1–2 exist:

- **Operate the loop:** ticket detail under **`$ARTIFACTS/<meaningful_id>/`**; cross-repo reference cards under **`$GLOBAL/<topic>/`**; recurring cross-repo lines to **`$GLOBAL/NEXT_TIME_CHECKS.md`**; repo-only lines to **`$ARTIFACTS/NEXT_TIME_CHECKS.md`**.
- **Resolve store location explicitly** — default **`AGENT_ARTIFACTS_HOME`**; confirm with **`resolve_artifact_path.py --repo-artifacts-root`** when paths are unclear.
- Optional store index: **`$AGENT_ARTIFACTS_HOME/README.md`** (from **`bootstrap_agent_artifacts.sh`**)
- **Periodic purge:** merge duplicates, delete stale bullets; **promote** twice-seen patterns to project **`AGENTS.md`** or project rules.
- **Tune this skill:** after the habit proves stable on a repo, move repo quirks into project **`AGENTS.md`** and keep SKILL generic.

### Session start (short)

1. Confirm repository root (or the root the user chose for this work).
2. Load project `AGENTS.md`, **`$GLOBAL/NEXT_TIME_CHECKS.md`**, and **`$ARTIFACTS/NEXT_TIME_CHECKS.md`** when present (legacy in-repo copy if that is all that exists).
3. Pick **`meaningful_id`** for new files; if unclear, ask once or use the best heuristic from `ARTIFACTS.md` / `AGENTS.md`.
4. Prefer **one** working artifact path for this thread under **`$ARTIFACTS/<meaningful_id>/`** instead of scattering new Markdown at repo root or inside the checkout.

### During work

- Write or extend analysis, review, or task notes under **`$ARTIFACTS/<meaningful_id>/`** per `ARTIFACTS.md`.
- Write cross-repo reference material under **`$GLOBAL/<topic>/`** (same Markdown schema; no `# Repository` section required when the fact is not tied to one checkout).
- When you learn something that would help **future unrelated** tickets, note it as a candidate for the appropriate **`NEXT_TIME_CHECKS`** file (global vs repo — see scope routing).

### Session end (short)

1. Add **0–3** bullets to **`$GLOBAL/NEXT_TIME_CHECKS.md`** when the lesson applies in **any** repository; add repo-only bullets to **`$ARTIFACTS/NEXT_TIME_CHECKS.md`**. Each bullet should include a **source** tag (issue id, PR, or path to the reference artifact).
2. For **ticket-specific** nuance, append to the ticket artifact’s durable sections instead of the global playbook.
3. For **cross-repo reference** detail (org maps, ownership tables, long evidence), write or update **`$GLOBAL/<topic>/`** — do not bury it under a repo-key path.
4. If a playbook does not exist and the user wants this habit, perform **Bootstrap** (repo **`$ARTIFACTS/NEXT_TIME_CHECKS.md`** and/or global **`$GLOBAL/NEXT_TIME_CHECKS.md`**) instead of improvising headings ad hoc.
5. Do **not** bulk-copy whole artifacts into `NEXT_TIME_CHECKS.md`; **compress** to imperative checks.

## Validation

- After updates, ensure paths are valid Markdown and **`NEXT_TIME_CHECKS.md`** filenames stay stable under **`$GLOBAL/`** and **`$ARTIFACTS/`**.
- Confirm repo-scoped durable files land under **`$ARTIFACTS/`** and cross-repo reference material under **`$GLOBAL/`**, not inside the project git checkout, unless the user chose a legacy in-repo path.

## Outputs / Artifacts

This skill should result in:

- read/follow guidance from project `AGENTS.md`, optional **`$GLOBAL/NEXT_TIME_CHECKS.md`**, and optional **`$ARTIFACTS/NEXT_TIME_CHECKS.md`**
- new or updated files under **`$GLOBAL/<topic>/`** for cross-repo knowledge
- new or updated files under **`$ARTIFACTS/<meaningful_id>/`** when work produced repo-scoped context
- optional updates to **`$GLOBAL/NEXT_TIME_CHECKS.md`** and/or **`$ARTIFACTS/NEXT_TIME_CHECKS.md`** (compressed, sourced bullets)
- **on bootstrap:** scaffolded playbooks under **`$GLOBAL/`** and/or **`$ARTIFACTS/`**, plus a single project **`AGENTS.md`** sentence when missing

## Companion Skills

- Workflow and analysis skills (`repository-technical-analysis`, PR/MR comment analysis, overlays) **consume** paths this skill helps standardize; invoke them after the start sequence when the task requires them.
- `plan-issues` when the user wants execution slicing after scope is clear.

## Safety Notes

- Never store secrets in `NEXT_TIME_CHECKS.md` or ticket artifacts; reference **where** to load them.
- This skill does not replace code review, tests, or transport skills.
- Keep `NEXT_TIME_CHECKS.md` **short**; archive or delete bullets that no longer apply.
- External storage avoids **`git clean`** data loss and accidental push of agent working notes.

## Self-Improving Behavior

When the same bullet would be copied a second time, prefer **tightening one line** in the appropriate **`NEXT_TIME_CHECKS.md`** (global vs repo) or promoting the pattern to project **`AGENTS.md`** / project rules if it is repo-wide.
