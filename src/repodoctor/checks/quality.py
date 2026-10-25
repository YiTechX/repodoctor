from __future__ import annotations

import re
from pathlib import PurePosixPath

from ..context import RepoContext
from ..models import Outcome, fail, ok
from ..registry import check

TEST_DIRS = frozenset({"tests", "test", "spec", "specs", "__tests__"})
TEST_FILE = re.compile(
    r"^test_.*\.py$|_test\.(?:py|go|rb|rs)$|\.(?:test|spec)\.[cm]?[jt]sx?$|"
    r"Tests?\.(?:java|kt|cs)$|_spec\.rb$"
)
LINT_FILE_PATTERNS = (
    ".eslintrc*",
    "eslint.config.*",
    "ruff.toml",
    ".ruff.toml",
    ".flake8",
    ".pylintrc",
    "pylintrc",
    ".golangci.y*ml",
    ".rubocop.yml",
    "clippy.toml",
    ".clippy.toml",
    ".stylelintrc*",
    "biome.json*",
    ".prettierrc*",
    "checkstyle.xml",
    "detekt.yml",
    ".scalafmt.conf",
    "rustfmt.toml",
    ".rustfmt.toml",
    "phpcs.xml*",
)
LINT_SECTION_MARKERS = (
    ("pyproject.toml", ("[tool.ruff", "[tool.pylint", "[tool.flake8", "[tool.black", "[tool.mypy")),
    ("setup.cfg", ("[flake8]", "[pylint", "[mypy]")),
    ("tox.ini", ("[flake8]",)),
    ("package.json", ('"eslintConfig"', '"prettier"')),
)
LARGE_FILE_BYTES = 5 * 1024 * 1024
MAX_LISTED = 3


def _looks_like_test(rel: str) -> bool:
    path = PurePosixPath(rel)
    if TEST_FILE.search(path.name):
        return True
    return any(part.lower() in TEST_DIRS for part in path.parts[:-1])


@check(
    id="tests-present",
    title="Automated tests present",
    category="quality",
    weight=8,
    description="Tests are what let contributors change code without fear. A project without "
    "tests is hard to trust and hard to contribute to.",
)
def tests_present(ctx: RepoContext) -> Outcome:
    for rel in ctx.files():
        if _looks_like_test(rel):
            return ok(f"Found tests such as {rel}")
    return fail(
        "No tests found",
        hint="Add a tests/ directory with at least one automated test",
    )


@check(
    id="gitignore-exists",
    title=".gitignore present",
    category="quality",
    weight=4,
    description="A .gitignore keeps build output, caches and local files out of version control.",
)
def gitignore_exists(ctx: RepoContext) -> Outcome:
    if ctx.is_file(".gitignore"):
        return ok("Found .gitignore")
    return fail("No .gitignore found", hint="Add a .gitignore for your language and tooling")


@check(
    id="editorconfig",
    title=".editorconfig present",
    category="quality",
    weight=2,
    description="EditorConfig keeps indentation and line endings consistent across editors.",
)
def editorconfig(ctx: RepoContext) -> Outcome:
    if ctx.is_file(".editorconfig"):
        return ok("Found .editorconfig")
    return fail("No .editorconfig found", hint="Add an .editorconfig at the repository root")


@check(
    id="linter-configured",
    title="Linter or formatter configured",
    category="quality",
    weight=3,
    description="A configured linter or formatter ends style debates and catches bugs early.",
)
def linter_configured(ctx: RepoContext) -> Outcome:
    found = ctx.named(*LINT_FILE_PATTERNS)
    if found:
        return ok(f"Found {found[0]}")
    for rel, markers in LINT_SECTION_MARKERS:
        if ctx.is_file(rel):
            text = ctx.read_text(rel)
            if any(marker in text for marker in markers):
                return ok(f"{rel} configures a linter or formatter")
    return fail(
        "No linter or formatter configuration found",
        hint="Configure a linter such as ruff, eslint or golangci-lint",
    )


@check(
    id="no-large-files",
    title="No oversized files committed",
    category="quality",
    weight=4,
    description="Files over 5 MB bloat the repository forever. Use Git LFS or release assets "
    "for large binaries.",
)
def no_large_files(ctx: RepoContext) -> Outcome:
    large = sorted(
        ((ctx.size(rel), rel) for rel in ctx.files() if ctx.size(rel) > LARGE_FILE_BYTES),
        reverse=True,
    )
    if not large:
        return ok("No files above 5 MB")
    listed = ", ".join(f"{rel} ({size / 1024 / 1024:.1f} MB)" for size, rel in large[:MAX_LISTED])
    extra = len(large) - MAX_LISTED
    suffix = f" and {extra} more" if extra > 0 else ""
    return fail(
        f"Oversized files: {listed}{suffix}",
        hint="Move large binaries to Git LFS or attach them to releases",
    )
