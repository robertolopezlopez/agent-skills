#!/usr/bin/env python3
"""Fetch Jira issues via acli (preferred) or jira-api and emit normalized JSON."""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS_ROOT = SCRIPT_DIR.parent
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

ISSUE_KEY_RE = re.compile(r"^([A-Z][A-Z0-9]+-\d+)$", re.IGNORECASE)
ISSUE_URL_RE = re.compile(
    r"https?://[^/]+/browse/(?P<key>[A-Z][A-Z0-9]+-\d+)/?",
    re.IGNORECASE,
)

DEFAULT_FIELDS = (
    "summary,status,issuetype,priority,assignee,reporter,created,updated,"
    "description,comment,labels"
)


def load_agent_config():
    infer = Path(__file__)
    candidates = [
        SCRIPTS_ROOT / "agent_config.py",
        Path.home() / ".cursor" / "skills" / "scripts" / "agent_config.py",
        Path.home() / ".codex" / "skills" / "scripts" / "agent_config.py",
    ]
    parts = infer.resolve().parts
    for idx, part in enumerate(parts):
        if part in {".cursor", ".codex"} and idx + 1 < len(parts) and parts[idx + 1] == "skills":
            runtime = part.lstrip(".")
            candidates.insert(1, Path.home() / f".{runtime}" / "skills" / "scripts" / "agent_config.py")
            break
    for path in candidates:
        if not path.is_file():
            continue
        spec = importlib.util.spec_from_file_location("agent_config", path)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return None


def parse_issue_key(value: str) -> str:
    cleaned = value.strip()
    url_match = ISSUE_URL_RE.search(cleaned)
    if url_match:
        return url_match.group("key").upper()
    key_match = ISSUE_KEY_RE.match(cleaned)
    if key_match:
        return key_match.group(1).upper()
    raise SystemExit(f"unsupported Jira issue key or URL: {value}")


def adf_text(node: object) -> str:
    if isinstance(node, dict):
        parts: list[str] = []
        node_type = node.get("type")
        if node_type == "text":
            parts.append(str(node.get("text", "")))
        for child in node.get("content", []) or []:
            parts.append(adf_text(child))
        if node_type in {"paragraph", "heading", "bulletList", "orderedList", "listItem"}:
            parts.append("\n")
        return "".join(parts)
    if isinstance(node, list):
        return "".join(adf_text(item) for item in node)
    return ""


def display_name(user: Any) -> str:
    if isinstance(user, dict):
        return str(user.get("displayName") or user.get("emailAddress") or user.get("name") or "")
    return str(user or "")


def slim_comments(fields: dict[str, Any]) -> list[dict[str, str]]:
    comments = (fields.get("comment") or {}).get("comments", [])
    out: list[dict[str, str]] = []
    for comment in comments:
        if not isinstance(comment, dict):
            continue
        body = re.sub(r"\n+", "\n", adf_text(comment.get("body") or "")).strip()
        if not body:
            continue
        out.append(
            {
                "id": str(comment.get("id") or ""),
                "author": display_name(comment.get("author")),
                "body": body,
                "created": str(comment.get("created") or ""),
            }
        )
    return out


def acli_available() -> bool:
    return shutil.which("acli") is not None


def acli_authenticated() -> bool:
    if not acli_available():
        return False
    result = subprocess.run(
        ["acli", "jira", "auth", "status"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def acli_site_host() -> str | None:
    if not acli_authenticated():
        return None
    result = subprocess.run(
        ["acli", "jira", "auth", "status"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("site:"):
            site = stripped.split(":", 1)[1].strip()
            if site:
                return site.split("/")[0]
    return None


def atlassian_api_base() -> str | None:
    import os

    inline = (os.environ.get("ATLASSIAN_API_BASE_URL") or "").strip()
    if inline:
        return inline.rstrip("/")
    ac = load_agent_config()
    if ac is None:
        return None
    value = ac.read_env_var("ATLASSIAN_API_BASE_URL", "atlassian.env", Path(__file__))
    if value:
        return value.strip().rstrip("/")
    return None


def browse_base_url(self_url: str | None, issue_key: str) -> str:
    site = acli_site_host()
    if site:
        host = site if site.startswith("http") else f"https://{site}"
        return f"{host.rstrip('/')}/browse/{issue_key}"
    api_base = atlassian_api_base()
    if api_base:
        return f"{api_base.rstrip('/')}/browse/{issue_key}"
    if self_url:
        parsed = urlparse(self_url)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}/browse/{issue_key}"
    return f"https://example.atlassian.net/browse/{issue_key}"


def fetch_via_acli(issue_key: str, fields: str) -> dict[str, Any]:
    command = [
        "acli",
        "jira",
        "workitem",
        "view",
        issue_key,
        "--json",
        "--fields",
        fields,
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "acli jira workitem view failed").strip()
        raise SystemExit(message)
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        raise SystemExit("acli jira workitem view returned unexpected payload")
    return payload


def jira_api_script() -> Path:
    candidates = [
        SCRIPT_DIR / "jira-api",
        SCRIPTS_ROOT / "jira" / "jira-api",
    ]
    ac = load_agent_config()
    if ac is not None:
        installed = ac.resolve_installed_script("jira/jira-api", Path(__file__))
        if installed is not None:
            candidates.insert(0, installed)
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise SystemExit("jira-api helper not found; sync scripts/jira/ from agent-skills")


def jira_request_script() -> Path:
    candidates = [
        SCRIPT_DIR / "jira-request",
        SCRIPTS_ROOT / "jira" / "jira-request",
    ]
    ac = load_agent_config()
    if ac is not None:
        installed = ac.resolve_installed_script("jira/jira-request", Path(__file__))
        if installed is not None:
            candidates.insert(0, installed)
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise SystemExit("jira-request helper not found; sync scripts/jira/ from agent-skills")


def fetch_via_jira_api(issue_key: str, fields: str) -> dict[str, Any]:
    script = jira_api_script()
    result = subprocess.run(
        [str(script), issue_key, fields],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "jira-api failed").strip()
        raise SystemExit(message)
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        raise SystemExit("jira-api returned unexpected payload")
    return payload


def fetch_transitions(issue_key: str) -> list[dict[str, Any]]:
    script = jira_request_script()
    result = subprocess.run(
        [str(script), "GET", f"/rest/api/3/issue/{issue_key}/transitions"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "jira-request transitions failed").strip()
        raise SystemExit(message)
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        return []
    transitions = payload.get("transitions") or []
    if not isinstance(transitions, list):
        return []
    slim: list[dict[str, Any]] = []
    for item in transitions:
        if not isinstance(item, dict):
            continue
        slim.append(
            {
                "id": item.get("id"),
                "name": item.get("name") or "",
                "to_status": ((item.get("to") or {}).get("name") or ""),
            }
        )
    return slim


def normalize_issue(raw: dict[str, Any], transport: str) -> dict[str, Any]:
    fields = raw.get("fields") if isinstance(raw.get("fields"), dict) else {}
    issue_key = str(raw.get("key") or "").upper()
    description = re.sub(r"\n+", "\n", adf_text(fields.get("description") or "")).strip()
    assignee = fields.get("assignee")
    reporter = fields.get("reporter")
    return {
        "issue_key": issue_key,
        "url": browse_base_url(str(raw.get("self") or ""), issue_key),
        "summary": str(fields.get("summary") or ""),
        "status": str((fields.get("status") or {}).get("name") or ""),
        "issuetype": str((fields.get("issuetype") or {}).get("name") or ""),
        "priority": str((fields.get("priority") or {}).get("name") or ""),
        "assignee": display_name(assignee) if assignee else "",
        "reporter": display_name(reporter) if reporter else "",
        "created": str(fields.get("created") or ""),
        "updated": str(fields.get("updated") or ""),
        "labels": [str(label) for label in (fields.get("labels") or [])],
        "description": description,
        "comments": slim_comments(fields),
        "comment_count": len(slim_comments(fields)),
        "transitions": [],
        "fields": fields,
        "transport": transport,
        "raw": raw,
    }


def fetch_issue(
    issue_key: str,
    *,
    fields: str = DEFAULT_FIELDS,
    with_transitions: bool = False,
) -> dict[str, Any]:
    raw: dict[str, Any] | None = None
    transport = ""

    if acli_authenticated():
        try:
            raw = fetch_via_acli(issue_key, fields)
            transport = "acli"
        except SystemExit:
            raw = None

    if raw is None:
        raw = fetch_via_jira_api(issue_key, fields)
        transport = "jira-api"

    normalized = normalize_issue(raw, transport)
    if with_transitions:
        try:
            normalized["transitions"] = fetch_transitions(issue_key)
        except SystemExit:
            normalized["transitions"] = []
    return normalized


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch normalized Jira issue context.")
    parser.add_argument("issue", nargs="?", help="Issue key (PROJ-123) or browse URL.")
    parser.add_argument("--url", help="Atlassian browse URL containing the issue key.")
    parser.add_argument(
        "--fields",
        default=DEFAULT_FIELDS,
        help="Comma-separated Jira fields for acli/jira-api fetch.",
    )
    parser.add_argument(
        "--with-transitions",
        action="store_true",
        help="Include available transitions via jira-request (REST fallback auth).",
    )
    parser.add_argument("--output", "-o", help="Write JSON to this path instead of stdout.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    source = args.url or args.issue
    if not source:
        parser.error("issue key or --url is required")

    issue_key = parse_issue_key(source)
    payload = fetch_issue(issue_key, fields=args.fields, with_transitions=args.with_transitions)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
