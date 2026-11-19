#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

private_root="$tmp_dir/private"
mkdir -p "$private_root/skills/demo/extra-skill" "$tmp_dir/home"
printf '%s\n' '---' 'name: extra-skill' 'description: demo extra manifest skill' '---' '# Extra Skill' '## Workflow' 'Do the thing.' > "$private_root/skills/demo/extra-skill/SKILL.md"
cat > "$private_root/skills_manifest.yaml" <<'EOF'
shared_files: []

skills:
  - name: extra-skill
    path: skills/demo/extra-skill
    status: stable
    type: core
    repo_scope: demo
    release_group: demo
EOF

sync() {
  HOME="$tmp_dir/home" \
    CODEX_HOME="$tmp_dir/home" \
    AGENT_SKILLS_SYNC_TARGETS=codex \
    AGENT_SKILLS_EXTRA_MANIFESTS="$private_root/skills_manifest.yaml" \
    "$repo_root/scripts/sync_skills.sh" "$@"
}

sync --all >/dev/null
[[ -f "$tmp_dir/home/skills/extra-skill/SKILL.md" ]]
[[ -f "$tmp_dir/home/skills/tdd/SKILL.md" ]]

sync --all --delete-missing >/dev/null
[[ -f "$tmp_dir/home/skills/extra-skill/SKILL.md" ]]
[[ -f "$tmp_dir/home/skills/tdd/SKILL.md" ]]

echo "extra manifest sync keeps both repositories' skills"
