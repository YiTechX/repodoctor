from __future__ import annotations

import fnmatch
import re
from pathlib import PurePosixPath

from ..context import RepoContext
from ..models import Outcome, fail, ok
from ..registry import check

SECRET_PATTERNS = (
    ("AWS access key ID", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("Slack token", re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("Stripe live key", re.compile(r"\b[sr]k_live_[0-9A-Za-z]{24,}\b")),
    (
        "Private key",
        re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY(?: BLOCK)?-----"),
    ),
)
ENV_FILE = re.compile(r"^\.env(?:\.(?!example$|sample$|template$|dist$)[\w.-]+)?$")
KEY_FILE_PATTERNS = (
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "*.p12",
    "*.pfx",
    "*.jks",
    "*.keystore",
)
MAX_LISTED = 5


def _ignore_patterns(ctx: RepoContext) -> list[str]:
    patterns = []
    for line in ctx.read_text(".gitignore").splitlines():
        entry = line.strip()
        if not entry or entry.startswith(("#", "!")):
            continue
        entry = entry.lstrip("/").removeprefix("**/")
        patterns.append(entry.rstrip("/"))
    return patterns


@check(
    id="no-committed-secrets",
    title="No secrets committed",
    category="security",
    weight=10,
    description="Scans text files for well-known credential formats such as AWS keys, GitHub "
    "tokens and private keys. Matches are reported by location only, never printed.",
)
def no_committed_secrets(ctx: RepoContext) -> Outcome:
    findings: list[str] = []
    for rel, text in ctx.text_files():
        for label, pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                findings.append(f"{rel}:{line} ({label})")
    if not findings:
        return ok("No known credential formats found")
    listed = ", ".join(findings[:MAX_LISTED])
    extra = len(findings) - MAX_LISTED
    suffix = f" and {extra} more" if extra > 0 else ""
    return fail(
        f"Possible secrets found: {listed}{suffix}",
        hint="Revoke the credentials, remove them from history and load them from the environment",
    )


@check(
    id="env-files-ignored",
    title="Environment files are git-ignored",
    category="security",
    weight=5,
    description="Files such as .env usually hold secrets and must be listed in .gitignore.",
)
def env_files_ignored(ctx: RepoContext) -> Outcome:
    env_files = [rel for rel in ctx.files() if ENV_FILE.match(PurePosixPath(rel).name)]
    if not env_files:
        return ok("No environment files present")
    patterns = _ignore_patterns(ctx)
    exposed = [
        rel
        for rel in env_files
        if not any(
            fnmatch.fnmatchcase(PurePosixPath(rel).name, pattern) or pattern == rel
            for pattern in patterns
        )
    ]
    if not exposed:
        return ok("Environment files are covered by .gitignore")
    return fail(
        f"Environment files not ignored: {', '.join(exposed[:MAX_LISTED])}",
        hint="Add them to .gitignore and keep a sanitised .env.example instead",
    )


@check(
    id="no-private-key-files",
    title="No private key files committed",
    category="security",
    weight=4,
    description="SSH keys and keystores should never live in a repository.",
)
def no_private_key_files(ctx: RepoContext) -> Outcome:
    found = ctx.named(*KEY_FILE_PATTERNS)
    if not found:
        return ok("No private key files found")
    return fail(
        f"Key material committed: {', '.join(found[:MAX_LISTED])}",
        hint="Remove the files, rotate the keys and add the patterns to .gitignore",
    )
