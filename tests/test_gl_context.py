import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts/gitlab/gl_context.py"
BOOTSTRAP = Path(__file__).parents[1] / "skills/core/gitlab/scripts/bootstrap_gitlab_artifact.py"


def load_module():
    spec = importlib.util.spec_from_file_location("gl_context", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def load_bootstrap():
    spec = importlib.util.spec_from_file_location("bootstrap_gitlab_artifact", BOOTSTRAP)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class GitLabContextTest(unittest.TestCase):
    def test_bootstrap_accepts_normalized_context(self):
        module = load_bootstrap()
        self.assertEqual(module.extract_mr({"merge_request": {"iid": 42}}), {"iid": 42})

    def test_parses_nested_project_url(self):
        module = load_module()
        parsed = module.parse_mr_input(
            "https://gitlab.example.com/group/subgroup/repo/-/merge_requests/42"
        )
        self.assertEqual(
            parsed,
            {"host": "gitlab.example.com", "project_path": "group/subgroup/repo", "mr_iid": 42},
        )

    def test_builds_normalized_context_with_unresolved_discussions(self):
        module = load_module()
        calls = []

        def api(endpoint, host, paginate=False):
            calls.append((endpoint, host, paginate))
            if endpoint.endswith("/discussions"):
                return [
                    {
                        "id": "thread-1",
                        "notes": [
                            {
                                "id": 9,
                                "body": "Please add a test",
                                "resolvable": True,
                                "resolved": False,
                                "system": False,
                                "author": {"username": "reviewer"},
                            }
                        ],
                    },
                    {"id": "system", "notes": [{"id": 10, "system": True}]},
                ]
            return {"iid": 42, "web_url": "https://gitlab.example.com/group/repo/-/merge_requests/42"}

        context = module.build_context(
            "42",
            full=True,
            api=api,
            identity=lambda: {
                "host": "gitlab.example.com",
                "project_path": "group/repo",
                "encoded_project_path": "group%2Frepo",
                "project_id": 7,
            },
        )

        self.assertEqual(context["mr_iid"], 42)
        self.assertEqual(context["unresolved_count"], 1)
        self.assertEqual(context["discussions"][0]["notes"][0]["url"], context["mr_link"] + "#note_9")
        self.assertEqual(calls[0][0], "/projects/7/merge_requests/42")
        self.assertTrue(calls[1][2])


if __name__ == "__main__":
    unittest.main()
