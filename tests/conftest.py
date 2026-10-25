from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path

import pytest

from repodoctor.checks import load_builtin_checks
from repodoctor.context import RepoContext
from repodoctor.models import Outcome
from repodoctor.registry import get_check, unregister

load_builtin_checks()

Files = Mapping[str, str | bytes]


@pytest.fixture
def make_repo(tmp_path: Path) -> Callable[[Files | None], Path]:
    def build(files: Files | None = None) -> Path:
        for rel, content in (files or {}).items():
            target = tmp_path / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                target.write_bytes(content)
            else:
                target.write_text(content, encoding="utf-8")
        return tmp_path

    return build


@pytest.fixture
def run_check(make_repo: Callable[[Files | None], Path]) -> Callable[..., Outcome]:
    def run(check_id: str, files: Files | None = None, exclude: tuple[str, ...] = ()) -> Outcome:
        root = make_repo(files)
        return get_check(check_id).func(RepoContext(root, exclude))

    return run


@pytest.fixture
def temporary_ids():
    registered: list[str] = []

    def track(check_id: str) -> str:
        registered.append(check_id)
        return check_id

    yield track
    for check_id in registered:
        unregister(check_id)
