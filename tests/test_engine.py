from __future__ import annotations

import pytest

import repodoctor
from repodoctor.context import RepoContext
from repodoctor.errors import RepoDoctorError
from repodoctor.models import Outcome, Status
from repodoctor.registry import all_checks, check, get_check
from repodoctor.runner import run_checks


def test_scan_returns_report_with_every_builtin_check(make_repo):
    report = repodoctor.scan(make_repo({"README.md": "hi"}), use_config=False)
    ids = {item.check.id for item in report.results}
    assert "readme-exists" in ids
    assert 0 <= report.score <= 100


def test_scan_rejects_missing_directory(tmp_path):
    with pytest.raises(RepoDoctorError, match="not a directory"):
        repodoctor.scan(tmp_path / "nope")


def test_disable_removes_checks(make_repo):
    report = repodoctor.scan(make_repo(), disable=["readme-exists"], use_config=False)
    assert "readme-exists" not in {item.check.id for item in report.results}


def test_only_filters_by_category(make_repo):
    report = repodoctor.scan(make_repo(), only=["security"], use_config=False)
    assert {item.check.category for item in report.results} == {"security"}


def test_unknown_ids_and_categories_are_errors(make_repo):
    root = make_repo()
    with pytest.raises(RepoDoctorError, match="unknown check ids"):
        repodoctor.scan(root, disable=["nope"], use_config=False)
    with pytest.raises(RepoDoctorError, match="unknown categories"):
        repodoctor.scan(root, only=["nope"], use_config=False)


def test_selecting_nothing_is_an_error(make_repo):
    every_id = [item.id for item in all_checks()]
    with pytest.raises(RepoDoctorError, match="no checks selected"):
        repodoctor.scan(make_repo(), disable=every_id, use_config=False)


def test_config_file_is_honoured(make_repo):
    root = make_repo(
        {".repodoctor.toml": 'disable = ["readme-exists"]\n[weights]\ngitignore-exists = 1\n'}
    )
    report = repodoctor.scan(root)
    by_id = {item.check.id: item for item in report.results}
    assert "readme-exists" not in by_id
    assert by_id["gitignore-exists"].check.weight == 1


def test_config_with_unknown_weight_id_is_an_error(make_repo):
    root = make_repo({".repodoctor.toml": "[weights]\nnope = 3\n"})
    with pytest.raises(RepoDoctorError, match="unknown check ids"):
        repodoctor.scan(root)


def test_exclude_option(make_repo):
    aws = "AKIA" + "ABCDEFGHIJKLMNOP"
    root = make_repo({"vendor/leak.txt": aws})
    flagged = repodoctor.scan(root, only=["security"], use_config=False)
    clean = repodoctor.scan(root, only=["security"], exclude=["vendor"], use_config=False)
    assert flagged.failed == 1
    assert clean.failed == 0


def test_crashing_check_is_reported_as_skipped(make_repo, temporary_ids):
    check_id = temporary_ids("engine-crashy")

    @check(id=check_id, title="Crashy", category="docs")
    def crashy(ctx):
        raise RuntimeError("kaboom")

    ctx = RepoContext(make_repo())
    [result] = run_checks(ctx, [get_check(check_id)])
    assert result.status is Status.SKIPPED
    assert "kaboom" in result.outcome.message


def test_check_returning_garbage_is_skipped(make_repo, temporary_ids):
    check_id = temporary_ids("engine-garbage")

    @check(id=check_id, title="Garbage", category="docs")
    def garbage(ctx):
        return True

    [result] = run_checks(RepoContext(make_repo()), [get_check(check_id)])
    assert isinstance(result.outcome, Outcome)
    assert result.status is Status.SKIPPED


def test_weight_overrides_apply(make_repo):
    ctx = RepoContext(make_repo())
    [result] = run_checks(ctx, [get_check("readme-exists")], {"readme-exists": 2})
    assert result.check.weight == 2
    assert get_check("readme-exists").weight == 10
