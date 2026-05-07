---
name: plan-issues
description: Break a scoped plan, task, or change into dependency-aware vertical slices that are ready for human or agent execution. Use when the goal is already understood and the user wants an actionable implementation breakdown rather than investigation or coding.
---

# Plan Issues

Use this skill for planning and decomposition work.

## When to Use

Use this skill when the user wants to:

- break a scoped change into actionable work items
- decompose a plan into vertical slices
- identify dependencies and blockers between work items
- prepare work for humans or agents
- turn an understood change into an execution-ready breakdown

## When Not to Use

Do not use this skill when:

- the main task is broad investigation or root-cause analysis; use `repository-technical-analysis`
- the main task is debugging or reproducing a concrete failure; use `diagnose`
- the main task is implementation through a test-first loop; use `tdd`
- the main task is only transport access to GitHub, GitLab, Jira, or Confluence
- the change is still too vague to decompose confidently
- a repository-specific overlay already fully defines the planning workflow

## Inputs

Accept any of:

- a scoped task or change request
- a local planning artifact
- a GitHub, GitLab, Jira, or Confluence item whose scope is already clear
- a feature, fix, or refactor description with enough detail to split into work items
- an already-approved plan that needs execution slicing

## First Read

- Read `AGENTS.md`, `README.md`, `Makefile`, and repo-specific contributor docs when present.
- If a local artifact exists for the task, read it first.
- Reuse `repository-technical-analysis` first if the problem or scope is still unclear.
- Reuse transport skills first if the plan depends on remote issue or MR context that has not yet been fetched.

## Workflow

1. Confirm the scope of the change.
2. Refuse to decompose until the goal is clear enough to split confidently.
3. Identify the smallest useful vertical slices.
4. Prefer slices that cut through the necessary layers end-to-end rather than grouping work by technical layer.
5. For each slice, define:
   - title
   - what to build or change
   - why it is separate
   - dependencies or blockers
   - whether it is suitable for an agent or needs human input
6. Review the breakdown for:
   - unnecessary coupling
   - overly large slices
   - hidden blockers
   - missing validation expectations
7. Produce the ordered work plan.
8. Suggest follow-on execution paths, such as `multi-spawn-agent`, `tdd`, or repository-specific contributor skills.

## Planning Rules

- Prefer vertical slices over horizontal slices.
- Prefer many thin executable slices over a few large ambiguous ones.
- Keep dependencies explicit.
- Mark human-needed decisions separately from agent-suitable execution work.
- Do not invent precision when the scope is still unclear.
- If decomposition reveals missing understanding, stop and recommend clarification before continuing.

## Validation

- Check that each slice is understandable on its own.
- Check that each slice has a clear purpose and a plausible validation path.
- Check that blockers are called out explicitly.
- Keep the final breakdown small enough to execute incrementally.

## Outputs / Artifacts

Return:

1. summary of the scoped change
2. ordered work items
3. dependencies and blockers
4. human-needed vs agent-suitable notes
5. recommended execution order
6. recommended follow-on skills

When the work is non-trivial, this skill may also write:

- `work_plan_<relevant_name>.md`

## Companion Skills

Use this skill as a planning decomposition layer.

Common pairings:

- `repository-technical-analysis` when scope is still unclear
- `multi-spawn-agent` when the breakdown is ready for delegated execution
- `tdd` when individual slices should be implemented test-first
- repository-specific contributor skills for local commands and validation
- transport skills such as `github`, `gitlab`, `jira`, or `confluence` when remote context is needed first

## Safety Notes

- Do not force decomposition when the problem is not yet understood.
- Do not mix planning decomposition with transport or implementation logic.
- Do not hide uncertainty inside fake precision.
