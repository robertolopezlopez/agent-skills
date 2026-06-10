# Agent B — SemanticSearch (Path B, precision)

You own **Path B only**. Read `benchmarks/fast-grep/METRICS.md` first.

## Setup

1. **Fresh chat** in `agent-skills`. **Do not** load `/fast-grep`.
2. Copy `templates/agent-b-results.csv` → `results/agent-b-results.csv` if missing.

## Required rows: S1, S2, S3

| Task | Query (use exact wording) |
|------|---------------------------|
| S1 | Where is skill sync implemented? |
| S2 | artifact path resolution |
| S3 | fast-search skill install |

## Per-task protocol (repeat 3×)

### T_tool (authoritative for Path B)

Wall clock **only the SemanticSearch tool call**:

1. Start timer.
2. Run **one** SemanticSearch with the exact query.
3. Stop timer when results return.
4. `T_tool_ms` = elapsed ms
5. `T_tool_source = semantic-search-timed`

### T_turn and T_e2e

- `T_turn_ms` — full turn through result presentation.
- `T_e2e_ms` — **required** when you run the optional Grep confirm: SemanticSearch start → Grep confirm done → summary. If no confirm, leave `T_e2e_ms` empty and note `no-confirm` in `notes`.

### Tokens (required)

From **Cursor per-request usage**:

- `tok_skill` = **0**
- `tok_tool_in`, `tok_tool_out`, `tok_reply`, `tok_total`
- `tok_source` = `cursor-usage`

### Result quality

- `hits_returned` — number of snippets / result blocks returned (estimate count from tool output structure)
- `hits_capped` — `no` unless the tool explicitly truncates
- `correct_top1` — is the right file in the **top 3**? `yes` / `no` / `novel`
- `tool_engine` = `semantic` (note `+agent-grep` in `notes` if you confirmed)

### Optional confirm (recommended for precision)

After SemanticSearch, run **one** Grep on the top candidate path. Record confirm in `notes`; include confirm duration inside `T_e2e_ms`.

## Do not

- Load `/fast-grep`
- Use `scripts/literal-search/fast-grep` as primary search
- Estimate tokens

## Done when

`agent-b-results.csv` has **3 rows** with `tok_source=cursor-usage`.
