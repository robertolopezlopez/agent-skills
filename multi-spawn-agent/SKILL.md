---
name: multi-spawn-agent
description: Use when the user explicitly asks for subagents, delegation, or parallel agent work and you want a reusable template for spawning multiple worker agents from a work definition file. Best for parallel implementation or validation tasks where each worker should use named skills, read a shared work definition or plan file, own specific files or directories, avoid overlapping write scopes, and return a summary, files changed, and validation.
---

# Multi Spawn Agent

Use this skill to structure parallel worker delegation after the user has explicitly authorized subagents.

If the user wants a reusable project-level starter instead of ad hoc delegation only, pair this skill with the shipped template in `codex-multi-agent-template/`.

## When to Use

Use this skill when the user has explicitly authorized subagents and wants:

- parallel implementation with disjoint write scopes
- parallel validation with bounded ownership
- work-definition-driven worker splits
- a reusable worker prompt structure for multiple tasks

## When Not to Use

Do not use this skill when:

- the user has not explicitly authorized subagents or parallel agent work
- the next step is blocked on a small urgent task better handled locally
- write scopes overlap heavily and would create merge churn
- a fixed starter layout from `codex-multi-agent-template/` is a better fit than dynamic worker splitting

## Inputs

Require a work definition file path as the primary input. This can be a plan or work-split document such as:

```text
work_plan.md
```

Use that file as the shared source of truth for worker scopes, ownership, constraints, and integration order.

## Validation

- Verify the work definition gives each worker a clear owner and disjoint write scope before spawning.
- Prefer fewer workers when tasks are tightly coupled or integration cost is high.
- Review returned worker changes before integrating them.
- Require each worker to report summary, files changed, and validation run.

## Workflow

1. Read the work definition file first and extract:
   - worker split
   - file or directory ownership
   - non-goals and constraints
   - dependency or integration order
2. Make a local plan from that file and identify tasks that are safe to run in parallel.
3. Spawn only **worker** agents for bounded tasks with disjoint write scopes.
4. Use `fork_context: true`.
5. For each worker:
   - explicitly mention the required skill names
   - tell the worker to read the shared work definition file
   - assign exact file or directory ownership
   - define explicit write scope and expected output files when possible
   - tell the worker which files to avoid when useful
   - say: `You are not alone in the codebase; do not revert others' changes.`
   - require: summary, files changed, and validation run
6. Do not wait immediately after spawning. Continue local integration or other non-overlapping work.
7. Wait only when a worker result is needed on the critical path.
8. Review returned changes before integrating them.
9. When rerunning similar delegation work, preserve durable learned sections such as `Worker Split Heuristics`, `Bad Split Patterns`, and `Integration Order Notes` when they still match the current work definition and write scopes.

## Outputs / Artifacts

This skill should produce:

- one or more worker prompts with explicit ownership
- a clear worker split derived from the work definition
- returned worker summaries including:
  - summary
  - files changed
  - validation run

When the work definition is updated during the task, preserve it as the source of truth for subsequent worker assignments.

## Worker Prompt Template

Use this template when spawning a flexible number of workers:

```text
Use the work definition file at <work definition file>.

Spawn N parallel worker agents, where N is determined by the work definition and the number of disjoint write scopes, with fork_context: true.

For each worker:
- explicitly mention the required skill names
- tell the worker to read <work definition file>
- give exact file or directory ownership
- tell the worker to avoid <other files> when needed
- say: "You are not alone in the codebase; do not revert others' changes."
- require: summary, files changed, and validation run

Workers:
1. <file ownership / task 1>
2. <file ownership / task 2>
...
N. <file ownership / task N>

Keep write scopes disjoint. Do not wait immediately after spawning. Continue local integration work and wait only when a result is needed on the critical path.
```

## Worker Result Contract

Require every worker to return:

1. short summary
2. files changed
3. validation run
4. blockers or open questions, if any

If a worker cannot keep to its assigned write scope, it should stop and report the conflict instead of expanding scope silently.

## Notes

- Treat the work definition file as authoritative unless the user says otherwise.
- When the user wants a copy-ready project setup, use `codex-multi-agent-template/` as the baseline scaffold and keep this skill focused on dynamic work-split logic.
- Choose the number of workers from the work definition and the number of truly independent write scopes.
- Do not force parallelism when tasks are tightly coupled.
- Prefer fewer workers when integration cost is high.
- Prefer workers over explorers when the delegated task includes concrete code changes.
- Keep ownership boundaries explicit to reduce merge conflicts.
- If two tasks touch the same files, keep one local or serialize them instead of spawning both.
- Reuse the same work definition file across workers to maintain coordination.
- When a split causes avoidable overlap, waiting, or integration churn, record it once in `Bad Split Patterns` with the smallest useful correction.

## Companion Template

This repository also ships `codex-multi-agent-template/` for a fixed role-based starter layout:

- `lead`
- `developer`
- `reviewer`
- `tester`

Use that template when the user wants:
- a copyable `.codex/config.toml`
- named role configs in `.codex/agents/*.toml`
- a shared `AGENTS.md`
- starter prompts for kickoff and status tracking

Use this skill when the user wants:
- dynamic worker counts
- work-definition-driven file ownership
- non-standard splits
- narrower or more flexible parallel execution than a fixed 4-role team

## Companion Skills

Common pairings:

- repository or language-specific contributor skills for actual worker execution
- `codex-multi-agent-template/` when the user wants a copyable fixed-role starter

## Team Sync Pattern

When workers uncover a major disagreement, blocked dependency, or architecture trade-off that cuts across write scopes, pause narrow execution and run a short team sync in the main thread.

A team sync should:

- restate the blocking issue briefly
- summarize the competing options
- name the ownership or integration impact
- choose one decision before resuming parallel work

Use team syncs sparingly. Prefer clear ownership and independent work when the split is still valid.

## Self-Improving Behavior

When rerunning delegation for the same or a similar work plan:

- preserve durable learned sections such as `## Worker Split Heuristics`, `## Bad Split Patterns`, and `## Integration Order Notes` when they still match the current work definition
- refresh split decisions against the current write scopes, dependencies, and integration order before reusing them
- promote repeated confirmed observations into short heuristics, preferably phrased like `split by X, not Y, when files overlap`
- demote, mark stale, or remove heuristics contradicted by better task decomposition evidence

## Safety Notes

- Do not spawn workers without explicit user authorization for subagents.
- Keep write scopes disjoint whenever possible.
- If two tasks touch the same files, serialize them or keep one local instead of parallelizing both.
- Do not treat delegation as a substitute for local ownership of the critical path.
