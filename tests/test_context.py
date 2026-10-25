from __future__ import annotations

import pytest

from repodoctor.context import RepoContext


def test_files_skip_ignored_directories(make_repo):
    root = make_repo(
        {
            "src/app.py": "x",
            ".github/workflows/ci.yml": "x",
            ".git/config": "x",
            "node_modules/pkg/index.js": "x",
            "pkg.egg-info/PKG-INFO": "x",
            "src/__pycache__/app.pyc": "x",
        }
    )
    assert RepoContext(root).files() == (".github/workflows/ci.yml", "src/app.py")


def test_find_doc_is_case_insensitive_and_checks_suffix(make_repo):
    root = make_repo({"Readme.MD": "x", "README.py": "x"})
    ctx = RepoContext(root)
    assert ctx.find_doc("README") == "Readme.MD"
    assert ctx.find_doc("CONTRIBUTING") is None


def test_find_doc_respects_directories(make_repo):
    root = make_repo({".github/SECURITY.md": "x"})
    ctx = RepoContext(root)
    assert ctx.find_doc("SECURITY") is None
    assert ctx.find_doc("SECURITY", dirs=("", ".github")) == ".github/SECURITY.md"


def test_matching_is_case_insensitive(make_repo):
    root = make_repo({".github/PULL_REQUEST_TEMPLATE.md": "x"})
    assert RepoContext(root).matching(".github/pull_request_template.*") == [
        ".github/PULL_REQUEST_TEMPLATE.md"
    ]


def test_named_matches_base_names_at_any_depth(make_repo):
    root = make_repo({"a/b/ruff.toml": "x", "a/other.toml": "x"})
    assert RepoContext(root).named("ruff.toml") == ["a/b/ruff.toml"]


def test_exclude_supports_globs_and_directories(make_repo):
    root = make_repo({"docs/a.md": "x", "src/a.py": "x", "src/b.gen.py": "x"})
    ctx = RepoContext(root, exclude=("docs/", "*.gen.py"))
    assert ctx.files() == ("src/a.py",)


def test_text_files_skip_binary_and_oversized(make_repo):
    root = make_repo({"a.txt": "hello", "b.bin": b"\0\1\2", "c.txt": "x" * 50})
    found = dict(RepoContext(root).text_files(max_size=10))
    assert found == {"a.txt": "hello"}


def test_language_counts(make_repo):
    root = make_repo({"a.py": "", "b.py": "", "c.go": "", "d.txt": ""})
    ctx = RepoContext(root)
    assert ctx.language_counts() == {"Python": 2, "Go": 1}
    assert ctx.has_language("Python")
    assert not ctx.has_language("Rust")


def test_read_text_missing_file_is_empty(make_repo):
    assert RepoContext(make_repo()).read_text("nope.txt") == ""


def test_read_toml(make_repo):
    root = make_repo({"ok.toml": "a = 1\n", "bad.toml": "[oops"})
    ctx = RepoContext(root)
    assert ctx.read_toml("ok.toml") == {"a": 1}
    assert ctx.read_toml("missing.toml") == {}
    with pytest.raises(ValueError):
        ctx.read_toml("bad.toml")


def test_size_and_name(make_repo):
    root = make_repo({"a.txt": "12345"})
    ctx = RepoContext(root)
    assert ctx.size("a.txt") == 5
    assert ctx.size("missing") == 0
    assert ctx.name == root.name
