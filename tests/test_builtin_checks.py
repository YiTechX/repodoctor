from __future__ import annotations

import pytest

from repodoctor.models import Status
from repodoctor.registry import all_checks

PASSED = Status.PASSED
FAILED = Status.FAILED
SKIPPED = Status.SKIPPED

BODY = "word " * 200
GOOD_README = f"# Title\n\n{BODY}\n\n## Usage\n\nRun it.\n"
GOOD_RST_README = f"Title\n=====\n\n{BODY}\n\nUsage\n-----\n\nRun it.\n"
LICENSE_TEXT = "Permission is hereby granted, free of charge, to any person obtaining a copy. " * 2
AWS_KEY = "AKIA" + "ABCDEFGHIJKLMNOP"
GITHUB_TOKEN = "ghp_" + "a" * 36
PRIVATE_KEY_HEADER = "-----BEGIN " + "RSA PRIVATE KEY-----"
COMPLETE_PYPROJECT = """
[project]
name = "demo"
version = "1.0.0"
description = "Demo"
readme = "README.md"
requires-python = ">=3.11"
license = { text = "MIT" }
"""
DYNAMIC_PYPROJECT = """
[project]
name = "demo"
dynamic = ["version"]
description = "Demo"
readme = "README.md"
requires-python = ">=3.11"
license = { text = "MIT" }
"""
PARTIAL_PYPROJECT = """
[project]
name = "demo"
"""
WORKFLOW_WITH_TESTS = "jobs:\n  t:\n    steps:\n      - run: python -m pytest\n"
WORKFLOW_WITHOUT_TESTS = "jobs:\n  t:\n    steps:\n      - run: echo hello\n"

CASES = [
    ("readme-exists", {"README.md": "hi"}, PASSED),
    ("readme-exists", {"readme.rst": "hi"}, PASSED),
    ("readme-exists", {"README": "hi"}, PASSED),
    ("readme-exists", {"docs/README.md": "hi"}, FAILED),
    ("readme-exists", {}, FAILED),
    ("readme-substance", {}, SKIPPED),
    ("readme-substance", {"README.md": "# Title\n"}, FAILED),
    ("readme-substance", {"README.md": BODY}, FAILED),
    ("readme-substance", {"README.md": GOOD_README}, PASSED),
    ("readme-substance", {"README.rst": GOOD_RST_README}, PASSED),
    ("readme-title", {}, SKIPPED),
    ("readme-title", {"README.md": "# Demo\n\nText\n"}, PASSED),
    ("readme-title", {"README.md": "\n\n# Demo\n"}, PASSED),
    ("readme-title", {"README.md": "Demo project without heading\n"}, FAILED),
    ("readme-title", {"README.md": ""}, FAILED),
    ("readme-usage", {}, SKIPPED),
    ("readme-usage", {"README.md": "# Title\n\nJust prose.\n"}, FAILED),
    ("readme-usage", {"README.md": "# Title\n\n## Installation\n"}, PASSED),
    ("readme-usage", {"README.md": "# Title\n\n## Quick start\n"}, PASSED),
    ("changelog-exists", {"CHANGELOG.md": "x"}, PASSED),
    ("changelog-exists", {"docs/CHANGES.md": "x"}, PASSED),
    ("changelog-exists", {"HISTORY.rst": "x"}, PASSED),
    ("changelog-exists", {}, FAILED),
    ("license-exists", {"LICENSE": LICENSE_TEXT}, PASSED),
    ("license-exists", {"LICENSE.md": LICENSE_TEXT}, PASSED),
    ("license-exists", {"COPYING": LICENSE_TEXT}, PASSED),
    ("license-exists", {"LICENSE": ""}, FAILED),
    ("license-exists", {"docs/LICENSE": LICENSE_TEXT}, FAILED),
    ("license-exists", {}, FAILED),
    ("contributing-guide", {"CONTRIBUTING.md": "x"}, PASSED),
    ("contributing-guide", {".github/CONTRIBUTING.md": "x"}, PASSED),
    ("contributing-guide", {"docs/contributing.md": "x"}, PASSED),
    ("contributing-guide", {}, FAILED),
    ("code-of-conduct", {"CODE_OF_CONDUCT.md": "x"}, PASSED),
    ("code-of-conduct", {".github/CODE_OF_CONDUCT.md": "x"}, PASSED),
    ("code-of-conduct", {}, FAILED),
    ("security-policy", {"SECURITY.md": "x"}, PASSED),
    ("security-policy", {".github/SECURITY.md": "x"}, PASSED),
    ("security-policy", {}, FAILED),
    ("issue-templates", {".github/ISSUE_TEMPLATE/bug.md": "x"}, PASSED),
    ("issue-templates", {".github/ISSUE_TEMPLATE.md": "x"}, PASSED),
    ("issue-templates", {".github/ISSUE_TEMPLATE/config.yml": "x"}, FAILED),
    ("issue-templates", {}, FAILED),
    ("pull-request-template", {".github/PULL_REQUEST_TEMPLATE.md": "x"}, PASSED),
    ("pull-request-template", {".github/pull_request_template.md": "x"}, PASSED),
    ("pull-request-template", {"docs/pull_request_template.md": "x"}, PASSED),
    ("pull-request-template", {}, FAILED),
    ("ci-configured", {".github/workflows/ci.yml": "x"}, PASSED),
    ("ci-configured", {".github/workflows/ci.yaml": "x"}, PASSED),
    ("ci-configured", {".gitlab-ci.yml": "x"}, PASSED),
    ("ci-configured", {"Jenkinsfile": "x"}, PASSED),
    ("ci-configured", {}, FAILED),
    ("ci-runs-tests", {}, SKIPPED),
    ("ci-runs-tests", {".github/workflows/ci.yml": WORKFLOW_WITH_TESTS}, PASSED),
    ("ci-runs-tests", {".gitlab-ci.yml": "script:\n  - go test ./...\n"}, PASSED),
    ("ci-runs-tests", {".github/workflows/ci.yml": WORKFLOW_WITHOUT_TESTS}, FAILED),
    ("dependency-updates", {".github/dependabot.yml": "x"}, PASSED),
    ("dependency-updates", {"renovate.json": "{}"}, PASSED),
    ("dependency-updates", {}, FAILED),
    ("pre-commit-hooks", {".pre-commit-config.yaml": "repos: []"}, PASSED),
    ("pre-commit-hooks", {}, FAILED),
    ("tests-present", {"tests/test_a.py": "x"}, PASSED),
    ("tests-present", {"test_a.py": "x"}, PASSED),
    ("tests-present", {"src/app.test.ts": "x"}, PASSED),
    ("tests-present", {"pkg/main_test.go": "x"}, PASSED),
    ("tests-present", {"spec/models/user.rb": "x"}, PASSED),
    ("tests-present", {"src/app.py": "x"}, FAILED),
    ("tests-present", {}, FAILED),
    ("gitignore-exists", {".gitignore": "x"}, PASSED),
    ("gitignore-exists", {}, FAILED),
    ("editorconfig", {".editorconfig": "root = true"}, PASSED),
    ("editorconfig", {}, FAILED),
    ("linter-configured", {"ruff.toml": ""}, PASSED),
    ("linter-configured", {"web/.eslintrc.json": "{}"}, PASSED),
    ("linter-configured", {"pyproject.toml": "[tool.ruff]\nline-length = 100\n"}, PASSED),
    ("linter-configured", {"pyproject.toml": "[project]\nname = 'x'\n"}, FAILED),
    ("linter-configured", {}, FAILED),
    ("no-large-files", {"small.bin": b"0" * 1024}, PASSED),
    ("no-large-files", {"huge.bin": b"0" * (5 * 1024 * 1024 + 1)}, FAILED),
    ("no-committed-secrets", {"app.py": "print('hello')\n"}, PASSED),
    ("no-committed-secrets", {"config.py": f"KEY = '{AWS_KEY}'\n"}, FAILED),
    ("no-committed-secrets", {"ci.txt": f"token {GITHUB_TOKEN}\n"}, FAILED),
    ("no-committed-secrets", {"key.txt": f"{PRIVATE_KEY_HEADER}\nabc\n"}, FAILED),
    ("no-committed-secrets", {"blob.bin": b"\0\0\0" + AWS_KEY.encode()}, PASSED),
    ("env-files-ignored", {}, PASSED),
    ("env-files-ignored", {".env": "A=1"}, FAILED),
    ("env-files-ignored", {".env": "A=1", ".gitignore": "node_modules\n"}, FAILED),
    ("env-files-ignored", {".env": "A=1", ".gitignore": "# .env\n"}, FAILED),
    ("env-files-ignored", {".env": "A=1", ".gitignore": ".env\n"}, PASSED),
    ("env-files-ignored", {".env": "A=1", ".gitignore": "/.env\n"}, PASSED),
    ("env-files-ignored", {".env.local": "A=1", ".gitignore": ".env*\n"}, PASSED),
    ("env-files-ignored", {".env.example": "A=", "README.md": "x"}, PASSED),
    ("no-private-key-files", {}, PASSED),
    ("no-private-key-files", {"id_rsa": "x"}, FAILED),
    ("no-private-key-files", {"certs/server.p12": "x"}, FAILED),
    ("no-private-key-files", {"id_rsa.pub": "x"}, PASSED),
    ("dependency-manifest", {"README.md": "x"}, SKIPPED),
    ("dependency-manifest", {"main.py": "x"}, FAILED),
    ("dependency-manifest", {"main.py": "x", "requirements-dev.txt": "pytest"}, PASSED),
    ("dependency-manifest", {"main.go": "x", "go.mod": "module x"}, PASSED),
    ("python-pyproject", {"main.go": "x"}, SKIPPED),
    ("python-pyproject", {"main.py": "x"}, FAILED),
    ("python-pyproject", {"main.py": "x", "pyproject.toml": ""}, PASSED),
    ("python-project-metadata", {"main.go": "x"}, SKIPPED),
    ("python-project-metadata", {"main.py": "x"}, SKIPPED),
    ("python-project-metadata", {"main.py": "x", "pyproject.toml": "[broken"}, FAILED),
    ("python-project-metadata", {"main.py": "x", "pyproject.toml": "[tool.ruff]\n"}, FAILED),
    ("python-project-metadata", {"main.py": "x", "pyproject.toml": PARTIAL_PYPROJECT}, FAILED),
    ("python-project-metadata", {"main.py": "x", "pyproject.toml": COMPLETE_PYPROJECT}, PASSED),
    ("python-project-metadata", {"main.py": "x", "pyproject.toml": DYNAMIC_PYPROJECT}, PASSED),
]


@pytest.mark.parametrize(("check_id", "files", "expected"), CASES)
def test_check_outcome(run_check, check_id, files, expected):
    outcome = run_check(check_id, files)
    assert outcome.status is expected, outcome.message


@pytest.mark.parametrize(("check_id", "files", "expected"), CASES)
def test_failures_explain_how_to_fix(run_check, check_id, files, expected):
    outcome = run_check(check_id, files)
    if outcome.status is FAILED:
        assert outcome.message
        assert outcome.hint


def builtin_checks():
    return [item for item in all_checks() if item.func.__module__.startswith("repodoctor.checks.")]


@pytest.mark.parametrize("item", builtin_checks(), ids=lambda item: item.id)
def test_every_builtin_check_covers_pass_and_fail(item):
    statuses = {expected for check_id, _, expected in CASES if check_id == item.id}
    assert PASSED in statuses, f"add a passing case for {item.id}"
    assert FAILED in statuses or SKIPPED in statuses, f"add a failing case for {item.id}"


@pytest.mark.parametrize("item", builtin_checks(), ids=lambda item: item.id)
def test_builtin_check_metadata(item):
    assert item.description.strip()
    assert item.title.strip()
    assert 1 <= item.weight <= 10


def test_secret_values_are_never_printed(run_check):
    outcome = run_check("no-committed-secrets", {"config.py": f"KEY = '{AWS_KEY}'\n"})
    assert AWS_KEY not in outcome.message
    assert "config.py:1" in outcome.message


def test_exclude_hides_files_from_checks(run_check):
    files = {"vendor/leak.py": f"KEY = '{AWS_KEY}'\n"}
    outcome = run_check("no-committed-secrets", files, exclude=("vendor",))
    assert outcome.status is PASSED
