---
name: multi-spawn-agent
description: Use when the user explicitly asks for subagents, delegation, or parallel agent work and you want a reusable template for spawning multiple worker agents from a work definition file. Best for parallel implementation or validation tasks where each worker should use named skills, read a shared work definition or plan file, own specific files or directories, avoid overlapping write scopes, and return a summary, files changed, and validation.
---

# Multi Spawn Agent

Use this skill to structure parallel worker delegation after the user has explicitly authorized subagents.

## Inputs

Require a work definition file path as the primary input. This can be a plan or work-split document such as:

```text
work_plan.md
```

Use that file as the shared source of truth for worker scopes, ownership, constraints, and integration order.

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
   - tell the worker which files to avoid when useful
   - say: `You are not alone in the codebase; do not revert others' changes.`
   - require: summary, files changed, and validation run
6. Do not wait immediately after spawning. Continue local integration or other non-overlapping work.
7. Wait only when a worker result is needed on the critical path.
8. Review returned changes before integrating them.
9. When rerunning similar delegation work, preserve durable learned sections such as `Worker Split Heuristics`, `Bad Split Patterns`, and `Integration Order Notes` when they still match the current work definition and write scopes.

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

## Notes

- Treat the work definition file as authoritative unless the user says otherwise.
- Choose the number of workers from the work definition and the number of truly independent write scopes.
- Do not force parallelism when tasks are tightly coupled.
- Prefer fewer workers when integration cost is high.
- Prefer workers over explorers when the delegated task includes concrete code changes.
- Keep ownership boundaries explicit to reduce merge conflicts.
- If two tasks touch the same files, keep one local or serialize them instead of spawning both.
- Reuse the same work definition file across workers to maintain coordination.
- When a split causes avoidable overlap, waiting, or integration churn, record it once in `Bad Split Patterns` with the smallest useful correction.

## Self-Improving Behavior

When rerunning delegation for the same or a similar work plan:

- preserve durable learned sections such as `## Worker Split Heuristics`, `## Bad Split Patterns`, and `## Integration Order Notes` when they still match the current work definition
- refresh split decisions against the current write scopes, dependencies, and integration order before reusing them
- promote repeated confirmed observations into short heuristics, preferably phrased like `split by X, not Y, when files overlap`
- demote, mark stale, or remove heuristics contradicted by better task decomposition evidence
