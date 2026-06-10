# Benchmark metrics — precision-first sources

Each metric has **one authoritative source**. Do not substitute estimates when the authoritative source is available.

## Time

| Metric | Authoritative source | Path | How to capture |
|--------|---------------------|------|----------------|
| **T_tool** | **Wall clock around the tool call** | **A** | Before/after a single **agent Grep tool** invocation. `T_tool_source=agent-grep-timed`. |
| **T_tool** | **Wall clock around the tool call** | **B** | Before/after a single **SemanticSearch** invocation. `T_tool_source=semantic-search-timed`. |
| **T_tool** | **`hyperfine` mean (ms)** | **C** | From `timing/<task>-hyperfine.json` → `fast-grep` row. |
| **T_tool** | **`hyperfine` mean (ms)** | **Engine reference** | Same JSON → `rg` row. |
| **T_turn** | **Wall clock for the full agent turn** | **A, B, C** | Required. |
| **T_e2e** | **Wall clock for multi-step path** | **B** | SemanticSearch → optional agent Grep confirm. |

### T_tool rules

- **Never** use `hyperfine` for Path **A** or **B** (tools run inside the agent runtime, not as shell commands).
- **`hyperfine` is required** for Path **C** and engine reference.

## Tokens

| Metric | Authoritative source | How to capture |
|--------|---------------------|----------------|
| **Tok_*** | **Runtime per-request usage** | Usage panel or export when available. |
| **tok_source** | `agent-usage` or `cursor-usage` | Not offline estimates. |

## Agent protocol (precision)

| Path | Skill | Tool | Required rows |
|------|-------|------|---------------|
| **A** | No `fast-grep` | **agent Grep tool** | L1, L3, L7 |
| **B** | No `fast-grep` | **SemanticSearch** | S1, S2, S3 |
| **C** | **`LITERAL-CODE-SEARCH.md`** (no skill load) | `scripts/literal-search/fast-grep` | L1, L3, L7 |

Run three **fresh chats in parallel** (one per path).

## Validation

```bash
benchmarks/fast-grep/validate-results.sh benchmarks/fast-grep/results/run-<timestamp>
```
