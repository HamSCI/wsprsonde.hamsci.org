"""Tests for Maidenhead conversion.

The reference values are real WSPRSonde sites, so a regression here shows up as
a station in the wrong place on a map rather than as an abstract failure.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from wsprsonde import maidenhead as M  # noqa: E402


@pytest.mark.parametrize(
    "locator, lat, lon",
    [
        ("FN21", 41.5, -75.0),               # KH2R as WSPRNet reports it
        ("FN21us", 41.7708, -74.2917),       # KH2R as the curated list records it
        ("IB59ui", -70.6458, -8.2917),       # DP0GVN, Neumayer III
        ("EQ79", 79.5, -85.0),               # VY0ERC, Eureka
        ("CM88mj", 38.3958, -122.9583),      # WB6CXC, Occidental
        ("EK70wb", 10.0625, -84.125),        # TI4JWC, Costa Rica
    ],
)
def test_to_latlon(locator, lat, lon):
    got_lat, got_lon = M.to_latlon(locator)
    assert got_lat == pytest.approx(lat, abs=1e-4)
    assert got_lon == pytest.approx(lon, abs=1e-4)


def test_four_character_grid_is_far_from_the_six_character_one():
    """KH2R's reported grid is ~65 km from its real one -- the reason we prefer the latter."""
    reported = M.to_latlon("FN21")
    curated = M.to_latlon("FN21us")
    assert abs(curated[0] - reported[0]) > 0.25
    assert abs(curated[1] - reported[1]) > 0.5


@pytest.mark.parametrize("locator", ["FN21", "FN21us", "IB59ui", "CM88mj12"])
def test_roundtrip(locator):
    lat, lon = M.to_latlon(locator)
    assert M.from_latlon(lat, lon, precision=len(locator)) == locator


@pytest.mark.parametrize("bad", ["", "F", "FN2", "FN21z", "SS00", "FN21zz", "12ab", None])
def test_invalid_rejected(bad):
    assert not M.is_valid(bad)
    with pytest.raises(ValueError):
        M.to_latlon(bad or "")


def test_normalise_accepts_any_case():
    assert M.normalise("fn21US") == "FN21us"


def test_precision():
    assert M.precision_of("EQ79") == 4
    assert M.precision_of("FN21us") == 6


@pytest.mark.parametrize("precision", [3, 5, 7, 10])
def test_from_latlon_rejects_bad_precision(precision):
    with pytest.raises(ValueError):
        M.from_latlon(41.0, -75.0, precision=precision)


def test_from_latlon_rejects_out_of_range():
    with pytest.raises(ValueError):
        M.from_latlon(95.0, 0.0)
