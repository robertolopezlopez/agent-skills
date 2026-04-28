---
name: github-issue-triage
description: Triage GitHub issues by interpreting normalized issue context, recommending category and next state, identifying missing information, and preparing follow-on actions. Use when the user wants a maintainer-facing GitHub issue triage workflow after GitHub issue context has been fetched.
---

# GitHub Issue Triage

Use this skill for maintainer-facing GitHub issue triage.

Use this skill as a workflow overlay on `github`.

## When to Use

Use this skill when the user wants to:

- triage a GitHub issue
- classify an issue as a bug or enhancement
- recommend the next workflow state for an issue
- identify missing information in an issue report
- prepare a maintainer-facing triage summary or follow-up
- get an issue ready for deeper investigation or implementation

## When Not to Use

Do not use this skill when:

- the task is only GitHub transport access or issue fetch; use `github`
- the task is focused on pull requests rather than issues
- the task is primarily broad repository investigation; use `repository-technical-analysis`
- the task is primarily focused debugging of a concrete failure; use `diagnose`
- the task is primarily implementation or test-first bug fixing; use `tdd`
- a repository-specific overlay already fully defines issue-triage workflow

## Inputs

Accept, in order of preference:

- normalized GitHub issue context already resolved by `github`
- a GitHub issue URL
- a GitHub issue number when repository context is known
- an existing local issue-analysis artifact, if one exists later in the workflow

This skill is issue-focused, not PR-focused.

If the user provides a pull request instead of an issue, redirect to a future PR-specific workflow.

## First Read

- Read the repository `AGENTS.md` before running commands.
- Consume normalized issue context from `github`.
- If the task may require technical investigation before triage is complete, be ready to pair with `repository-technical-analysis`.
- If a concrete bug report needs reproduction or narrowing before classification, be ready to pair with `diagnose`.
- Default to recommendation mode first instead of direct GitHub writes unless the user explicitly asks for updates.

## Companion Skills

Use this skill as the workflow and decision layer on top of `github`.

Common pairings:

- `github` for transport, issue identity, comments, labels, assignees, and normalized issue context
- `repository-technical-analysis` when the issue needs deeper evidence-backed investigation
- `diagnose` when a bug report must be isolated or reproduced before next-state recommendation
- `tdd` when the issue is ready to become test-first implementation work
- repository-specific overlays when a project has its own issue policy or coding workflow

## Workflow

1. Start from normalized issue context resolved by `github`.
2. Read:
   - issue title
   - issue body
   - labels
   - comments
   - current state
   - assignees
   - timestamps
3. Summarize the issue in maintainer-friendly terms.
4. Recommend a category:
   - `bug`
   - `enhancement`
   - or another repo-appropriate category when explicitly defined by project policy
5. Recommend a next state, such as:
   - `needs-triage`
   - `needs-info`
   - `ready-for-agent`
   - `ready-for-human`
   - `wontfix`
6. Explain the reasoning for both recommendations.
7. Identify any missing information that blocks confident triage.
8. If the issue appears to require technical evidence before classification:
   - recommend or trigger follow-on work with `repository-technical-analysis`
   - or use `diagnose` when the issue already describes a concrete failing behavior
9. If the issue is already clear enough for follow-on implementation, prepare the next-step summary accordingly.
10. Return the triage recommendation.
11. Only draft or apply GitHub comments, labels, or updates if the user explicitly asks for that.

## Triage Rules

- Default to recommendation mode first.
- Separate classification from implementation.
- Do not assume a bug report is reproducible without evidence.
- If the issue lacks enough information for confident triage, recommend `needs-info`.
- If the issue is clear, actionable, and suitable for follow-on work, recommend the appropriate ready state.
- Treat exact label names and workflow states as project policy, not universal hardcoded truth.
- If the current repo has no explicit issue-state convention, explain the recommended next state in plain language.

## Validation

- Ensure transport context comes from `github`, not duplicated fetch logic here.
- Keep issue triage separate from PR workflows.
- Keep technical investigation separate from triage when deeper evidence is still needed.
- If recommending a ready state, make sure the issue is specific enough to support the recommendation.

## Outputs / Artifacts

Return:

1. issue summary
2. recommended category
3. recommended next state
4. reasoning
5. missing information, if any
6. recommended next action

Optional later outputs may include:

- a draft maintainer reply
- a draft implementation brief
- a local issue-triage artifact

This skill does not need to write a local artifact by default.

## Safety Notes

- Do not mix GitHub transport behavior into this skill.
- Do not silently apply maintainer workflow policy that the repository has not established.
- Do not default to direct GitHub writes unless the user explicitly asks for them.
- Keep pull-request workflows out of scope for this skill.
