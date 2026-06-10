# Benchmark metrics — precision-first sources

Each metric has **one authoritative source**. Do not substitute estimates when the authoritative source is available.

## Paths

| Path | Model | Shell engine |
|------|--------|--------------|
| **A** | **agent Grep tool** | N/A (in-agent) |
| **B** | **SemanticSearch** | N/A (in-agent) |
| **C** | **`fast-grep` wrapper** → host `rg`/… | `fast-grep` |
| **D** | **`fast-grep.env` + direct host CLI** (`LITERAL-CODE-SEARCH.md`) | `preferred-host` |

Path **D** is the production policy: read **`fast-grep.env`**, run **`rg`**/`ag`/… directly — no wrapper, no skill.

## Time

| Metric | Authoritative source | Path | How to capture |
|--------|---------------------|------|----------------|
| **T_tool** | **Wall clock around the tool call** | **A** | Before/after a single **agent Grep tool** invocation. `T_tool_source=agent-grep-timed`. |
| **T_tool** | **Wall clock around the tool call** | **B** | Before/after a single **SemanticSearch** invocation. `T_tool_source=semantic-search-timed`. |
| **T_tool** | **`hyperfine` mean (ms)** | **C** | From `timing/<task>-hyperfine.json` → `fast-grep` row. |
| **T_tool** | **`hyperfine` mean (ms)** | **D** | From `timing/<task>-hyperfine.json` → `preferred-host` row. |
| **T_tool** | **`hyperfine` mean (ms)** | **Engine reference** | Same JSON → `rg` row (baseline). |
| **T_turn** | **Wall clock for the full agent turn** | **A, B, C, D** | Required. |
| **T_e2e** | **Wall clock for multi-step path** | **B** | SemanticSearch → optional agent Grep confirm. |

### T_tool rules

- **Never** use `hyperfine` for Path **A** or **B** (tools run inside the agent runtime, not as shell commands).
- **`hyperfine` is required** for Path **C**, **D**, and engine reference.

## Tokens

| Metric | Authoritative source | How to capture |
|--------|---------------------|----------------|
| **Tok_*** | **Runtime per-request usage** | Usage panel or export when available. |
| **tok_source** | `agent-usage` or `cursor-usage` | Not offline estimates. |

## Agent protocol (precision)

| Path | Skill | Tool | Required rows |
|------|-------|------|---------------|
| **A** | No skill | **agent Grep tool** | L1, L3, L7 |
| **B** | No skill | **SemanticSearch** | S1, S2, S3 |
| **C** | **`LITERAL-CODE-SEARCH.md`** | `scripts/literal-search/fast-grep` wrapper | L1, L3, L7 |
| **D** | **`LITERAL-CODE-SEARCH.md`** | `fast-grep.env` → direct **`rg`**/`ag`/… | L1, L3, L7 |

Run **four** fresh chats in parallel (one per path A–D).

## Validation

```bash
benchmarks/fast-grep/validate-results.sh benchmarks/fast-grep/results/run-<timestamp>
```
