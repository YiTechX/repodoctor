from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from .checks import load_builtin_checks
from .config import Config, load_config
from .context import RepoContext
from .errors import RepoDoctorError
from .models import Check
from .plugins import load_entry_point_plugins, load_plugin_path
from .registry import all_checks, categories
from .runner import run_checks
from .scoring import Report


def prepare_registry(plugins: Iterable[str | Path] = ()) -> None:
    load_builtin_checks()
    load_entry_point_plugins()
    for plugin in plugins:
        load_plugin_path(plugin)


def select_checks(
    *,
    disable: Iterable[str] = (),
    only: Iterable[str] = (),
    weight_ids: Iterable[str] = (),
) -> list[Check]:
    checks = all_checks()
    known = {item.id for item in checks}
    disabled = set(disable)
    unknown_ids = sorted((disabled | set(weight_ids)) - known)
    if unknown_ids:
        raise RepoDoctorError(f"unknown check ids: {', '.join(unknown_ids)}")
    wanted = set(only)
    unknown_categories = sorted(wanted - set(categories()))
    if unknown_categories:
        known_categories = ", ".join(categories())
        raise RepoDoctorError(
            f"unknown categories: {', '.join(unknown_categories)} (known: {known_categories})"
        )
    selected = [
        item
        for item in checks
        if item.id not in disabled and (not wanted or item.category in wanted)
    ]
    if not selected:
        raise RepoDoctorError("no checks selected")
    return selected


def scan_repository(
    path: str | Path = ".",
    *,
    config: Config | None = None,
    disable: Iterable[str] = (),
    only: Iterable[str] = (),
    exclude: Iterable[str] = (),
    plugins: Iterable[str | Path] = (),
) -> Report:
    root = Path(path)
    if not root.is_dir():
        raise RepoDoctorError(f"not a directory: {path}")
    settings = config if config is not None else load_config(root)
    prepare_registry(plugins)
    selected = select_checks(
        disable=[*settings.disable, *disable],
        only=only,
        weight_ids=settings.weights,
    )
    ctx = RepoContext(root, [*settings.exclude, *exclude])
    results = run_checks(ctx, selected, settings.weights)
    return Report(ctx.root, tuple(results))
