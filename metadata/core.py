"""Tag logic: copy "Artist - Title.mp3" filenames into the ID3 artist and title."""

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import List, Optional, Tuple

try:
    from mutagen import MutagenError
    from mutagen.easyid3 import EasyID3
    from mutagen.id3 import ID3NoHeaderError
except ModuleNotFoundError as error:
    raise ModuleNotFoundError(
        "metadata needs mutagen: run '.\\.venv\\Scripts\\pip.exe install -r requirements.txt'",
        name="mutagen",
    ) from error

from rename.core import SEPARATOR

DEFAULT_DIRECTORY = Path("My playlist")


@dataclass(frozen=True)
class TagUpdate:
    """One file's wanted tags next to its current ones, or why it was skipped."""

    source: Path
    artist: Optional[str] = None
    title: Optional[str] = None
    current_artist: Optional[str] = None
    current_title: Optional[str] = None
    skip_reason: Optional[str] = None

    @property
    def skipped(self) -> bool:
        return self.skip_reason is not None

    @property
    def up_to_date(self) -> bool:
        return (
            not self.skipped
            and self.artist == self.current_artist
            and self.title == self.current_title
        )

    @property
    def pending(self) -> bool:
        return not self.skipped and not self.up_to_date


def parse_name(file_name: str) -> Optional[Tuple[str, str]]:
    """Split "Artist - Title.mp3" on the first separator; None if it doesn't fit."""
    artist, separator, title = Path(file_name).stem.partition(SEPARATOR)
    if not separator or not artist.strip() or not title.strip():
        return None
    return artist, title


def _load_tags(path: Path) -> EasyID3:
    try:
        return EasyID3(path)
    except ID3NoHeaderError:
        return EasyID3()


def read_tags(path: Path) -> Tuple[Optional[str], Optional[str]]:
    tags = _load_tags(path)
    artist = tags.get("artist", [None])[0]
    title = tags.get("title", [None])[0]
    return artist, title


def write_tags(path: Path, artist: str, title: str) -> None:
    tags = _load_tags(path)
    tags["artist"] = artist
    tags["title"] = title
    tags.save(path)


def plan_updates(directory: Path, since: Optional[date] = None) -> List[TagUpdate]:
    """Work out which files need new tags, without writing anything.

    Searches `directory` recursively. With `since`, files last modified on or
    before that day are ignored, which only speeds up the scan: files whose
    tags already match are never rewritten anyway.
    """
    plan = []

    for source in sorted(directory.rglob("*.mp3")):
        if since and date.fromtimestamp(source.stat().st_mtime) <= since:
            continue

        parsed = parse_name(source.name)
        if parsed is None:
            plan.append(
                TagUpdate(source, skip_reason=f"name is not 'Artist{SEPARATOR}Title'")
            )
            continue

        try:
            current_artist, current_title = read_tags(source)
        except MutagenError as error:
            plan.append(TagUpdate(source, skip_reason=f"cannot read tags ({error})"))
            continue

        artist, title = parsed
        plan.append(TagUpdate(source, artist, title, current_artist, current_title))

    return plan


def apply_updates(plan: List[TagUpdate]) -> List[TagUpdate]:
    """Write the tags of every pending entry in the plan and return those done."""
    done = []

    for entry in plan:
        if not entry.pending:
            continue
        write_tags(entry.source, entry.artist, entry.title)
        done.append(entry)

    return done
