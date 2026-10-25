from __future__ import annotations

from pathlib import Path

from .errors import ScaffoldError
from .registry import CATEGORY_PATTERN, ID_PATTERN, MAX_WEIGHT, MIN_WEIGHT

TEMPLATE = """from repodoctor.models import fail, ok
from repodoctor.registry import check


@check(
    id="{check_id}",
    title="{title}",
    category="{category}",
    weight={weight},
    description="Describe what this check verifies and why it matters.",
)
def {function}(ctx):
    if ctx.is_file("README.md"):
        return ok("README.md exists")
    return fail("README.md is missing", hint="Create a README.md at the repository root")
"""


def write_check_scaffold(check_id: str, category: str, weight: int, directory: str | Path) -> Path:
    if not ID_PATTERN.match(check_id):
        raise ScaffoldError(f"invalid check id {check_id!r}: use lowercase words joined by dashes")
    if not CATEGORY_PATTERN.match(category):
        raise ScaffoldError(f"invalid category {category!r}")
    if not MIN_WEIGHT <= weight <= MAX_WEIGHT:
        raise ScaffoldError(f"weight must be between {MIN_WEIGHT} and {MAX_WEIGHT}")
    function = check_id.replace("-", "_")
    if function[0].isdigit():
        function = f"check_{function}"
    target_dir = Path(directory)
    target = target_dir / f"{function}.py"
    if target.exists():
        raise ScaffoldError(f"{target} already exists")
    target_dir.mkdir(parents=True, exist_ok=True)
    title = check_id.replace("-", " ").capitalize()
    target.write_text(
        TEMPLATE.format(
            check_id=check_id,
            title=title,
            category=category,
            weight=weight,
            function=function,
        ),
        encoding="utf-8",
    )
    return target
