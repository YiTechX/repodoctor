from __future__ import annotations

import json

from ..scoring import Report, score_of
from .base import RenderOptions, reporter

INDENT = 2


def report_to_dict(report: Report) -> dict:
    return {
        "root": str(report.root),
        "score": report.score,
        "grade": report.grade,
        "summary": {
            "passed": report.passed,
            "failed": report.failed,
            "skipped": report.skipped,
        },
        "categories": {
            category: {"score": score_of(results), "checks": len(results)}
            for category, results in report.by_category()
        },
        "results": [
            {
                "id": result.check.id,
                "title": result.check.title,
                "category": result.check.category,
                "weight": result.check.weight,
                "status": result.status.value,
                "message": result.outcome.message,
                "hint": result.outcome.hint,
            }
            for result in report.results
        ],
    }


@reporter("json")
def render_json(report: Report, options: RenderOptions) -> str:
    return json.dumps(report_to_dict(report), indent=INDENT, ensure_ascii=False) + "\n"
