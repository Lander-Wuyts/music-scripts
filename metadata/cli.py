"""Command line interface for the metadata package."""

import argparse
import sys
from datetime import date

from rename.cli import TEST_MODE_BANNER, directory_argument

from .core import DEFAULT_DIRECTORY, apply_updates, plan_updates


def date_argument(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a YYYY-MM-DD date")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="metadata",
        description='Write the artist and title tags of "Artist - Title.mp3" files '
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
    if entry.title != entry.current_title:
        changes.append(f"title '{entry.current_title or ''}' ==> '{entry.title}'")
    return ", ".join(changes)


def main(argv=None) -> int:
    args = parse_args(argv)

    if not args.directory.is_dir():
        print(f"Directory not found: {args.directory}", file=sys.stderr)
        return 1

    plan = plan_updates(args.directory, args.since)
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
        for entry in apply_updates(plan):
            print(f"Tagged '{entry.source.relative_to(args.directory)}'")

    pending = sum(entry.pending for entry in plan)
    up_to_date = sum(entry.up_to_date for entry in plan)
    if args.execute:
        print(f"\n{pending} file(s) tagged, {up_to_date} already correct")
    else:
        print(f"\n{pending} file(s) would be tagged, {up_to_date} already correct")
        print("Use flag '-e' to execute program")

    return 0
