#!/usr/bin/env python3
"""Monitor one CircleCI workflow lineage with conservative infrastructure retries."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse


UUID_RE = re.compile(r"^[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$")
FAILED = {"failed", "failing", "error", "timedout", "infrastructure_fail"}
IGNORED = {"canceled", "not_run"}
ENVIRONMENT = {"timedout", "infrastructure_fail"}
TRANSIENT_OUTPUT_RE = re.compile(
    r"Exceeded timeout of \d+ ms for a test|"
    r"\b(?:ECONNRESET|ETIMEDOUT|EAI_AGAIN)\b|"
    r"connection reset by peer|socket hang up|TLS handshake timeout|"
    r"temporary failure in name resolution",
    re.IGNORECASE,
)


def resolve_workflow_id(value: str) -> str:
    if UUID_RE.fullmatch(value):
        return value
    workflow_id = parse_qs(urlparse(value).query).get("workflowId", [""])[0]
    if UUID_RE.fullmatch(workflow_id):
        return workflow_id
    raise ValueError("expected a workflow UUID or CircleCI URL containing workflowId")


def find_pr_rebase() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "gh-pr-rebase/scripts/check_pr.py"
        if candidate.is_file():
            return candidate
    raise RuntimeError("gh-pr-rebase not found; sync the gh-pr-rebase skill")


def inspect_pr(branch: str, helper=None, run=subprocess.run):
    completed = run(
        [str(helper or find_pr_rebase()), branch],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def classify_failed_jobs(jobs, fetch_detail, fetch_output=lambda _detail: ""):
    result = {"environment": [], "transient": [], "code": [], "ambiguous": []}
    for job in jobs:
        status = str(job.get("status", "")).lower()
        if status in IGNORED or status not in FAILED:
            continue
        name = job.get("name") or str(job.get("job_number", "unknown"))
        try:
            detail = fetch_detail(job) or {}
        except (RuntimeError, subprocess.SubprocessError, json.JSONDecodeError):
            result["ambiguous"].append(name)
            continue
        combined = {**job, **detail}
        markers = {
            str(combined.get("status", "")).lower(),
            str(combined.get("outcome", "")).lower(),
        }
        if combined.get("timedout") is True or combined.get("infrastructure_fail") is True:
            markers.add("timedout" if combined.get("timedout") else "infrastructure_fail")
        if markers & ENVIRONMENT:
            result["environment"].append(name)
            continue
        try:
            output = fetch_output(detail)
        except (RuntimeError, subprocess.SubprocessError, json.JSONDecodeError):
            result["ambiguous"].append(name)
            continue
        if TRANSIENT_OUTPUT_RE.search(output):
            result["transient"].append(name)
        elif str(detail.get("outcome", "")).lower() == "failed":
            result["code"].append(name)
        else:
            result["ambiguous"].append(name)
    return result


def find_cli_launcher() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "circleci/scripts/circleci-cli"
        if candidate.is_file():
            return candidate
    raise RuntimeError("circleci-cli not found; sync the circleci skill")


def normalize_cli_status(resource, running_failure="failed") -> str:
    phase = str(resource.get("phase") or "").lower()
    raw = str(
        resource.get("outcome")
        or resource.get("current_outcome")
        or resource.get("status")
        or ""
    ).lower()
    status = {"succeeded": "success", "errored": "error"}.get(raw, raw)
    if phase in {"started", "running"}:
        return running_failure if status in FAILED else "running"
    if status:
        return status
    return "unknown" if phase == "ended" else phase or "unknown"


class CLIClient:
    def __init__(self, launcher: Path, run=subprocess.run):
        self.launcher = launcher
        self.run = run
        self.workflows = {}

    def command(self, *args, json_output=True):
        completed = self.run(
            [str(self.launcher), *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(completed.stdout) if json_output else None

    def fetch_workflow(self, workflow_id: str):
        workflow = self.command("workflow", "get", workflow_id, "--json")
        workflow["status"] = normalize_cli_status(workflow, "failing")
        self.workflows[workflow_id] = workflow
        return workflow

    def fetch_jobs(self, workflow_id: str):
        workflow = self.workflows.get(workflow_id) or self.fetch_workflow(workflow_id)
        return [
            {**job, "status": normalize_cli_status(job)}
            for job in workflow.get("jobs", [])
        ]

    def fetch_job_detail(self, job):
        job_id = job.get("id")
        if not job_id:
            return {}
        detail = self.command("job", "get", str(job_id), "--json")
        detail.setdefault("outcome", normalize_cli_status(detail))
        return detail

    def fetch_failed_output(self, detail) -> str:
        job_id = detail.get("id")
        if not job_id:
            return ""
        messages = []
        executions = detail.get("executions") or [{"index": 0}]
        for execution in executions:
            index = execution.get("index", 0)
            args = ["job", "output", "list", str(job_id)]
            if index:
                args.extend(("--execution", str(index)))
            payload = self.command(*args, "--json")
            messages.extend(
                str(step.get("output", ""))
                for step in payload.get("steps", [])
                if normalize_cli_status(step) in FAILED
                or step.get("exit_code") not in {None, 0}
            )
        return "\n".join(messages)

    def cancel_workflow(self, workflow_id: str):
        self.command(
            "workflow", "cancel", workflow_id, "--force", json_output=False
        )

    def rerun_workflow(self, workflow_id: str) -> str:
        rerun = self.command(
            "workflow", "rerun", workflow_id, "--from-failed", "--json"
        )
        next_id = rerun.get("workflow_id")
        if not next_id:
            raise RuntimeError("rerun response omitted workflow_id")
        return next_id


class Client:
    def __init__(self, helper: Path):
        self.helper = helper

    def request(self, method: str, path: str, body: Path | None = None, root: str | None = None):
        command = [str(self.helper)]
        if root:
            command.append(root)
        command.extend((method, path))
        if body:
            command.append(str(body))
        completed = subprocess.run(command, check=True, capture_output=True, text=True)
        return json.loads(completed.stdout)

    def request_url(self, url: str):
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise RuntimeError("invalid CircleCI output URL")
        path = parsed.path or "/"
        if parsed.query:
            path += f"?{parsed.query}"
        return self.request("GET", path, root=f"{parsed.scheme}://{parsed.netloc}")


def build_client(request_helper: Path | None, find_cli=find_cli_launcher):
    if request_helper:
        return Client(request_helper)
    return CLIClient(find_cli())


def fetch_jobs(client: Client, workflow_id: str):
    if hasattr(client, "fetch_jobs"):
        return client.fetch_jobs(workflow_id)
    items = []
    token = None
    while True:
        query = f"?{urlencode({'page-token': token})}" if token else ""
        page = client.request("GET", f"/workflow/{workflow_id}/job{query}")
        items.extend(page.get("items", []))
        token = page.get("next_page_token")
        if not token:
            return items


def fetch_job_detail(client: Client, job):
    if hasattr(client, "fetch_job_detail"):
        return client.fetch_job_detail(job)
    slug = job.get("project_slug")
    number = job.get("job_number")
    if not slug or number is None:
        return {}
    return client.request(
        "GET", f"/project/{slug}/{number}", root="https://circleci.com/api/v1.1"
    )


def fetch_failed_output(client: Client, detail) -> str:
    if hasattr(client, "fetch_failed_output"):
        return client.fetch_failed_output(detail)
    messages = []
    for step in detail.get("steps", []):
        for action in step.get("actions", []):
            failed = (
                action.get("failed") is True
                or str(action.get("status", "")).lower() == "failed"
                or action.get("exit_code") not in {None, 0}
            )
            output_url = action.get("output_url")
            if not failed or not output_url:
                continue
            payload = client.request_url(output_url)
            records = payload if isinstance(payload, list) else [payload]
            messages.extend(
                str(record.get("message", ""))
                for record in records
                if isinstance(record, dict)
            )
    return "\n".join(messages)


def rerun_workflow(client: Client, workflow_id: str, body: Path) -> str:
    if hasattr(client, "rerun_workflow"):
        return client.rerun_workflow(workflow_id)
    rerun = client.request("POST", f"/workflow/{workflow_id}/rerun", body)
    next_id = rerun.get("workflow_id")
    if not next_id:
        raise RuntimeError("rerun response omitted workflow_id")
    return next_id


def fetch_workflow(client: Client, workflow_id: str):
    if hasattr(client, "fetch_workflow"):
        return client.fetch_workflow(workflow_id)
    return client.request("GET", f"/workflow/{workflow_id}")


def cancel_workflow(client: Client, workflow_id: str):
    if hasattr(client, "cancel_workflow"):
        return client.cancel_workflow(workflow_id)
    return client.request("POST", f"/workflow/{workflow_id}/cancel")


def monitor(
    client: Client,
    workflow_id: str,
    retry_infra: bool,
    timeout: int,
    poll: int,
    pr_branch: str | None = None,
    pr_poll: int = 300,
    fetch_pr=None,
    clock=None,
    sleep=None,
):
    clock = clock or time.monotonic
    sleep = sleep or time.sleep
    fetch_pr = fetch_pr or inspect_pr
    started = clock()
    deadline = started + timeout
    next_pr_check = started
    lineage = [workflow_id]
    attempt = 1
    last_status = None
    rerun_body = Path(__file__).parents[1] / "assets/rerun-from-failed.json"

    while clock() < deadline:
        now = clock()
        if pr_branch and now >= next_pr_check:
            pr = fetch_pr(pr_branch)
            next_pr_check = now + pr_poll
            if pr.get("status") == "conflict":
                return {
                    "status": "pr_conflict",
                    "attempts": attempt,
                    "workflow_ids": lineage,
                    "pr": pr,
                    "remaining_seconds": max(0, int(deadline - clock())),
                }
        workflow = fetch_workflow(client, workflow_id)
        status = str(workflow.get("status", "unknown")).lower()
        if status != last_status:
            print(f"attempt={attempt} workflow={workflow_id} status={status}", file=sys.stderr)
            last_status = status
        if status == "success":
            return {"status": status, "attempts": attempt, "workflow_ids": lineage}
        if status in {"unauthorized", "canceled", "not_run"}:
            return {"status": status, "attempts": attempt, "workflow_ids": lineage}

        jobs = fetch_jobs(client, workflow_id)
        classification = classify_failed_jobs(
            jobs,
            lambda job: fetch_job_detail(client, job),
            lambda detail: fetch_failed_output(client, detail),
        )
        retryable = (
            retry_infra
            and (classification["environment"] or classification["transient"])
            and not classification["code"]
            and not classification["ambiguous"]
        )
        if status in FAILED - {"failing"} or (
            status == "failing" and classification["code"]
        ):
            if not retryable:
                return {
                    "status": status,
                    "attempts": attempt,
                    "workflow_ids": lineage,
                    "classification": classification,
                }
            workflow_id = rerun_workflow(client, workflow_id, rerun_body)
            lineage.append(workflow_id)
            attempt += 1
            last_status = None
            continue

        if status == "failing" and retryable:
            cancel_workflow(client, workflow_id)
            while clock() < deadline:
                canceled = fetch_workflow(client, workflow_id)
                if str(canceled.get("status", "")).lower() == "canceled":
                    break
                sleep(min(poll, max(0, deadline - clock())))
            else:
                return {"status": "timeout", "attempts": attempt, "workflow_ids": lineage}
            workflow_id = rerun_workflow(client, workflow_id, rerun_body)
            lineage.append(workflow_id)
            attempt += 1
            last_status = None
            continue
        sleep(min(poll, max(0, deadline - clock())))

    return {"status": "timeout", "attempts": attempt, "workflow_ids": lineage}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workflow")
    parser.add_argument("--retry-infra", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=7200)
    parser.add_argument("--poll-seconds", type=int, default=60)
    parser.add_argument("--pr-branch")
    parser.add_argument("--request-helper", type=Path)
    args = parser.parse_args()
    try:
        result = monitor(
            build_client(args.request_helper),
            resolve_workflow_id(args.workflow),
            args.retry_infra,
            args.timeout_seconds,
            args.poll_seconds,
            pr_branch=args.pr_branch,
        )
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print(json.dumps(result, separators=(",", ":")))
    return 0 if result["status"] == "success" else 3


if __name__ == "__main__":
    raise SystemExit(main())
