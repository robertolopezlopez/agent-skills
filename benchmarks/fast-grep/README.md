# fast-grep benchmark harness (precision-first)

Compare **agent Grep tool** (A), **SemanticSearch** (B), **`fast-grep` wrapper** (C), and **`fast-grep.env` + direct host CLI** (D). See **`METRICS.md`**.

## Layout

```text
benchmarks/fast-grep/
├── METRICS.md
├── pilot-tasks.json
├── run-pilot.sh
├── validate-results.sh
├── merge-results.sh
├── prompts/
│   ├── agent-a-agent-grep.md
│   ├── agent-b-semantic-search.md
│   ├── agent-c-fast-grep.md
│   └── agent-d-literal-env.md
└── results/
```

## Quick start

```bash
benchmarks/fast-grep/run-pilot.sh
# Four parallel fresh chats — prompts/coordinator.md
benchmarks/fast-grep/validate-results.sh benchmarks/fast-grep/results/run-<id>
benchmarks/fast-grep/merge-results.sh benchmarks/fast-grep/results/run-<id>
```

## Paths

| Path | Tool | Notes |
|------|------|-------|
| **A** | **agent Grep tool** | Last literal resort in IDE |
| **B** | **SemanticSearch** | Semantic suite only |
| **C** | **`fast-grep` wrapper** → host `rg`/… | Install gate + prefs |
| **D** | **`fast-grep.env` → `rg`/`ag`/… direct** | **Production policy** (no wrapper) |

## Literal search model (agent-portable)

```text
fast-grep.env (after first discover) → host CLI (Path D) → fast-grep wrapper (Path C) → agent Grep tool (Path A)
```

SemanticSearch is **not** the literal fallback.

## Companion docs

- `LITERAL-CODE-SEARCH.md` (synced skills root)
- `AGENTS.md` (Literal code search)
