# gitlab

The `gitlab` skill fetches and normalizes GitLab merge request context.

Bootstrap artifacts follow the shared schema in `../ARTIFACTS.md`.

## Optional local artifact bootstrap

This skill can also bootstrap a local markdown artifact from fetched MR JSON without changing its existing context contract for dependent skills.

Typical outputs:

- `review_mr_<MR>.md`
- `analysis_mr_<MR>.md`

Example helper usage:

```bash
glab api /projects/<project_id>/merge_requests/<MR> > /tmp/mr_<MR>.json
python3 gitlab/scripts/bootstrap_gitlab_artifact.py --json /tmp/mr_<MR>.json --mr <MR>
```

Use `--type analysis` for investigation-heavy MR work.

Bootstrap remains local-only:

- reads MR data
- writes local markdown artifact
- does not modify GitLab

Recommended use from prompts:

- `Use gitlab to bootstrap an artifact for MR 123`
- `Use gitlab to fetch MR 123 and fill review_mr_123.md`
- `Bootstrap a local review artifact from https://example.com/group/project/-/merge_requests/123`

The bootstrap helper validates the generated artifact automatically with `../scripts/validate_artifact.py` or the installed copy under **`~/.cursor/skills/scripts/`** or **`~/.codex/skills/scripts/`** matching the active runtime.
If the artifact already exists, it preserves local follow-up sections such as `## Follow-up Findings` and `## Improvement Candidates` while refreshing GitLab-derived sections from live MR data.
