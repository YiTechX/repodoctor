from __future__ import annotations

import dataclasses
from collections.abc import Iterable
from pathlib import Path

from .config import Config
from .engine import scan_repository
from .remote import checkout, is_remote
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
    options = {
        "config": None if use_config else Config(),
        "disable": disable,
        "only": only,
        "exclude": exclude,
        "plugins": plugins,
    }
    if isinstance(path, str) and is_remote(path):
        with checkout(path) as root:
            report = scan_repository(root, **options)
        return dataclasses.replace(report, source=path)
    return scan_repository(path, **options)
