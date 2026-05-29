"""Local feature extraction for workspace images (no network calls)."""

from __future__ import annotations

import logging
from pathlib import Path

from colorthief import ColorThief

logger = logging.getLogger(__name__)

PALETTE_SIZE = 3


def rgb_to_hex(red: int, green: int, blue: int) -> str:
    return f"#{red:02x}{green:02x}{blue:02x}"


def palette_hex_from_file(
    image_path: Path,
    count: int = PALETTE_SIZE,
) -> list[str]:
    """Return up to `count` unique dominant colors as #rrggbb hex strings."""
    if not image_path.is_file() or count < 1:
        return []
    try:
        colors = ColorThief(str(image_path)).get_palette(
            color_count=max(2, min(count, PALETTE_SIZE)),
            quality=1,
        )
        hexes: list[str] = []
        seen: set[str] = set()
        for red, green, blue in colors:
            hex_color = rgb_to_hex(red, green, blue)
            if hex_color in seen:
                continue
            seen.add(hex_color)
            hexes.append(hex_color)
            if len(hexes) >= count:
                break
        return hexes
    except Exception:
        logger.exception("Failed to extract palette from %s", image_path)
        return []

