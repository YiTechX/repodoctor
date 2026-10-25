from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from repodoctor.errors import RegistryError
from repodoctor.models import Check, CheckResult, Outcome, Status
from repodoctor.reporters import RenderOptions, get_reporter, reporter, reporter_names
from repodoctor.reporters.badge import badge_color
from repodoctor.scoring import Report


def make_report():
    def entry(check_id, category, weight, status, message, hint=""):
        item = Check(
            id=check_id,
            title=f"Title {check_id}",
            category=category,
            weight=weight,
            func=lambda ctx: None,
        )
        return CheckResult(item, Outcome(status, message, hint))

    return Report(
        Path("/tmp/demo"),
        (
            entry("readme", "docs", 10, Status.PASSED, "Found README.md"),
            entry("changelog", "docs", 5, Status.FAILED, "No changelog | missing", "Add one"),
            entry("tests", "quality", 5, Status.SKIPPED, "Nothing to inspect"),
        ),
    )


def test_all_formats_are_registered():
    assert {"text", "json", "markdown", "badge"} <= set(reporter_names())


def test_text_report_content():
    output = get_reporter("text")(make_report(), RenderOptions())
    assert "RepoDoctor report for /tmp/demo" in output
    assert "DOCS" in output
    assert "Title readme" in output
    assert "Add one" in output
    assert "Score 67/100" in output
    assert "1 passed, 1 failed, 1 skipped" in output
    assert "\033[" not in output


def test_text_report_color_and_ascii_modes():
    report = make_report()
    colored = get_reporter("text")(report, RenderOptions(color=True))
    assert "\033[31m" in colored
    plain = get_reporter("text")(report, RenderOptions(unicode=False))
    assert plain.isascii()


def test_text_report_hides_hints_for_passing_checks():
    output = get_reporter("text")(make_report(), RenderOptions())
    assert output.count("Add one") == 1


def test_json_report_structure():
    data = json.loads(get_reporter("json")(make_report(), RenderOptions()))
    assert data["score"] == 67
    assert data["grade"] == "D"
    assert data["summary"] == {"passed": 1, "failed": 1, "skipped": 1}
    assert data["categories"]["docs"] == {"score": 67, "checks": 2}
    first = data["results"][0]
    assert first["id"] == "readme"
    assert first["status"] == "passed"
    assert set(first) == {"id", "title", "category", "weight", "status", "message", "hint"}


def test_markdown_report_escapes_pipes_and_lists_improvements():
    output = get_reporter("markdown")(make_report(), RenderOptions())
    assert output.startswith("# RepoDoctor report")
    assert "No changelog \\| missing" in output
    assert "## How to improve" in output
    assert "**Title changelog**: Add one" in output


def test_markdown_report_without_failures_has_no_improvement_section():
    report = Report(Path("."), make_report().results[:1])
    output = get_reporter("markdown")(report, RenderOptions())
    assert "How to improve" not in output


def test_badge_is_valid_svg_with_score():
    svg = get_reporter("badge")(make_report(), RenderOptions())
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")
    assert "67/100" in svg
    assert "repo health" in svg


@pytest.mark.parametrize(
    ("score", "color"),
    [(100, "#4c1"), (85, "#97ca00"), (75, "#dfb317"), (65, "#fe7d37"), (10, "#e05d44")],
)
def test_badge_color_scale(score, color):
    assert badge_color(score) == color


def test_unknown_format_lists_alternatives():
    with pytest.raises(RegistryError, match="available"):
        get_reporter("yaml")


def test_custom_reporters_can_be_registered_once():
    name = "unit-test-format"

    @reporter(name)
    def render(report, options):
        return "custom"

    assert get_reporter(name)(make_report(), RenderOptions()) == "custom"
    with pytest.raises(RegistryError, match="duplicate"):
        reporter(name)(render)
    from repodoctor.reporters import base

    del base._REPORTERS[name]
