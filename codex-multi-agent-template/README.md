# Codex Multi-Agent Template

Copy-ready multi-agent starter for Codex CLI.

Use this when you want a project to have:
- a shared `AGENTS.md`
- a `.codex/config.toml` with named roles
- per-role agent configs
- paste-ready prompts for starting and tracking a run

## Roles

| Role | Access | Responsibility |
|------|--------|----------------|
| lead | read-only | Explore repo, write design, coordinate, approve plan, final summary |
| developer | write | Implement approved design, run validation |
| reviewer | read-only | Review correctness, regressions, security, missing tests |
| tester | read-only | Validate test coverage, CI readiness, edge cases |

Only the **developer** writes files.

## Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | shared workflow and guardrails |
| `.codex/config.toml` | registers roles and multi-agent settings |
| `.codex/agents/*.toml` | per-role model, sandbox, and instructions |
| `prompts/standard-multi-agent-prompt.txt` | paste-ready starter prompt |
| `prompts/status-dump.txt` | lightweight progress snapshot |

## Quick Start

Copy into a target project:

```bash
cp -r codex-multi-agent-template/.codex/ my-project/.codex/
cp codex-multi-agent-template/AGENTS.md my-project/
cp -r codex-multi-agent-template/prompts/ my-project/.codex-prompts/  # optional
```

Verify:

```bash
cd my-project
test -f AGENTS.md && echo "ok: AGENTS.md" || echo "MISSING: AGENTS.md"
test -f .codex/config.toml && echo "ok: config.toml" || echo "MISSING: config.toml"
ls .codex/agents/*.toml
```

Then start Codex in that project and paste `prompts/standard-multi-agent-prompt.txt`.

## Notes

- Replace model names in `.codex/agents/*.toml` with any compatible models in your environment.
- When revisiting this template later, suggest newer suitable model defaults when available, but keep updates explicit rather than automatic.
- Treat this template as a baseline. Adapt role wording and validation steps per repository.
- If you need flexible worker splits instead of fixed roles, use the `multi-spawn-agent` skill in this repository.
