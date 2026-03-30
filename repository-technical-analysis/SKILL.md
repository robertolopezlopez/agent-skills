---
name: repository-technical-analysis
description: Use this when performing technical analysis in a code repository, including test failure investigation, root-cause analysis, architecture inspection, incident debugging, regression triage, or performance analysis. Covers evidence-first investigation, targeted reproduction, root-cause grouping, and concise recommendations.
---

# Repository Technical Analysis

Use this skill for investigation-first work across repositories.

## First Read

- Read local workflow and contributor docs first when they exist: `AGENTS.md`, `README`, `CONTRIBUTING.md`, `Makefile`, and `pyproject.toml`.
- Prefer evidence collection before proposing fixes.
- Do not edit code until the failure mode or hypothesis is clear enough to defend.

## Workflow

Use this loop for technical analysis tasks:

1. Start from the user's task and gather the repositories, documents, tickets, URLs, or artifacts they provided.
2. Identify the narrowest reliable reproduction. Expand to broader coverage only when the failure surface is still unclear.
3. Use any relevant local material as research input, including repositories, notes, logs, and prior analysis files.
4. Fetch online material when needed, including documentation or API references.
5. Run the tests, scripts, benchmarks, or reproduction steps that best isolate the issue.
6. Write the analysis incrementally to `analysis_<relevant_name>.md` when the investigation is non-trivial.
7. Iterate until the findings are confirmed, reduced to a small set of defensible hypotheses, or blocked by a clearly stated dependency.

## Investigation Rules

- Prefer targeted reproduction after the first broad run.
- Verify assumptions against the code before making architectural claims.
- Call out whether a conclusion is confirmed, likely, or still speculative.
- When multiple failures share one cause, report the shared cause once and list the impact clearly.
- Keep recommendations concrete: what should change, why, and how confident the evidence is.
- If `git` or `curl` fails because of authentication or authorization problems, stop immediately and inform the user instead of continuing with incomplete inputs.
- If `git` times out while fetching or pushing resources, stop immediately and inform the user instead of continuing with incomplete inputs.

## Validation

- Use repo commands where practical, but prefer direct commands when tighter control is needed.
- After approved code changes, run the lint, format, and test commands that are relevant to the fix.
- Prefer the smallest validation set that proves or disproves the hypothesis before expanding coverage.

## Output Expectations

Technical analysis output should usually include:

1. What was run
2. What failed or regressed
3. The most likely root cause or competing hypotheses
4. The proposed fix or next step
5. Any blocker, missing dependency, or uncertainty

## General Notes

- For reference repositories, switch to the default branch and update them before relying on them.
- When a project also has a repo-specific overlay skill, use both: keep the generic investigation workflow here and let the overlay provide project-local commands, configs, and anchors.
