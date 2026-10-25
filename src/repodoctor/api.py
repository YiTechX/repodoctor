from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from .config import Config
from .engine import scan_repository
from .scoring import Report


def scan(
    path: str | Path = ".",
    *,
    disable: Iterable[str] = (),
    only: Iterable[str] = (),
    exclude: Iterable[str] = (),
    plugins: Iterable[str | Path] = (),
    use_config: bool = True,
) -> Report:
    return scan_repository(
        path,
        config=None if use_config else Config(),
        disable=disable,
        only=only,
        exclude=exclude,
        plugins=plugins,
    )
