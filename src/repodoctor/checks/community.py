from __future__ import annotations

from ..context import RepoContext
from ..models import Outcome, fail, ok
from ..registry import check

COMMUNITY_DIRS = ("", ".github", "docs")
LICENSE_STEMS = ("LICENSE", "LICENCE", "COPYING", "UNLICENSE", "LICENSE-MIT", "LICENSE-APACHE")
MIN_LICENSE_CHARS = 80

ISSUE_TEMPLATE_PATTERNS = (
    ".github/issue_template/*",
    ".github/issue_template.*",
    "issue_template.*",
    "docs/issue_template.*",
    ".gitlab/issue_templates/*",
)
PR_TEMPLATE_PATTERNS = (
    ".github/pull_request_template.*",
    ".github/pull_request_template/*",
    "pull_request_template.*",
    "docs/pull_request_template.*",
    ".gitlab/merge_request_templates/*",
)


def _community_doc(ctx: RepoContext, stems: tuple[str, ...], label: str, hint: str) -> Outcome:
    found = ctx.find_doc(*stems, dirs=COMMUNITY_DIRS)
    if found:
        return ok(f"Found {found}")
    return fail(f"No {label} found", hint=hint)


@check(
    id="license-exists",
    title="License present",
    category="community",
    weight=8,
    description="Without a license, nobody can legally use, modify or share the code. Pick one "
    "at choosealicense.com and add it as LICENSE.",
)
def license_exists(ctx: RepoContext) -> Outcome:
    found = ctx.find_doc(*LICENSE_STEMS, dirs=("",))
    if found is None:
        return fail("No license file found", hint="Add a LICENSE file, for example the MIT license")
    if len(ctx.read_text(found).strip()) < MIN_LICENSE_CHARS:
        return fail(f"{found} is empty or too short", hint="Paste the full license text")
    return ok(f"Found {found}")


@check(
    id="contributing-guide",
    title="Contributing guide present",
    category="community",
    weight=6,
    description="A CONTRIBUTING file tells newcomers how to set up the project, run the tests "
    "and submit changes. It is the single biggest lever for attracting contributors.",
)
def contributing_guide(ctx: RepoContext) -> Outcome:
    return _community_doc(
        ctx,
        ("CONTRIBUTING",),
        "contributing guide",
        "Add a CONTRIBUTING.md covering setup, tests and the pull request process",
    )


@check(
    id="code-of-conduct",
    title="Code of conduct present",
    category="community",
    weight=4,
    description="A code of conduct sets expectations for behaviour and tells people how to "
    "report problems.",
)
def code_of_conduct(ctx: RepoContext) -> Outcome:
    return _community_doc(
        ctx,
        ("CODE_OF_CONDUCT", "CODE-OF-CONDUCT"),
        "code of conduct",
        "Add a CODE_OF_CONDUCT.md, for example the Contributor Covenant",
    )


@check(
    id="security-policy",
    title="Security policy present",
    category="community",
    weight=3,
    description="A security policy explains how to report vulnerabilities privately instead of "
    "opening a public issue.",
)
def security_policy(ctx: RepoContext) -> Outcome:
    return _community_doc(
        ctx,
        ("SECURITY",),
        "security policy",
        "Add a SECURITY.md describing supported versions and how to report vulnerabilities",
    )


@check(
    id="issue-templates",
    title="Issue templates present",
    category="community",
    weight=3,
    description="Issue templates guide reporters to include the details maintainers need.",
)
def issue_templates(ctx: RepoContext) -> Outcome:
    candidates = ctx.matching(*ISSUE_TEMPLATE_PATTERNS)
    found = [rel for rel in candidates if not rel.lower().endswith("config.yml")]
    if found:
        return ok(f"Found {found[0]}")
    return fail(
        "No issue templates found",
        hint="Add templates under .github/ISSUE_TEMPLATE/ for bugs and feature requests",
    )


@check(
    id="pull-request-template",
    title="Pull request template present",
    category="community",
    weight=3,
    description="A pull request template reminds contributors to describe and test their change.",
)
def pull_request_template(ctx: RepoContext) -> Outcome:
    found = ctx.matching(*PR_TEMPLATE_PATTERNS)
    if found:
        return ok(f"Found {found[0]}")
    return fail(
        "No pull request template found",
        hint="Add .github/pull_request_template.md with a short checklist",
    )
