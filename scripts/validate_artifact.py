#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

CORE_SECTIONS = [
    '# Task',
    '## Summary',
    '## Type',
    '## Repository',
    '## Context Links',
    '## Selected Skills',
    '## Defaults Files',
    '## Assumptions',
    '## Initial Plan',
    '## Validation Plan',
    '## Open Questions',
    '## Description',
    '## Actionable Context',
]
DETAIL_SECTIONS = {'## Jira Details', '## GitLab Details', '## GitHub Details'}
NAME_PATTERNS = [
    re.compile(r'^task_[a-z0-9][a-z0-9-]*\.md$'),
    re.compile(r'^review_mr_\d+\.md$'),
    re.compile(r'^analysis_[a-z0-9][a-z0-9_-]*\.md$'),
    re.compile(r'^analysis_mr_\d+\.md$'),
    re.compile(r'^work_plan_mr_\d+\.md$'),
    re.compile(r'^analysis_mr_\d+_issue_\d+\.md$'),
    re.compile(r'^mr_\d+_comment_report\.md$'),
    re.compile(r'^review_pr_\d+\.md$'),
    re.compile(r'^analysis_pr_\d+\.md$'),
    re.compile(r'^work_plan_pr_\d+\.md$'),
    re.compile(r'^analysis_pr_\d+_issue_\d+\.md$'),
    re.compile(r'^pr_\d+_comment_report\.md$'),
    re.compile(r'^triage_issue_\d+\.md$'),
    re.compile(r'^analysis_issue_\d+\.md$'),
]


def extract_headings(text: str) -> list[str]:
    return [line.rstrip() for line in text.splitlines() if line.startswith('#')]


def validate_name(path: Path) -> list[str]:
    if any(p.match(path.name) for p in NAME_PATTERNS):
        return []
    return [f'unexpected artifact filename: {path.name}']


def validate_core_sections(headings: list[str]) -> list[str]:
    errors: list[str] = []
    positions: dict[str, int] = {}
    for section in CORE_SECTIONS:
        try:
            positions[section] = headings.index(section)
        except ValueError:
            errors.append(f'missing section: {section}')
    detail_positions = [i for i, h in enumerate(headings) if h in DETAIL_SECTIONS]
    if not detail_positions:
        errors.append(
            'missing domain details section: one of ## Jira Details, ## GitLab Details, or ## GitHub Details'
        )
    if errors:
        return errors

    ordered = CORE_SECTIONS[:-2]
    prev = -1
    for section in ordered:
        pos = positions[section]
        if pos <= prev:
            errors.append(f'section out of order: {section}')
        prev = pos

    detail_pos = detail_positions[0]
    if detail_pos <= positions['## Open Questions']:
        errors.append('domain details section must appear after ## Open Questions')
    if detail_pos >= positions['## Description']:
        errors.append('domain details section must appear before ## Description')

    if positions['## Description'] <= detail_pos:
        errors.append('## Description must appear after domain details section')
    if positions['## Actionable Context'] <= positions['## Description']:
        errors.append('## Actionable Context must appear after ## Description')
    return errors


def validate_file(path: Path) -> list[str]:
    text = path.read_text()
    headings = extract_headings(text)
    errors = validate_name(path)
    errors.extend(validate_core_sections(headings))
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description='Validate a local workflow artifact against the shared schema.')
    parser.add_argument('paths', nargs='+', help='Artifact markdown file(s) to validate')
    args = parser.parse_args()

    total_errors = 0
    for raw in args.paths:
        path = Path(raw)
        if not path.exists():
            print(f'{path}: missing file')
            total_errors += 1
            continue
        errors = validate_file(path)
        if errors:
            print(f'{path}: FAIL')
            for error in errors:
                print(f'  - {error}')
            total_errors += len(errors)
        else:
            print(f'{path}: OK')
    raise SystemExit(1 if total_errors else 0)


if __name__ == '__main__':
    main()
