from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from .models import CheckResult, Status, category_sort_key

GRADE_THRESHOLDS = ((90, "A"), (80, "B"), (70, "C"), (60, "D"))


def score_of(results: Iterable[CheckResult]) -> int:
    earned = 0
    possible = 0
    for result in results:
        if result.status is Status.SKIPPED:
            continue
        possible += result.check.weight
        if result.status is Status.PASSED:
            earned += result.check.weight
    if possible == 0:
        return 100
    return round(100 * earned / possible)


def grade_of(score: int) -> str:
    for threshold, letter in GRADE_THRESHOLDS:
        if score >= threshold:
            return letter
    return "F"


@dataclass(frozen=True)
class Report:
    root: Path
    results: tuple[CheckResult, ...]

    @property
    def score(self) -> int:
        return score_of(self.results)

    @property
    def grade(self) -> str:
        return grade_of(self.score)

    @property
    def passed(self) -> int:
        return self._count(Status.PASSED)

    @property
    def failed(self) -> int:
        return self._count(Status.FAILED)

    @property
    def skipped(self) -> int:
        return self._count(Status.SKIPPED)

    def by_category(self) -> list[tuple[str, tuple[CheckResult, ...]]]:
        grouped: dict[str, list[CheckResult]] = {}
        for result in self.results:
            grouped.setdefault(result.check.category, []).append(result)
        ordered = sorted(grouped, key=category_sort_key)
        return [(name, tuple(grouped[name])) for name in ordered]

    def failures(self) -> list[CheckResult]:
        return [result for result in self.results if result.status is Status.FAILED]

    def _count(self, status: Status) -> int:
        return sum(1 for result in self.results if result.status is status)
