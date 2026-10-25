# Roadmap

Everything here is open for anyone to pick up. Comment on the matching issue, or open one with
the **New check idea** template, and say you are working on it so nobody duplicates effort.

Check ids, categories and weights are suggestions. Better ideas are welcome.

## Good first issues: new checks

Each one is a single function plus a few test rows. See [CONTRIBUTING.md](CONTRIBUTING.md).

### Community

- [ ] `codeowners-file` (weight 2): a `CODEOWNERS` file exists in the root, `.github/` or `docs/`.
- [ ] `funding-file` (weight 1): `.github/FUNDING.yml` exists.
- [ ] `support-file` (weight 1): a `SUPPORT.md` tells people where to ask questions.
- [ ] `issue-template-config` (weight 1): `.github/ISSUE_TEMPLATE/config.yml` routes questions away from issues.
- [ ] `recent-activity` (weight 3): the repository has a commit in the last 12 months, read from `.git/logs/HEAD`.

### Docs

- [ ] `readme-badges` (weight 2): the README contains at least one badge image.
- [ ] `readme-relative-links` (weight 3): relative links in the README point to files that exist.
- [ ] `readme-license-section` (weight 1): the README mentions the license.
- [ ] `citation-file` (weight 1): research-style projects ship a `CITATION.cff`.
- [ ] `docs-directory` (weight 2): projects with more than 20 source files have a `docs/` directory.

### Quality

- [ ] `gitattributes-file` (weight 1): a `.gitattributes` normalises line endings.
- [ ] `todo-density` (weight 2): fewer than one `TODO` or `FIXME` per 200 lines of code.
- [ ] `no-committed-build-output` (weight 3): no tracked `dist/`, `build/`, `*.pyc` or `node_modules/`.
- [ ] `test-to-source-ratio` (weight 2): there is at least one test file for every five source files.

### Automation

- [ ] `ci-python-version-matrix` (weight 2): Python projects test on more than one interpreter version.
- [ ] `release-workflow` (weight 2): a workflow publishes tagged releases.
- [ ] `stale-bot` (weight 1): a stale-issue workflow or configuration exists.

### Security

- [ ] `actions-pinned-versions` (weight 3): workflow `uses:` lines avoid moving refs such as `@main`.
- [ ] `actions-minimal-permissions` (weight 3): every workflow declares `permissions:`.
- [ ] `dockerfile-pinned-base-image` (weight 3): `FROM` lines never use `:latest` or an untagged image.
- [ ] `no-hardcoded-passwords` (weight 4): flags `password = "..."` style assignments in config files.

### Packaging

- [ ] `py-typed-marker` (weight 2): typed Python libraries ship a `py.typed` marker.
- [ ] `node-lockfile` (weight 3): projects with a `package.json` commit a lockfile.
- [ ] `python-dependency-pinning` (weight 2): applications pin dependencies in a lockfile or requirements file.
- [ ] `semver-tags` (weight 2): git tags follow semantic versioning, read from `.git/packed-refs`.

## Help wanted: features

- [ ] **`repodoctor fix`**: generate missing files (LICENSE, CODE_OF_CONDUCT, SECURITY, `.gitignore`,
  issue templates) from built-in templates, with a dry run mode.
- [ ] **`--format html`**: a self-contained HTML dashboard with filters and category charts.
- [ ] **`--format sarif`**: upload results to GitHub code scanning.
- [ ] **`--format junit`**: show failed checks in any CI test report UI.
- [ ] **`repodoctor diff`**: compare two JSON reports and show what improved or regressed.
- [ ] **`repodoctor init`**: write a starter `.repodoctor.toml` based on what the repository contains.
- [ ] **Remote scans**: `repodoctor scan github:owner/repo` using a shallow clone.
- [ ] **Profiles**: presets such as `library`, `application` and `docs-site` that change weights.
- [ ] **Parallel execution** for very large repositories.
- [ ] **Translated hints**: a `--lang` option with community-maintained message catalogues.

## Big bets

- [ ] Ecosystem packs as separate plugins: JavaScript and TypeScript, Go, Rust, Java.
- [ ] A public plugin directory listing third-party check packs.
- [ ] A badge service that renders the score of any public repository.
- [ ] An editor extension that shows the report inline.

## Done

See [CHANGELOG.md](CHANGELOG.md).
