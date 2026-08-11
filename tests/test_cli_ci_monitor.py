import importlib.util
import json
import subprocess
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).parents[1]
    / "skills/cli/cli-ci-monitor/scripts/monitor_workflow.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("monitor_workflow", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class MonitorWorkflowTest(unittest.TestCase):
    def test_resolves_workflow_id_from_circleci_url(self):
        module = load_module()
        workflow_id = "c444ed26-4e07-4bc0-9e16-37e884566f0d"
        url = f"https://app.circleci.com/pipelines/gh/snyk/cli/38962/details?job=x&workflowId={workflow_id}"
        self.assertEqual(module.resolve_workflow_id(url), workflow_id)

    def test_resolves_pr_from_branch_with_local_gh(self):
        module = load_module()
        calls = []

        def run(command, **kwargs):
            calls.append((command, kwargs))
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=json.dumps({"number": 123, "url": "https://github.com/snyk/cli/pull/123"}),
            )

        result = module.resolve_pr("feature/branch", run=run)

        self.assertEqual(result["number"], 123)
        self.assertEqual(calls[0][0][:4], ["gh", "pr", "view", "feature/branch"])

    def test_returns_pr_conflict_with_remaining_deadline(self):
        module = load_module()
        result = module.monitor(
            object(),
            "workflow",
            False,
            timeout=7200,
            poll=60,
            pr_branch="feature/branch",
            fetch_pr=lambda _branch: {
                "number": 123,
                "url": "https://github.com/snyk/cli/pull/123",
                "mergeable": "CONFLICTING",
            },
            clock=lambda: 100,
        )

        self.assertEqual(result["status"], "pr_conflict")
        self.assertEqual(result["pr"]["number"], 123)
        self.assertEqual(result["remaining_seconds"], 7200)

    def test_checks_pr_every_five_minutes_while_monitoring_ci(self):
        module = load_module()
        now = 0
        checks = []

        class FakeClient:
            def request(self, method, path, body=None, root=None):
                if path == "/workflow/workflow":
                    return {"status": "success" if now >= 601 else "running"}
                if path == "/workflow/workflow/job":
                    return {"items": []}
                raise AssertionError((method, path, body, root))

        def clock():
            return now

        def sleep(seconds):
            nonlocal now
            now += seconds

        def fetch_pr(branch):
            checks.append((now, branch))
            return {"number": 123, "mergeable": "MERGEABLE"}

        result = module.monitor(
            FakeClient(),
            "workflow",
            False,
            timeout=700,
            poll=60,
            pr_branch="feature/branch",
            fetch_pr=fetch_pr,
            clock=clock,
            sleep=sleep,
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(checks, [(0, "feature/branch"), (300, "feature/branch"), (600, "feature/branch")])

    def test_classifies_only_structured_infrastructure_evidence_as_retryable(self):
        module = load_module()
        jobs = [
            {"name": "timeout", "status": "failed", "job_number": 1},
            {"name": "test", "status": "failed", "job_number": 2},
            {"name": "unknown", "status": "failed", "job_number": 3},
            {"name": "downstream", "status": "canceled", "job_number": 4},
        ]
        details = {
            1: {"outcome": "timedout", "timedout": True},
            2: {"outcome": "failed"},
            3: {},
        }

        result = module.classify_failed_jobs(jobs, lambda job: details[job["job_number"]])

        self.assertEqual(result["environment"], ["timeout"])
        self.assertEqual(result["transient"], [])
        self.assertEqual(result["code"], ["test"])
        self.assertEqual(result["ambiguous"], ["unknown"])

    def test_classifies_jest_test_timeout_output_as_transient(self):
        module = load_module()
        jobs = [{"name": "acceptance", "status": "failed", "job_number": 1}]

        result = module.classify_failed_jobs(
            jobs,
            lambda _job: {"outcome": "failed"},
            lambda _detail: 'thrown: "Exceeded timeout of 120000 ms for a test."',
        )

        self.assertEqual(result["transient"], ["acceptance"])
        self.assertEqual(result["code"], [])

    def test_keeps_ordinary_test_failure_classified_as_code(self):
        module = load_module()
        jobs = [{"name": "acceptance", "status": "failed", "job_number": 1}]

        result = module.classify_failed_jobs(
            jobs,
            lambda _job: {"outcome": "failed"},
            lambda _detail: "Expected true, received false",
        )

        self.assertEqual(result["transient"], [])
        self.assertEqual(result["code"], ["acceptance"])

    def test_keeps_failed_output_fetch_errors_ambiguous(self):
        module = load_module()
        jobs = [{"name": "acceptance", "status": "failed", "job_number": 1}]

        def fail_output(_detail):
            raise RuntimeError("output unavailable")

        result = module.classify_failed_jobs(
            jobs,
            lambda _job: {"outcome": "failed"},
            fail_output,
        )

        self.assertEqual(result["ambiguous"], ["acceptance"])
        self.assertEqual(result["code"], [])

    def test_retries_transient_failure_then_follows_rerun_id(self):
        module = load_module()

        class FakeClient:
            def __init__(self):
                self.old_reads = 0

            def request_url(self, url):
                self.assert_url = url
                return [{"message": "Exceeded timeout of 120000 ms for a test."}]

            def request(self, method, path, body=None, root=None):
                if method == "GET" and path == "/workflow/old":
                    self.old_reads += 1
                    return {"status": "failing" if self.old_reads == 1 else "canceled"}
                if method == "GET" and path == "/workflow/old/job":
                    return {"items": [{"name": "timeout", "status": "failed", "job_number": 1, "project_slug": "gh/snyk/cli"}]}
                if root == "https://circleci.com/api/v1.1":
                    return {
                        "outcome": "failed",
                        "steps": [{"actions": [{
                            "failed": True,
                            "output_url": "https://output.example/log?token=secret",
                        }]}],
                    }
                if method == "POST" and path == "/workflow/old/cancel":
                    return {}
                if method == "POST" and path == "/workflow/old/rerun":
                    return {"workflow_id": "new"}
                if method == "GET" and path == "/workflow/new":
                    return {"status": "success"}
                if method == "GET" and path == "/workflow/new/job":
                    return {"items": []}
                raise AssertionError((method, path, root))

        result = module.monitor(FakeClient(), "old", True, timeout=5, poll=0)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["workflow_ids"], ["old", "new"])


if __name__ == "__main__":
    unittest.main()
