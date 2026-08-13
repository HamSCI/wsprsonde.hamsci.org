"""Build the WSPRSonde location product consumed by ``polar-psws``.

Joins the curated station list (``data/wsprsonde_stations.csv``) to the on-air
record from the WsprDaemon ClickHouse endpoint and writes:

``products/wsprsonde_locations.csv``
    One row per WSPRSonde unit, with position, status, and both the assigned and
    the measured frequency offset.

``products/wsprsonde_locations_manifest.json``
    Provenance: when the queries ran, what windows they covered, which endpoint
    answered, the thresholds applied, and the resulting counts. A CSV of station
    positions is worthless six months later if nobody can say when "active" was
    measured, so the manifest is written every time and is not optional.

``products/wsprsonde_candidates.csv``
    Transmitters the simultaneity scan flagged as WSPRSonde-like but which are
    not in the curated list -- see :func:`wsprsonde.wsprdaemon.simultaneity`.
    Written as a prompt for a human to investigate, not as a claim.

Run::

    python -m wsprsonde.build_locations            # from src/, or with src on PYTHONPATH
    PYTHONPATH=src python -m wsprsonde.build_locations --window-days 60
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from . import stations as S
from . import wsprdaemon as WD

REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCTS_DIR = REPO_ROOT / "products"

#: Columns of the output product, in order. Both ``offset_assigned_hz`` and
#: ``offset_observed_hz`` are carried: the assignment is what was coordinated,
#: the observation is what the radio is actually doing, and the whole point of
#: the exercise is to see where they differ.
OUTPUT_COLUMNS = [
    "station_id", "site_id", "call", "site_label", "region", "country",
    "grid", "grid_precision", "lat", "lon",
    "hardware", "gpsdo", "mode", "antenna",
    "offset_assigned_hz", "offset_observed_hz", "offset_spread_hz", "offset_check",
    "record_status", "on_air_status", "last_spot_utc", "days_since_last_spot",
    "spots_in_window", "reporters_in_window", "bands_in_window", "power_dbm_reported",
    "date_in_service", "date_out_service", "funding", "ok_to_list_public", "notes",
]


def build_rows(stations: list[S.Station]) -> list[dict]:
    """Flatten resolved stations into the output schema.

    Positions come from the curated locator, never from the one in the spot
    record: WSPRNet usually carries only a 4-character grid, whose cell centre
    can be tens of kilometres from the site. Where the two disagree the curated
    value wins and the spot-record grid stays in the notes.
    """
    rows = []
    for st in stations:
        lat, lon = st.position
        activity = st.activity
        rows.append({
            "station_id": st.station_id,
            "site_id": st.site_id,
            "call": st.call,
            "site_label": st.site_label,
            "region": st.region,
            "country": st.country,
            "grid": st.grid,
            "grid_precision": st.grid_precision if st.grid_precision else "",
            "lat": f"{lat:.4f}" if lat is not None else "",
            "lon": f"{lon:.4f}" if lon is not None else "",
            "hardware": st.hardware,
            "gpsdo": st.gpsdo,
            "mode": st.mode,
            "antenna": st.antenna,
            "offset_assigned_hz": st.offset_assigned_hz,
            "offset_observed_hz": st.observed_offset.get("offset_hz", ""),
            "offset_spread_hz": st.observed_offset.get("spread_hz", ""),
            "offset_check": st.offset_check,
            "record_status": st.record_status,
            "on_air_status": st.on_air_status,
            "last_spot_utc": activity.last_spot if activity else "",
            "days_since_last_spot": st.days_since_last_spot if activity else "",
            "spots_in_window": activity.spots if activity else 0,
            "reporters_in_window": activity.reporters if activity else 0,
            "bands_in_window": activity.bands if activity else 0,
            "power_dbm_reported": activity.power_dbm if activity else "",
            "date_in_service": st.date_in_service,
            "date_out_service": st.date_out_service,
            "funding": st.funding,
            "ok_to_list_public": st.ok_to_list_public,
            "notes": st.notes,
        })
    return rows


def write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    """Write ``rows`` to ``path`` with a fixed column order."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    """Build the location product. Returns a process exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--stations", type=Path, default=None,
                        help="curated station CSV (default: data/wsprsonde_stations.csv)")
    parser.add_argument("--out-dir", type=Path, default=PRODUCTS_DIR)
    parser.add_argument("--window-days", type=int, default=S.ACTIVITY_WINDOW_DAYS,
                        help="activity look-back window")
    parser.add_argument("--offset-days", type=int, default=3,
                        help="window for the frequency-offset measurement")
    parser.add_argument("--host", default=WD.DEFAULT_HOST)
    parser.add_argument("--no-candidates", action="store_true",
                        help="skip the WSPRSonde-like discovery scan")
    args = parser.parse_args(argv)

    as_of = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    station_list = S.load(args.stations)
    calls = sorted({st.call for st in station_list})
    print(f"curated stations : {len(station_list)} units, {len(calls)} callsigns")

    print(f"querying {args.host} ...")
    activities = WD.activity(calls, days=args.window_days, host=args.host)
    offsets = WD.observed_offsets(calls, days=args.offset_days, host=args.host)
    S.resolve(station_list, activities, offsets, as_of=as_of)

    rows = build_rows(station_list)
    out_csv = args.out_dir / "wsprsonde_locations.csv"
    write_csv(out_csv, OUTPUT_COLUMNS, rows)

    candidates: list[dict] = []
    if not args.no_candidates:
        known = {c.upper() for c in calls}
        candidates = [c for c in WD.simultaneity(days=args.offset_days, host=args.host)
                      if c["call"].upper() not in known]
        write_csv(args.out_dir / "wsprsonde_candidates.csv",
                  ["call", "max_simultaneous", "median_simultaneous", "slots"], candidates)

    counts = {
        "units": len(rows),
        "sites": len({r["site_id"] for r in rows}),
        "active": sum(r["on_air_status"] == "active" for r in rows),
        "intermittent": sum(r["on_air_status"] == "intermittent" for r in rows),
        "silent": sum(r["on_air_status"] == "silent" for r in rows),
        "positioned": sum(bool(r["lat"]) for r in rows),
        "offset_mismatch": sum(r["offset_check"] == "MISMATCH" for r in rows),
        "offset_incoherent": sum(r["offset_check"] == "incoherent" for r in rows),
        "candidates_unlisted": len(candidates),
    }
    manifest = {
        "generated_utc": as_of,
        "endpoint": args.host,
        "source_table": "wspr.rx",
        "curated_list": str((args.stations or S.DEFAULT_STATIONS_CSV).relative_to(REPO_ROOT)),
        "windows": {"activity_days": args.window_days, "offset_days": args.offset_days},
        "thresholds": {
            "active_within_days": S.ACTIVE_WITHIN_DAYS,
            "offset_match_tolerance_hz": S.OFFSET_TOLERANCE_HZ,
            "offset_incoherent_hz": S.OFFSET_INCOHERENT_HZ,
        },
        "counts": counts,
        "caveats": [
            "Positions are Maidenhead cell centres from the curated list, not surveyed "
            "coordinates. A 4-character locator is ~78 km across at 40 deg latitude.",
            "on_air_status is evidence of reception, not of transmitter health. A silent "
            "station may be off the air, or may simply not have been heard.",
            "ok_to_list_public reflects the consent column in the G3ZIL metadata and is "
            "'unknown' for most stations. Do not publish a station without checking it.",
        ],
    }
    (args.out_dir / "wsprsonde_locations_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )

    print(f"\nwrote {out_csv.relative_to(REPO_ROOT)}")
    for key, value in counts.items():
        print(f"  {key:<20} {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
