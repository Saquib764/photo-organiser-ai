"""Tests for dominant color extraction."""

from pathlib import Path

from PIL import Image

from app.services.image_features import palette_hex_from_file, rgb_to_hex


def test_rgb_to_hex() -> None:
    assert rgb_to_hex(170, 187, 204) == "#aabbcc"


def test_palette_hex_from_file(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"
    Image.new("RGB", (32, 32), (180, 60, 60)).save(image_path)
    colors = palette_hex_from_file(image_path)
    assert colors
    assert colors[0].startswith("#")
    assert len(colors[0]) == 7


def test_palette_hex_from_file_returns_up_to_three(tmp_path: Path) -> None:
    image_path = tmp_path / "palette.png"
    Image.new("RGB", (64, 64), (200, 80, 80)).save(image_path)
    colors = palette_hex_from_file(image_path, count=3)
    assert 1 <= len(colors) <= 3
    assert all(c.startswith("#") and len(c) == 7 for c in colors)


def test_palette_hex_missing_file(tmp_path: Path) -> None:
    assert palette_hex_from_file(tmp_path / "missing.png") == []
