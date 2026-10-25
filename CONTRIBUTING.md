# Contributing to RepoDoctor

Thank you for wanting to help. RepoDoctor is built so that your first pull request can be small,
useful and merged within a day. Most contributions are a single new check of about twenty lines.

## Your first contribution in 10 minutes

1. Fork the repository and clone your fork.
2. Install everything: `make dev` (or `python -m pip install -e ".[dev]"`).
3. Pick an idea from [ROADMAP.md](ROADMAP.md). Anything under **Good first issues** is ready to go.
4. Generate a starter file: `repodoctor new-check my-check-id --category quality --output-dir src/repodoctor/checks`
5. Edit the generated function so it inspects the repository and returns `ok(...)` or `fail(...)`.
6. Add rows for it to `CASES` in `tests/test_builtin_checks.py`. One passing row and one failing row is enough.
7. Run `make check`. It runs the linter, the tests and RepoDoctor on itself.
8. Open a pull request. The template lists what reviewers look at.

If you get stuck at any step, open a draft pull request and ask. Nobody will mind.

## Project layout

```
src/repodoctor/
  checks/        one module per category, each check is a decorated function
  reporters/     text, json, markdown and badge output
  context.py     RepoContext: everything a check can ask about the repository
  registry.py    the @check decorator and the check registry
  engine.py      selects checks, runs them and builds a Report
  scoring.py     score and grade calculation
  cli.py         command line interface
tests/           pytest suite, table driven for the built-in checks
docs/            guides, start with writing-checks.md
```

## Writing a check

A check is a function that receives a `RepoContext` and returns an `Outcome`.

```python
from repodoctor.models import fail, ok, skip
from repodoctor.registry import check


@check(
    id="readme-title",
    title="README starts with a title",
    category="docs",
    weight=2,
    description="The first line of the README should be a heading with the project name.",
)
def readme_title(ctx):
    readme = ctx.find_doc("README")
    if readme is None:
        return skip("No README to inspect")
    lines = ctx.read_text(readme).lstrip().splitlines()
    if lines and lines[0].startswith("#"):
        return ok("README starts with a heading")
    return fail("README does not start with a heading", hint="Begin with '# Project name'")
```

Rules of thumb:

- Return `skip(...)` when the check does not apply, for example a Python check in a Go project.
  Skipped checks do not affect the score.
- Every failure needs a `hint` that tells the reader exactly what to do.
- Pick the weight by impact: 1 to 3 nice to have, 4 to 6 important, 7 to 10 essential.
- Never execute code from the audited repository and never print secret values.
- Stay on the standard library. RepoDoctor has zero runtime dependencies on purpose.

This is the real `readme-title` check. The full guide, including every helper on `RepoContext`,
is in [docs/writing-checks.md](docs/writing-checks.md).

## Code style

- The code base is comment free. Names, small functions and tests carry the explanation.
  If you feel a comment is needed, extract a function or rename something instead.
- Python 3.11 or newer, type hints on public functions, `ruff` for linting and formatting.
- Keep functions short and focused. Prefer early returns over nesting.
- Follow the patterns in the module you are touching.

## Tests

- `make test` runs the suite. It takes about a second.
- Built-in checks are tested through the `CASES` table in `tests/test_builtin_checks.py`.
  A meta test fails if a built-in check has no passing or no failing case.
- Bug fixes come with a test that fails without the fix.

## Commit messages and pull requests

- Use [Conventional Commits](https://www.conventionalcommits.org/): `feat: add funding-file check`,
  `fix: handle empty LICENSE`, `docs: clarify plugin loading`.
- Keep pull requests focused. One check or one fix per pull request is ideal.
- Add a line to `CHANGELOG.md` under **Unreleased**.
- Maintainers aim to review within two days. Feel free to ping politely after that.

## Reporting bugs and suggesting checks

Use the issue templates. The **New check idea** template is the fastest way to propose a check,
and you can mark that you would like to build it yourself.

## Recognition

Every contributor is thanked by name in the release notes. Regular contributors are invited to
become maintainers with review and release rights.

## Code of conduct

By taking part you agree to follow our [Code of Conduct](CODE_OF_CONDUCT.md).
