# private-service-parallel-tests

Local setup notes for the `private-service-parallel-tests` skill.

## Local Defaults File

Use this file for non-secret local defaults for unit and integration test runs.

Use:

```bash
~/.codex/private-service.env
```

as the per-skill defaults file path.

Suggested variables:

```bash
GUIDED_EXPERIENCE_SERVICE_REPO=~/workspace/private-service
GUIDED_EXPERIENCE_SERVICE_DEFAULT_BRANCH=origin/main
GUIDED_EXPERIENCE_SERVICE_PYTEST_WORKERS=10
GUIDED_EXPERIENCE_SERVICE_UNIT_PYTEST_EXPR=not integration and not functional
GUIDED_EXPERIENCE_SERVICE_INTEGRATION_PYTEST_EXPR=integration and not skip_ci
# optional
# ML_PLATFORM_BASE_URL=https://...
```

Precedence:

1. explicit command arguments
2. exported environment variables
3. `~/.codex/private-service.env`

Do not store `IAC_TOKEN` or other secrets in this file.
Keep using `cicd/scripts/set_weaviate_config.sh` when production Weaviate settings are required.

## Optional Artifact Input

This skill can also start from a local workflow artifact such as:

- `task_<issue>.md`
- `review_mr_<MR>.md`
- `analysis_mr_<MR>.md`

When an artifact is provided, read it first and reuse its scope, validation intent, assumptions, and open questions before running broad test suites.
Artifacts reused or updated by this skill should follow the shared schema in `../ARTIFACTS.md`.
