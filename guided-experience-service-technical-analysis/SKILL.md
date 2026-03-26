---
name: private-service-technical-analysis
description: Use this when performing technical analysis in the private-service repository, including test failure investigation, root-cause analysis, architecture inspection, incident debugging, regression triage, or performance analysis. Covers evidence-first investigation, parallel pytest execution with 10 workers, root-cause grouping, approval-before-editing, and concise engineering recommendations.
---

# Guided Experience Service Technical Analysis

Use this skill for investigation-first work in this repository.

## First Read

- Read `AGENTS.md` before starting.
- Use `uv` for Python commands and scripts.
- Prefer evidence collection before proposing fixes.
- Do not edit code until the failure mode or hypothesis is clear enough to defend.

## Workflow

Use this loop for technical analysis tasks:

1. Start from the user's task description and gather any repositories, documents, tickets, URLs, or other resources they provided.
2. For git repositories used as references, clone them into `~/workspace`. If a repository already exists there, update it with `git pull` instead of creating a duplicate copy.
3. Use any relevant material in `~/workspace` as research input, including local repositories, notes, artifacts, and previously generated analysis files.
4. Fetch online material when needed, including `curl` requests for documentation, APIs, or other reference resources.
5. Run any unit or integration tests that are relevant to the investigation. Prefer the narrowest command that reproduces the issue, but expand to broader coverage when the failure surface is unclear. When using pytest, prefer `-n 10` unless there is a reason to use fewer workers.
6. Write the analysis incrementally to `analysis_<relevant_name>.md`.
7. Iterate steps 2 through 6 until the analysis is complete and the findings are defensible.
8. Create a presentation in `analysis_<relevant_name>_slides.html` and companion notes in `analysis_<relevant_name>_slides_notes.md`.

## Investigation Rules

- Prefer targeted reproduction after the first broad run.
- Verify assumptions against the code before making architectural claims.
- Call out whether a conclusion is confirmed, likely, or still speculative.
- When multiple failures share one cause, report the shared cause once and list the impact clearly.
- Keep recommendations concrete: what should change, why, and how confident the evidence is.
- If `git` or `curl` fails because of authentication or authorization problems, stop immediately and inform the user instead of continuing with incomplete inputs.

## Validation

- Use repo commands where practical, but prefer direct `uv run pytest ...` commands when tighter control is needed. Prefer running pytest with `-n 10` unless the task requires different parallelism.
- Run `make lint` after code changes are approved and implemented.
- Run `make format` when formatting drift is introduced.

## Environment Notes

- If the analysis depends on production Weaviate behavior, source `cicd/scripts/set_weaviate_config.sh` first.
- Use `Makefile` targets when they match the task; use direct pytest commands when tighter control is needed.
- Pytest markers and ruff settings are defined in `pyproject.toml`.

## Output Expectations

Technical analysis output should usually include:

1. What was run
2. What failed or regressed
3. The most likely root cause or competing hypotheses
4. The proposed fix or next step
5. Any blocker, missing dependency, or uncertainty

## Useful Repo Anchors

- `AGENTS.md` for repo workflow rules
- `Makefile` for standard lint, format, and test targets
- `pyproject.toml` for pytest markers and ruff configuration
- `cicd/scripts/set_weaviate_config.sh` for production Weaviate settings
