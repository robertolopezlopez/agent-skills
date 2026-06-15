#!/usr/bin/env python3
"""Resolve remote-derived project identity from a Git repository or explicit remote URL."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import quote

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS_ROOT = SCRIPT_DIR.parent
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from parse_remote_url import RemoteUrlParseError, parse_remote_url


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
    try:
        host, project_path = parse_remote_url(remote_url)
    except RemoteUrlParseError as exc:
        raise SystemExit(str(exc)) from exc
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
