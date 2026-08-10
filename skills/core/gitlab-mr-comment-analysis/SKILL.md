---
name: gitlab-mr-comment-analysis
description: Analyze normalized unresolved GitLab MR discussions, group them into stable subsections in one artifact, support selected quick fixes, and delegate disjoint groups only when authorized.
---

# GitLab MR Comment Analysis

Group reviewer feedback in one durable artifact; use `gitlab` for all transport and identity.

## When to Use

Use when the user wants unresolved GitLab MR comments grouped, analyzed, refreshed, or selectively addressed.

## When Not to Use

For metadata or discussion fetch alone, use `gitlab`; for implementation without review grouping, use the repository contributor skill.

## Inputs

- MR IID/URL, normalized `gl-fetch mr ... --full` JSON, or existing MR artifact.
- Optional selected issue numbers or stable labels such as `issue_02`.
- Default artifact: `$ARTIFACTS/mr-<IID>/review_mr_<IID>.md`; use `analysis_mr_<IID>.md` only when already chosen for investigation-heavy work. Existing legacy root files remain valid.

## Workflow

1. Read repository `AGENTS.md`, the main artifact when present, and `gitlab`.
2. Refresh with the `gitlab` skill's resolved `gl-fetch mr '<iid-or-url>' --full`; live thread state wins over cached prose.
3. Filter non-system discussions to actionable unresolved threads unless the user asks otherwise.
4. Group comments sharing one underlying problem. Upsert one section only:

   ```text
   ## Grouped unresolved comments
   1 → issue_01

   ### issue_01 — <short title>
   - Links/authors
   - Problem and proposed solution
   - Affected files/modules
   - Technical analysis and verdict
   - Recommended next action
   - Reply status, confidence, open questions
   - History (only when prior snapshots matter)
   ```

5. Preserve stable `issue_*` labels across reruns. Keep session numbering only as a current selection index.
6. For quick-fix requests, map requested numbers to stable labels and update only those subsections.
7. Merge durable content from legacy split files into matching subsections; remove split files only after a successful merge.
8. Pair repository-specific analysis/contributor skills when conclusions require code evidence or patches.
9. Return a 2–3-line summary per group and the full main-artifact path.

## Parallel Work

Use `multi-spawn-agent` only when explicitly authorized. Assign disjoint `### issue_*` subsections, pass enough context through the runtime-supported mechanism, prohibit edits outside assigned blocks, and serialize overlapping groups.

## Validation

- Refresh live discussions before editing.
- Keep exactly one main MR Markdown artifact unless the user directs otherwise.
- Preserve bootstrap sections and stable issue labels.
- Cite MR notes and repository evidence; distinguish confirmed conclusions from open questions.

## Outputs / Artifacts

Update exactly one:

- `$ARTIFACTS/<meaningful_id>/review_mr_<IID>.md`
- `$ARTIFACTS/<meaningful_id>/analysis_mr_<IID>.md`
- an already-active legacy root equivalent

## Companion Skills

Use `gitlab` for transport, repository overlays for code evidence, and `multi-spawn-agent` only when explicitly authorized.

## Safety Notes

- Never post or resolve GitLab discussions without an explicit request.
- Skip resolved threads by default.
- Keep transport/project parsing in `gitlab`; keep code conclusions in repository overlays.
