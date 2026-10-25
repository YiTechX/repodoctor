from __future__ import annotations

import pytest

from repodoctor.errors import RegistryError
from repodoctor.models import ok
from repodoctor.registry import all_checks, categories, check, get_check, register


def make(check_id, **overrides):
    options = {"id": check_id, "title": "Title", "category": "docs", "weight": 3}
    options.update(overrides)
    return check(**options)


def test_decorator_registers_and_returns_function(temporary_ids):
    check_id = temporary_ids("t-register")

    @make(check_id, description="Explains itself")
    def sample(ctx):
        return ok("fine")

    assert get_check(check_id).func is sample
    assert get_check(check_id).description == "Explains itself"
    assert sample(None).message == "fine"


def test_description_defaults_to_title(temporary_ids):
    check_id = temporary_ids("t-default-description")
    make(check_id, title="Hello")(lambda ctx: ok("x"))
    assert get_check(check_id).description == "Hello"


def test_duplicate_ids_are_rejected(temporary_ids):
    check_id = temporary_ids("t-duplicate")
    make(check_id)(lambda ctx: ok("x"))
    with pytest.raises(RegistryError, match="duplicate"):
        make(check_id)(lambda ctx: ok("y"))


@pytest.mark.parametrize("bad_id", ["", "Upper", "has space", "-dash", "trailing-", "double--dash"])
def test_invalid_ids_are_rejected(bad_id):
    with pytest.raises(RegistryError):
        make(bad_id)(lambda ctx: ok("x"))


@pytest.mark.parametrize("weight", [0, 11, -1, True, 2.5, "3"])
def test_invalid_weights_are_rejected(weight):
    with pytest.raises(RegistryError):
        make("t-bad-weight", weight=weight)(lambda ctx: ok("x"))


@pytest.mark.parametrize("category", ["", "Docs", "1docs", "has space"])
def test_invalid_categories_are_rejected(category):
    with pytest.raises(RegistryError):
        make("t-bad-category", category=category)(lambda ctx: ok("x"))


def test_blank_title_is_rejected():
    with pytest.raises(RegistryError):
        make("t-blank-title", title="   ")(lambda ctx: ok("x"))


def test_unknown_check_raises():
    with pytest.raises(RegistryError, match="unknown check id"):
        get_check("does-not-exist")


def test_checks_are_ordered_by_category_then_weight(temporary_ids):
    light = temporary_ids("t-order-light")
    heavy = temporary_ids("t-order-heavy")
    make(light, category="zz-custom", weight=1)(lambda ctx: ok("x"))
    make(heavy, category="zz-custom", weight=9)(lambda ctx: ok("x"))
    ordered = [item.id for item in all_checks()]
    assert ordered.index(heavy) < ordered.index(light)
    assert categories()[-1] == "zz-custom"
    assert ordered.index("readme-exists") < ordered.index(heavy)


def test_register_accepts_prebuilt_check(temporary_ids):
    check_id = temporary_ids("t-prebuilt")
    from repodoctor.models import Check

    item = Check(id=check_id, title="T", category="docs", weight=2, func=lambda ctx: ok("x"))
    assert register(item) is item
