# Agent A — agent Grep tool (Path A, precision)

You own **Path A only**. Read `benchmarks/fast-grep/METRICS.md` first.

## Setup

1. **Fresh chat** in `agent-skills`. **Do not** load `/fast-grep`.
2. Copy `templates/agent-a-results.csv` → `results/agent-a-results.csv` if missing.
3. Read `pilot-tasks.json` and the shell `timing-summary.json` path from the coordinator (engine reference only).

## Required rows: L1, L3, L7

| Task | Pattern | Path |
|------|---------|------|
| L1 | `FAST_GREP_BENCH_L1_UNIQUE_SLICE_9f3a2c` | `benchmarks/fast-grep/fixtures` |
| L3 | `error` | `.` |
| L7 | `import` | `skills/core` |

Use **`head_limit: 50`** on every **agent Grep tool** call (when the runtime provides it).

## Per-task protocol (repeat 3×)

### T_tool (authoritative for Path A)

Wall clock **only the agent Grep tool call**:

1. Note start ms (`Date.now()` or stopwatch).
2. Run **one** **agent Grep tool** invocation.
3. Note end ms when tool output is available.
4. `T_tool_ms = end - start`
5. `T_tool_source = agent-grep-timed`

Do **not** use shell `hyperfine` or turn duration as `T_tool_ms`.

### T_turn (required)

Wall clock from your search instruction through the assistant finishing the result summary. `T_e2e_ms` — leave empty on Path A.

### Tokens (required — no estimates)

From **runtime per-request usage** (usage panel / export when available):

- `tok_skill` = **0**
- `tok_tool_in`, `tok_tool_out`, `tok_reply`, `tok_total`
- `tok_source` = `agent-usage` (or `cursor-usage` on Cursor)

If usage is not visible, set `tok_source=unavailable` and stop.

### Result quality

- `hits_returned` — count lines in Grep output
- `hits_capped` — `yes` if more than 50 matches existed
- `correct_top1` — `yes` / `no` / `novel` (human label)
- `tool_engine` = `agent-grep`

### CSV row

Append to `results/agent-a-results.csv`. Example:

```csv
run-20260610-120000,A,L1,medium,FAST_GREP_BENCH_L1_UNIQUE_SLICE_9f3a2c,benchmarks/fast-grep/fixtures,agent-grep,42,agent-grep-timed,5100,,0,980,120,340,1840,agent-usage,1,no,yes,
```

## Do not

- Load `/fast-grep` or run `scripts/literal-search/fast-grep`
- Run SemanticSearch (literal path only)
- Estimate tokens with tiktoken
- Edit `fast-grep.env` or install packages

## Done when

`agent-a-results.csv` has **3 rows** and every row has `tok_source` in `agent-usage` or `cursor-usage`.
