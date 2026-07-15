# Artifacts directory

When the user says **"the artifacts directory"** (or similar), resolve the
relevant path under **`$AGENT_ARTIFACTS_HOME`** with the synced
`resolve_artifact_path.py` helper. Do not create a new in-repository
`_artifacts_/` directory unless the user explicitly asks for it.

- Ticket/session work: `$ARTIFACTS/<meaningful_id>/`
- General technical-analysis reference: `$KNOWLEDGE/`
- Cross-repository material: `$GLOBAL/<topic>/`

Read existing files in the resolved directory before creating duplicates.
Full policy: `ARTIFACTS.md` in the active runtime's synced skills root.
