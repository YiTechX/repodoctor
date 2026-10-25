from __future__ import annotations

import re
from collections.abc import Callable

from .errors import RegistryError
from .models import Check, CheckFunc, category_sort_key

ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CATEGORY_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")
MIN_WEIGHT = 1
MAX_WEIGHT = 10

_CHECKS: dict[str, Check] = {}


def validate_weight(weight: object) -> int:
    if (
        isinstance(weight, bool)
        or not isinstance(weight, int)
        or not MIN_WEIGHT <= weight <= MAX_WEIGHT
    ):
        raise RegistryError(f"weight must be an integer between {MIN_WEIGHT} and {MAX_WEIGHT}")
    return weight


def register(item: Check) -> Check:
    if not ID_PATTERN.match(item.id):
        raise RegistryError(f"invalid check id {item.id!r}: use lowercase words joined by dashes")
    if not CATEGORY_PATTERN.match(item.category):
        raise RegistryError(f"invalid category {item.category!r} for check {item.id}")
    if not item.title.strip():
        raise RegistryError(f"check {item.id} needs a title")
    validate_weight(item.weight)
    if item.id in _CHECKS:
        raise RegistryError(f"duplicate check id: {item.id}")
    _CHECKS[item.id] = item
    return item


def check(
    *,
    id: str,
    title: str,
    category: str,
    weight: int = 5,
    description: str = "",
) -> Callable[[CheckFunc], CheckFunc]:
    def decorator(func: CheckFunc) -> CheckFunc:
        register(
            Check(
                id=id,
                title=title,
                category=category,
                weight=weight,
                func=func,
                description=description or title,
            )
        )
        return func

    return decorator


def unregister(check_id: str) -> None:
    _CHECKS.pop(check_id, None)


def all_checks() -> list[Check]:
    return sorted(
        _CHECKS.values(),
        key=lambda item: (category_sort_key(item.category), -item.weight, item.id),
    )


def get_check(check_id: str) -> Check:
    try:
        return _CHECKS[check_id]
    except KeyError:
        raise RegistryError(f"unknown check id: {check_id}") from None


def categories() -> list[str]:
    return sorted({item.category for item in _CHECKS.values()}, key=category_sort_key)
