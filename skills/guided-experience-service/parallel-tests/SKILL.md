---
name: guided-experience-service-parallel-tests
description: Run guided-experience-service unit and integration suites with repo-specific `uv`/pytest prerequisites, optionally in authorized parallel workers, then analyze and report failures separately.
---

# Guided Experience Service Parallel Tests

Use this skill for broad test execution in `../../../../guided-experience-service` when the goal is to run both the unit and integration suites in parallel. Prefer 2 parallel workers when subagents are available and explicitly authorized by the user, then review any failures or suspicious errors with `repository-technical-analysis` plus `guided-experience-service-technical-analysis`.

## When to Use

Use this skill when the user wants:

- both unit and integration suites run for `guided-experience-service`
- broad parallel validation in this repository
- follow-up failure analysis after broad test execution

## When Not to Use

Do not use this skill when:

- the task only needs a narrow targeted test command
- the task is outside the `guided-experience-service` repository
- the user has not authorized subagents and broad parallelization is the main reason to invoke this skill

## First Read

- Read `../../../../guided-experience-service/AGENTS.md` before running commands.
- Run commands from the repository root: `../../../../guided-experience-service`.
- Use `uv` for Python commands and scripts.
- If the user provides a local artifact such as `task_<issue>.md`, `review_mr_<MR>.md`, or `analysis_mr_<MR>.md`, read it first and reuse its repo context, assumptions, validation plan, and open questions before running broad test suites.

## Workflow

1. Start in `../../../../guided-experience-service`.
2. Ensure dependencies are installed with `uv sync` when needed.
3. If subagents are explicitly authorized, use 2 parallel workers:
   - Worker 1 owns unit test execution only.
   - Worker 2 owns integration test execution only.
4. Run the unit suite with 10 pytest workers:

```bash
uv run pytest -v -m "not integration and not functional" -n 10
```

5. Just before the integration suite, run:

```bash
make install-splunk-app-deps
```

6. Run the integration suite with 10 pytest workers:

```bash
uv run pytest -v -m "integration and not skip_ci" -n 10
```

7. Before running the integration suite, fail fast if `IAC_TOKEN` is not set.
8. Wait for both suites to finish.
9. If the integration suite depends on production Weaviate behavior, source `cicd/scripts/set_weaviate_config.sh` before running the relevant commands.
10. If failures suggest extra local infrastructure is needed, use the repo Makefile helpers such as `make test-db-start` and `make test-db-stop`.
11. After both suites finish, use `repository-technical-analysis` together with `guided-experience-service-technical-analysis` to review any failing tests, suspicious errors, environment gaps, or likely root causes.
12. Report the raw test outcomes first, then the follow-up technical analysis.
13. When rerunning similar broad test execution, preserve durable learned sections such as `Frequent Failure Clusters`, `Known Prerequisite Gaps`, `Fastest Reliable Suite Order`, and `Flaky or Low-Signal Checks` when they still match current test output and environment state.

## Parallel Worker Template

When subagents are allowed, use a 2-worker split like this:

```text
Spawn 2 parallel worker agents with fork_context: true.

Worker 1:
- own unit test execution only
- run from ../../../../guided-experience-service
- run: uv run pytest -v -m "not integration and not functional" -n 10
- return: summary, failing tests, and validation run

Worker 2:
- own integration test execution only
- run from ../../../../guided-experience-service
- fail immediately with a clear error if IAC_TOKEN is unset
- run: make install-splunk-app-deps
- run: uv run pytest -v -m "integration and not skip_ci" -n 10
- source cicd/scripts/set_weaviate_config.sh first when needed
- return: summary, failing tests, and validation run

After both workers finish:
- use repository-technical-analysis plus guided-experience-service-technical-analysis to review failures or suspicious errors
- report raw test results separately from the follow-up analysis

Do not wait immediately after spawning. Wait after both workers have started or when results are needed.
```

## Command Selection Rules

- Prefer the direct `uv run pytest ... -n 10` commands above because the current `Makefile` test targets do not expose worker count.
- Prefer 2 parallel workers over a single sequential run when subagents are explicitly authorized.
- Prefer repo targets such as `make test-db-start` and `make test-db-stop` for database lifecycle instead of ad hoc docker commands.
- Run `make install-splunk-app-deps` immediately before the integration suite.
- For integration execution, check `IAC_TOKEN` first and stop with a clear error if it is missing.
- After the unit and integration runs complete, use `repository-technical-analysis` with `guided-experience-service-technical-analysis` to analyze failures, suspicious stack traces, environment problems, and likely root causes.
- Do not run functional tests unless the user asks for them; this skill is for unit and integration suites.
- When a suite, prerequisite step, or helper command proves flaky or low-signal, record it once in `Flaky or Low-Signal Checks` or `Known Prerequisite Gaps` with the shortest useful explanation.

## Validation

- Run the exact unit and integration commands documented by this skill unless the repo workflow has changed.
- Fail fast on missing prerequisites such as `IAC_TOKEN` before expensive integration execution.
- Report raw suite outcomes separately from follow-up technical analysis.
- Prefer repo-native helpers for environment lifecycle when they exist.

## Reporting

When summarizing results:

1. State the exact commands run.
2. Separate unit and integration outcomes.
3. List failing tests or modules clearly.
4. Call out missing environment or auth prerequisites explicitly.
5. Add a separate technical-analysis section that summarizes likely root causes, failure groupings, and next debugging steps.

## Outputs / Artifacts

This skill should provide:

- unit suite outcome
- integration suite outcome
- exact commands run
- missing prerequisite or environment notes
- follow-up technical analysis when failures occur

## Artifact-Aware Behavior

When a local workflow artifact is provided:

- read it first for scope, validation intent, and known risks
- reuse its links, assumptions, and open questions when reporting failures
- still treat current test output as the source of truth for pass/fail state
- preserve the shared core sections from `../ARTIFACTS.md` when updating the same artifact or reporting back into it

This is additive only and does not replace the existing unit/integration test workflow.

## Companion Skills

Common pairings:

- `repository-technical-analysis` for failure investigation after test execution
- `guided-experience-service-technical-analysis` for repo-specific failure analysis
- `multi-spawn-agent` only when subagents are explicitly authorized

## Self-Improving Behavior

When rerunning broad unit and integration execution for the same repository state or failure family:

- read any existing task or analysis artifact first
- preserve durable learned sections such as `## Frequent Failure Clusters`, `## Known Prerequisite Gaps`, `## Fastest Reliable Suite Order`, and `## Flaky or Low-Signal Checks` when they still match current output and environment state
- refresh conclusions against the live unit output, integration output, dependency state, and environment checks before reusing them
- promote repeated confirmed observations into short operational heuristics, preferably phrased like `when suite X fails with Y, check Z first`
- demote, mark stale, or remove heuristics contradicted by new output or environment evidence

This keeps broad test-run artifacts useful across reruns without replacing the normal execution and follow-up analysis workflow.

## Safety Notes

- Do not run functional tests unless the user asks for them.
- Do not treat missing prerequisites as flaky failures; report them explicitly.
- Keep unit and integration results separated in both execution and reporting.

## Useful Repo Anchors

- `../../../../guided-experience-service/AGENTS.md` for repo workflow rules
- `../../../../guided-experience-service/Makefile` for test and database helper targets
- `../../../../guided-experience-service/pyproject.toml` for pytest markers and dev dependencies
- `../../../../guided-experience-service/cicd/scripts/set_weaviate_config.sh` for production Weaviate settings
