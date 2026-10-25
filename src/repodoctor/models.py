from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .context import RepoContext

CATEGORY_ORDER = ("docs", "community", "automation", "quality", "security", "packaging")


def category_sort_key(category: str) -> tuple[int, str]:
    if category in CATEGORY_ORDER:
        return (CATEGORY_ORDER.index(category), "")
    return (len(CATEGORY_ORDER), category)


class Status(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class Outcome:
    status: Status
    message: str
    hint: str = ""


def ok(message: str) -> Outcome:
    return Outcome(Status.PASSED, message)


def fail(message: str, hint: str = "") -> Outcome:
    return Outcome(Status.FAILED, message, hint)


def skip(message: str) -> Outcome:
    return Outcome(Status.SKIPPED, message)


CheckFunc = Callable[["RepoContext"], Outcome]


@dataclass(frozen=True)
class Check:
    id: str
    title: str
    category: str
    weight: int
    func: CheckFunc
    description: str = ""


@dataclass(frozen=True)
class CheckResult:
    check: Check
    outcome: Outcome

    @property
    def status(self) -> Status:
        return self.outcome.status
