#!/usr/bin/env python3
"""Fetch GitLab merge requests via glab and emit normalized JSON."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import quote, urlparse


MR_URL_RE = re.compile(r"^(?P<project>.+)/-/merge_requests/(?P<iid>\d+)/?$")


def parse_mr_input(value: str) -> dict[str, object]:
    if value.isdigit():
        return {"mr_iid": int(value)}
    parsed = urlparse(value)
    match = MR_URL_RE.match(parsed.path.strip("/"))
    if parsed.scheme in {"http", "https"} and parsed.hostname and match:
        return {
            "host": parsed.hostname,
            "project_path": match.group("project"),
            "mr_iid": int(match.group("iid")),
        }
    raise SystemExit("expected an MR IID or GitLab merge-request URL")


def find_identity_helper() -> Path:
    candidate = Path(__file__).parents[1] / "git/git-repo-identity"
    if candidate.is_file():
        return candidate
    raise SystemExit("git-repo-identity not found; sync shared skill helpers")


def resolve_identity() -> dict[str, object]:
    result = subprocess.run(
        [str(find_identity_helper()), "--json"], capture_output=True, text=True, check=False
    )
    if result.returncode:
        raise SystemExit((result.stderr or result.stdout or "repository identity failed").strip())
    return json.loads(result.stdout)


def glab_api(endpoint: str, host: str, paginate: bool = False):
    command = ["glab", "api", endpoint]
    if host:
        command.extend(("--hostname", host))
    if paginate:
        command.append("--paginate")
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        raise SystemExit((result.stderr or result.stdout or "glab api failed").strip())
    return json.loads(result.stdout)


def slim_mr(raw):
    fields = (
        "iid", "title", "description", "state", "draft", "work_in_progress", "web_url",
        "source_branch", "target_branch", "labels", "author", "sha", "merge_status",
    )
    return {field: raw.get(field) for field in fields}


def normalize_discussions(raw_discussions, mr_link: str):
    discussions = []
    for raw in raw_discussions or []:
        notes = []
        for note in raw.get("notes") or []:
            if note.get("system"):
                continue
            note_id = note.get("id")
            notes.append(
                {
                    "id": note_id,
                    "url": f"{mr_link}#note_{note_id}" if note_id else mr_link,
                    "author": (note.get("author") or {}).get("username") or "",
                    "body": note.get("body") or "",
                    "created_at": note.get("created_at") or "",
                    "resolvable": bool(note.get("resolvable")),
                    "resolved": bool(note.get("resolved")),
                    "position": note.get("position"),
                }
            )
        if notes:
            discussions.append(
                {
                    "id": raw.get("id") or "",
                    "individual_note": bool(raw.get("individual_note")),
                    "resolved": not any(note["resolvable"] and not note["resolved"] for note in notes),
                    "notes": notes,
                }
            )
    return discussions


def build_context(value: str, full: bool, api=glab_api, identity=resolve_identity):
    parsed = parse_mr_input(value)
    resolved = identity() if "project_path" not in parsed else {}
    host = str(parsed.get("host") or resolved.get("host") or "gitlab.com")
    project_path = str(parsed.get("project_path") or resolved.get("project_path") or "")
    project_id = resolved.get("project_id")
    project_ref = str(project_id or resolved.get("encoded_project_path") or quote(project_path, safe=""))
    if not project_ref:
        raise SystemExit("could not resolve GitLab project identity")
    iid = int(parsed["mr_iid"])
    base = f"/projects/{project_ref}/merge_requests/{iid}"
    raw_mr = api(base, host, False)
    mr = slim_mr(raw_mr)
    mr_link = str(mr.get("web_url") or f"https://{host}/{project_path}/-/merge_requests/{iid}")
    discussions = normalize_discussions(api(f"{base}/discussions", host, True), mr_link) if full else []
    return {
        "transport": "glab",
        "host": host,
        "project_path": project_path,
        "encoded_project_path": quote(project_path, safe=""),
        "project_id": project_id,
        "mr_iid": iid,
        "mr_link": mr_link,
        "merge_request": mr,
        "discussions": discussions,
        "unresolved_count": sum(not discussion["resolved"] for discussion in discussions),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="object_type", required=True)
    mr_parser = subparsers.add_parser("mr")
    mr_parser.add_argument("mr")
    mr_parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    print(json.dumps(build_context(args.mr, args.full), separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
