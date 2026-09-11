"""Measure how crowded the 200 Hz WSPR/FST4W window is, and how many WSPRSondes fit.

Regenerates every measured number in
``docs/technical_note_channel_capacity.md``. That note argues the network is
close to exhausting its channel plan, and an argument of that kind is worth
nothing if the numbers behind it cannot be re-run when the network grows.

Three measurements, all read-only aggregates against ``wspr.rx``:

``population``
    Distinct transmitters and spot counts per band over the window. Answers
    "how many stations share this 200 Hz in a day".

``simultaneity``
    Distinct transmitters per 2-minute slot, as mean, median and peak. Answers
    "how many are keyed at the same instant", which is the number that bears on
    collisions. The daily figure over-counts, because a station heard at
    03:00 and again at 15:00 is one transmitter and two slots.

``histogram``
    Distinct transmitters per bin across the window. Answers "is any part of
    the window quiet enough to be worth reserving". Casual WSPR randomises its
    transmit offset within the window, so one station appears in several bins
    and the column sum exceeds the distinct-transmitter count. The shape is the
    result, not the totals.

The grid arithmetic in :func:`channel_plan` needs no network access.

Run::

    PYTHONPATH=src python -m wsprsonde.window_occupancy
    PYTHONPATH=src python -m wsprsonde.window_occupancy --hours 24 --histogram-band 14
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from . import wsprdaemon as WD

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATIONS = REPO_ROOT / "data" / "wsprsonde_stations.csv"

#: Width of the WSPR/FST4W sub-band, in Hz. The window runs 1400-1600 Hz above
#: the dial frequency; ``wsprdaemon.BAND_BASE_HZ`` carries its bottom edge per
#: band, so offsets in this module run 0-200.
WINDOW_HZ = 200

#: Occupied bandwidth of one WSPR-2 or FST4W-120 signal, in Hz. Both are
#: 4-GFSK at 1.46 Hz tone spacing. Franke, Somerville and Taylor, *Quick-Start
#: Guide to FST4 and FST4W*, Table 1, give 5.9 Hz for FST4W-120; Griffiths et
#: al. (2022) Table 1 states that "except for measured spectral width and an
#: SNR threshold of -31.4 dB WSPR-2 has the same parameters as FST4W-120".
#: This is the spacing a non-overlapping channel plan has to respect.
OCCUPIED_BW_HZ = 5.9

#: Occupied bandwidth of the longer FST4W sequences, in Hz, from the same
#: table. Recorded because they set the theoretical floor on channel spacing,
#: and *not* used as the basis of a channel plan: Griffiths et al. find -900
#: "may only be of practical value for one-hop ionospheric paths" and -1800
#: "of very specialised use on non-ionospheric paths or on lower the HF bands".
#: A sonde has to be decodable on multi-hop paths, so 5.9 Hz is the honest
#: figure for this network. See §3 of the technical note.
FST4W_OCCUPIED_BW_HZ: dict[int, float] = {120: 5.9, 300: 2.2, 900: 0.72, 1800: 0.36}

#: The current allocation grid, as recorded in R2.2 of the requirements: one
#: offset per unit applied to all of its bands, on a 10 Hz grid from 1450 Hz
#: upward. Expressed here as Hz above the window bottom, so 1450 reads as 50.
GRID_START_HZ = 50
GRID_STEP_HZ = 10

#: Bands to report on by default: the eight a WSPRSonde-8 transmits.
DEFAULT_BANDS = (3, 7, 10, 14, 18, 21, 24, 28)


def grid_slots(start_hz: int = GRID_START_HZ, step_hz: int = GRID_STEP_HZ,
               occupied_bw_hz: float = OCCUPIED_BW_HZ) -> list[int]:
    """Return the usable channel offsets on the allocation grid.

    The last slot is the highest whose signal still fits inside the window: a
    signal centred at 1590 Hz spans roughly 1587 to 1593 and clears the 1600 Hz
    edge, while one centred at 1600 would not.

    Examples
    --------
    >>> slots = grid_slots()
    >>> len(slots), 1400 + slots[0], 1400 + slots[-1]
    (15, 1450, 1590)
    >>> len(grid_slots(start_hz=0))
    20
    >>> len(grid_slots(start_hz=0, step_hz=6))
    33
    """
    top = WINDOW_HZ - occupied_bw_hz / 2
    return [hz for hz in range(start_hz, WINDOW_HZ, step_hz) if hz <= top]


def channel_plan(stations_csv: Path = DEFAULT_STATIONS, **kwargs) -> dict:
    """Compare the allocation grid against the registry's live assignments.

    Retired units release their channels, so they are excluded. Units carrying
    an off-grid assignment (R2.2's recorded exceptions) consume a channel
    without consuming a grid slot, and are counted separately.

    Returns
    -------
    dict
        ``slots``, ``used``, ``off_grid``, ``free``, ``unassigned`` and
        ``spare``, the last being free slots less units awaiting an assignment.
    """
    with open(stations_csv, newline="", encoding="utf-8") as handle:
        rows = [r for r in csv.DictReader(handle) if r["record_status"] != "retired"]
    slots = grid_slots(**kwargs)
    assigned = {int(r["offset_assigned_hz"]) for r in rows if r["offset_assigned_hz"]}
    used = sorted(assigned.intersection(slots))
    unassigned = [r["call"] for r in rows if not r["offset_assigned_hz"]]
    free = sorted(set(slots) - assigned)
    return {
        "slots": slots,
        "used": used,
        "off_grid": sorted(assigned - set(slots)),
        "free": free,
        "unassigned": unassigned,
        "spare": len(free) - len(unassigned),
    }


def population(hours: int = 24, bands: tuple[int, ...] = DEFAULT_BANDS, **kwargs) -> list[dict]:
    """Distinct transmitters and spots per band over the window."""
    in_bands = ", ".join(str(b) for b in bands)
    return WD.query_rows(
        f"""
        SELECT band,
               uniqExact(tx_sign) AS transmitters,
               count()            AS spots
        FROM wspr.rx
        WHERE time >= now() - INTERVAL {int(hours)} HOUR
          AND band IN ({in_bands})
        GROUP BY band ORDER BY band
        """,
        **kwargs,
    )


def simultaneity(hours: int = 24, bands: tuple[int, ...] = DEFAULT_BANDS, **kwargs) -> list[dict]:
    """Distinct transmitters per 2-minute slot per band: mean, median and peak.

    ``wspr.rx`` keys ``time`` to the start of the transmission slot, so
    grouping on it groups by slot with no rounding.
    """
    in_bands = ", ".join(str(b) for b in bands)
    return WD.query_rows(
        f"""
        SELECT band,
               round(avg(n))                 AS mean_per_slot,
               toInt32(quantile(0.5)(n))     AS median_per_slot,
               max(n)                        AS peak_per_slot
        FROM (
          SELECT band, time, uniqExact(tx_sign) AS n
          FROM wspr.rx
          WHERE time >= now() - INTERVAL {int(hours)} HOUR
            AND band IN ({in_bands})
          GROUP BY band, time
        )
        GROUP BY band ORDER BY band
        """,
        **kwargs,
    )


def histogram(band: int = 14, hours: int = 24, bin_hz: int = 10, **kwargs) -> list[dict]:
    """Distinct transmitters per frequency bin across the 200 Hz window."""
    base = WD._band_base_sql()
    return WD.query_rows(
        f"""
        SELECT intDiv(toInt32(round(frequency - {base})), {int(bin_hz)}) * {int(bin_hz)} AS bin_hz,
               uniqExact(tx_sign) AS transmitters
        FROM wspr.rx
        WHERE time >= now() - INTERVAL {int(hours)} HOUR
          AND band = {int(band)}
          AND (frequency - {base}) BETWEEN 0 AND {WINDOW_HZ - 1}
        GROUP BY bin_hz ORDER BY bin_hz
        """,
        **kwargs,
    )


def main(argv: list[str] | None = None) -> int:
    """Print the occupancy report behind the channel-capacity technical note."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--hours", type=int, default=24,
                        help="look-back window for the live measurements")
    parser.add_argument("--histogram-band", type=int, default=14,
                        help="band (integer MHz) for the window histogram")
    parser.add_argument("--bin-hz", type=int, default=10, help="histogram bin width")
    parser.add_argument("--stations", type=Path, default=DEFAULT_STATIONS)
    parser.add_argument("--host", default=WD.DEFAULT_HOST)
    parser.add_argument("--offline", action="store_true",
                        help="channel-plan arithmetic only, no queries")
    args = parser.parse_args(argv)
    net = {"host": args.host}

    plan = channel_plan(args.stations)
    print(f"Channel plan: {len(plan['slots'])} slots on a {GRID_STEP_HZ} Hz grid, "
          f"{1400 + plan['slots'][0]}-{1400 + plan['slots'][-1]} Hz")
    print(f"  in use on grid   {len(plan['used']):>3}  {[1400 + o for o in plan['used']]}")
    print(f"  off-grid         {len(plan['off_grid']):>3}  {[1400 + o for o in plan['off_grid']]}")
    print(f"  free             {len(plan['free']):>3}  {[1400 + o for o in plan['free']]}")
    print(f"  awaiting one     {len(plan['unassigned']):>3}  {plan['unassigned']}")
    print(f"  spare            {plan['spare']:>3}")
    if args.offline:
        return 0

    print(f"\nWindow population, last {args.hours} h")
    print(f"  {'band':>5} {'transmitters':>13} {'spots':>12}")
    for row in population(args.hours, **net):
        print(f"  {row['band']:>5} {row['transmitters']:>13} {row['spots']:>12}")

    print(f"\nSimultaneous transmitters per 2-minute slot, last {args.hours} h")
    print(f"  {'band':>5} {'mean':>6} {'median':>7} {'peak':>6}")
    for row in simultaneity(args.hours, **net):
        print(f"  {row['band']:>5} {row['mean_per_slot']:>6} "
              f"{row['median_per_slot']:>7} {row['peak_per_slot']:>6}")

    rows = histogram(args.histogram_band, args.hours, args.bin_hz, **net)
    peak = max(int(r["transmitters"]) for r in rows)
    print(f"\nWindow histogram, band {args.histogram_band} MHz, last {args.hours} h")
    for row in rows:
        low = 1400 + int(row["bin_hz"])
        n = int(row["transmitters"])
        print(f"  {low:>5}-{low + args.bin_hz - 1:<5} {n:>5} {'#' * round(50 * n / peak)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
