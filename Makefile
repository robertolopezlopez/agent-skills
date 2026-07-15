.PHONY: validate validate-skills validate-artifacts validate-rules sync-skills sync-skills-codex sync-skills-cursor sync-cursor-rules sync-codex-rules install-hooks

validate:
	./scripts/validate_repo.sh

validate-skills:
	python3 scripts/validate_skill.py

validate-artifacts:
	@artifact_paths="$$(find . -maxdepth 1 -type f \( -name 'task_*.md' -o -name 'review_mr_*.md' -o -name 'analysis_mr_*.md' -o -name 'work_plan_mr_*.md' -o -name 'mr_*_comment_report.md' -o -name 'review_pr_*.md' -o -name 'analysis_pr_*.md' -o -name 'work_plan_pr_*.md' -o -name 'pr_*_comment_report.md' \) | sort)"; \
	if [ -n "$$artifact_paths" ]; then \
		python3 scripts/validate_artifact.py $$artifact_paths; \
	else \
		echo "No matching workflow artifacts found"; \
	fi

validate-rules:
	bash tests/test_sync_codex_rules.sh

sync-skills:
	./scripts/sync_skills.sh --all

sync-skills-codex:
	./scripts/sync_skills.sh --all --codex-only

sync-skills-cursor:
	./scripts/sync_skills.sh --all --cursor-only

sync-cursor-rules:
	./scripts/sync_cursor_rules.sh --overwrite

sync-codex-rules:
	./scripts/sync_codex_rules.sh --overwrite

install-hooks:
	./scripts/install_hooks.sh
