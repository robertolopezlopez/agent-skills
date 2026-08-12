#!/usr/bin/env python3
"""Check one GitHub PR for merge conflicts."""

import argparse
import json
import subprocess


FIELDS = "number,url,headRefName,baseRefName,mergeable,mergeStateStatus"


def inspect_pr(ref, run=subprocess.run):
    result = run(
        ["gh", "pr", "view", ref, "--json", FIELDS],
        check=True,
        capture_output=True,
        text=True,
    )
    pr = json.loads(result.stdout)
    if pr.get("mergeable") == "CONFLICTING" or pr.get("mergeStateStatus") == "DIRTY":
        pr["status"] = "conflict"
    elif pr.get("mergeable") == "MERGEABLE":
        pr["status"] = "clean"
    else:
        pr["status"] = "unknown"
    return pr


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pr")
    args = parser.parse_args()
    try:
        result = inspect_pr(args.pr)
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
