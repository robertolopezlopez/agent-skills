# Benchmark coordinator — precision, 4 parallel agents

Read `METRICS.md` before starting.

## Phase 1 — Shell

```bash
command -v hyperfine rg
# Ensure fast-grep.env has a preferred tool (e.g. fast-grep-prefs.sh show)
benchmarks/fast-grep/run-pilot.sh
```

Shell phase times three engines per task: **`rg`** (baseline), **`preferred-host`** (Path D), **`fast-grep`** (Path C).

## Phase 2 — Parallel agents

| Chat | Skill | Prompt | Path |
|------|-------|--------|------|
| 1 | **No** | `prompts/agent-a-agent-grep.md` | **agent Grep tool** (A) |
| 2 | **No** | `prompts/agent-b-semantic-search.md` | **SemanticSearch** (B) |
| 3 | **No** | `prompts/agent-c-fast-grep.md` | **`fast-grep` wrapper** (C) |
| 4 | **No** | `prompts/agent-d-literal-env.md` | **`fast-grep.env` + host CLI** (D) |

Give each agent the run directory name from phase 1.

## Phase 3 — Validate and merge

```bash
RUN_DIR=benchmarks/fast-grep/results/run-<timestamp>
benchmarks/fast-grep/validate-results.sh "$RUN_DIR"
benchmarks/fast-grep/merge-results.sh "$RUN_DIR"
```
