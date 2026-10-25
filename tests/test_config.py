from __future__ import annotations

import pytest

from repodoctor.config import Config, load_config
from repodoctor.errors import ConfigError


def test_defaults_when_no_config(make_repo):
    assert load_config(make_repo()) == Config()


def test_standalone_config_file(make_repo):
    root = make_repo(
        {
            ".repodoctor.toml": (
                'disable = ["changelog-exists"]\n'
                'exclude = ["vendor"]\n'
                "fail_under = 75\n"
                "[weights]\n"
                "readme-exists = 9\n"
            )
        }
    )
    config = load_config(root)
    assert config.disable == ("changelog-exists",)
    assert config.exclude == ("vendor",)
    assert config.fail_under == 75
    assert config.weights == {"readme-exists": 9}


def test_pyproject_section(make_repo):
    root = make_repo({"pyproject.toml": "[tool.repodoctor]\nfail_under = 60\n"})
    assert load_config(root).fail_under == 60


def test_standalone_file_wins_over_pyproject(make_repo):
    root = make_repo(
        {
            ".repodoctor.toml": "fail_under = 10\n",
            "pyproject.toml": "[tool.repodoctor]\nfail_under = 99\n",
        }
    )
    assert load_config(root).fail_under == 10


def test_pyproject_without_section_is_ignored(make_repo):
    root = make_repo({"pyproject.toml": "[project]\nname = 'x'\n"})
    assert load_config(root) == Config()


def test_broken_pyproject_does_not_break_config_loading(make_repo):
    root = make_repo({"pyproject.toml": "[broken"})
    assert load_config(root) == Config()


def test_broken_standalone_file_is_an_error(make_repo):
    root = make_repo({".repodoctor.toml": "[broken"})
    with pytest.raises(ConfigError, match="cannot read"):
        load_config(root)


@pytest.mark.parametrize(
    "content",
    [
        'unknown = "x"\n',
        "disable = 'not-a-list'\n",
        "disable = [1, 2]\n",
        "fail_under = 101\n",
        "fail_under = -1\n",
        "fail_under = true\n",
        "fail_under = 'high'\n",
        "weights = 5\n",
        "[weights]\nreadme-exists = 0\n",
        "[weights]\nreadme-exists = 'heavy'\n",
    ],
)
def test_invalid_config_values(make_repo, content):
    root = make_repo({".repodoctor.toml": content})
    with pytest.raises(ConfigError):
        load_config(root)
