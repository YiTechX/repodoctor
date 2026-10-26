# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Remote scans: `repodoctor github:owner/repo`, `gitlab:`, `codeberg:` and `https://` git URLs are
  shallow-cloned into a temporary directory, audited and removed. Also available through
  `repodoctor.scan()`.
- JSON reports include a `source` field naming the remote repository.
- `make badge` regenerates the README health badge.

## [0.1.0] - 2026-10-25

### Added

- `repodoctor scan` audits a repository and prints a score, a grade and a to-do list.
- 26 built-in checks across docs, community, automation, quality, security and packaging.
- Output formats: text, JSON, Markdown and an SVG badge.
- Plugin system: load extra checks with `--plugin` or the `repodoctor.checks` entry point group.
- `repodoctor new-check` scaffolds a new check in seconds.
- `repodoctor list` and `repodoctor explain` to browse the available checks.
- Configuration through `.repodoctor.toml` or `[tool.repodoctor]` in `pyproject.toml`.
- `--fail-under` for CI gating and a reusable GitHub Action.
- Python API: `repodoctor.scan()`.

[Unreleased]: https://github.com/YiTechX/repodoctor/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/YiTechX/repodoctor/releases/tag/v0.1.0
