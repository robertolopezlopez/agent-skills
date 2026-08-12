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
    def test_cli_client_gets_and_normalizes_workflow_jobs(self):
        module = load_module()
        calls = []

        def run(command, **kwargs):
            calls.append((command, kwargs))
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=json.dumps(
                    {
                        "id": "workflow",
                        "phase": "started",
                        "current_outcome": "failed",
                        "jobs": [
                            {
                                "id": "job-id",
                                "name": "acceptance",
                                "phase": "ended",
                                "outcome": "failed",
                            }
                        ],
                    }
                ),
            )

        client = module.CLIClient(Path("/circleci-cli"), run=run)

        workflow = client.fetch_workflow("workflow")
        jobs = client.fetch_jobs("workflow")

        self.assertEqual(workflow["status"], "failing")
        self.assertEqual(jobs[0]["status"], "failed")
        self.assertEqual(
            calls,
            [
                (
                    ["/circleci-cli", "workflow", "get", "workflow", "--json"],
                    {"check": True, "capture_output": True, "text": True},
                )
            ],
        )

    def test_normalizes_circleci_cli_terminal_outcomes(self):
        module = load_module()

        self.assertEqual(
            module.normalize_cli_status({"phase": "ended", "outcome": "succeeded"}),
            "success",
        )
        self.assertEqual(
            module.normalize_cli_status({"phase": "ended", "outcome": "errored"}),
            "error",
        )
        self.assertEqual(
            module.normalize_cli_status(
                {"phase": "started", "current_outcome": "succeeded"}
            ),
            "running",
        )

    def test_cli_client_fetches_failed_job_output(self):
        module = load_module()
        calls = []
        responses = [
            {
                "id": "job-id",
                "status": "failed",
                "executions": [{"index": 0}],
            },
            {
                "id": "job-id",
                "steps": [
                    {"name": "checkout", "outcome": "success", "output": "ok"},
                    {
                        "name": "test",
                        "outcome": "failed",
                        "exit_code": 1,
                        "output": 'thrown: "Exceeded timeout of 120000 ms for a test."',
                    },
                ],
            },
        ]

        def run(command, **_kwargs):
            calls.append(command)
            return subprocess.CompletedProcess(command, 0, stdout=json.dumps(responses.pop(0)))

        client = module.CLIClient(Path("/circleci-cli"), run=run)
        detail = client.fetch_job_detail({"id": "job-id"})
        output = client.fetch_failed_output(detail)

        self.assertIn("Exceeded timeout", output)
        self.assertEqual(
            calls,
            [
                ["/circleci-cli", "job", "get", "job-id", "--json"],
                ["/circleci-cli", "job", "output", "list", "job-id", "--json"],
            ],
        )

    def test_cli_client_fetches_output_from_parallel_executions(self):
        module = load_module()
        calls = []

        def run(command, **_kwargs):
            calls.append(command)
            execution = (
                command[command.index("--execution") + 1]
                if "--execution" in command
                else "0"
            )
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=json.dumps(
                    {
                        "steps": [
                            {
                                "outcome": "failed",
                                "exit_code": 1,
                                "output": f"failure for {execution}",
                            }
                        ]
                    }
                ),
            )

        client = module.CLIClient(Path("/circleci-cli"), run=run)
        output = client.fetch_failed_output(
            {"id": "job-id", "executions": [{"index": 0}, {"index": 1}]}
        )

        self.assertIn("failure for 0", output)
        self.assertIn("failure for 1", output)
        self.assertEqual(
            calls,
            [
                ["/circleci-cli", "job", "output", "list", "job-id", "--json"],
                [
                    "/circleci-cli",
                    "job",
                    "output",
                    "list",
                    "job-id",
                    "--execution",
                    "1",
                    "--json",
                ],
            ],
        )

    def test_cli_client_cancels_and_reruns_from_failed(self):
        module = load_module()
        calls = []

        def run(command, **_kwargs):
            calls.append(command)
            stdout = json.dumps({"workflow_id": "new"}) if "rerun" in command else ""
            return subprocess.CompletedProcess(command, 0, stdout=stdout)

        client = module.CLIClient(Path("/circleci-cli"), run=run)

        client.cancel_workflow("old")
        workflow_id = client.rerun_workflow("old")

        self.assertEqual(workflow_id, "new")
        self.assertEqual(
            calls,
            [
                ["/circleci-cli", "workflow", "cancel", "old", "--force"],
                [
                    "/circleci-cli",
                    "workflow",
                    "rerun",
                    "old",
                    "--from-failed",
                    "--json",
                ],
            ],
        )

    def test_build_client_defaults_to_cli_and_keeps_explicit_request_fallback(self):
        module = load_module()

        cli = module.build_client(None, find_cli=lambda: Path("/circleci-cli"))
        request = module.build_client(Path("/circleci-request"))

        self.assertIsInstance(cli, module.CLIClient)
        self.assertEqual(cli.launcher, Path("/circleci-cli"))
        self.assertIsInstance(request, module.Client)
        self.assertEqual(request.helper, Path("/circleci-request"))

    def test_resolves_workflow_id_from_circleci_url(self):
        module = load_module()
        workflow_id = "c444ed26-4e07-4bc0-9e16-37e884566f0d"
        url = f"https://app.circleci.com/pipelines/gh/snyk/cli/38962/details?job=x&workflowId={workflow_id}"
        self.assertEqual(module.resolve_workflow_id(url), workflow_id)

    def test_uses_gh_pr_rebase_helper(self):
        module = load_module()
        calls = []

        def run(command, **kwargs):
            calls.append((command, kwargs))
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=json.dumps({"number": 123, "status": "clean"}),
            )

        result = module.inspect_pr("feature/branch", Path("/monitor-pr"), run=run)

        self.assertEqual(result["number"], 123)
        self.assertEqual(calls[0][0], ["/monitor-pr", "feature/branch"])

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
                "status": "conflict",
            },
            clock=lambda: 100,
        )

        self.assertEqual(result["status"], "pr_conflict")
        self.assertEqual(result["pr"]["number"], 123)
        self.assertEqual(result["remaining_seconds"], 7200)

    def test_returns_pr_out_of_date_with_remaining_deadline(self):
        module = load_module()
        result = module.monitor(
            object(),
            "workflow",
            False,
            timeout=7200,
            poll=60,
            pr_branch="feature/branch",
            fetch_pr=lambda _branch: {"number": 123, "status": "out_of_date"},
            clock=lambda: 100,
        )

        self.assertEqual(result["status"], "pr_out_of_date")
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
            return {"number": 123, "status": "clean"}

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

    def test_retries_terminal_cli_infrastructure_outcome(self):
        module = load_module()

        class FakeClient:
            def fetch_workflow(self, workflow_id):
                return {"status": "timedout" if workflow_id == "old" else "success"}

            def fetch_jobs(self, workflow_id):
                return [{"id": "job", "name": "test", "status": "timedout"}]

            def fetch_job_detail(self, _job):
                return {"id": "job", "status": "timedout"}

            def fetch_failed_output(self, _detail):
                return ""

            def rerun_workflow(self, _workflow_id):
                return "new"

        result = module.monitor(FakeClient(), "old", True, timeout=5, poll=0)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["workflow_ids"], ["old", "new"])

    def test_alerts_once_when_failing_state_needs_attention(self):
        module = load_module()
        alerts = []

        class FakeClient:
            def fetch_workflow(self, _workflow_id):
                return {"status": "failing"}

            def fetch_jobs(self, _workflow_id):
                return [{"id": "job", "name": "test", "status": "failed"}]

            def fetch_job_detail(self, _job):
                return {"id": "job", "outcome": "failed"}

            def fetch_failed_output(self, _detail):
                return "assertion failed"

        result = module.monitor(
            FakeClient(),
            "workflow",
            False,
            timeout=5,
            poll=0,
            alert=lambda: alerts.append("alert"),
        )

        self.assertEqual(result["status"], "failing")
        self.assertEqual(alerts, ["alert"])

    def test_returns_early_for_failed_job_while_other_job_runs(self):
        module = load_module()
        now = 100

        class FakeClient:
            def fetch_workflow(self, _workflow_id):
                return {"status": "failing"}

            def fetch_jobs(self, _workflow_id):
                return [
                    {"id": "failed", "name": "Linux arm64", "status": "failed"},
                    {"id": "running", "name": "Windows", "status": "running"},
                ]

            def fetch_job_detail(self, _job):
                return {"id": "failed", "outcome": "infrastructure_fail"}

            def fetch_failed_output(self, _detail):
                return ""

        def sleep(seconds):
            nonlocal now
            now += seconds

        result = module.monitor(
            FakeClient(),
            "workflow",
            False,
            timeout=120,
            poll=60,
            clock=lambda: now,
            sleep=sleep,
            alert=lambda: None,
        )

        self.assertEqual(result["status"], "failing")
        self.assertEqual(result["classification"]["environment"], ["Linux arm64"])
        self.assertEqual(result["remaining_seconds"], 120)


if __name__ == "__main__":
    unittest.main()
