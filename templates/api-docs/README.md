# API reference cache

Runtime-local REST API reference material for agent transport skills.

**Resolved path:** `$AGENT_CONFIG_HOME/api-docs/` (Cursor: `~/.cursor/api-docs/`; Codex: `~/.codex/api-docs/`).

```bash
python3 ~/.cursor/skills/scripts/agent_config.py --api-docs-root
python3 ~/.cursor/skills/scripts/agent_config.py --api-docs-dir jira-rest-v3
```

## Layout

```text
api-docs/
  <service-slug>/
    README.md          # index: canonical URLs, version, last refreshed
    endpoints.md       # optional: endpoints the skill uses most
    ...                # optional: fetched HTML, OpenAPI JSON, vendor PDFs
```

## First use

When a transport skill needs API details and `<service-slug>/` is missing or stale:

1. Fetch or summarize official docs from the URLs listed in the skill.
2. Write `README.md` with source links, API version, and refresh date.
3. Add focused notes for endpoints, auth, and payload shapes the workflow needs.

## Later uses

Read this tree before re-downloading docs or guessing endpoint shapes.

Do not store tokens or credentials here.
