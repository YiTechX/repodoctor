from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .errors import ConfigError, RegistryError
from .registry import validate_weight

CONFIG_FILE = ".repodoctor.toml"
PYPROJECT_FILE = "pyproject.toml"
ALLOWED_KEYS = ("disable", "exclude", "fail_under", "weights")


@dataclass(frozen=True)
class Config:
    disable: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()
    fail_under: int | None = None
    weights: dict[str, int] = field(default_factory=dict)


def load_config(root: str | Path) -> Config:
    base = Path(root)
    standalone = base / CONFIG_FILE
    if standalone.is_file():
        return parse_config(_read_toml(standalone), CONFIG_FILE)
    pyproject = base / PYPROJECT_FILE
    if pyproject.is_file():
        try:
            data = _read_toml(pyproject)
        except ConfigError:
            return Config()
        table = data.get("tool", {})
        section = table.get("repodoctor") if isinstance(table, dict) else None
        if isinstance(section, dict):
            return parse_config(section, f"{PYPROJECT_FILE} [tool.repodoctor]")
    return Config()


def parse_config(table: dict[str, Any], source: str) -> Config:
    unknown = sorted(set(table) - set(ALLOWED_KEYS))
    if unknown:
        allowed = ", ".join(ALLOWED_KEYS)
        raise ConfigError(f"{source}: unknown keys {', '.join(unknown)} (allowed: {allowed})")
    return Config(
        disable=_string_list(table, "disable", source),
        exclude=_string_list(table, "exclude", source),
        fail_under=_fail_under(table, source),
        weights=_weights(table, source),
    )


def _read_toml(path: Path) -> dict[str, Any]:
    try:
        with open(path, "rb") as handle:
            return tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"cannot read {path.name}: {exc}") from exc


def _string_list(table: dict[str, Any], key: str, source: str) -> tuple[str, ...]:
    value = table.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ConfigError(f"{source}: {key} must be a list of strings")
    return tuple(value)


def _fail_under(table: dict[str, Any], source: str) -> int | None:
    value = table.get("fail_under")
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 100:
        raise ConfigError(f"{source}: fail_under must be an integer between 0 and 100")
    return value


def _weights(table: dict[str, Any], source: str) -> dict[str, int]:
    value = table.get("weights", {})
    if not isinstance(value, dict):
        raise ConfigError(f"{source}: weights must be a table of check ids to integers")
    weights: dict[str, int] = {}
    for check_id, weight in value.items():
        try:
            weights[check_id] = validate_weight(weight)
        except RegistryError as exc:
            raise ConfigError(f"{source}: weight for {check_id}: {exc}") from exc
    return weights
