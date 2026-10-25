import importlib
import pkgutil


def load_builtin_checks() -> list[str]:
    loaded = []
    for module in pkgutil.iter_modules(__path__):
        importlib.import_module(f"{__name__}.{module.name}")
        loaded.append(module.name)
    return loaded
