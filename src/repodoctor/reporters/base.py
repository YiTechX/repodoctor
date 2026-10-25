from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from ..errors import RegistryError
from ..scoring import Report


@dataclass(frozen=True)
class RenderOptions:
    color: bool = False
    unicode: bool = True


Reporter = Callable[[Report, RenderOptions], str]

_REPORTERS: dict[str, Reporter] = {}


def reporter(name: str) -> Callable[[Reporter], Reporter]:
    def decorator(func: Reporter) -> Reporter:
        if name in _REPORTERS:
            raise RegistryError(f"duplicate reporter: {name}")
        _REPORTERS[name] = func
        return func

    return decorator


def reporter_names() -> list[str]:
    return sorted(_REPORTERS)


def get_reporter(name: str) -> Reporter:
    try:
        return _REPORTERS[name]
    except KeyError:
        known = ", ".join(reporter_names())
        raise RegistryError(f"unknown format {name!r} (available: {known})") from None
