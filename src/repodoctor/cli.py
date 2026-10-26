from __future__ import annotations

import argparse
import dataclasses
import os
import sys
from contextlib import nullcontext
from pathlib import Path

from ._version import __version__
from .config import load_config
from .engine import prepare_registry, scan_repository
from .errors import RepoDoctorError
from .registry import all_checks, get_check
from .remote import checkout, is_remote
from .reporters import RenderOptions, get_reporter
from .scaffold import write_check_scaffold

COMMANDS = ("scan", "list", "explain", "new-check")
TOP_LEVEL_FLAGS = ("-h", "--help", "--version")
EXIT_OK = 0
EXIT_BELOW_THRESHOLD = 1
EXIT_USAGE = 2
DEFAULT_SCAFFOLD_DIR = "."


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="repodoctor",
        description="Audit the health of a code repository: get a score, a grade and a to-do list.",
    )
    parser.add_argument("--version", action="version", version=f"repodoctor {__version__}")
    commands = parser.add_subparsers(dest="command", metavar="COMMAND")

    plugin_args = argparse.ArgumentParser(add_help=False)
    plugin_args.add_argument(
        "--plugin",
        action="append",
        default=[],
        metavar="PATH",
        help="load extra checks from a Python file or a directory of Python files",
    )

    scan = commands.add_parser(
        "scan",
        parents=[plugin_args],
        help="audit a repository (default command)",
        description="Audit a repository and print its health report.",
    )
    scan.add_argument(
        "path",
        nargs="?",
        default=".",
        help="repository directory, github:owner/repo or an https:// git URL (default: .)",
    )
    scan.add_argument("-f", "--format", default="text", help="text, json, markdown or badge")
    scan.add_argument("-o", "--output", metavar="FILE", help="write the report to a file")
    scan.add_argument(
        "--fail-under",
        type=int,
        metavar="SCORE",
        help="exit with status 1 when the score is below SCORE",
    )
    scan.add_argument("--disable", action="append", default=[], metavar="ID", help="skip a check")
    scan.add_argument(
        "--only",
        action="append",
        default=[],
        metavar="CATEGORY",
        help="run only checks from this category",
    )
    scan.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="PATTERN",
        help="ignore files matching this glob or directory",
    )
    scan.add_argument("--no-color", action="store_true", help="disable colored output")
    scan.set_defaults(handler=_scan)

    listing = commands.add_parser(
        "list",
        parents=[plugin_args],
        help="list every available check",
    )
    listing.set_defaults(handler=_list)

    explain = commands.add_parser(
        "explain",
        parents=[plugin_args],
        help="describe a check and why it matters",
    )
    explain.add_argument("check_id", metavar="ID")
    explain.set_defaults(handler=_explain)

    scaffold = commands.add_parser(
        "new-check",
        help="generate a starter file for a new check",
    )
    scaffold.add_argument("check_id", metavar="ID", help="for example: has-funding-file")
    scaffold.add_argument("--category", default="quality")
    scaffold.add_argument("--weight", type=int, default=5)
    scaffold.add_argument(
        "--output-dir",
        default=DEFAULT_SCAFFOLD_DIR,
        metavar="DIR",
        help="where to write the file (default: current directory)",
    )
    scaffold.set_defaults(handler=_new_check)
    return parser


def _supports_unicode(stream) -> bool:
    encoding = (getattr(stream, "encoding", None) or "ascii").lower().replace("-", "")
    return encoding.startswith("utf")


def _scan(args: argparse.Namespace) -> int:
    if args.fail_under is not None and not 0 <= args.fail_under <= 100:
        raise RepoDoctorError("--fail-under must be between 0 and 100")
    remote = is_remote(args.path)
    with checkout(args.path) if remote else nullcontext(Path(args.path)) as root:
        config = load_config(root) if root.is_dir() else None
        report = scan_repository(
            root,
            config=config,
            disable=args.disable,
            only=args.only,
            exclude=args.exclude,
            plugins=args.plugin,
        )
    if remote:
        report = dataclasses.replace(report, source=args.path)
    render = get_reporter(args.format)
    writing_file = args.output is not None
    use_color = (
        args.format == "text"
        and not writing_file
        and not args.no_color
        and "NO_COLOR" not in os.environ
        and sys.stdout.isatty()
    )
    options = RenderOptions(color=use_color, unicode=writing_file or _supports_unicode(sys.stdout))
    rendered = render(report, options)
    if writing_file:
        Path(args.output).write_text(rendered, encoding="utf-8")
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(rendered)
    threshold = args.fail_under
    if threshold is None and config is not None:
        threshold = config.fail_under
    if threshold is not None and report.score < threshold:
        print(
            f"repodoctor: score {report.score} is below the required {threshold}",
            file=sys.stderr,
        )
        return EXIT_BELOW_THRESHOLD
    return EXIT_OK


def _list(args: argparse.Namespace) -> int:
    prepare_registry(args.plugin)
    checks = all_checks()
    id_width = max(len(item.id) for item in checks)
    category_width = max(len(item.category) for item in checks)
    for item in checks:
        print(
            f"{item.id.ljust(id_width)}  {item.category.ljust(category_width)}  "
            f"{item.weight:>2}  {item.title}"
        )
    print(f"\n{len(checks)} checks", file=sys.stderr)
    return EXIT_OK


def _explain(args: argparse.Namespace) -> int:
    prepare_registry(args.plugin)
    item = get_check(args.check_id)
    print(f"{item.id}: {item.title}")
    print(f"category: {item.category}   weight: {item.weight}")
    print()
    print(item.description)
    return EXIT_OK


def _new_check(args: argparse.Namespace) -> int:
    target = write_check_scaffold(args.check_id, args.category, args.weight, args.output_dir)
    print(f"Created {target}")
    print(f"Try it with: repodoctor scan . --plugin {target}")
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or (args[0] not in COMMANDS and args[0] not in TOP_LEVEL_FLAGS):
        args.insert(0, "scan")
    parser = build_parser()
    parsed = parser.parse_args(args)
    try:
        return parsed.handler(parsed)
    except RepoDoctorError as exc:
        print(f"repodoctor: error: {exc}", file=sys.stderr)
        return EXIT_USAGE
