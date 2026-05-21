"""
Unit tests — Chromatic Identity
Tests the core colour extraction and era assignment logic.
"""
import pytest
import numpy as np
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "code"))

from colors import get_dominant_colors, get_era, rgb_to_hsv


# ── get_era ──────────────────────────────────────────────────────────────

def test_era_bv_maier():
    assert get_era("bv", "bottega-veneta-women-fall-winter-2016-milan") == "BV — Tomas Maier"

def test_era_bv_lee():
    assert get_era("bv", "bottega-veneta-women-spring-summer-2020-milan") == "BV — Daniel Lee"

def test_era_bv_blazy():
    assert get_era("bv", "bottega-veneta-women-fall-winter-2023-milan") == "BV — Matthieu Blazy"

def test_era_lv_jacobs():
    assert get_era("lv", "louis-vuitton-women-fall-winter-2013-paris") == "LV — Marc Jacobs"

def test_era_lv_ghesquiere():
    assert get_era("lv", "louis-vuitton-women-spring-summer-2019-paris") == "LV — Nicolas Ghesquière"

def test_era_boundary_bv_2018():
    """2018 is last Maier year."""
    assert get_era("bv", "bottega-veneta-women-fall-winter-2018-milan") == "BV — Tomas Maier"

def test_era_boundary_bv_2019():
    """2019 is first Lee year."""
    assert get_era("bv", "bottega-veneta-women-spring-summer-2019-milan") == "BV — Daniel Lee"

def test_era_no_year_returns_unknown():
    assert get_era("bv", "bottega-veneta-no-date") == "inconnu"


# ── rgb_to_hsv ───────────────────────────────────────────────────────────

def test_hsv_pure_red():
    h, s, v = rgb_to_hsv([255, 0, 0])
    assert abs(h - 0.0) < 0.01
    assert abs(s - 1.0) < 0.01
    assert abs(v - 1.0) < 0.01

def test_hsv_pure_white():
    h, s, v = rgb_to_hsv([255, 255, 255])
    assert abs(s - 0.0) < 0.01
    assert abs(v - 1.0) < 0.01

def test_hsv_pure_black():
    h, s, v = rgb_to_hsv([0, 0, 0])
    assert abs(v - 0.0) < 0.01

def test_hsv_output_range():
    """H, S, V must all be in [0, 1]."""
    for rgb in [[128, 64, 200], [255, 128, 0], [10, 200, 150]]:
        h, s, v = rgb_to_hsv(rgb)
        assert 0.0 <= h <= 1.0
        assert 0.0 <= s <= 1.0
        assert 0.0 <= v <= 1.0


# ── get_dominant_colors ──────────────────────────────────────────────────

def test_dominant_colors_returns_n_colors():
    """Should return exactly N colours."""
    from PIL import Image, ImageDraw
    fake_img = Path("tests/fixtures/test_image.jpg")
    fake_img.parent.mkdir(parents=True, exist_ok=True)

    # Image avec 5 zones de couleurs distinctes
    img = Image.new("RGB", (100, 100))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0,  0,  20, 100], fill=(255, 0,   0))
    draw.rectangle([20, 0,  40, 100], fill=(0,   255, 0))
    draw.rectangle([40, 0,  60, 100], fill=(0,   0,   255))
    draw.rectangle([60, 0,  80, 100], fill=(255, 255, 0))
    draw.rectangle([80, 0, 100, 100], fill=(128, 0,   128))
    img.save(str(fake_img))

    colors = get_dominant_colors(fake_img, n=5)
    assert len(colors) == 5

def test_dominant_colors_valid_rgb():
    """Each colour must have 3 components in [0, 255]."""
    from PIL import Image
    fake_img = Path("tests/fixtures/test_image2.jpg")
    img = Image.new("RGB", (50, 50), color=(200, 100, 50))
    img.save(str(fake_img))

    colors = get_dominant_colors(fake_img, n=3)
    for rgb in colors:
        assert len(rgb) == 3
        for c in rgb:
            assert 0 <= c <= 255