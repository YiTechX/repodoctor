# Writing checks

A check is a plain function decorated with `@check`. This guide covers everything you need to write,
test and distribute one.

## Anatomy of a check

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

This is the real `readme-title` check from `src/repodoctor/checks/docs.py`.

| Argument      | Meaning                                                                       |
| ------------- | ----------------------------------------------------------------------------- |
| `id`          | Unique, lowercase, words joined by dashes. Used in `--disable` and config.    |
| `title`       | Short label shown in reports.                                                 |
| `category`    | `docs`, `community`, `automation`, `quality`, `security`, `packaging` or your own. |
| `weight`      | 1 to 10. Share of the score this check is worth.                              |
| `description` | Shown by `repodoctor explain ID`. Say what is checked and why it matters.     |

## Outcomes

| Helper                 | Effect on the score                                    |
| ---------------------- | ------------------------------------------------------ |
| `ok(message)`          | Counts as passed.                                      |
| `fail(message, hint)`  | Counts as failed. The hint tells the reader how to fix it. |
| `skip(message)`        | Ignored. Use it when the check does not apply.         |

If a check raises an exception it is reported as skipped with the error message, so one buggy
check never takes down a whole run.

## What `RepoContext` offers

| Member                              | Description                                                                 |
| ----------------------------------- | --------------------------------------------------------------------------- |
| `root`                              | `Path` of the repository.                                                   |
| `files()`                           | Sorted tuple of relative POSIX paths. Skips `.git`, `node_modules`, caches. |
| `exists(rel)`, `is_file(rel)`, `is_dir(rel)` | Filesystem tests relative to the root.                             |
| `read_text(rel, limit)`             | Decoded text, empty string if unreadable.                                   |
| `read_toml(rel)`                    | Parsed TOML. Empty dict if missing, raises `ValueError` if invalid.         |
| `size(rel)`                         | Size in bytes, `0` if unreadable.                                           |
| `find_doc(*stems, dirs=...)`        | Case-insensitive lookup like `README`, `README.md`, `readme.rst`.           |
| `matching(*patterns)`               | Case-insensitive glob over full relative paths.                             |
| `named(*patterns)`                  | Case-insensitive glob over base names at any depth.                         |
| `text_files(max_size)`              | Iterator of `(path, text)` for non-binary files.                            |
| `language_counts()`, `has_language(name)` | Source files per language, detected by extension.                     |

Files excluded through `--exclude` or `.repodoctor.toml` never show up in these helpers.

## Writing good checks

- **Be precise.** A false positive costs more trust than a missed problem.
- **Explain the fix.** Hints should be copy-and-paste actionable.
- **Skip, do not fail**, when the check is irrelevant to the project type.
- **Stay read-only.** Checks must never modify or execute anything in the audited repository.
- **Protect secrets.** Report locations, never values.
- **Keep it fast.** Reuse `ctx.files()`; it is computed once per run.

## Testing a built-in check

Add rows to `CASES` in `tests/test_builtin_checks.py`:

```python
(("readme-title", {"README.md": "# Demo\n"}, PASSED),)
(("readme-title", {"README.md": "No heading here\n"}, FAILED),)
(("readme-title", {}, SKIPPED),)
```

Each row is `(check id, files to create in a temporary repository, expected status)`. A meta test makes sure every
built-in check has both a passing and a failing row.

## Keeping a check private or shipping it as a plugin

Generate a starter file anywhere and load it explicitly:

```
repodoctor new-check my-team-rule --category quality --output-dir ./repodoctor_checks
repodoctor scan . --plugin ./repodoctor_checks
```

`--plugin` accepts a Python file or a directory of Python files. Files starting with an underscore are ignored.

To distribute a pack of checks on PyPI, expose the module that defines them through an entry point:

```toml
[project.entry-points."repodoctor.checks"]
my_team_rules = "my_team_rules.checks"
```

Installing the package is enough; RepoDoctor imports the module on every run.

Configuration files in an audited repository can never load plugins, so scanning an untrusted
repository does not execute its code.

## Custom output formats

Reporters work the same way as checks:

```python
from repodoctor.reporters import reporter


@reporter("csv")
def render_csv(report, options):
    rows = ["id,status"]
    rows.extend(f"{item.check.id},{item.status.value}" for item in report.results)
    return "\n".join(rows) + "\n"
```

Load the module with `--plugin` and run `repodoctor scan . --format csv`.
