import importlib.util
import json
import subprocess
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "skills/core/gh-pr-rebase/scripts/check_pr.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_pr", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CheckPRTest(unittest.TestCase):
    def test_inspects_branch_with_gh_and_normalizes_conflict(self):
        module = load_module()
        calls = []

        def run(command, **kwargs):
            calls.append((command, kwargs))
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=json.dumps({"number": 123, "mergeable": "CONFLICTING"}),
            )

        result = module.inspect_pr("feature", run)

        self.assertEqual(result["status"], "conflict")
        self.assertEqual(calls[0][0][:4], ["gh", "pr", "view", "feature"])

    def test_keeps_unknown_mergeability_unknown(self):
        module = load_module()
        run = lambda command, **kwargs: subprocess.CompletedProcess(
            command, 0, stdout=json.dumps({"mergeable": "UNKNOWN"})
        )

        self.assertEqual(module.inspect_pr("feature", run)["status"], "unknown")


if __name__ == "__main__":
    unittest.main()
