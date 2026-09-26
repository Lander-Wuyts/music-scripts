"""Filename logic for the "Artist - Title.mp3" convention."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

DEFAULT_ROOT = Path(r"E:\Torrents")
SEPARATOR = " - "


@dataclass(frozen=True)
class Rename:
    """One planned rename, or one file that will be left alone."""

    source: Path
    target: Optional[Path] = None
    skip_reason: Optional[str] = None

    @property
    def skipped(self) -> bool:
        return self.target is None


def album_directory(band: str, directory: Optional[Path] = None) -> Path:
    return directory or DEFAULT_ROOT / band


def new_name(band: str, file_name: str, strip: int) -> str:
    """Strip `strip` leading characters, or trailing ones (before the extension) if negative."""
    if strip < 0:
        path = Path(file_name)
        return f"{path.stem[:strip]}{path.suffix}"
    return f"{band}{SEPARATOR}{file_name[strip:]}"


def plan_renames(directory: Path, band: str, strip: int) -> List[Rename]:
    """Work out what would change, without touching the filesystem."""
    plan = []

    prefix = f"{band}{SEPARATOR}"

    for source in sorted(directory.glob("*.mp3")):
        if abs(strip) >= len(source.stem):
            plan.append(
                Rename(source, skip_reason="--strip removes the whole name")
            )
            continue

        target = source.with_name(new_name(band, source.name, strip))

        if target.exists():
            plan.append(
                Rename(source, skip_reason=f"'{target.name}' already exists")
            )
        else:
            plan.append(Rename(source, target))

    return plan


def apply_renames(plan: List[Rename]) -> List[Rename]:
    """Perform every non-skipped rename in the plan and return those done."""
    done = []

    for entry in plan:
        if entry.skipped:
            continue
        entry.source.rename(entry.target)
        done.append(entry)

    return done
