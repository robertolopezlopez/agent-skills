# Benchmark coordinator — precision, 3 parallel agents

Read `METRICS.md` before starting.

## Phase 1 — Shell

```bash
command -v hyperfine rg
benchmarks/fast-grep/run-pilot.sh
```

## Phase 2 — Parallel agents

| Chat | Skill | Prompt | Path |
|------|-------|--------|------|
| 1 | **No** | `prompts/agent-a-agent-grep.md` | **agent Grep tool** |
| 2 | **No** | `prompts/agent-b-semantic-search.md` | **SemanticSearch** |
| 3 | **No** (use `LITERAL-CODE-SEARCH.md`) | `prompts/agent-c-fast-grep.md` | **`scripts/literal-search/fast-grep`** |

Give each agent the run directory name from phase 1.

## Phase 3 — Validate and merge

```bash
RUN_DIR=benchmarks/fast-grep/results/run-<timestamp>
benchmarks/fast-grep/validate-results.sh "$RUN_DIR"
benchmarks/fast-grep/merge-results.sh "$RUN_DIR"
```
