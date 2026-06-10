# fast-grep benchmark harness (precision-first)

Compare **agent Grep tool** (A), **SemanticSearch** (B), and **`fast-grep`** host CLI (C). See **`METRICS.md`**.

## Layout

```text
benchmarks/fast-grep/
├── METRICS.md
├── pilot-tasks.json
├── run-pilot.sh
├── validate-results.sh
├── merge-results.sh
├── prompts/
│   ├── agent-a-agent-grep.md   # Path A: agent Grep tool
│   ├── agent-b-semantic-search.md
│   └── agent-c-fast-grep.md
└── results/
```

## Quick start

```bash
benchmarks/fast-grep/run-pilot.sh
# Three parallel fresh chats — prompts/coordinator.md
benchmarks/fast-grep/validate-results.sh benchmarks/fast-grep/results/run-<id>
benchmarks/fast-grep/merge-results.sh benchmarks/fast-grep/results/run-<id>
```

## Paths

| Path | Tool | Last literal resort? |
|------|------|----------------------|
| **A** | **agent Grep tool** (when runtime provides it) | Yes — IDE/agent runtimes |
| **B** | **SemanticSearch** | N/A (semantic suite) |
| **C** | **`fast-grep` script** → host `rg`/… | Host CLI; agent Grep on exit **4** |

## Literal search model (agent-portable)

```text
fast-grep.env (after first discover) → host CLI → agent Grep tool (runtime)
```

SemanticSearch is **not** the literal fallback.

## Companion docs

- `LITERAL-CODE-SEARCH.md` (synced skills root)
- `AGENTS.md` (Literal code search)
