from __future__ import annotations

import re
from pathlib import PurePosixPath

from ..context import RepoContext
from ..models import Outcome, fail, ok, skip
from ..registry import check

MARKDOWN_HEADING = re.compile(r"^#{1,6}\s+\S", re.MULTILINE)
RST_UNDERLINE = re.compile(r"^(?:={3,}|-{3,}|~{3,}|\^{3,})\s*$", re.MULTILINE)
USAGE_HEADING = re.compile(
    r"^\s*(?:#{1,6}\s*)?(?:installation|install|usage|getting started|quick ?start|examples?)\b",
    re.IGNORECASE | re.MULTILINE,
)
CHANGELOG_STEMS = ("CHANGELOG", "CHANGES", "HISTORY", "NEWS", "RELEASES", "RELEASE_NOTES")
MIN_README_WORDS = 150
MIN_README_SECTIONS = 2


@check(
    id="readme-exists",
    title="README present",
    category="docs",
    weight=10,
    description="A README is the front door of a project. Without one, visitors cannot tell what "
    "the project does, how to install it or whether it is maintained.",
)
def readme_exists(ctx: RepoContext) -> Outcome:
    found = ctx.find_doc("README")
    if found:
        return ok(f"Found {found}")
    return fail(
        "No README found",
        hint="Add a README.md that explains what the project does and how to use it",
    )


@check(
    id="readme-substance",
    title="README has real content",
    category="docs",
    weight=5,
    description="A README should be more than a title. It needs enough words and at least a "
    "couple of sections so readers can navigate it.",
)
def readme_substance(ctx: RepoContext) -> Outcome:
    readme = ctx.find_doc("README")
    if readme is None:
        return skip("No README to inspect")
    text = ctx.read_text(readme)
    words = len(text.split())
    pattern = RST_UNDERLINE if PurePosixPath(readme).suffix.lower() == ".rst" else MARKDOWN_HEADING
    sections = len(pattern.findall(text))
    if words < MIN_README_WORDS:
        return fail(
            f"{readme} has only {words} words",
            hint=f"Expand the README to at least {MIN_README_WORDS} words",
        )
    if sections < MIN_README_SECTIONS:
        return fail(
            f"{readme} has {sections} section(s)",
            hint=f"Organise the README into at least {MIN_README_SECTIONS} headed sections",
        )
    return ok(f"{readme} has {words} words in {sections} sections")


@check(
    id="readme-title",
    title="README starts with a title",
    category="docs",
    weight=2,
    description="The first line of the README should be a heading with the project name so "
    "that it renders well on hosting sites and package indexes.",
)
def readme_title(ctx: RepoContext) -> Outcome:
    readme = ctx.find_doc("README")
    if readme is None:
        return skip("No README to inspect")
    lines = ctx.read_text(readme).lstrip().splitlines()
    if lines and lines[0].startswith("#"):
        return ok("README starts with a heading")
    return fail(
        "README does not start with a heading",
        hint="Begin the README with a line like '# Project name'",
    )


@check(
    id="readme-usage",
    title="README explains installation or usage",
    category="docs",
    weight=5,
    description="Readers should be able to get started in seconds. Add an Installation, Usage, "
    "Quick start or Examples section to the README.",
)
def readme_usage(ctx: RepoContext) -> Outcome:
    readme = ctx.find_doc("README")
    if readme is None:
        return skip("No README to inspect")
    if USAGE_HEADING.search(ctx.read_text(readme)):
        return ok("README has an installation or usage section")
    return fail(
        "README has no installation or usage section",
        hint="Add an Installation or Usage section with a copy-pasteable example",
    )


@check(
    id="changelog-exists",
    title="Changelog present",
    category="docs",
    weight=3,
    description="A changelog tells users what changed between releases so they can upgrade "
    "with confidence.",
)
def changelog_exists(ctx: RepoContext) -> Outcome:
    found = ctx.find_doc(*CHANGELOG_STEMS, dirs=("", "docs"))
    if found:
        return ok(f"Found {found}")
    return fail(
        "No changelog found",
        hint="Add a CHANGELOG.md following the Keep a Changelog format",
    )
