from __future__ import annotations

import pytest

import repodoctor
from repodoctor.errors import PluginError, RegistryError
from repodoctor.plugins import load_entry_point_plugins, load_plugin_path
from repodoctor.registry import get_check

PLUGIN = """
from repodoctor.models import fail, ok
from repodoctor.registry import check


@check(id="{check_id}", title="Has marker", category="custom", weight=4)
def has_marker(ctx):
    if ctx.is_file("MARKER"):
        return ok("marker found")
    return fail("marker missing", hint="create MARKER")
"""


def write_plugin(directory, name, check_id):
    path = directory / name
    path.write_text(PLUGIN.format(check_id=check_id), encoding="utf-8")
    return path


def test_plugin_file_registers_checks(tmp_path, temporary_ids):
    check_id = temporary_ids("plugin-file-check")
    path = write_plugin(tmp_path, "my_plugin.py", check_id)
    assert load_plugin_path(path)
    assert get_check(check_id).category == "custom"


def test_loading_the_same_plugin_twice_is_harmless(tmp_path, temporary_ids):
    check_id = temporary_ids("plugin-twice-check")
    path = write_plugin(tmp_path, "twice.py", check_id)
    load_plugin_path(path)
    load_plugin_path(path)


def test_plugin_directory_loads_every_public_module(tmp_path, temporary_ids):
    first = temporary_ids("plugin-dir-one")
    second = temporary_ids("plugin-dir-two")
    plugins = tmp_path / "plugins"
    plugins.mkdir()
    write_plugin(plugins, "one.py", first)
    write_plugin(plugins, "two.py", second)
    write_plugin(plugins, "_private.py", "plugin-dir-private")
    assert len(load_plugin_path(plugins)) == 2
    assert get_check(first)
    assert get_check(second)
    with pytest.raises(RegistryError):
        get_check("plugin-dir-private")


def test_plugin_checks_take_part_in_scans(tmp_path, make_repo, temporary_ids):
    check_id = temporary_ids("plugin-scan-check")
    plugin = write_plugin(tmp_path, "scan_plugin.py", check_id)
    root = make_repo({"MARKER": "x"})
    report = repodoctor.scan(root, plugins=[plugin], only=["custom"], use_config=False)
    assert [item.check.id for item in report.results] == [check_id]
    assert report.score == 100


def test_missing_plugin_path(tmp_path):
    with pytest.raises(PluginError, match="not a Python file"):
        load_plugin_path(tmp_path / "missing.py")


def test_non_python_plugin_path(tmp_path):
    path = tmp_path / "plugin.txt"
    path.write_text("x", encoding="utf-8")
    with pytest.raises(PluginError):
        load_plugin_path(path)


def test_plugin_that_crashes_on_import(tmp_path):
    path = tmp_path / "crashy.py"
    path.write_text("raise RuntimeError('boom')\n", encoding="utf-8")
    with pytest.raises(PluginError, match="boom"):
        load_plugin_path(path)


def test_plugin_with_invalid_check_reports_registry_error(tmp_path):
    path = tmp_path / "invalid.py"
    path.write_text(
        "from repodoctor.registry import check\n"
        "@check(id='Bad Id', title='x', category='docs')\n"
        "def f(ctx):\n    return None\n",
        encoding="utf-8",
    )
    with pytest.raises(RegistryError):
        load_plugin_path(path)


def test_entry_point_loading_without_plugins_installed():
    assert isinstance(load_entry_point_plugins(), list)
