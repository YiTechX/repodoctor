from __future__ import annotations

import fnmatch
import os
import tomllib
from collections import Counter
from collections.abc import Iterable, Iterator
from pathlib import Path, PurePosixPath
from typing import Any

IGNORED_DIRS = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".tox",
        ".nox",
        ".eggs",
        ".cache",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".idea",
        ".vscode",
        ".gradle",
        ".next",
        "site-packages",
        "dist",
        "build",
    }
)

DOC_SUFFIXES = frozenset({"", ".md", ".markdown", ".rst", ".txt", ".adoc"})
DEFAULT_DOC_DIRS = ("",)

LANGUAGE_SUFFIXES = {
    ".py": "Python",
    ".js": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".kt": "Kotlin",
    ".rb": "Ruby",
    ".php": "PHP",
    ".c": "C",
    ".h": "C",
    ".cpp": "C++",
    ".cc": "C++",
    ".hpp": "C++",
    ".cs": "C#",
    ".swift": "Swift",
    ".scala": "Scala",
    ".ex": "Elixir",
    ".exs": "Elixir",
    ".dart": "Dart",
    ".lua": "Lua",
    ".sh": "Shell",
}

BINARY_SNIFF_BYTES = 2048
DEFAULT_READ_LIMIT = 500_000
DEFAULT_SCAN_LIMIT = 1_000_000


class RepoContext:
    def __init__(self, root: str | Path, exclude: Iterable[str] = ()) -> None:
        self.root = Path(root).resolve()
        self.exclude = tuple(exclude)
        self._files: tuple[str, ...] | None = None
        self._by_dir: dict[str, list[str]] | None = None
        self._languages: Counter[str] | None = None

    @property
    def name(self) -> str:
        return self.root.name

    def path(self, rel: str) -> Path:
        return self.root / rel

    def exists(self, rel: str) -> bool:
        return self.path(rel).exists()

    def is_file(self, rel: str) -> bool:
        return self.path(rel).is_file()

    def is_dir(self, rel: str) -> bool:
        return self.path(rel).is_dir()

    def files(self) -> tuple[str, ...]:
        if self._files is None:
            self._files = tuple(sorted(self._walk()))
        return self._files

    def size(self, rel: str) -> int:
        try:
            return self.path(rel).stat().st_size
        except OSError:
            return 0

    def read_text(self, rel: str, limit: int = DEFAULT_READ_LIMIT) -> str:
        data = self._read_bytes(rel, limit)
        return data.decode("utf-8", errors="replace") if data is not None else ""

    def read_toml(self, rel: str) -> dict[str, Any]:
        try:
            with open(self.path(rel), "rb") as handle:
                return tomllib.load(handle)
        except OSError:
            return {}

    def text_files(self, max_size: int = DEFAULT_SCAN_LIMIT) -> Iterator[tuple[str, str]]:
        for rel in self.files():
            if self.size(rel) > max_size:
                continue
            data = self._read_bytes(rel, max_size)
            if data is None or b"\0" in data[:BINARY_SNIFF_BYTES]:
                continue
            yield rel, data.decode("utf-8", errors="replace")

    def matching(self, *patterns: str) -> list[str]:
        lowered = [pattern.lower() for pattern in patterns]
        return [
            rel
            for rel in self.files()
            if any(fnmatch.fnmatchcase(rel.lower(), pattern) for pattern in lowered)
        ]

    def named(self, *patterns: str) -> list[str]:
        lowered = [pattern.lower() for pattern in patterns]
        return [
            rel
            for rel in self.files()
            if any(fnmatch.fnmatchcase(PurePosixPath(rel).name.lower(), p) for p in lowered)
        ]

    def find_doc(self, *stems: str, dirs: Iterable[str] = DEFAULT_DOC_DIRS) -> str | None:
        wanted = {stem.lower() for stem in stems}
        index = self._index()
        for directory in dirs:
            for rel in index.get(directory or ".", []):
                path = PurePosixPath(rel)
                if path.stem.lower() in wanted and path.suffix.lower() in DOC_SUFFIXES:
                    return rel
        return None

    def language_counts(self) -> Counter[str]:
        if self._languages is None:
            counts: Counter[str] = Counter()
            for rel in self.files():
                language = LANGUAGE_SUFFIXES.get(PurePosixPath(rel).suffix.lower())
                if language:
                    counts[language] += 1
            self._languages = counts
        return self._languages

    def has_language(self, language: str) -> bool:
        return self.language_counts().get(language, 0) > 0

    def _index(self) -> dict[str, list[str]]:
        if self._by_dir is None:
            index: dict[str, list[str]] = {}
            for rel in self.files():
                index.setdefault(str(PurePosixPath(rel).parent), []).append(rel)
            self._by_dir = index
        return self._by_dir

    def _read_bytes(self, rel: str, limit: int) -> bytes | None:
        try:
            with open(self.path(rel), "rb") as handle:
                return handle.read(limit)
        except OSError:
            return None

    def _walk(self) -> Iterator[str]:
        for current, dirs, names in os.walk(self.root):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.endswith(".egg-info")]
            base = Path(current).relative_to(self.root)
            for name in names:
                rel = (base / name).as_posix()
                if not self._excluded(rel):
                    yield rel

    def _excluded(self, rel: str) -> bool:
        for pattern in self.exclude:
            trimmed = pattern.rstrip("/")
            if fnmatch.fnmatchcase(rel, pattern) or rel == trimmed or rel.startswith(trimmed + "/"):
                return True
        return False
