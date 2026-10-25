from __future__ import annotations

from ..models import Status
from ..scoring import Report, score_of
from .base import RenderOptions, reporter

STATUS_ICONS = {Status.PASSED: "✅", Status.FAILED: "❌", Status.SKIPPED: "⏭️"}


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


@reporter("markdown")
def render_markdown(report: Report, options: RenderOptions) -> str:
    lines = [
        "# RepoDoctor report",
        "",
        f"**Score:** {report.score}/100 · **Grade:** {report.grade} · "
        f"{report.passed} passed, {report.failed} failed, {report.skipped} skipped",
        "",
    ]
    for category, results in report.by_category():
        lines.append(f"## {category.capitalize()} ({score_of(results)}/100)")
        lines.append("")
        lines.append("| | Check | Weight | Details |")
        lines.append("| --- | --- | ---: | --- |")
        for result in results:
            icon = STATUS_ICONS[result.status]
            title = _cell(result.check.title)
            message = _cell(result.outcome.message)
            lines.append(f"| {icon} | {title} | {result.check.weight} | {message} |")
        lines.append("")
    failures = report.failures()
    if failures:
        lines.append("## How to improve")
        lines.append("")
        for result in failures:
            hint = result.outcome.hint or result.outcome.message
            lines.append(f"- **{result.check.title}**: {hint}")
        lines.append("")
    return "\n".join(lines)
