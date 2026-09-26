"""Command line interface for the rename package."""

import argparse
import sys
from pathlib import Path

from .core import DEFAULT_ROOT, album_directory, apply_renames, plan_renames

TEST_MODE_BANNER = "######################## Test mode ########################"


def directory_argument(value: str) -> Path:
    """Build a Path from -d, tolerating Windows quoting quirks.

    In `-d "E:\\Folder\\"` the shell treats the final `\\"` as an escaped quote, so the
    value arrives with a stray `"` glued to the end.
    """
    return Path(value.strip().rstrip('"').strip())


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="rename",
        description='Rename an album\'s MP3 files to "Artist - Title.mp3".',
    )
    parser.add_argument(
        "-n", "--name",
        required=True,
        help="band name"
    )
    parser.add_argument(
        "-s", "--strip",
        required=True,
        type=int,
        help="number of leading characters to strip from each filename; "
        "a negative number strips that many trailing characters (the .mp3 is kept)",
    )
    parser.add_argument(
        "-e", "--execute",
        action="store_true",
        help="perform the renames (default is a dry run)",
    )
    parser.add_argument(
        "-d", "--directory",
        type=directory_argument,
        help=f"folder holding the MP3 files (default: {DEFAULT_ROOT}\\<name>)",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    directory = album_directory(args.name, args.directory)
    if not directory.is_dir():
        print(f"Directory not found: {directory}", file=sys.stderr)
        return 1

    plan = plan_renames(directory, args.name, args.strip)
    if not plan:
        print(f"No .mp3 files found in {directory}", file=sys.stderr)
        return 1

    if not args.execute:
        print(TEST_MODE_BANNER)

    for entry in plan:
        if entry.skipped:
            print(f"! Skipped '{entry.source.name}': {entry.skip_reason}")
        elif not args.execute:
            print(f"# To change: '{entry.source.name}' ==> '{entry.target.name}'")

    if args.execute:
        for entry in apply_renames(plan):
            print(f"Renamed '{entry.source.name}' to '{entry.target.name}'")

    pending = sum(not entry.skipped for entry in plan)
    if args.execute:
        print(f"\n{pending} file(s) renamed")
    else:
        print(f"\n{pending} file(s) would be renamed")
        print("Use flag '-e' to execute program")

    return 0
