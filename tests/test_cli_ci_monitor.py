import importlib.util
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
        self.assertEqual(result["code"], ["test"])
        self.assertEqual(result["ambiguous"], ["unknown"])

    def test_cancels_failing_workflow_then_follows_rerun_id(self):
        module = load_module()

        class FakeClient:
            def __init__(self):
                self.old_reads = 0

            def request(self, method, path, body=None, root=None):
                if method == "GET" and path == "/workflow/old":
                    self.old_reads += 1
                    return {"status": "failing" if self.old_reads == 1 else "canceled"}
                if method == "GET" and path == "/workflow/old/job":
                    return {"items": [{"name": "timeout", "status": "failed", "job_number": 1, "project_slug": "gh/snyk/cli"}]}
                if root:
                    return {"outcome": "timedout"}
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
