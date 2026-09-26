"""Command line interface for the metadata package."""

import argparse
import shutil
import sys
from datetime import date
from pathlib import Path

from rename.cli import TEST_MODE_BANNER, directory_argument

from .core import DEFAULT_DIRECTORY, apply_updates, plan_updates


BAR_LENGTH = 20


class StatusLine:
    """A single progress line on stderr, redrawn in place.

    Does nothing when stderr is not a terminal, so redirected output stays clean.
    """

    def __init__(self, directory: Path):
        self.directory = directory
        self.enabled = sys.stderr.isatty()
        self.width = 0

    def update(self, action: str, position: int, total: int, path: Path) -> None:
        if not self.enabled:
            return
        done = BAR_LENGTH * position // total
        bar = "*" * done + " " * (BAR_LENGTH - done)
        line = (
            f"{action} [{position}/{total}] [{bar}] {100 * position // total:3}% "
            f"{path.relative_to(self.directory)}"
        )
        # Keep it on one line; wrapping would break the in-place redraw.
        line = line[: shutil.get_terminal_size().columns - 1]
        sys.stderr.write("\r" + line.ljust(self.width))
        sys.stderr.flush()
        self.width = len(line)

    def clear(self) -> None:
        if self.enabled and self.width:
            sys.stderr.write("\r" + " " * self.width + "\r")
            sys.stderr.flush()
            self.width = 0


def date_argument(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a YYYY-MM-DD date")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="metadata",
        description='Write the artist, album artist and title tags of "Artist - Title.mp3" files '
        "from their filenames.",
    )
    parser.add_argument(
        "-d",
        "--directory",
        type=directory_argument,
        default=DEFAULT_DIRECTORY,
        help=f"folder to search recursively (default: {DEFAULT_DIRECTORY})",
    )
    parser.add_argument(
        "--since",
        type=date_argument,
        help="only look at files modified after this YYYY-MM-DD date",
    )
    parser.add_argument(
        "-e",
        "--execute",
        action="store_true",
        help="write the tags (default is a dry run)",
    )
    return parser.parse_args(argv)


def describe(entry) -> str:
    changes = []
    if entry.artist != entry.current_artist:
        changes.append(f"artist '{entry.current_artist or ''}' ==> '{entry.artist}'")
    if entry.artist != entry.current_album_artist:
        changes.append(
            f"album artist '{entry.current_album_artist or ''}' ==> '{entry.artist}'"
        )
    if entry.title != entry.current_title:
        changes.append(f"title '{entry.current_title or ''}' ==> '{entry.title}'")
    return ", ".join(changes)


def main(argv=None) -> int:
    args = parse_args(argv)

    if not args.directory.is_dir():
        print(f"Directory not found: {args.directory}", file=sys.stderr)
        return 1

    status = StatusLine(args.directory)
    plan = plan_updates(
        args.directory,
        args.since,
        lambda position, total, path: status.update(
            "Reading", position, total, path
        ),
    )
    status.clear()
    if not plan and args.since:
        print(f"No .mp3 files modified after {args.since} in {args.directory}")
        return 0
    if not plan:
        print(f"No .mp3 files found in {args.directory}", file=sys.stderr)
        return 1

    if not args.execute:
        print(TEST_MODE_BANNER)

    for entry in plan:
        name = entry.source.relative_to(args.directory)
        if entry.skipped:
            print(f"! Skipped '{name}': {entry.skip_reason}")
        elif entry.pending and not args.execute:
            print(f"# To change: '{name}': {describe(entry)}")

    if args.execute:
        done = apply_updates(
            plan,
            lambda position, total, path: status.update(
                "Writing", position, total, path
            ),
        )
        status.clear()
        for entry in done:
            print(f"Tagged '{entry.source.relative_to(args.directory)}'")

    pending = sum(entry.pending for entry in plan)
    up_to_date = sum(entry.up_to_date for entry in plan)
    if args.execute:
        print(f"\n{pending} file(s) tagged, {up_to_date} already correct")
    else:
        print(f"\n{pending} file(s) would be tagged, {up_to_date} already correct")
        print("Use flag '-e' to execute program")

    return 0
