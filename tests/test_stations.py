"""Tests for the curated station list and the observed/administrative join.

These run against the real ``data/wsprsonde_stations.csv`` -- the file is small,
hand-edited and load-bearing, so validating the shipped copy is more useful than
validating a fixture. Nothing here touches the network; observations are
injected.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from wsprsonde import stations as S  # noqa: E402
from wsprsonde.wsprdaemon import Activity  # noqa: E402


@pytest.fixture
def station_list():
    """Freshly loaded each test: several tests mutate a station in place."""
    return S.load()


def test_curated_list_loads_and_validates(station_list):
    """load() enforces unique ids, known statuses and valid locators."""
    assert len(station_list) > 15


def test_every_deployed_station_has_a_position(station_list):
    """A deployed station with no locator cannot be mapped, which is a data bug."""
    missing = [st.station_id for st in station_list
               if st.record_status == "deployed" and st.position == (None, None)]
    assert missing == []


def test_site_id_collapses_the_two_occidental_units(station_list):
    """WB6CXC runs two WS-8s at one site: two units, two assignments, one dot."""
    units = [st for st in station_list if st.site_id == "WB6CXC-CM88mj"]
    assert len(units) == 2
    assert len({st.station_id for st in units}) == 2
    assert len({st.position for st in units}) == 1


def test_duplicate_station_id_rejected(tmp_path):
    csv = tmp_path / "dup.csv"
    header = ",".join(S.Station.__dataclass_fields__.keys() - {"activity", "observed_offset"})
    csv.write_text(
        "station_id,site_id,call,site_label,region,country,grid,hardware,gpsdo,"
        "offset_assigned_hz,mode,antenna,date_in_service,date_out_service,funding,"
        "ok_to_list_public,record_status,notes\n"
        "A,A,W1AW,x,x,USA,FN31,WS-8,,50,WSPR,,,,,,deployed,\n"
        "A,A,W1AW,x,x,USA,FN31,WS-8,,50,WSPR,,,,,,deployed,\n",
    )
    assert header  # header composition is incidental; the duplicate is the point
    with pytest.raises(ValueError, match="duplicate station_id"):
        S.load(csv)


def test_invalid_grid_rejected(tmp_path):
    csv = tmp_path / "bad.csv"
    csv.write_text(
        "station_id,site_id,call,site_label,region,country,grid,hardware,gpsdo,"
        "offset_assigned_hz,mode,antenna,date_in_service,date_out_service,funding,"
        "ok_to_list_public,record_status,notes\n"
        "A,A,W1AW,x,x,USA,ZZ99zz,WS-8,,50,WSPR,,,,,,deployed,\n",
    )
    with pytest.raises(ValueError, match="invalid Maidenhead locator"):
        S.load(csv)


def test_unknown_record_status_rejected(tmp_path):
    csv = tmp_path / "status.csv"
    csv.write_text(
        "station_id,site_id,call,site_label,region,country,grid,hardware,gpsdo,"
        "offset_assigned_hz,mode,antenna,date_in_service,date_out_service,funding,"
        "ok_to_list_public,record_status,notes\n"
        "A,A,W1AW,x,x,USA,FN31,WS-8,,50,WSPR,,,,,,probably_fine,\n",
    )
    with pytest.raises(ValueError, match="record_status"):
        S.load(csv)


def _activity(last_spot: str) -> Activity:
    return Activity(call="W1AW", spots=1000, reporters=50, bands=8,
                    first_spot="2026-08-01 00:00:00", last_spot=last_spot,
                    grid="FN31", power_dbm=30)


@pytest.mark.parametrize(
    "last_spot, expected",
    [
        ("2026-08-13 12:00:00", "active"),        # same day
        ("2026-08-11 18:00:00", "active"),        # inside the 2-day grace
        ("2026-08-09 12:00:00", "intermittent"),  # outside it
    ],
)
def test_on_air_status(station_list, last_spot, expected):
    station = station_list[0]
    S.resolve([station], {station.call: _activity(last_spot)}, {},
              as_of="2026-08-13 18:00:00")
    assert station.on_air_status == expected


def test_silent_when_nothing_heard(station_list):
    station = station_list[0]
    S.resolve([station], {}, {}, as_of="2026-08-13 18:00:00")
    assert station.on_air_status == "silent"
    assert station.days_since_last_spot is None


@pytest.mark.parametrize(
    "assigned, observed, spread, expected",
    [
        ("50", 50, 1, "ok"),
        ("50", 52, 1, "ok"),           # inside the 2 Hz tolerance
        ("50", 53, 1, "MISMATCH"),     # outside it
        ("80", 131, 23, "MISMATCH"),   # KD0EAG: real, coherent, wrong
        ("150", 165, 115, "incoherent"),  # VY0ERC: bands disagree, unmeasurable
        ("", 50, 1, ""),               # no assignment on record
        ("50", None, 0, ""),           # nothing heard
    ],
)
def test_offset_check(station_list, assigned, observed, spread, expected):
    station = station_list[0]
    station.offset_assigned_hz = assigned
    station.observed_offset = (
        {} if observed is None else {"offset_hz": observed, "spread_hz": spread}
    )
    assert station.offset_check == expected
