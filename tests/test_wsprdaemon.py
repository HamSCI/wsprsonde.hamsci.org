"""Tests for the WsprDaemon client that do not touch the network.

The query builders and the response parser are worth testing offline; the
queries themselves are exercised by running ``build_locations``. There is
deliberately no mock of the endpoint -- a mock of a server whose real quirks
(errors returned as HTTP 200, ``\\N`` for NULL) are the whole reason this module
exists would test the mock, not the client.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from wsprsonde import wsprdaemon as WD  # noqa: E402


def test_band_bases_cover_the_wspr_bands():
    """Every band a WSPRSonde-8 or a BeaconBlaster-6 can key must have a base."""
    for band in (1, 3, 5, 7, 10, 14, 18, 21, 24, 28, 50):
        assert band in WD.BAND_BASE_HZ


def test_band_base_sql_is_generated_from_the_table():
    """One definition of the band bases, not two."""
    sql = WD._band_base_sql()
    for band, base in WD.BAND_BASE_HZ.items():
        assert f"band={band},{base}" in sql
    assert sql.endswith(", 0)")


def test_band_base_sql_honours_the_column_name():
    assert "b=3,3570000" in WD._band_base_sql("b")


@pytest.mark.parametrize(
    "band, frequency, offset",
    [
        (3, 3_570_035, 35),      # KH2R on 80 m
        (10, 10_140_235, 135),   # WB6CXC on 30 m: base is 10.1401, not 10.1400
        (5, 5_366_136, 36),      # DP0GVN on 60 m
        (14, 14_097_037, 37),
    ],
)
def test_offset_arithmetic_matches_observed_frequencies(band, frequency, offset):
    """The offsets the community coordinates on are frequency minus band base.

    30 m is the one that catches people: its WSPR window starts at 10.1401 MHz,
    not 10.1400, so a naive base gives an offset 100 Hz too high.
    """
    assert frequency - WD.BAND_BASE_HZ[band] == offset


def test_empty_call_list_short_circuits():
    """No callsigns means no request -- these are volunteer-run servers."""
    assert WD.activity([]) == {}
    assert WD.observed_offsets([]) == {}
