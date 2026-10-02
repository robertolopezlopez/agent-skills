# Artifacts directory

Codex uses the synced **`ARTIFACTS.md`** as the canonical artifact policy.
Resolve paths with its `resolve_artifact_path.py` helper; do not create
repository-local artifact directories unless the user explicitly asks.
