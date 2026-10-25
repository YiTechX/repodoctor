from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from repodoctor.cli import main
from repodoctor.registry import unregister

SRC = Path(__file__).resolve().parents[1] / "src"


def test_scan_prints_report_and_exits_zero(make_repo, capsys):
    root = make_repo({"README.md": "hello"})
    assert main([str(root)]) == 0
    output = capsys.readouterr().out
    assert "RepoDoctor report" in output
    assert "README present" in output


def test_path_defaults_to_current_directory(make_repo, capsys, monkeypatch):
    monkeypatch.chdir(make_repo({"README.md": "hello"}))
    assert main([]) == 0
    assert "RepoDoctor report" in capsys.readouterr().out


def test_explicit_scan_command(make_repo, capsys):
    assert main(["scan", str(make_repo())]) == 0
    assert "RepoDoctor report" in capsys.readouterr().out


def test_json_format(make_repo, capsys):
    assert main([str(make_repo()), "--format", "json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["results"]


def test_markdown_and_badge_formats(make_repo, capsys):
    root = str(make_repo())
    assert main([root, "-f", "markdown"]) == 0
    assert capsys.readouterr().out.startswith("# RepoDoctor report")
    assert main([root, "-f", "badge"]) == 0
    assert capsys.readouterr().out.startswith("<svg")


def test_output_file(make_repo, tmp_path, capsys):
    target = tmp_path / "out" / "report.json"
    target.parent.mkdir()
    assert main([str(make_repo()), "-f", "json", "-o", str(target)]) == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Report written" in captured.err
    assert json.loads(target.read_text(encoding="utf-8"))["results"]


def test_fail_under_flag(make_repo, capsys):
    root = str(make_repo())
    assert main([root, "--fail-under", "100"]) == 1
    assert "below the required 100" in capsys.readouterr().err
    assert main([root, "--fail-under", "0"]) == 0


def test_fail_under_from_config(make_repo):
    root = make_repo({".repodoctor.toml": "fail_under = 100\n"})
    assert main([str(root)]) == 1
    assert main([str(root), "--fail-under", "0"]) == 0


def test_fail_under_out_of_range(make_repo, capsys):
    assert main([str(make_repo()), "--fail-under", "150"]) == 2
    assert "between 0 and 100" in capsys.readouterr().err


def test_disable_and_only(make_repo, capsys):
    root = str(make_repo())
    assert main([root, "-f", "json", "--only", "docs", "--disable", "readme-usage"]) == 0
    data = json.loads(capsys.readouterr().out)
    ids = {item["id"] for item in data["results"]}
    assert "readme-usage" not in ids
    assert {item["category"] for item in data["results"]} == {"docs"}


def test_exclude_option(make_repo, capsys):
    aws = "AKIA" + "ABCDEFGHIJKLMNOP"
    root = str(make_repo({"vendor/leak.txt": aws}))
    assert main([root, "-f", "json", "--only", "security"]) == 0
    assert json.loads(capsys.readouterr().out)["summary"]["failed"] == 1
    assert main([root, "-f", "json", "--only", "security", "--exclude", "vendor"]) == 0
    assert json.loads(capsys.readouterr().out)["summary"]["failed"] == 0


@pytest.mark.parametrize(
    "arguments",
    [
        ["--format", "yaml"],
        ["--disable", "nope"],
        ["--only", "nope"],
        ["--plugin", "missing.py"],
    ],
)
def test_usage_errors_exit_two(make_repo, capsys, arguments):
    assert main([str(make_repo()), *arguments]) == 2
    assert "repodoctor: error:" in capsys.readouterr().err


def test_missing_directory_exits_two(tmp_path, capsys):
    assert main([str(tmp_path / "missing")]) == 2
    assert "not a directory" in capsys.readouterr().err


def test_invalid_config_exits_two(make_repo, capsys):
    root = make_repo({".repodoctor.toml": "bogus = 1\n"})
    assert main([str(root)]) == 2
    assert "unknown keys" in capsys.readouterr().err


def test_list_command(capsys):
    assert main(["list"]) == 0
    output = capsys.readouterr().out
    assert "readme-exists" in output
    assert "no-committed-secrets" in output


def test_explain_command(capsys):
    assert main(["explain", "license-exists"]) == 0
    output = capsys.readouterr().out
    assert "license-exists: License present" in output
    assert "category: community" in output


def test_explain_unknown_check(capsys):
    assert main(["explain", "nope"]) == 2
    assert "unknown check id" in capsys.readouterr().err


def test_version_flag(capsys):
    with pytest.raises(SystemExit) as raised:
        main(["--version"])
    assert raised.value.code == 0
    assert "repodoctor" in capsys.readouterr().out


def test_new_check_scaffold_is_immediately_usable(make_repo, tmp_path, capsys):
    plugins = tmp_path / "plugins"
    try:
        assert (
            main(
                [
                    "new-check",
                    "has-sponsor-file",
                    "--category",
                    "community",
                    "--weight",
                    "2",
                    "--output-dir",
                    str(plugins),
                ]
            )
            == 0
        )
        created = plugins / "has_sponsor_file.py"
        assert created.is_file()
        assert "#" not in created.read_text(encoding="utf-8")
        capsys.readouterr()
        root = str(make_repo({"README.md": "hello"}))
        assert main([root, "--plugin", str(created), "-f", "json", "--only", "community"]) == 0
        ids = {item["id"] for item in json.loads(capsys.readouterr().out)["results"]}
        assert "has-sponsor-file" in ids
    finally:
        unregister("has-sponsor-file")


def test_new_check_refuses_to_overwrite(tmp_path, capsys):
    arguments = ["new-check", "dup-check", "--output-dir", str(tmp_path)]
    assert main(arguments) == 0
    assert main(arguments) == 2
    assert "already exists" in capsys.readouterr().err


@pytest.mark.parametrize(
    "arguments",
    [
        ["new-check", "Bad Id"],
        ["new-check", "ok-id", "--category", "Bad"],
        ["new-check", "ok-id", "--weight", "99"],
    ],
)
def test_new_check_validation(tmp_path, capsys, arguments):
    assert main([*arguments, "--output-dir", str(tmp_path)]) == 2
    assert not list(tmp_path.iterdir())


def test_module_entry_point(make_repo):
    environment = {**os.environ, "PYTHONPATH": str(SRC)}
    completed = subprocess.run(
        [sys.executable, "-m", "repodoctor", str(make_repo()), "--format", "json"],
        capture_output=True,
        text=True,
        env=environment,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)["results"]
