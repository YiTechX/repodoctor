# Launch kit

Everything needed to introduce RepoDoctor to the world. Copy, adjust and post.

## Before posting

Do these first. Each one removes a reason for a visitor to leave.

1. **Publish to PyPI.** `pip install repodoctor` converts far better than a git URL. Create the
   `pypi` environment and a trusted publisher on PyPI, then push a tag: `git tag v0.2.0 && git push --tags`.
   Afterwards, replace the `git+https://` install lines in the README with `pip install repodoctor`
   and add a PyPI version badge.
2. **Release the Action.** Create the `v0` tag so `uses: YiTechX/repodoctor@v0` works, then publish
   the Action to the GitHub Marketplace from the release page.
3. **Repository settings.** Description: *Health score, grade and to-do list for any code
   repository. Zero dependencies, pluggable.* Topics: `repository-health`, `audit`, `cli`,
   `github-action`, `open-source`, `best-practices`, `developer-tools`, `python`, `code-quality`,
   `hacktoberfest`.
4. **Social preview image.** Upload a 1280×640 screenshot of a colored terminal report under
   Settings → General → Social preview. Links shared on social sites show this image.
5. **Good first issues.** Turn the items in [ROADMAP.md](../ROADMAP.md) into issues labelled
   `good first issue` and `help wanted`. They are listed on github.com/contribute,
   goodfirstissue.dev and up-for-grabs.net, which bring a steady stream of first-time contributors.
6. **Enable Discussions** so users have a place to show off their score.

## Hacker News (Show HN)

**Title:** Show HN: RepoDoctor – a health score and to-do list for any Git repository

> I kept running the same checklist on every repository I joined or open sourced: is there a
> license, does CI actually run the tests, are `.env` files ignored, is there a security policy.
> RepoDoctor turns that checklist into one command that prints a score from 0 to 100, a grade and
> a prioritized to-do list with a fix hint for every failure.
>
> You can point it at any public repository: `repodoctor github:pallets/flask`. It makes a shallow
> clone, audits it and deletes it. It has zero dependencies, never executes the code it audits and
> every check is a plugin of about twenty lines.
>
> Popular projects score between 79 and 95. I would love feedback on which checks are missing or
> wrong.

Post on a weekday between 14:00 and 16:00 UTC and stay around for a few hours to answer comments.

## Reddit

Subreddits: r/Python, r/opensource, r/programming, r/github, r/devops, r/coolgithubprojects.
Read each subreddit's self-promotion rules first and post to one or two per day, not all at once.

**Title:** I built a CLI that grades any GitHub repository's health (React gets an A, Express a C)

> RepoDoctor runs 26 checks across docs, community files, CI, tests, security and packaging, and
> gives you a score, a grade and a list of fixes. Try it on any public repository without cloning
> it yourself: `repodoctor github:owner/repo`. Zero dependencies, MIT licensed, and new checks are
> about twenty lines each, so first-time contributors are very welcome.

## X, Bluesky, Mastodon, LinkedIn

> How healthy is your repo? 🩺
>
> `repodoctor github:you/your-project`
>
> One command → score, grade and a to-do list. 26 checks, zero dependencies, works for any
> language. Even React and Django leave points on the table.
>
> github.com/YiTechX/repodoctor

Attach a screenshot or a short terminal recording (asciinema or vhs) of a colored report.

## Blog post outline (dev.to, Hashnode, Medium)

**Title:** I scanned 10 famous open source projects for repository health. Here is what they miss.

1. The checklist every maintainer forgets.
2. The results table from the README, and the most common gaps: code of conduct, pull request
   templates, pre-commit hooks.
3. How to run it on your own project and add the badge.
4. How to write your own check in twenty lines.

## Lists to submit to

Open a pull request that adds RepoDoctor to:

- awesome-python (Code Analysis section)
- awesome-cli-apps (Development section)
- awesome-github (Tools section)
- awesome-actions (Static Analysis section)
- awesome-readme (Tools section)
- best-of-python-dev

Follow each list's contribution rules; most require a minimum age or star count.

## Newsletters

Submit the repository to Python Weekly, PyCoder's Weekly, Console.dev, Changelog News and
TLDR. These link to new tools every week and reach hundreds of thousands of developers.

## Keep the momentum

- Answer every issue and pull request within a day for the first month.
- Release often and post a short changelog each time. Every release is a reason to share again.
- Thank first-time contributors publicly.
- Feature projects that show the badge in the README.
