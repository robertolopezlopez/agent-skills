# Agent artifacts store

Durable working notes for Cursor and Codex agents live **outside** git checkouts.

**Default root:** `$AGENT_ARTIFACTS_HOME` (see below). This file lives at **`$AGENT_ARTIFACTS_HOME/README.md`**.

## Default root resolution

1. exported **`AGENT_ARTIFACTS_HOME`**
2. **`~/.cursor/agent-artifacts`** when **`~/.cursor`** exists
3. **`~/.codex/agent-artifacts`**

Set **`AGENT_ARTIFACTS_HOME`** in your shell profile when you want **one shared store** for both Cursor and Codex on the same machine.

## Layout

```text
agent-artifacts/
├── README.md                         # this file
├── _global/                          # cross-repo org knowledge ($GLOBAL/)
│   ├── NEXT_TIME_CHECKS.md
│   └── <topic>/                      # e.g. snyk-repo-ownership/
│       └── *.md
├── knowledge/                        # general technical-analysis reference ($KNOWLEDGE/)
│   └── analysis_<topic>.md
└── <repo-key>/                       # e.g. github.com-snyk-cli ($ARTIFACTS/)
    ├── NEXT_TIME_CHECKS.md           # repo-specific session notes
    └── <meaningful_id>/              # e.g. CLI-1474, pr-336, mr-1447
        ├── task_<issue>.md
        ├── review_mr_<iid>.md
        ├── review_pr_<number>.md
        ├── analysis_<topic>.md
        └── fix_draft_<topic>.md      # informal working drafts
```

Shorthand in skills:

- **`$GLOBAL/`** → **`$AGENT_ARTIFACTS_HOME/_global/`**
- **`$KNOWLEDGE/`** → **`$AGENT_ARTIFACTS_HOME/knowledge/`** (store root — **not** under **`<repo-key>/`**)
- **`$ARTIFACTS/`** → **`$AGENT_ARTIFACTS_HOME/<repo-key>/`** for the active repository

## User phrase

When the user says **"the artifacts directory"** (or similar: "artifact path", "save to artifacts", "write the analysis md"):

1. Resolve the relevant folder under **`$ARTIFACTS/<meaningful_id>/`** for the active ticket, PR, MR, or branch — **not** in-repo **`_artifacts_/`** unless they explicitly ask for that.
2. Use **`$KNOWLEDGE/`** for general technical-analysis reference — store root, not under **`<repo-key>/`**.
3. Use **`$GLOBAL/`** for cross-repo org reference material.

## Path resolution

From a git checkout (replace the skills root with your runtime install):

```bash
# Cursor — repo-scoped
python3 ~/.cursor/skills/scripts/resolve_artifact_path.py --repo-artifacts-root
python3 ~/.cursor/skills/scripts/resolve_artifact_path.py --meaningful-id CLI-1474 --basename analysis_topic.md

# General knowledge (store root)
python3 ~/.cursor/skills/scripts/resolve_artifact_path.py --knowledge-artifacts-root
python3 ~/.cursor/skills/scripts/resolve_artifact_path.py --scope knowledge --basename analysis_ufm_gaf.md

# Codex
python3 ~/.codex/skills/scripts/resolve_artifact_path.py --repo-artifacts-root
python3 ~/.codex/skills/scripts/resolve_artifact_path.py --meaningful-id mr-1447 --basename review_mr_1447.md

# Cross-repo org reference
python3 ~/.cursor/skills/scripts/resolve_artifact_path.py --global-artifacts-root
python3 ~/.cursor/skills/scripts/resolve_artifact_path.py --scope global \
  --meaningful-id snyk-repo-ownership --basename repo-snyk-docker-registry-v2-client.md
```

Read existing files in the target directory before creating duplicates. Prefer extending an existing analysis or review artifact in place.

## Schema and bootstrap

- Full schema: **`ARTIFACTS.md`** next to your synced skills root (`~/.cursor/skills/ARTIFACTS.md` or `~/.codex/skills/ARTIFACTS.md`)
- One-time machine setup from the agent-skills repository: **`./scripts/bootstrap_agent_artifacts.sh`**
- Cursor phrase rule (optional): **`~/.cursor/rules/agent-artifacts-directory.mdc`** (installed by the bootstrap script with **`--cursor-rule`**)
