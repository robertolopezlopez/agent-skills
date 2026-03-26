---
name: private-service-technical-analysis
description: Use this with repository-technical-analysis when performing technical analysis in the private-service repository. Adds repo-specific uv usage, pytest commands, Weaviate setup, and local investigation anchors.
---

# Guided Experience Service Technical Analysis

Use this skill as a repo-specific overlay for `repository-technical-analysis`.

## First Read

- Read `AGENTS.md` before starting.
- Use `uv` for Python commands and scripts.
- Load `repository-technical-analysis` for the general investigation workflow and reporting structure. Keep this skill focused on repo-local rules.

## Repo Workflow

- For broad reproduction, start with `uv run pytest -v -m "not integration and not functional" -n 10` and `uv run pytest -v -m "integration and not skip_ci" -n 10`.
- For narrower reproduction, use the smallest `uv run pytest ...` command that still reproduces the issue.
- When the analysis depends on production Weaviate behavior, source `cicd/scripts/set_weaviate_config.sh` first.
- Create `analysis_<relevant_name>.md`, `analysis_<relevant_name>_slides.html`, and `analysis_<relevant_name>_slides_notes.md` when the investigation requires a written artifact or presentation.

## Repo Investigation Rules

- If `git` or `curl` fails because of authentication or authorization problems, stop immediately and inform the user instead of continuing with incomplete inputs.
- If `git` times out while fetching or pushing resources, stop immediately and inform the user instead of continuing with incomplete inputs.

## Repo Validation

- Use `Makefile` targets when they match the task; use direct `uv run pytest ...` commands when tighter control is needed.
- Run `make lint` after code changes are approved and implemented.
- Run `make format` when formatting drift is introduced.

## Environment Notes

- Pytest markers and ruff settings are defined in `pyproject.toml`.

## Useful Repo Anchors

- `repository-technical-analysis` for the generic investigation workflow
- `AGENTS.md` for repo workflow rules
- `Makefile` for standard lint, format, and test targets
- `pyproject.toml` for pytest markers and ruff configuration
- `cicd/scripts/set_weaviate_config.sh` for production Weaviate settings
