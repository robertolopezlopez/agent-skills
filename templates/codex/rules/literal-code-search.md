# Literal code search

For literal repository searches (symbols, strings, imports, configuration keys,
and error text), use the host shell and the synced literal-search workflow.
Prefer `rg`, then the configured fallback chain; use an agent-provided Grep tool
only after the host workflow reports that no usable CLI exists, when shell access
is unavailable, or when the user explicitly requests it.

Before the first literal search in a session, resolve and follow
`LITERAL-CODE-SEARCH.md` from the active runtime's synced skills root. Read
`fast-grep.env` when configured, ask before installing missing tools, and use an
OS-appropriate installation command.
