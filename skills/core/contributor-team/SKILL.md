---
name: contributor-team
description: Run a lead/developer/reviewer/tester team for one task — design, parallel design review, approval, implementation, parallel audit, bounded fix loop, final summary — with a ponytail-driven reviewer, on Cursor or Codex.
---

# Contributor Team

Fixed-role team workflow from `codex-multi-agent-template`, runtime-independent. The calling agent is **lead**; only **developer** writes files.

## When to Use

Use when the user asks for a team, multi-agent, or lead/reviewer/tester run on one scoped task. Invoking this skill is the authorization to spawn subagents.

## When Not to Use

- Flexible N-worker splits by file ownership — use `multi-spawn-agent`.
- Small tasks a single contributor skill finishes faster than one review round.

## Inputs

- Task statement (required).
- Optional: repo contributor skill to hand the developer (`cli-contributor`, `python-fastapi-contributor`, …), max fix rounds (default 2).

## First Read

Repo `AGENTS.md`; `references/roles.md` (role prompts). Resolve the skills root once (`python3 <skills-root>/scripts/agent_config.py --skills-root`) and pick repo overlays when present: contributor (`cli-contributor`, …), reviewer (`cli-branch-change-reviewer`, …), tests (`cli-parallel-tests`, …); otherwise use the core skills named below. If `ponytail-review` is absent, tell the user how to install the ponytail plugin for the active runtime, do not install, run the reviewer on `branch-change-reviewer` alone, and report the gap.

## Runtime Mapping

| Runtime | Spawn | Read-only enforcement |
|---|---|---|
| Codex, `.codex/config.toml` defines roles `lead`/`developer`/`reviewer`/`tester` | named roles in multi-agent mode | `sandbox_mode = "read-only"` |
| Any runtime with generic subagents (Cursor `Task`, Codex without named roles, …) | one subagent per role, prompt block from `references/roles.md` | prompt rule "do not modify files"; lead checks `git status --porcelain` after each read-only phase |
| No subagent spawning | lead runs each role's block in-thread, sequentially, in phase order | same `git status` check; parallel phases become sequential |

Subagents share no memory and may not auto-discover skills: pass the design text verbatim and absolute `SKILL.md` paths for every skill named in a role block.

## Workflow

1. **Design (lead).** Explore read-only with `repository-technical-analysis`; write a design: scope, acceptance criteria, risks, open questions, files likely touched, with path:line evidence. Keep it under ~40 lines. Use `plan-issues` only when splitting into disjoint developer scopes.
2. **Design review (parallel).** Spawn reviewer (`ponytail-review` ladder: needed at all? exists already? stdlib? one line?) and tester (testability, missing criteria, CI, edge cases). Each returns blocker/warning/nit findings with evidence.
3. **Approve (lead).** Resolve feedback; on material disagreement run the `multi-spawn-agent` Team Sync Pattern in-thread; record the approved design. Nothing is implemented before this step.
4. **Implement (developer).** Spawn developer with the approved design, the contributor skill, `tdd`, and `ponytail`. Developer returns summary, files changed, commands run with exit codes, assumptions. Split into several developers only via `multi-spawn-agent`.
5. **Audit (parallel).** Reviewer runs `branch-change-reviewer` (or its repo overlay) including uncommitted changes, chat output only, plus `ponytail-review` on the diff; tester runs the narrowest documented tests/lint (repo parallel-tests overlay for broad runs) and reports commands, pass/fail, gaps.
6. **Fix loop.** On blockers, developer fixes and reviewer re-reviews, at most `max fix rounds`; then escalate to the user with the open blockers.
7. **Summary (lead).** Changed files, validation run, risks, next steps, plus `ponytail-review` net-lines metric or `Lean already. Ship.`

## Validation

- `git status --porcelain` unchanged after steps 1, 2, 5 (read-only phases).
- Developer-reported commands re-run or spot-checked by tester before the summary.
- Every finding cites a path, line range, or command output.

## Outputs / Artifacts

Final summary in chat. Write `$ARTIFACTS/<meaningful_id>/team-run.md` (path via synced `resolve_artifact_path.py`, per `ARTIFACTS.md`) only when the user asks or the run exceeds one fix round.

## Companion Skills

`repository-technical-analysis`, `branch-change-reviewer`, `ponytail-review`, `ponytail`, `tdd`, repo overlays (contributor, reviewer, parallel-tests), `multi-spawn-agent` for team sync and disjoint developer scopes, `plan-issues` when splitting.

## Safety Notes

- Only developer modifies files; lead reverts nothing and rewrites nothing itself.
- Do not skip phases or start implementation before approval.
- Blockers that change scope or architecture return to the lead, not to the developer.
