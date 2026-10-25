from __future__ import annotations

from ..context import RepoContext
from ..models import Outcome, fail, ok, skip
from ..registry import check

MANIFEST_PATTERNS = (
    "requirements*.txt",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "pipfile",
    "environment.yml",
    "package.json",
    "go.mod",
    "cargo.toml",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "gemfile",
    "composer.json",
    "mix.exs",
    "*.csproj",
    "*.fsproj",
    "deno.json",
    "pubspec.yaml",
    "package.swift",
    "cmakelists.txt",
    "conanfile.txt",
    "dune-project",
    "*.cabal",
)
REQUIRED_PROJECT_FIELDS = ("name", "version", "description", "readme", "requires-python")


@check(
    id="dependency-manifest",
    title="Dependency manifest present",
    category="packaging",
    weight=4,
    description="A manifest such as pyproject.toml, package.json or go.mod makes the project "
    "installable and its dependencies explicit.",
)
def dependency_manifest(ctx: RepoContext) -> Outcome:
    if not ctx.language_counts():
        return skip("No source code detected")
    found = ctx.named(*MANIFEST_PATTERNS)
    if found:
        return ok(f"Found {found[0]}")
    return fail(
        "No dependency manifest found",
        hint="Add the manifest your ecosystem expects, for example pyproject.toml",
    )


@check(
    id="python-pyproject",
    title="Python project uses pyproject.toml",
    category="packaging",
    weight=3,
    description="pyproject.toml is the standard place for Python packaging and tool "
    "configuration (PEP 517, PEP 518 and PEP 621).",
)
def python_pyproject(ctx: RepoContext) -> Outcome:
    if not ctx.has_language("Python"):
        return skip("Not a Python project")
    if ctx.is_file("pyproject.toml"):
        return ok("Found pyproject.toml")
    return fail(
        "No pyproject.toml found",
        hint="Migrate setup.py or setup.cfg metadata to a pyproject.toml",
    )


@check(
    id="python-project-metadata",
    title="Python package metadata complete",
    category="packaging",
    weight=4,
    description="A complete [project] table (name, version, description, readme, "
    "requires-python and license) makes the package discoverable and installable.",
)
def python_project_metadata(ctx: RepoContext) -> Outcome:
    if not ctx.has_language("Python"):
        return skip("Not a Python project")
    if not ctx.is_file("pyproject.toml"):
        return skip("No pyproject.toml to inspect")
    try:
        data = ctx.read_toml("pyproject.toml")
    except ValueError as exc:
        return fail("pyproject.toml is not valid TOML", hint=str(exc))
    project = data.get("project")
    if not isinstance(project, dict):
        return fail(
            "pyproject.toml has no [project] table",
            hint="Declare your package metadata in a [project] table (PEP 621)",
        )
    dynamic = project.get("dynamic", [])
    missing = [
        name for name in REQUIRED_PROJECT_FIELDS if name not in project and name not in dynamic
    ]
    if "license" not in project and "license-files" not in project and "license" not in dynamic:
        missing.append("license")
    if missing:
        return fail(
            f"[project] is missing: {', '.join(missing)}",
            hint="Fill in the missing fields so the package renders well on PyPI",
        )
    return ok("[project] metadata is complete")
