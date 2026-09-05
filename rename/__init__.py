"""Rename MP3 files to the "Artist - Title.mp3" convention.

Run as ``python -m rename``, or use the functions below from other scripts.
"""

from .core import (
    DEFAULT_ROOT,
    SEPARATOR,
    Rename,
    album_directory,
    apply_renames,
    new_name,
    plan_renames,
)

__all__ = [
    "DEFAULT_ROOT",
    "SEPARATOR",
    "Rename",
    "album_directory",
    "apply_renames",
    "new_name",
    "plan_renames",
]

__version__ = "1.0.0"
