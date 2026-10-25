# RepoDoctor

**One command. A health score, a grade and a prioritized to-do list for any code repository.**

[![CI](https://github.com/YiTechX/repodoctor/actions/workflows/ci.yml/badge.svg)](https://github.com/YiTechX/repodoctor/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Good first issues](https://img.shields.io/badge/good%20first%20issues-plenty-7057ff.svg)](ROADMAP.md)

RepoDoctor looks at a repository the way a new contributor, a security reviewer and a
maintainer would, and tells you exactly what to fix first. It has **zero dependencies**, runs
anywhere Python runs, works on projects in any language and never executes the code it audits.

- 26 built-in checks across docs, community, automation, quality, security and packaging
- Weighted score from 0 to 100 and a grade from A to F
- Every failure comes with a hint that tells you how to fix it
- Output as text, JSON, Markdown for pull request comments, or an SVG badge for your README
- Drop-in GitHub Action that fails the build when health drops
- **Every check is a plugin.** Writing a new one takes about twenty lines

## Quick start

```bash
pip install git+https://github.com/YiTechX/repodoctor.git
repodoctor .
```

Or without installing anything permanent:

```bash
pipx run --spec git+https://github.com/YiTechX/repodoctor.git repodoctor .
```

## What it looks like

```text
RepoDoctor report for ~/projects/my-app

DOCS
  ✔ README present                         Found README.md
  ✘ README has real content                README.md has only 6 words
      ↳ Expand the README to at least 150 words
  ✘ README explains installation or usage  README has no installation or usage section
      ↳ Add an Installation or Usage section with a copy-pasteable example
  ✘ Changelog present                      No changelog found
      ↳ Add a CHANGELOG.md following the Keep a Changelog format
  ✔ README starts with a title             README starts with a heading

COMMUNITY
  ✘ License present                        No license file found
      ↳ Add a LICENSE file, for example the MIT license
  ✘ Contributing guide present             No contributing guide found
      ↳ Add a CONTRIBUTING.md covering setup, tests and the pull request process
  ...

SECURITY
  ✔ No secrets committed                   No known credential formats found
  ✘ Environment files are git-ignored      Environment files not ignored: .env
      ↳ Add them to .gitignore and keep a sanitised .env.example instead
  ✔ No private key files committed         No private key files found

Score 41/100  Grade F  ████████████░░░░░░░░░░░░░░░░░░
8 passed, 16 failed, 2 skipped
```

RepoDoctor audits itself in CI and keeps a score of 95 or above.

## What it checks

| Category | Check | Weight | What it verifies |
| --- | --- | ---: | --- |
| docs | `readme-exists` | 10 | README present |
| docs | `readme-substance` | 5 | README has real content |
| docs | `readme-usage` | 5 | README explains installation or usage |
| docs | `changelog-exists` | 3 | Changelog present |
| docs | `readme-title` | 2 | README starts with a title |
| community | `license-exists` | 8 | License present |
| community | `contributing-guide` | 6 | Contributing guide present |
| community | `code-of-conduct` | 4 | Code of conduct present |
| community | `issue-templates` | 3 | Issue templates present |
| community | `pull-request-template` | 3 | Pull request template present |
| community | `security-policy` | 3 | Security policy present |
| automation | `ci-configured` | 8 | Continuous integration configured |
| automation | `ci-runs-tests` | 4 | CI runs the test suite |
| automation | `dependency-updates` | 2 | Automated dependency updates |
| automation | `pre-commit-hooks` | 2 | Pre-commit hooks configured |
| quality | `tests-present` | 8 | Automated tests present |
| quality | `gitignore-exists` | 4 | .gitignore present |
| quality | `no-large-files` | 4 | No oversized files committed |
| quality | `linter-configured` | 3 | Linter or formatter configured |
| quality | `editorconfig` | 2 | .editorconfig present |
| security | `no-committed-secrets` | 10 | No secrets committed |
| security | `env-files-ignored` | 5 | Environment files are git-ignored |
| security | `no-private-key-files` | 4 | No private key files committed |
| packaging | `dependency-manifest` | 4 | Dependency manifest present |
| packaging | `python-project-metadata` | 4 | Python package metadata complete |
| packaging | `python-pyproject` | 3 | Python project uses pyproject.toml |

Run `repodoctor explain <id>` to learn why a check exists. Checks that do not apply to a project
(a Python check in a Go repository, for example) are skipped and never lower the score.

## Usage

| Command | What it does |
| --- | --- |
| `repodoctor` | Audit the current directory |
| `repodoctor path/to/repo` | Audit another directory |
| `repodoctor . --format markdown` | Choose `text`, `json`, `markdown` or `badge` |
| `repodoctor . --format badge -o health.svg` | Write the report to a file |
| `repodoctor . --fail-under 80` | Exit with status 1 below a score of 80 |
| `repodoctor . --only security` | Run a single category (repeatable) |
| `repodoctor . --disable changelog-exists` | Skip a check (repeatable) |
| `repodoctor . --exclude vendor` | Ignore a directory or glob (repeatable) |
| `repodoctor . --plugin ./my_checks` | Load extra checks from a file or directory |
| `repodoctor list` | List every check |
| `repodoctor explain license-exists` | Explain why a check matters |
| `repodoctor new-check my-rule` | Scaffold a new check |

Exit codes: `0` success, `1` score below the threshold, `2` invalid usage or configuration.

## Configuration

Put a `.repodoctor.toml` in the repository root, or a `[tool.repodoctor]` table in `pyproject.toml`:

```toml
fail_under = 80
disable = ["changelog-exists"]
exclude = ["vendor", "*.generated.py"]

[weights]
readme-exists = 10
tests-present = 9
```

Configuration files never load plugins, so auditing an untrusted repository is safe.

## GitHub Action

```yaml
name: Repository health
on: [push, pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: YiTechX/repodoctor@v0
        with:
          fail-under: "80"
```

The report is added to the job summary of every run.

Add the badge to your README by committing the output of `repodoctor . --format badge -o health.svg`.

## Python API

```python
import repodoctor

report = repodoctor.scan(".")
print(report.score, report.grade)

for result in report.failures():
    print(result.check.id, result.outcome.hint)
```

## Write your own check

```python
from repodoctor import check, fail, ok


@check(
    id="has-makefile",
    title="Makefile present",
    category="quality",
    weight=2,
    description="A Makefile gives contributors one place to find common tasks.",
)
def has_makefile(ctx):
    if ctx.is_file("Makefile"):
        return ok("Found Makefile")
    return fail("No Makefile found", hint="Add a Makefile with test and lint targets")
```

Save it as `my_checks/has_makefile.py` and run `repodoctor . --plugin my_checks`. Share a whole pack
of checks on PyPI through the `repodoctor.checks` entry point. The complete guide is in
[docs/writing-checks.md](docs/writing-checks.md).

## Contributing

Contributions are what make this project useful, and the bar for a first pull request is low on
purpose. The [roadmap](ROADMAP.md) lists more than twenty ready-to-build checks and several bigger
features, each small enough for a first contribution.

1. Pick an idea from [ROADMAP.md](ROADMAP.md).
2. Run `repodoctor new-check <id>` to generate the starter file.
3. Add two test rows and open a pull request.

Read [CONTRIBUTING.md](CONTRIBUTING.md) for the full walkthrough. Please follow our
[Code of Conduct](CODE_OF_CONDUCT.md). Found a vulnerability? See [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE)
