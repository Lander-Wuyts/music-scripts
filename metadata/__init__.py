"""Write ID3 artist and title tags from "Artist - Title.mp3" filenames.

Run as ``python -m metadata``, or use the functions below from other scripts.
"""

from .core import (
    DEFAULT_DIRECTORY,
    TagUpdate,
    apply_updates,
    parse_name,
    plan_updates,
    read_tags,
    write_tags,
)

__all__ = [
    "DEFAULT_DIRECTORY",
    "TagUpdate",
    "apply_updates",
    "parse_name",
    "plan_updates",
    "read_tags",
    "write_tags",
]

__version__ = "1.0.0"
