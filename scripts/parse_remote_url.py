#!/usr/bin/env python3
"""Parse Git remote URLs into host and namespace/project path."""
from __future__ import annotations

import re
import sys
from urllib.parse import urlparse


SSH_RE = re.compile(
    r"^(?:(?P<user>[^@]+)@)?(?P<host>[^:\/]+):(?P<path>.+?)(?:\.git)?$"
)


class RemoteUrlParseError(ValueError):
    """Raised when a remote URL cannot be parsed."""


def normalize_git_path(path: str) -> str:
    if path.endswith(".git"):
        path = path[:-4]
    return path.strip("/")


def parse_remote_url(remote_url: str) -> tuple[str, str]:
    """Return ``(host, project_path)`` for HTTPS, SSH, and scp-style remotes."""
    remote_url = remote_url.strip()
    if not remote_url:
        raise RemoteUrlParseError("empty remote URL")

    if "://" in remote_url:
        parsed = urlparse(remote_url)
        if parsed.hostname and parsed.path:
            return parsed.hostname, normalize_git_path(parsed.path.lstrip("/"))

    ssh_match = SSH_RE.match(remote_url)
    if ssh_match:
        return ssh_match.group("host"), normalize_git_path(ssh_match.group("path"))

    raise RemoteUrlParseError(f"unsupported remote URL format: {remote_url}")


def tail_path_segments(project_path: str, count: int = 2) -> tuple[str, ...] | None:
    parts = [part for part in project_path.split("/") if part]
    if len(parts) < count:
        return None
    return tuple(parts[-count:])


def _self_test() -> None:
    cases = [
        ("git@github.com:org/repo.git", ("github.com", "org/repo")),
        ("https://github.com/org/repo.git", ("github.com", "org/repo")),
        ("git@gitlab.example.com:group/sub/project.git", ("gitlab.example.com", "group/sub/project")),
        ("ssh://git@gitlab.com/group/project.git", ("gitlab.com", "group/project")),
        ("git@github.com-personal:robertolopezlopez/agent-skills.git", ("github.com-personal", "robertolopezlopez/agent-skills")),
    ]
    for url, expected in cases:
        got = parse_remote_url(url)
        if got != expected:
            raise SystemExit(f"parse_remote_url({url!r}) = {got!r}, expected {expected!r}")
    assert tail_path_segments("group/sub/project") == ("sub", "project")
    assert tail_path_segments("org") is None
    print("parse_remote_url self-test: ok")


def main() -> int:
    if len(sys.argv) == 2 and sys.argv[1] in {"--self-test", "-t"}:
        _self_test()
        return 0
    if len(sys.argv) != 2:
        print("usage: parse_remote_url.py REMOTE_URL | --self-test", file=sys.stderr)
        return 2
    host, project_path = parse_remote_url(sys.argv[1])
    print(f"host={host}")
    print(f"project_path={project_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
