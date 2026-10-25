from __future__ import annotations

from pathlib import Path

import pytest

from repodoctor.models import Check, CheckResult, Outcome, Status
from repodoctor.scoring import Report, grade_of, score_of


def result(status, weight=5, category="docs", check_id="x"):
    item = Check(id=check_id, title=check_id, category=category, weight=weight, func=lambda c: None)
    return CheckResult(item, Outcome(status, "message", "hint"))


def test_score_is_weighted_ratio_of_passed_checks():
    results = [result(Status.PASSED, 6), result(Status.FAILED, 2), result(Status.PASSED, 2)]
    assert score_of(results) == 80


def test_skipped_checks_do_not_count():
    results = [result(Status.PASSED, 5), result(Status.SKIPPED, 10)]
    assert score_of(results) == 100


def test_score_without_applicable_checks_is_full():
    assert score_of([]) == 100
    assert score_of([result(Status.SKIPPED)]) == 100


def test_all_failed_scores_zero():
    assert score_of([result(Status.FAILED, 4), result(Status.FAILED, 6)]) == 0


@pytest.mark.parametrize(
    ("score", "grade"),
    [
        (100, "A"),
        (90, "A"),
        (89, "B"),
        (80, "B"),
        (79, "C"),
        (70, "C"),
        (69, "D"),
        (60, "D"),
        (59, "F"),
        (0, "F"),
    ],
)
def test_grades(score, grade):
    assert grade_of(score) == grade


def test_report_counts_and_grouping():
    results = (
        result(Status.PASSED, 5, "security", "a"),
        result(Status.FAILED, 5, "docs", "b"),
        result(Status.SKIPPED, 5, "docs", "c"),
    )
    report = Report(Path("."), results)
    assert (report.passed, report.failed, report.skipped) == (1, 1, 1)
    assert report.score == 50
    assert report.grade == "F"
    assert [name for name, _ in report.by_category()] == ["docs", "security"]
    assert [item.check.id for item in report.failures()] == ["b"]
