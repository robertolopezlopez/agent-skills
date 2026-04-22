# AGENTS.md — Multi-Agent Workflow

> Codex CLI auto-loads this file into every agent conversation. It defines the shared workflow, guardrails, and safety rules for the team.

## Workflow

Codex spawns agents in parallel and collects their results. The lead coordinates each phase; within a phase, independent work should run concurrently.

```text
Phase 1:  lead explores repo, produces design
Phase 2:  reviewer + tester review design IN PARALLEL → lead approves
Phase 3:  developer implements approved design
Phase 4:  reviewer + tester audit changes IN PARALLEL
Phase 5:  if blockers → developer fixes → reviewer re-reviews (max 2 rounds)
Phase 6:  lead produces final summary
```

1. **lead** explores the repo, scopes the work, and writes a design with acceptance criteria, risks, and open questions.
2. **reviewer** and **tester** review the design in parallel.
3. **lead** incorporates feedback, resolves open questions, and approves the final design.
4. **developer** implements the approved design with scoped diffs and runs validation.
5. **reviewer** and **tester** audit the implementation in parallel.
6. If the reviewer finds blockers, **developer** fixes them and **reviewer** re-reviews, up to 2 rounds before escalation.
7. **lead** produces the final summary: what changed, how it was validated, risks, and next steps.

For larger tasks, the lead may split implementation into independent sub-tasks so work and review can overlap safely.

## Role Output Contract

Each role should return concise structured output.

### lead

Should produce:
- scope
- acceptance criteria
- risks
- open questions
- final decision when reviewer and tester disagree

### developer

Should produce:
- summary
- files changed
- validation run
- blockers or assumptions that affected implementation

### reviewer

Should produce:
- blocker vs non-blocker assessment
- findings with file paths or evidence when possible
- re-review result after fixes when needed

### tester

Should produce:
- commands run
- pass/fail summary
- failing tests or suspicious signals
- environment gaps or setup blockers

## Write-Scope Ownership

- The lead owns planning, task decomposition, and final summary.
- The developer owns code changes unless the lead explicitly splits implementation into disjoint worker scopes.
- Reviewer and tester are read-only by default.
- If implementation is split further, each worker must own explicit files or directories.
- Do not assign overlapping write scopes unless the lead intentionally serializes the work.

## Handoff Rules

- The developer must not start until the lead approves the design.
- Reviewer and tester should review the same approved design, not separate versions.
- Findings should be handed back with enough detail for the developer to act without guessing.
- If a blocker changes scope or architecture, return control to the lead before proceeding.
- Every phase handoff should state whether the next role is blocked or clear to proceed.

## Team Sync

For hard problems, conflicting feedback, or major scope or architecture decisions, the lead should call a **team sync**.

Use a team sync when:
- reviewer and tester disagree
- developer hits an unexpected blocker
- architecture or scope needs a decision
- the normal review loop is stuck

How it works:
1. lead broadcasts the issue and options
2. each agent replies with perspective and recommendation
3. lead makes the final decision if consensus is not reached
4. workflow resumes with the recorded decision

Any agent may request a sync by flagging the issue to the lead.

## Engineering Guardrails

- **Scoped diffs**: change only what the task requires
- **Reuse patterns**: prefer existing utilities and conventions
- **Run validation**: tests, lint, and format checks relevant to the task
- **Report evidence**: cite file paths, line numbers, and command output
- **State assumptions**: do not guess silently
- **Suggest model refreshes when relevant**: if a newer suitable model exists for these roles, recommend it explicitly, but do not change model defaults without approval
- **Keep handoffs crisp**: every role should clearly state outcome, blockers, and next owner

## Safety Rules

- **Only the developer may modify code.** All other agents are read-only.
- The developer must not begin until the lead approves the design.
- Do not skip workflow phases.
- Do not silently expand ownership beyond the assigned write scope.
