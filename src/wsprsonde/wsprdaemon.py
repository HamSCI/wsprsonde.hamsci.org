"""Read-only client for the WsprDaemon ClickHouse endpoint.

The WsprDaemon project exposes its spot archive over the ClickHouse HTTP
interface with no credentials required. Two tables matter here:

``wspr.rx``
    The full WSPRNet record. Every spot of every transmitter, from every
    reporting receiver. This is the table to use for "is this WSPRSonde on the
    air", because a sonde is heard by whoever happens to be listening and we
    want the widest possible receiver population.

``wsprdaemon.spots``
    Extended spots (SNR *plus* calibrated noise) from WsprDaemon client sites
    only -- about 5% of receivers. Better data, far fewer ears. Not used for
    liveness, because a sonde can be perfectly healthy and simply not be heard
    by any of those ~80 sites.

Endpoint conventions, all of them load-bearing (see
``polar-psws/docs/wsprdaemon_extended_spots_access.md`` for the full write-up):

* **HTTP on port 80**, not HTTPS and not the usual ClickHouse port 8123.
* **GET with the query in the ``query=`` parameter.** POST bodies are rejected
  by the front-end nginx with 403.
* **Always bound the query by time.** nginx returns 504 on long queries, and
  ``wspr.rx`` holds over 12 billion rows.
* **Errors arrive as HTTP 200** with a body starting ``Code: NNN. DB::Exception``,
  so the status code cannot be trusted; :func:`query` checks the body.
* ``wd10``, ``wd1`` and ``wd2`` are consistent mirrors. Default to ``wd10`` --
  it lets the WsprDaemon team manage load.

These are volunteer-run servers carrying a live operational load. Everything in
this module is a small aggregate over a short window, run one request at a time.
Keep it that way.

.. note::
   ``wd1.wsprdaemon.org`` also exposes a PostgreSQL service on 5432 with a
   ``spots`` hypertable, and it is tempting to poll that instead. As of
   2026-08-13 that table is unusable: any query touching it fails with
   ``could not open file "pg_tblspc/18143/..."`` because a TimescaleDB chunk's
   tablespace is missing. The ClickHouse endpoint is the supported path.
"""

from __future__ import annotations

import urllib.parse
import urllib.request
from dataclasses import dataclass

DEFAULT_HOST = "http://wd10.wsprdaemon.org/"

#: Lowest transmit frequency of each WSPR/FST4W sub-band, in Hz. The audio tone
#: a transmitter uses sits 1400-1600 Hz above the dial frequency, so the "offset"
#: the WSPRSonde community coordinates on is ``frequency - BAND_BASE_HZ[band]``,
#: i.e. Hz above the bottom of the 200 Hz window. Paul Elliott (WB6CXC) quotes
#: the same number with 1400 added -- his "1450" is this module's 50.
#:
#: Keys are the ``band`` column of ``wspr.rx``, which is the band's **integer
#: MHz**, not its wavelength. ``wsprdaemon.spots`` uses wavelength in metres for
#: the same column; do not mix them.
BAND_BASE_HZ: dict[int, int] = {
    1: 1_838_000,     # 160 m
    3: 3_570_000,     # 80 m
    5: 5_366_100,     # 60 m
    7: 7_040_000,     # 40 m
    10: 10_140_100,   # 30 m
    14: 14_097_000,   # 20 m
    18: 18_106_000,   # 17 m
    21: 21_096_000,   # 15 m
    24: 24_926_000,   # 12 m
    28: 28_126_000,   # 10 m
    50: 50_294_400,   # 6 m
}


#: Transmission mode by the ``code`` column of ``wspr.rx``, for spots reported
#: **on or after 2023-01-16**. This is WSPRNet's own encoding, and it is the
#: one to measure mode with: it has been uniform since that date. Source: the
#: WSPR/FST4W mapping table published at https://wspr.live/ (read 2026-09-11),
#: confirmed against known-mode WSPRSondes month by month from 2024-07 to
#: 2026-09 (WW0WWV always 1; WB6CXC, KH2R, N4RVE, KD0EAG always 3).
#:
#: It does **not** describe ``wsprdaemon.spots``; see :data:`MODE_BY_WD_MODE`.
MODE_BY_CODE: dict[int, str] = {
    1: "WSPR",          # WSPR-2, the 2-minute mode
    2: "WSPR-15",
    3: "FST4W",         # FST4W-120
    4: "FST4W-300",
    5: "FST4W-900",
    8: "FST4W-1800",
}

#: The same modes in WsprDaemon's own encoding: the ``mode`` column of the
#: WsprDaemon **PostgreSQL** tables, which Gwyn Griffiths' ``wsprsonde`` table
#: carries, **and the** ``code`` **column of** ``wsprdaemon.spots`` (Gwyn
#: Griffiths, `issue #6
#: <https://github.com/HamSCI/wsprsonde.hamsci.org/issues/6>`_, confirmed
#: 2026-09-11 on ``wd10``, ``wd1`` and ``wd2``: every WSPR-2 sonde reads 2).
#: Same published source as :data:`MODE_BY_CODE`.
#:
#: ``wsprdaemon.spots.code`` has **not** carried this encoding consistently.
#: WW0WWV, which ``wspr.rx`` shows as WSPR-2 throughout, reads 1 from 2024-07
#: to 2025-04, 2 from 2025-05 to 2025-10, 1 again from 2025-11 to 2026-02 and 2
#: from 2026-03 on (measured 2026-09-11 on ``wd10``; the cause was not
#: established). Read it with this table only from
#: :data:`WD_SPOTS_CODE_STABLE_DATE`, and take mode history from ``wspr.rx``.
MODE_BY_WD_MODE: dict[int, str] = {
    2: "WSPR",          # WSPR-2
    15: "WSPR-15",
    3: "FST4W",         # FST4W-120
    6: "FST4W-300",
    16: "FST4W-900",
    31: "FST4W-1800",
}

#: **The two encodings agree on FST4W-120 and disagree on WSPR-2**, which is
#: what makes the trap subtle: a system that confuses them is correct on every
#: FST4W station and wrong on every WSPR one, so it looks half right. Store the
#: mode by name and translate per source; never compare two sources' numbers.

#: ``wspr.rx.code`` before 2023-01-16 did not separate WSPR-2 from FST4W-120:
#: both were reported as ``1``. Any mode history that reaches back past that
#: date must come from the unit record or the curator's table, never from the
#: spot archive.
CODE_MODE_SPLIT_DATE = "2023-01-16"

#: First month in which ``wsprdaemon.spots.code`` has read consistently in the
#: WsprDaemon encoding of :data:`MODE_BY_WD_MODE` for every known WSPRSonde.
#: Earlier values flip between the two encodings (see that table's note), so a
#: mode read from ``wsprdaemon.spots`` before this date is not evidence.
WD_SPOTS_CODE_STABLE_DATE = "2026-03-01"


class WsprDaemonError(RuntimeError):
    """The endpoint returned a ClickHouse exception or an unusable response."""


def _band_base_sql(column: str = "band") -> str:
    """Render :data:`BAND_BASE_HZ` as a ClickHouse ``multiIf`` expression.

    Generated rather than written out so the table has exactly one definition.

    Examples
    --------
    >>> _band_base_sql().startswith("multiIf(band=1,1838000")
    True
    """
    arms = ", ".join(f"{column}={band},{base}" for band, base in BAND_BASE_HZ.items())
    return f"multiIf({arms}, 0)"


def query(sql: str, host: str = DEFAULT_HOST, timeout: float = 120.0) -> str:
    """Run one read-only SQL statement and return the raw response body.

    Parameters
    ----------
    sql : str
        ClickHouse SQL. Append a ``FORMAT`` clause to control the output; this
        function does not add one.
    host : str, optional
        Endpoint URL.
    timeout : float, optional
        Socket timeout in seconds.

    Returns
    -------
    str

    Raises
    ------
    WsprDaemonError
        If the endpoint reports a ClickHouse exception. These arrive with HTTP
        status 200, so the body must be inspected rather than the status code.
    """
    url = f"{host}?{urllib.parse.urlencode({'query': sql})}"
    with urllib.request.urlopen(url, timeout=timeout) as response:  # noqa: S310
        body = response.read().decode("utf-8", errors="replace")
    if body.lstrip().startswith("Code:") and "DB::Exception" in body:
        raise WsprDaemonError(body.strip().splitlines()[0])
    return body


def query_rows(sql: str, **kwargs) -> list[dict[str, str]]:
    """Run a query with ``FORMAT TSVWithNames`` and return a list of dicts.

    ClickHouse writes SQL ``NULL`` as the two characters ``\\N``; those are
    converted to empty strings here so downstream code never sees the literal.

    Parameters
    ----------
    sql : str
        SQL **without** a ``FORMAT`` clause; one is appended.
    **kwargs
        Passed to :func:`query`.

    Returns
    -------
    list of dict
    """
    body = query(f"{sql}\nFORMAT TSVWithNames", **kwargs)
    lines = body.rstrip("\n").split("\n")
    if not lines or not lines[0]:
        return []
    header = lines[0].split("\t")
    return [
        {k: ("" if v == "\\N" else v) for k, v in zip(header, line.split("\t"))}
        for line in lines[1:]
        if line
    ]


@dataclass(frozen=True)
class Activity:
    """On-air evidence for one transmitter callsign over a time window.

    Attributes
    ----------
    call : str
        Transmitter callsign as it appears in ``tx_sign``.
    spots : int
        Reception reports in the window. A *reception* count, not a transmission
        count -- it scales with how many people were listening, so it says
        nothing about transmitter health beyond "greater than zero".
    reporters : int
        Distinct receiving callsigns. The useful sanity check: a handful of
        reporters on a station that should be widely heard suggests an antenna
        or power problem rather than a dead transmitter.
    bands : int
        Distinct bands spotted.
    first_spot, last_spot : str
        UTC timestamps, ``YYYY-MM-DD HH:MM:SS``.
    grid : str
        Most-reported transmitter locator. Usually 4-character, and therefore
        usually worse than the locator in the curated station list.
    power_dbm : int
        Most-reported transmit power. A WSPRSonde reports 30 dBm (1 W) by
        default; a departure from the expected value is a configuration error
        worth catching.
    """

    call: str
    spots: int
    reporters: int
    bands: int
    first_spot: str
    last_spot: str
    grid: str
    power_dbm: int


def activity(calls: list[str], days: int = 30, **kwargs) -> dict[str, Activity]:
    """Return on-air evidence for each callsign, keyed by callsign.

    Callsigns with no spots in the window are simply absent from the result --
    that absence is the signal, and the caller decides what it means.

    Parameters
    ----------
    calls : list of str
        Transmitter callsigns.
    days : int, optional
        Length of the look-back window.
    **kwargs
        Passed to :func:`query`.

    Returns
    -------
    dict
        ``{callsign: Activity}``.
    """
    if not calls:
        return {}
    quoted = ", ".join(f"'{c}'" for c in calls)
    rows = query_rows(
        f"""
        SELECT tx_sign,
               count()             AS spots,
               uniqExact(rx_sign)  AS reporters,
               uniqExact(band)     AS bands,
               min(time)           AS first_spot,
               max(time)           AS last_spot,
               topK(1)(tx_loc)[1]  AS grid,
               topK(1)(power)[1]   AS power_dbm
        FROM wspr.rx
        WHERE time >= now() - INTERVAL {int(days)} DAY
          AND tx_sign IN ({quoted})
        GROUP BY tx_sign
        """,
        **kwargs,
    )
    return {
        r["tx_sign"]: Activity(
            call=r["tx_sign"],
            spots=int(r["spots"]),
            reporters=int(r["reporters"]),
            bands=int(r["bands"]),
            first_spot=r["first_spot"],
            last_spot=r["last_spot"],
            grid=r["grid"],
            power_dbm=int(r["power_dbm"]),
        )
        for r in rows
    }


def observed_offsets(calls: list[str], days: int = 3, **kwargs) -> dict[str, dict]:
    """Measure each callsign's on-air frequency offset, per band and overall.

    A WSPRSonde is configured with one offset applied to every band, so this is
    the measurement that verifies a frequency assignment was actually applied --
    and the one that detects two sondes assigned the same channel.

    The per-band figure is a **median over reception reports**, not a single
    reading. Each report carries the receiving station's own frequency error, so
    individual spots scatter by several Hz even from a GPS-disciplined
    transmitter; the median across many receivers is stable to about 1 Hz.

    Parameters
    ----------
    calls : list of str
        Transmitter callsigns.
    days : int, optional
        Look-back window. Three days is enough for a well-heard station and
        keeps the query cheap.
    **kwargs
        Passed to :func:`query`.

    Returns
    -------
    dict
        ``{callsign: {'offset_hz': int, 'spread_hz': int, 'per_band': {band: int}}}``.
        ``spread_hz`` is the range across bands: a healthy sonde reads 0-2 Hz,
        and a large value means the bands disagree, which a single configured
        offset cannot explain.
    """
    if not calls:
        return {}
    quoted = ", ".join(f"'{c}'" for c in calls)
    bands = ", ".join(str(b) for b in BAND_BASE_HZ)
    rows = query_rows(
        f"""
        SELECT tx_sign,
               band,
               toInt32(round(median(frequency - {_band_base_sql()}))) AS offset_hz,
               count() AS n
        FROM wspr.rx
        WHERE time >= now() - INTERVAL {int(days)} DAY
          AND tx_sign IN ({quoted})
          AND band IN ({bands})
        GROUP BY tx_sign, band
        HAVING n >= 20 AND offset_hz BETWEEN 0 AND 200
        """,
        **kwargs,
    )
    out: dict[str, dict] = {}
    for row in rows:
        entry = out.setdefault(row["tx_sign"], {"per_band": {}})
        entry["per_band"][int(row["band"])] = int(row["offset_hz"])
    for entry in out.values():
        values = sorted(entry["per_band"].values())
        entry["offset_hz"] = values[len(values) // 2]
        entry["spread_hz"] = values[-1] - values[0]
    return out


def simultaneity(days: int = 3, min_slots: int = 50, **kwargs) -> list[dict]:
    """Find transmitters that key several bands in the *same* 2-minute slot.

    This answers the question Nathaniel Frissell put to the group on
    2026-07-31 -- whether a WSPRSonde can be recognised from the spot record
    without being told which callsigns to look for.

    A constant frequency offset does **not** identify one: an ordinary WSJT-X
    station band-hopping with a fixed TX audio tone produces exactly the same
    signature, and a scan on that criterion alone returns dozens of ordinary
    stations. What no band-hopping station can imitate is transmitting on many
    bands *at once*, which is what a WSPRSonde does by construction. Grouping
    spots by ``(tx_sign, time)`` and counting distinct bands separates the two
    cleanly.

    The method has one real limitation, and it is not fixable from the spot
    record: it needs somebody to have *heard* several of those bands in the same
    slot. Weakly-heard sondes -- the polar sites especially -- fall below the
    threshold not because they are misbehaving but because nobody was listening
    on enough bands. Treat a hit as strong evidence and a miss as no evidence.

    Parameters
    ----------
    days : int, optional
        Look-back window.
    min_slots : int, optional
        Minimum number of slots in which the station was heard at all, to
        exclude one-off decoding artefacts.
    **kwargs
        Passed to :func:`query`.

    Returns
    -------
    list of dict
        One row per candidate, with ``call``, ``max_simultaneous``,
        ``median_simultaneous`` and ``slots``, most simultaneous first.
    """
    rows = query_rows(
        f"""
        WITH slots AS (
            SELECT tx_sign, time, uniqExact(band) AS bands_in_slot
            FROM wspr.rx
            WHERE time >= now() - INTERVAL {int(days)} DAY
            GROUP BY tx_sign, time
        )
        SELECT tx_sign                        AS call,
               toInt32(max(bands_in_slot))    AS max_simultaneous,
               toInt32(median(bands_in_slot)) AS median_simultaneous,
               count()                        AS slots
        FROM slots
        GROUP BY tx_sign
        HAVING median_simultaneous >= 3 AND slots >= {int(min_slots)}
        ORDER BY median_simultaneous DESC, max_simultaneous DESC, slots DESC
        """,
        **kwargs,
    )
    for row in rows:
        for key in ("max_simultaneous", "median_simultaneous", "slots"):
            row[key] = int(row[key])
    return rows
