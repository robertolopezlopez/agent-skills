import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts/github/apply_pr_thread_groups.py"
SPEC = importlib.util.spec_from_file_location("apply_pr_thread_groups", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class ApplyPrThreadGroupsTest(unittest.TestCase):
    def test_output_marks_thread_and_workflow_states(self):
        pr = {
            "pr_number": 42,
            "canonical_url": "https://github.com/example/repo/pull/42",
            "review_threads": [
                {
                    "is_resolved": False,
                    "comments": [{"body": "Fix this", "author": "reviewer"}],
                },
                {
                    "is_resolved": True,
                    "comments": [{"body": "Done", "author": "reviewer"}],
                },
            ],
            "review_thread_count": 2,
            "unresolved_review_thread_count": 1,
        }

        output = MODULE.build_grouped_section(pr)

        self.assertIn("Thread states: open 1; resolved 1", output)
        self.assertIn("- Thread state: open (live refresh)", output)
        self.assertIn("- Workflow status: pending", output)
        self.assertIn("## Resolved threads", output)
        resolved_output = output.split("## Resolved threads", 1)[1]
        self.assertIn("### issue_02 — Done", resolved_output)
        self.assertIn("- Thread state: resolved (live refresh)", resolved_output)
        self.assertNotIn("- Workflow status:", resolved_output)
        self.assertIn("- Proposed changes: none", resolved_output)


if __name__ == "__main__":
    unittest.main()
