from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from .errors import RepoDoctorError

HOST_PREFIXES = {
    "github:": "https://github.com/",
    "gitlab:": "https://gitlab.com/",
    "codeberg:": "https://codeberg.org/",
}
URL_PREFIX = "https://"
SLUG = re.compile(r"[A-Za-z0-9_.-]+(/[A-Za-z0-9_.-]+)+")
CLONE_TIMEOUT = 300
# Symlinks are checked out as plain files so a hostile repository cannot point a check at
# files outside the clone. Hooks are never cloned, so nothing from the repository runs.
CLONE_COMMAND = (
    "git",
    "-c",
    "core.symlinks=false",
    "clone",
    "--depth",
    "1",
    "--single-branch",
    "--no-tags",
    "--quiet",
)


def is_remote(target: str) -> bool:
    if Path(target).exists():
        return False
    return target.startswith(URL_PREFIX) or target.lower().startswith(tuple(HOST_PREFIXES))


def remote_url(target: str) -> str:
    lowered = target.lower()
    for prefix, base in HOST_PREFIXES.items():
        if lowered.startswith(prefix):
            slug = target[len(prefix) :].strip("/").removesuffix(".git")
            if not SLUG.fullmatch(slug) or ".." in slug:
                raise RepoDoctorError(f"expected {prefix}owner/repo, got: {target}")
            return f"{base}{slug}.git"
    if target.startswith(URL_PREFIX) and len(target) > len(URL_PREFIX):
        return target
    raise RepoDoctorError(f"not a remote repository: {target}")


@contextmanager
def checkout(target: str) -> Iterator[Path]:
    url = remote_url(target)
    if shutil.which("git") is None:
        raise RepoDoctorError("scanning a remote repository requires git on PATH")
    workdir = tempfile.mkdtemp(prefix="repodoctor-")
    destination = Path(workdir) / "repo"
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_LFS_SKIP_SMUDGE": "1"}
    try:
        try:
            subprocess.run(
                [*CLONE_COMMAND, "--", url, str(destination)],
                check=True,
                capture_output=True,
                text=True,
                env=env,
                timeout=CLONE_TIMEOUT,
            )
        except subprocess.CalledProcessError as exc:
            detail = (exc.stderr or "").strip().splitlines()
            reason = detail[-1] if detail else f"git exited with status {exc.returncode}"
            raise RepoDoctorError(f"could not clone {url}: {reason}") from exc
        except subprocess.TimeoutExpired as exc:
            raise RepoDoctorError(f"cloning {url} took longer than {CLONE_TIMEOUT}s") from exc
        yield destination
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
