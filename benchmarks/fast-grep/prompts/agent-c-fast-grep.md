# Agent C — literal-search helper (Path C, precision)

You own **Path C only**. Read `benchmarks/fast-grep/METRICS.md` first.

## Setup

1. **Fresh chat** in `agent-skills`. Follow synced **`LITERAL-CODE-SEARCH.md`** (no skill load).
2. Copy `templates/agent-c-results.csv` → `results/agent-c-results.csv` if missing.
3. Read shell outputs from the coordinator's run directory:
   - `timing-summary.json`
   - `timing/<task>-hyperfine.json`

## Required rows: L1, L3, L7

| Task | Command |
|------|---------|
| L1 | `scripts/literal-search/fast-grep --literal 'FAST_GREP_BENCH_L1_UNIQUE_SLICE_9f3a2c' benchmarks/fast-grep/fixtures` |
| L3 | `scripts/literal-search/fast-grep --literal 'error' .` |
| L7 | `scripts/literal-search/fast-grep --literal 'import' skills/core` |

## Per-task protocol (repeat 3×)

### T_tool (authoritative for Path C)

**Do not time the shell yourself.** Copy from shell artifacts:

1. Open `timing-summary.json` → task → `fast-grep` → `T_tool_ms` (hyperfine mean).
2. `T_tool_source = hyperfine-mean`
3. If hyperfine stats are missing, mark run **incomplete** — do not substitute single-run timing.

### T_turn (required)

Wall clock for the full agent turn (instruction → helper run → present results). Separate from `T_tool_ms`.

### Tokens (required)

From **Cursor per-request usage**:

- `tok_skill` — **0** for Path C (no skill load; policy is **`AGENTS.md`**)
- `tok_tool_in`, `tok_tool_out`, `tok_reply`, `tok_total`
- `tok_source` = `cursor-usage`

### Result quality

- Run the shell helper (not the agent Grep tool unless exit **4**).
- `tool_engine` — from stderr `# fast-grep: tool=rg` (or `ag`, etc.)
- `hits_returned` / `hits_capped` — count from helper stdout (compare to `out/<task>-fast-grep.txt` in run dir)
- `correct_top1` — human label

### CSV example

```csv
run-20260610-120000,C,L1,medium,FAST_GREP_BENCH_L1_UNIQUE_SLICE_9f3a2c,benchmarks/fast-grep/fixtures,rg,47.0,hyperfine-mean,6200,,2700,1100,90,280,4170,cursor-usage,1,no,yes,
```

## Do not

- Do not use the agent Grep tool when the shell helper succeeds
- Change `fast-grep.env` or install packages
- Estimate tokens or `T_tool_ms`

## Done when

`agent-c-results.csv` has **3 rows** with `tok_source=cursor-usage` and `T_tool_source=hyperfine-mean`.
