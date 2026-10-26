from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import repodoctor
from repodoctor import remote
from repodoctor.cli import main
from repodoctor.errors import RepoDoctorError


@pytest.mark.parametrize(
    ("target", "url"),
    [
        ("github:pallets/flask", "https://github.com/pallets/flask.git"),
        ("GitHub:pallets/flask.git", "https://github.com/pallets/flask.git"),
        ("gitlab:group/sub/project", "https://gitlab.com/group/sub/project.git"),
        ("codeberg:forgejo/forgejo/", "https://codeberg.org/forgejo/forgejo.git"),
        ("https://example.com/repo.git", "https://example.com/repo.git"),
    ],
)
def test_remote_url(target, url):
    assert remote.is_remote(target)
    assert remote.remote_url(target) == url


@pytest.mark.parametrize(
    "target", ["github:flask", "github:owner/../etc", "github:owner/re po", "https://"]
)
def test_remote_url_rejects_bad_targets(target):
    with pytest.raises(RepoDoctorError):
        remote.remote_url(target)


def test_local_paths_are_not_remote():
    assert not remote.is_remote(".")
    assert not remote.is_remote("owner/repo")
    assert not remote.is_remote("http://example.com/repo.git")


@pytest.mark.skipif(sys.platform == "win32", reason="colons are not allowed in Windows paths")
def test_existing_directory_wins_over_remote_prefix(make_repo, monkeypatch):
    monkeypatch.chdir(make_repo({"github:owner/repo/README.md": "hi"}))
    assert not remote.is_remote("github:owner/repo")


@pytest.fixture
def fake_clone(monkeypatch):
    calls: list[list[str]] = []

    def run(command, **kwargs):
        calls.append(command)
        destination = Path(command[-1])
        destination.mkdir(parents=True)
        (destination / "README.md").write_text("# Remote\n", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(remote.shutil, "which", lambda name: "/usr/bin/git")
    monkeypatch.setattr(remote.subprocess, "run", run)
    return calls


def test_checkout_clones_shallow_and_cleans_up(fake_clone):
    with remote.checkout("github:owner/repo") as root:
        assert (root / "README.md").is_file()
    assert not root.exists()
    command = fake_clone[0]
    assert command[:3] == ["git", "-c", "core.symlinks=false"]
    assert "--depth" in command
    assert command[-2] == "https://github.com/owner/repo.git"


def test_cli_scans_remote_repository(fake_clone, capsys):
    assert main(["github:owner/repo", "-f", "json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["source"] == "github:owner/repo"
    assert any(r["id"] == "readme-exists" and r["status"] == "passed" for r in data["results"])


def test_cli_text_report_names_the_remote(fake_clone, capsys):
    assert main(["scan", "github:owner/repo", "--no-color"]) == 0
    assert "RepoDoctor report for github:owner/repo" in capsys.readouterr().out


def test_api_scans_remote_repository(fake_clone):
    report = repodoctor.scan("github:owner/repo")
    assert report.source == "github:owner/repo"
    assert report.label == "github:owner/repo"


def test_clone_failure_is_reported(monkeypatch, capsys):
    def run(command, **kwargs):
        raise subprocess.CalledProcessError(128, command, stderr="fatal: repository not found\n")

    monkeypatch.setattr(remote.shutil, "which", lambda name: "/usr/bin/git")
    monkeypatch.setattr(remote.subprocess, "run", run)
    assert main(["github:owner/missing"]) == 2
    assert "repository not found" in capsys.readouterr().err


def test_missing_git_is_reported(monkeypatch):
    monkeypatch.setattr(remote.shutil, "which", lambda name: None)
    with pytest.raises(RepoDoctorError, match="requires git"), remote.checkout("github:a/b"):
        pass
