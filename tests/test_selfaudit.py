from __future__ import annotations

from pathlib import Path

import pytest

import repodoctor

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(
    not (PROJECT_ROOT / "pyproject.toml").is_file(), reason="not running from a source checkout"
)
def test_project_passes_its_own_audit():
    report = repodoctor.scan(PROJECT_ROOT)
    failing = [f"{item.check.id}: {item.outcome.message}" for item in report.failures()]
    assert report.score >= 95, failing
