#!/usr/bin/env python3
"""Resolve remote-derived project identity from a Git repository or explicit remote URL."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from urllib.parse import quote, urlparse


SSH_RE = re.compile(
    r"^(?:(?P<user>[^@]+)@)?(?P<host>[^:\/]+):(?P<path>.+?)(?:\.git)?$"
)


@dataclass
class ProjectIdentity:
    remote: str | None
    remote_url: str
    host: str
    project_path: str
    encoded_project_path: str
    project_id: int | None = None


def run(*args: str) -> str:
    result = subprocess.run(
        list(args),
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def get_remote_url(remote: str) -> str:
    try:
        url = run("git", "config", "--get", f"remote.{remote}.url")
    except subprocess.CalledProcessError as exc:
        raise SystemExit(
            f"Failed to read remote '{remote}'. Run inside a git repo or pass --remote-url."
        ) from exc
    if not url:
        raise SystemExit(f"Remote '{remote}' has no configured URL.")
    return url


def normalize_path(path: str) -> str:
    if path.endswith(".git"):
        path = path[:-4]
    return path.strip("/")


def parse_remote_url(remote_url: str) -> tuple[str, str]:
    remote_url = remote_url.strip()

    if "://" in remote_url:
        parsed = urlparse(remote_url)
        if parsed.hostname and parsed.path:
            return parsed.hostname, normalize_path(parsed.path.lstrip("/"))

    ssh_match = SSH_RE.match(remote_url)
    if ssh_match:
        return ssh_match.group("host"), normalize_path(ssh_match.group("path"))

    raise SystemExit(f"Unsupported remote URL format: {remote_url}")


def fetch_gitlab_project_id(host: str, encoded_project_path: str) -> int:
    try:
        output = run(
            "glab",
            "api",
            f"/projects/{encoded_project_path}",
            "--hostname",
            host,
        )
    except FileNotFoundError as exc:
        raise SystemExit("`glab` is required to fetch a GitLab numeric project ID.") from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() if exc.stderr else "glab api request failed."
        raise SystemExit(stderr) from exc

    try:
        payload = json.loads(output)
    except json.JSONDecodeError as exc:
        raise SystemExit("Failed to parse `glab api` JSON output.") from exc

    project_id = payload.get("id")
    if not isinstance(project_id, int):
        raise SystemExit("GitLab API response did not contain an integer `id`.")
    return project_id


def resolve_identity(remote: str | None, remote_url: str, fetch_id: bool) -> ProjectIdentity:
    host, project_path = parse_remote_url(remote_url)
    encoded_project_path = quote(project_path, safe="")
    project_id = fetch_gitlab_project_id(host, encoded_project_path) if fetch_id else None
    return ProjectIdentity(
        remote=remote,
        remote_url=remote_url,
        host=host,
        project_path=project_path,
        encoded_project_path=encoded_project_path,
        project_id=project_id,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remote", default="origin", help="Git remote name to inspect.")
    parser.add_argument("--remote-url", help="Explicit remote URL. Skips local git lookup.")
    parser.add_argument(
        "--fetch-id",
        action="store_true",
        help="Fetch the GitLab numeric project ID with glab api.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    args = parser.parse_args()

    remote = None if args.remote_url else args.remote
    remote_url = args.remote_url or get_remote_url(args.remote)
    identity = resolve_identity(remote, remote_url, args.fetch_id)

    if args.json:
        print(json.dumps(asdict(identity), indent=2, sort_keys=True))
        return 0

    print(f"remote={identity.remote or '<provided>'}")
    print(f"remote_url={identity.remote_url}")
    print(f"host={identity.host}")
    print(f"project_path={identity.project_path}")
    print(f"encoded_project_path={identity.encoded_project_path}")
    if identity.project_id is not None:
        print(f"project_id={identity.project_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
