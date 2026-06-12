#!/usr/bin/env python3
"""Fetch GitHub issues or pull requests via gh and emit normalized JSON."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ISSUE_URL_RE = re.compile(
    r"^https?://[^/]+/(?P<owner>[^/]+)/(?P<repo>[^/]+)/issues/(?P<number>\d+)/?$",
    re.IGNORECASE,
)
PR_URL_RE = re.compile(
    r"^https?://[^/]+/(?P<owner>[^/]+)/(?P<repo>[^/]+)/pull/(?P<number>\d+)/?$",
    re.IGNORECASE,
)

REVIEW_THREADS_QUERY = """
query($owner: String!, $repo: String!, $number: Int!, $after: String) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      reviewThreads(first: 100, after: $after) {
        pageInfo { hasNextPage endCursor }
        totalCount
        nodes {
          id
          isResolved
          isCollapsed
          comments(first: 100) {
            nodes {
              id
              url
              body
              createdAt
              path
              line
              originalLine
              diffHunk
              author { login }
            }
          }
        }
      }
    }
  }
}
""".strip()


def gh_cmd(*args: str, repo: str | None = None) -> Any:
    command = ["gh", *args]
    if repo:
        command.extend(["-R", repo])
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "gh command failed").strip()
        raise SystemExit(message)
    if not result.stdout.strip():
        return None
    return json.loads(result.stdout)


def gh_api_list(path: str) -> list[Any]:
    result = subprocess.run(
        ["gh", "api", path, "--paginate"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "gh api failed").strip()
        raise SystemExit(message)
    raw = result.stdout.strip()
    if not raw:
        return []
    payload = json.loads(raw)
    if isinstance(payload, list):
        return payload
    return [payload]


def gh_graphql(query: str, variables: dict[str, Any]) -> dict[str, Any]:
    command = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        if isinstance(value, bool):
            command.extend(["-F", f"{key}={str(value).lower()}"])
        elif isinstance(value, int):
            command.extend(["-F", f"{key}={value}"])
        elif value is None:
            continue
        else:
            command.extend(["-f", f"{key}={value}"])
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "gh api graphql failed").strip()
        raise SystemExit(message)
    payload = json.loads(result.stdout)
    if isinstance(payload, dict) and payload.get("errors"):
        errors = payload["errors"]
        message = "; ".join(str(item.get("message") or item) for item in errors)
        raise SystemExit(message or "gh api graphql returned errors")
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        raise SystemExit("gh api graphql returned unexpected payload")
    return data


def parse_url(url: str) -> tuple[str, str, str, int]:
    for pattern, object_type in ((ISSUE_URL_RE, "issue"), (PR_URL_RE, "pull_request")):
        match = pattern.match(url.strip())
        if match:
            return (
                match.group("owner"),
                match.group("repo"),
                object_type,
                int(match.group("number")),
            )
    raise SystemExit(f"unsupported GitHub URL shape: {url}")


def repo_slug(owner: str, repo: str) -> str:
    return f"{owner}/{repo}"


def label_names(raw: Any) -> list[str]:
    if not raw:
        return []
    if isinstance(raw, list):
        names: list[str] = []
        for item in raw:
            if isinstance(item, dict):
                name = item.get("name")
                if name:
                    names.append(str(name))
            elif item:
                names.append(str(item))
        return names
    return [str(raw)]


def login_name(raw: Any) -> str:
    if isinstance(raw, dict):
        return str(raw.get("login") or raw.get("name") or "")
    return str(raw or "")


def slim_conversation_comment(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": raw.get("id"),
        "url": raw.get("html_url") or "",
        "author": login_name(raw.get("user")),
        "body": raw.get("body") or "",
        "created_at": raw.get("created_at") or "",
    }


def slim_review(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": raw.get("id"),
        "state": raw.get("state") or "",
        "author": login_name(raw.get("user")),
        "body": raw.get("body") or "",
        "submitted_at": raw.get("submitted_at") or "",
        "commit_id": raw.get("commit_id") or "",
        "html_url": raw.get("html_url") or "",
    }


def slim_review_comment(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": raw.get("id"),
        "url": raw.get("html_url") or "",
        "author": login_name(raw.get("user")),
        "body": raw.get("body") or "",
        "path": raw.get("path") or "",
        "line": raw.get("line"),
        "original_line": raw.get("original_line"),
        "side": raw.get("side") or "",
        "created_at": raw.get("created_at") or "",
        "in_reply_to_id": raw.get("in_reply_to_id"),
    }


def slim_thread_comment(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": raw.get("id") or "",
        "url": raw.get("url") or "",
        "author": login_name(raw.get("author")),
        "body": raw.get("body") or "",
        "created_at": raw.get("createdAt") or "",
        "path": raw.get("path") or "",
        "line": raw.get("line"),
        "original_line": raw.get("originalLine"),
        "diff_hunk": raw.get("diffHunk") or "",
    }


def normalize_review_thread(raw: dict[str, Any]) -> dict[str, Any]:
    comments_raw = ((raw.get("comments") or {}).get("nodes") or [])
    comments = [slim_thread_comment(item) for item in comments_raw if isinstance(item, dict)]
    return {
        "thread_id": raw.get("id") or "",
        "is_resolved": bool(raw.get("isResolved")),
        "is_collapsed": bool(raw.get("isCollapsed")),
        "comment_count": len(comments),
        "comments": comments,
    }


def fetch_review_threads(owner: str, repo: str, number: int) -> list[dict[str, Any]]:
    threads: list[dict[str, Any]] = []
    after: str | None = None
    while True:
        variables: dict[str, Any] = {
            "owner": owner,
            "repo": repo,
            "number": number,
        }
        if after:
            variables["after"] = after
        data = gh_graphql(REVIEW_THREADS_QUERY, variables)
        pull_request = ((data.get("repository") or {}).get("pullRequest") or {})
        review_threads = pull_request.get("reviewThreads") or {}
        nodes = review_threads.get("nodes") or []
        for node in nodes:
            if isinstance(node, dict):
                threads.append(normalize_review_thread(node))
        page_info = review_threads.get("pageInfo") or {}
        if page_info.get("hasNextPage"):
            after = page_info.get("endCursor")
            if not after:
                break
            continue
        break
    return threads


def summarize_review_threads(threads: list[dict[str, Any]]) -> dict[str, int]:
    unresolved = sum(1 for thread in threads if not thread.get("is_resolved"))
    return {
        "review_thread_count": len(threads),
        "unresolved_review_thread_count": unresolved,
        "resolved_review_thread_count": len(threads) - unresolved,
    }


def normalize_issue(data: dict[str, Any], owner: str, repo: str) -> dict[str, Any]:
    number = int(data.get("number") or 0)
    canonical = data.get("url") or f"https://github.com/{owner}/{repo}/issues/{number}"
    return {
        "repository_owner": owner,
        "repository_name": repo,
        "object_type": "issue",
        "object_number": number,
        "canonical_url": canonical,
        "state": data.get("state") or "",
        "title": data.get("title") or "",
        "body": data.get("body") or "",
        "labels": label_names(data.get("labels")),
        "assignees": [login_name(a) for a in data.get("assignees") or [] if login_name(a)],
        "author": login_name(data.get("author")),
        "created_at": data.get("createdAt") or "",
        "updated_at": data.get("updatedAt") or "",
    }


def normalize_pull_request(data: dict[str, Any], owner: str, repo: str) -> dict[str, Any]:
    number = int(data.get("number") or 0)
    canonical = data.get("url") or f"https://github.com/{owner}/{repo}/pull/{number}"
    base = data.get("baseRefName") or ""
    head = data.get("headRefName") or ""
    draft = data.get("isDraft")
    if draft is None:
        draft = data.get("draft")
    return {
        "repository_owner": owner,
        "repository_name": repo,
        "object_type": "pull_request",
        "object_number": number,
        "pr_number": number,
        "canonical_url": canonical,
        "state": data.get("state") or "",
        "title": data.get("title") or "",
        "body": data.get("body") or "",
        "labels": label_names(data.get("labels")),
        "assignees": [],
        "author": login_name(data.get("author")),
        "created_at": data.get("createdAt") or "",
        "updated_at": data.get("updatedAt") or "",
        "source_branch": head,
        "target_branch": base,
        "draft": bool(draft),
    }


def infer_repo_from_remote() -> tuple[str, str] | None:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    url = result.stdout.strip()
    if url.endswith(".git"):
        url = url[:-4]
    owner = ""
    repo = ""
    if "://" in url:
        parsed = urlparse(url)
        parts = [part for part in parsed.path.strip("/").split("/") if part]
        if len(parts) >= 2:
            owner, repo = parts[-2], parts[-1]
    elif ":" in url:
        path = url.split(":", 1)[1].strip("/")
        parts = [part for part in path.split("/") if part]
        if len(parts) >= 2:
            owner, repo = parts[-2], parts[-1]
    if owner and repo:
        return owner, repo
    return None


def fetch_issue(
    number: int,
    owner: str | None,
    repo: str | None,
    *,
    full: bool = False,
) -> dict[str, Any]:
    del full
    repo_flag = repo_slug(owner, repo) if owner and repo else None
    fields = "number,title,body,state,url,author,labels,assignees,createdAt,updatedAt"
    data = gh_cmd("issue", "view", str(number), "--json", fields, repo=repo_flag)
    if not isinstance(data, dict):
        raise SystemExit("gh issue view returned unexpected payload")
    if not owner or not repo:
        inferred = infer_repo_from_remote()
        if not inferred:
            raise SystemExit("owner/repo required when not in a git checkout with origin")
        owner, repo = inferred
    return normalize_issue(data, owner, repo)


def attach_pr_review_data(
    normalized: dict[str, Any],
    owner: str,
    repo: str,
    number: int,
    *,
    full: bool,
) -> dict[str, Any]:
    normalized["fetch_depth"] = "full" if full else "overview"
    try:
        reviews = gh_api_list(f"repos/{owner}/{repo}/pulls/{number}/reviews")
        comments = gh_api_list(f"repos/{owner}/{repo}/pulls/{number}/comments")
        normalized["reviews"] = [slim_review(item) for item in reviews if isinstance(item, dict)]
        normalized["review_comments"] = [
            slim_review_comment(item) for item in comments if isinstance(item, dict)
        ]
    except SystemExit:
        normalized["reviews"] = []
        normalized["review_comments"] = []

    if not full:
        return normalized

    try:
        conversation = gh_api_list(f"repos/{owner}/{repo}/issues/{number}/comments")
        normalized["conversation_comments"] = [
            slim_conversation_comment(item) for item in conversation if isinstance(item, dict)
        ]
    except SystemExit:
        normalized["conversation_comments"] = []

    try:
        threads = fetch_review_threads(owner, repo, number)
        normalized["review_threads"] = threads
        normalized.update(summarize_review_threads(threads))
    except SystemExit:
        normalized["review_threads"] = []
        normalized.update(
            {
                "review_thread_count": 0,
                "unresolved_review_thread_count": 0,
                "resolved_review_thread_count": 0,
            }
        )
    return normalized


def fetch_pull_request(
    number: int,
    owner: str | None,
    repo: str | None,
    *,
    full: bool = False,
) -> dict[str, Any]:
    repo_flag = repo_slug(owner, repo) if owner and repo else None
    fields = (
        "number,title,body,state,url,author,labels,createdAt,updatedAt,"
        "baseRefName,headRefName,isDraft"
    )
    data = gh_cmd("pr", "view", str(number), "--json", fields, repo=repo_flag)
    if not isinstance(data, dict):
        raise SystemExit("gh pr view returned unexpected payload")
    if not owner or not repo:
        inferred = infer_repo_from_remote()
        if not inferred:
            raise SystemExit("owner/repo required when not in a git checkout with origin")
        owner, repo = inferred
    normalized = normalize_pull_request(data, owner, repo)
    return attach_pr_review_data(normalized, owner, repo, number, full=full)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch normalized GitHub issue or PR context via gh.")
    parser.add_argument("object_type", choices=["issue", "pr", "pull_request"])
    parser.add_argument("number", type=int, nargs="?", help="Issue or PR number.")
    parser.add_argument("--url", help="GitHub issue or pull request URL.")
    parser.add_argument("--owner", help="Repository owner (optional in git checkout).")
    parser.add_argument("--repo", help="Repository name (optional in git checkout).")
    parser.add_argument(
        "--full",
        action="store_true",
        help=(
            "For pull requests: include review threads (GraphQL), conversation comments, "
            "and thread summary counts for github-pr-comment-analysis."
        ),
    )
    parser.add_argument("--output", "-o", help="Write JSON to this path instead of stdout.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    object_type = "pull_request" if args.object_type in {"pr", "pull_request"} else "issue"
    owner = args.owner
    repo = args.repo
    number = args.number

    if args.url:
        parsed_owner, parsed_repo, parsed_type, parsed_number = parse_url(args.url)
        owner = owner or parsed_owner
        repo = repo or parsed_repo
        object_type = parsed_type
        number = parsed_number

    if number is None:
        parser.error("number or --url is required")

    if object_type == "issue":
        payload = fetch_issue(number, owner, repo, full=args.full)
    else:
        payload = fetch_pull_request(number, owner, repo, full=args.full)

    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
