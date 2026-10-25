from __future__ import annotations

import re

from ..context import RepoContext
from ..models import Outcome, fail, ok, skip
from ..registry import check

CI_PATTERNS = (
    ".github/workflows/*.yml",
    ".github/workflows/*.yaml",
    ".gitlab-ci.yml",
    ".circleci/config.yml",
    ".travis.yml",
    "azure-pipelines.yml",
    "bitbucket-pipelines.yml",
    "jenkinsfile",
    ".drone.yml",
    "appveyor.yml",
    ".woodpecker.yml",
    ".woodpecker/*",
)
DEPENDENCY_BOT_PATTERNS = (
    ".github/dependabot.yml",
    ".github/dependabot.yaml",
    "renovate.json",
    "renovate.json5",
    ".renovaterc",
    ".renovaterc.json",
    ".github/renovate.json",
    ".github/renovate.json5",
)
HOOK_PATTERNS = (".pre-commit-config.yaml", ".pre-commit-config.yml", "lefthook.yml", ".husky/*")
TEST_COMMAND = re.compile(
    r"\b(pytest|py\.test|unittest|tox|nox|npm (?:run )?test|yarn test|pnpm test|bun test|"
    r"go test|cargo (?:nextest|test)|mvnw? [^\n]*\btest\b|gradlew? [^\n]*\btest\b|rspec|"
    r"rake test|make test|ctest|dotnet test|phpunit|jest|vitest|mocha)\b",
    re.IGNORECASE,
)


@check(
    id="ci-configured",
    title="Continuous integration configured",
    category="automation",
    weight=8,
    description="Continuous integration runs your checks on every change so regressions are "
    "caught before they are merged.",
)
def ci_configured(ctx: RepoContext) -> Outcome:
    found = ctx.matching(*CI_PATTERNS)
    if found:
        return ok(f"Found {found[0]}")
    return fail(
        "No CI configuration found",
        hint="Add a GitHub Actions workflow in .github/workflows/ that runs your tests",
    )


@check(
    id="ci-runs-tests",
    title="CI runs the test suite",
    category="automation",
    weight=4,
    description="Having CI is not enough: it has to execute the tests.",
)
def ci_runs_tests(ctx: RepoContext) -> Outcome:
    configs = ctx.matching(*CI_PATTERNS)
    if not configs:
        return skip("No CI configuration to inspect")
    for rel in configs:
        if TEST_COMMAND.search(ctx.read_text(rel)):
            return ok(f"{rel} runs tests")
    return fail(
        "No CI configuration appears to run tests",
        hint="Add a step that runs your test command, for example pytest or npm test",
    )


@check(
    id="dependency-updates",
    title="Automated dependency updates",
    category="automation",
    weight=2,
    description="Dependabot or Renovate keeps dependencies and CI actions current and "
    "surfaces security fixes quickly.",
)
def dependency_updates(ctx: RepoContext) -> Outcome:
    found = ctx.matching(*DEPENDENCY_BOT_PATTERNS)
    if found:
        return ok(f"Found {found[0]}")
    return fail(
        "No dependency update bot configured",
        hint="Add .github/dependabot.yml or a Renovate configuration",
    )


@check(
    id="pre-commit-hooks",
    title="Pre-commit hooks configured",
    category="automation",
    weight=2,
    description="Pre-commit hooks catch formatting and lint problems before they reach review.",
)
def pre_commit_hooks(ctx: RepoContext) -> Outcome:
    found = ctx.matching(*HOOK_PATTERNS)
    if found:
        return ok(f"Found {found[0]}")
    return fail(
        "No pre-commit hooks configured",
        hint="Add a .pre-commit-config.yaml with your formatter and linter",
    )
