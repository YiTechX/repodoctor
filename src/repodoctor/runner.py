from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import replace

from .context import RepoContext
from .models import Check, CheckResult, Outcome, Status
from .registry import validate_weight


def run_checks(
    ctx: RepoContext,
    checks: Iterable[Check],
    weights: Mapping[str, int] | None = None,
) -> list[CheckResult]:
    overrides = weights or {}
    results: list[CheckResult] = []
    for item in checks:
        if item.id in overrides:
            item = replace(item, weight=validate_weight(overrides[item.id]))
        results.append(CheckResult(item, _execute(item, ctx)))
    return results


def _execute(item: Check, ctx: RepoContext) -> Outcome:
    try:
        outcome = item.func(ctx)
    except Exception as exc:
        return Outcome(Status.SKIPPED, f"Check crashed: {type(exc).__name__}: {exc}")
    if not isinstance(outcome, Outcome):
        return Outcome(Status.SKIPPED, "Check returned something other than an Outcome")
    return outcome
