from __future__ import annotations

import hashlib
import importlib.util
import sys
from importlib.metadata import entry_points
from pathlib import Path

from .errors import PluginError, RepoDoctorError

ENTRY_POINT_GROUP = "repodoctor.checks"


def load_plugin_path(path: str | Path) -> list[str]:
    target = Path(path).resolve()
    if target.is_dir():
        files = sorted(item for item in target.glob("*.py") if not item.name.startswith("_"))
        loaded: list[str] = []
        for item in files:
            loaded.extend(load_plugin_path(item))
        return loaded
    if target.is_file() and target.suffix == ".py":
        return [_load_file(target)]
    raise PluginError(f"plugin path is not a Python file or directory: {path}")


def load_entry_point_plugins() -> list[str]:
    loaded: list[str] = []
    for entry in entry_points(group=ENTRY_POINT_GROUP):
        try:
            entry.load()
        except RepoDoctorError:
            raise
        except Exception as exc:
            raise PluginError(f"cannot load plugin {entry.name}: {exc}") from exc
        loaded.append(entry.name)
    return loaded


def _load_file(path: Path) -> str:
    digest = hashlib.sha1(str(path).encode("utf-8")).hexdigest()[:12]
    name = f"repodoctor_plugin_{digest}"
    if name in sys.modules:
        return name
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise PluginError(f"cannot import plugin file: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except RepoDoctorError:
        del sys.modules[name]
        raise
    except Exception as exc:
        del sys.modules[name]
        raise PluginError(f"cannot load plugin {path.name}: {exc}") from exc
    return name
