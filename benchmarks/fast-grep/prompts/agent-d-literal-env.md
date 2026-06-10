# Agent D — fast-grep.env + direct host CLI (Path D, precision)

You own **Path D only**. Read `benchmarks/fast-grep/METRICS.md` first.

## Setup

1. **Fresh chat** in `agent-skills`. Follow synced **`LITERAL-CODE-SEARCH.md`** (no skill load, no `fast-grep` wrapper script).
2. Copy `templates/agent-d-results.csv` → `results/agent-d-results.csv` if missing.
3. Read shell outputs from the coordinator's run directory:
   - `timing-summary.json` (`preferred_host` section)
   - `timing/<task>-hyperfine.json`

## Required rows: L1, L3, L7

**Protocol per task:**

1. Read prefs: `$(agent_config.py --literal-search-dir)/fast-grep-prefs.sh show` (do **not** change `fast-grep.env`).
2. Run the **preferred host binary directly** (from `PREFERRED_SEARCH_TOOL` / shell `preferred-host` cmd in `timing-summary.json`).

| Task | After prefs check, run (example when preferred=ripgrep) |
|------|--------------------------------------------------------|
| L1 | `rg -F --no-heading --line-number --color=never 'FAST_GREP_BENCH_L1_UNIQUE_SLICE_9f3a2c' benchmarks/fast-grep/fixtures` |
| L3 | `rg -F --no-heading --line-number --color=never 'error' .` |
| L7 | `rg -F --no-heading --line-number --color=never 'import' skills/core` |

Use **`ag`**, **`ugrep`**, etc. when prefs say so — match the `preferred-host` command in `timing-summary.json` for that task.

## Per-task protocol (repeat 3×)

### T_tool (authoritative for Path D)

**Do not time the shell yourself.** Copy from shell artifacts:

1. Open `timing-summary.json` → task → `preferred-host` → `T_tool_ms` (hyperfine mean).
2. `T_tool_source = hyperfine-mean`
3. `tool_engine` = `preferred_binary` from the same task entry (e.g. `rg`, `ag`).

### T_turn (required)

Wall clock for the full agent turn (read prefs → host search → present results).

### Tokens (required)

From **Cursor per-request usage**:

- `tok_skill` — **0** (policy doc / rule only; no skill load)
- `tok_tool_in`, `tok_tool_out`, `tok_reply`, `tok_total`
- `tok_source` = `cursor-usage`

### Result quality

- **Do not** run `scripts/literal-search/fast-grep` (that is Path C).
- **Do not** use the agent Grep tool unless the host binary is missing.
- `hits_returned` / `hits_capped` — compare to `out/<task>-preferred-host.txt` in the run dir

### CSV example

```csv
run-20260610-120000,D,L1,medium,FAST_GREP_BENCH_L1_UNIQUE_SLICE_9f3a2c,benchmarks/fast-grep/fixtures,rg,10.2,hyperfine-mean,4100,,2400,900,80,210,3490,cursor-usage,1,no,yes,
```

## Do not

- Load `/fast-grep` or run the `fast-grep` wrapper (Path C)
- Change `fast-grep.env` or install packages
- Estimate tokens or `T_tool_ms`

## Done when

`agent-d-results.csv` has **3 rows** with `tok_source=cursor-usage` and `T_tool_source=hyperfine-mean`.
