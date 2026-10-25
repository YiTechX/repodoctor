from __future__ import annotations

from ..models import CheckResult, Status
from ..scoring import Report
from .base import RenderOptions, reporter

BAR_WIDTH = 30
RESET = "\033[0m"
STYLES = {
    "bold": "\033[1m",
    "dim": "\033[2m",
    "green": "\033[32m",
    "red": "\033[31m",
    "yellow": "\033[33m",
}
UNICODE_SYMBOLS = {
    Status.PASSED: "✔",
    Status.FAILED: "✘",
    Status.SKIPPED: "○",
    "hint": "↳",
    "full": "█",
    "empty": "░",
}
ASCII_SYMBOLS = {
    Status.PASSED: "+",
    Status.FAILED: "x",
    Status.SKIPPED: "-",
    "hint": "->",
    "full": "#",
    "empty": ".",
}
STATUS_COLORS = {Status.PASSED: "green", Status.FAILED: "red", Status.SKIPPED: "yellow"}
GRADE_COLORS = {"A": "green", "B": "green", "C": "yellow", "D": "yellow", "F": "red"}


class _Painter:
    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    def __call__(self, style: str, text: str) -> str:
        if not self.enabled:
            return text
        return f"{STYLES[style]}{text}{RESET}"


def _result_line(result: CheckResult, width: int, paint: _Painter, symbols: dict) -> list[str]:
    status = result.status
    mark = paint(STATUS_COLORS[status], symbols[status])
    title = result.check.title.ljust(width)
    lines = [f"  {mark} {title}  {paint('dim', result.outcome.message)}"]
    if status is Status.FAILED and result.outcome.hint:
        lines.append(f"      {paint('yellow', symbols['hint'])} {result.outcome.hint}")
    return lines


@reporter("text")
def render_text(report: Report, options: RenderOptions) -> str:
    paint = _Painter(options.color)
    symbols = UNICODE_SYMBOLS if options.unicode else ASCII_SYMBOLS
    width = max((len(result.check.title) for result in report.results), default=0)
    lines = [paint("bold", f"RepoDoctor report for {report.root}"), ""]
    for category, results in report.by_category():
        lines.append(paint("bold", category.upper()))
        for result in results:
            lines.extend(_result_line(result, width, paint, symbols))
        lines.append("")
    filled = round(report.score * BAR_WIDTH / 100)
    bar = symbols["full"] * filled + symbols["empty"] * (BAR_WIDTH - filled)
    grade_color = GRADE_COLORS[report.grade]
    lines.append(
        f"{paint('bold', 'Score')} {paint(grade_color, f'{report.score}/100')}  "
        f"{paint('bold', 'Grade')} {paint(grade_color, report.grade)}  {paint(grade_color, bar)}"
    )
    lines.append(f"{report.passed} passed, {report.failed} failed, {report.skipped} skipped")
    return "\n".join(lines) + "\n"
