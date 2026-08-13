"""The curated WSPRSonde station list, and how a station's status is decided.

``data/wsprsonde_stations.csv`` is the **administrative** record: what the
project believes it has deployed, where, with what hardware, on what assigned
frequency. It is maintained by hand and it goes stale -- that is the whole
reason the WSPRSonde management system described in
``docs/requirements_wsprsonde_management_system.md`` is being proposed.

The on-air record from :mod:`wsprsonde.wsprdaemon` is the **observational**
counterpart. Neither is authoritative on its own, and the interesting entries
are the ones where they disagree: a station the list calls deployed that has not
been heard in a month, or one whose measured frequency offset is not the offset
it was assigned. :func:`resolve` joins them and keeps both, rather than
overwriting one with the other.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

from . import maidenhead
from .wsprdaemon import Activity

#: Default location of the curated list, relative to the repository root.
DEFAULT_STATIONS_CSV = Path(__file__).resolve().parents[2] / "data" / "wsprsonde_stations.csv"

#: ``record_status`` values the curated list may carry. These describe what the
#: project *intends*, not what the radio is doing.
RECORD_STATUS = ("deployed", "unknown", "retired", "in_transit", "pending_shipment")

#: A station is called ``active`` if it was spotted within this many days. Two
#: days rather than one: WSPR propagation on a quiet band at a remote site can
#: genuinely produce a day with no reception reports, and calling that an outage
#: would cry wolf. Two consecutive silent days at a station that is normally
#: heard is a real signal.
ACTIVE_WITHIN_DAYS = 2

#: Look-back window for the activity query. Long enough to distinguish "off the
#: air last week" from "off the air since last year", which is the distinction
#: that decides whether somebody needs to be emailed.
ACTIVITY_WINDOW_DAYS = 30

#: Tolerance on the assigned-vs-measured frequency offset comparison, in Hz.
OFFSET_TOLERANCE_HZ = 2

#: Disagreement between a station's bands, in Hz, above which no single offset
#: can be said to exist at all. Set to a quarter of the 200 Hz WSPR window: a
#: station whose bands are scattered that widely is not running one coordinated
#: channel, whether through a hardware fault or through too few reception
#: reports to measure. Below this the offset is reported and compared, with
#: ``offset_spread_hz`` left visible so a modest but real per-band error -- the
#: ~23 Hz a BeaconBlaster typically shows -- is not hidden by the verdict.
OFFSET_INCOHERENT_HZ = 50


@dataclass
class Station:
    """One WSPRSonde unit, as recorded in the curated list.

    A *unit*, not a site: WB6CXC runs two WS-8s at Occidental, one for 80-10 m
    and one for 160/6 m. They share a ``site_id`` and are one dot on a map, but
    they are two independent frequency assignments and two things that can fail,
    so they are two rows here.
    """

    station_id: str
    site_id: str
    call: str
    site_label: str
    region: str
    country: str
    grid: str
    hardware: str
    gpsdo: str
    offset_assigned_hz: str
    mode: str
    antenna: str
    date_in_service: str
    date_out_service: str
    funding: str
    ok_to_list_public: str
    record_status: str
    notes: str

    #: Filled in by :func:`resolve` from the WsprDaemon record.
    activity: Activity | None = None
    observed_offset: dict = field(default_factory=dict)

    @property
    def position(self) -> tuple[float | None, float | None]:
        """Cell-centre ``(lat, lon)`` of :attr:`grid`, or ``(None, None)``."""
        if not maidenhead.is_valid(self.grid):
            return None, None
        return maidenhead.to_latlon(self.grid)

    @property
    def grid_precision(self) -> int | None:
        """Locator length, as a proxy for position quality. See :mod:`.maidenhead`."""
        return maidenhead.precision_of(self.grid) if maidenhead.is_valid(self.grid) else None

    @property
    def on_air_status(self) -> str:
        """Observed status: ``active``, ``intermittent`` or ``silent``.

        Deliberately distinct from ``record_status``. A station can be
        administratively ``deployed`` and observationally ``silent``; that pair
        is the single most useful thing this table produces, because it is a
        work item rather than a datum.

        ``intermittent`` means heard during the window but not within the last
        :data:`ACTIVE_WITHIN_DAYS` days -- an outage with a known start date.
        ``silent`` means not heard at all in the whole
        :data:`ACTIVITY_WINDOW_DAYS`-day window, which carries no start date and
        so says nothing about *when* the station stopped.
        """
        if self.activity is None or self.days_since_last_spot is None:
            return "silent"
        if self.days_since_last_spot <= ACTIVE_WITHIN_DAYS:
            return "active"
        return "intermittent"

    @property
    def days_since_last_spot(self) -> float | None:
        """Days between the last reception report and the query time."""
        return None if self.activity is None else self._age_days

    _age_days: float | None = None

    @property
    def offset_check(self) -> str:
        """Verdict on the measured offset: ``ok``, ``MISMATCH``, ``incoherent`` or ``""``.

        Three outcomes, because two different things can go wrong and they need
        different people to act:

        ``incoherent``
            The station's bands disagree by :data:`OFFSET_INCOHERENT_HZ` or
            more, so there is no single offset to compare against. VY0ERC is in
            this state -- heard on a handful of bands by a handful of receivers,
            per-band medians scattered over 100 Hz. The finding is "not heard
            well enough to measure", not "transmitting on the wrong frequency",
            and reporting it as the latter would send somebody chasing a fault
            that is not there.
        ``MISMATCH``
            A coherent offset was measured and it is not the assigned one. This
            is a real coordination problem. KD0EAG shows it: assigned 80 Hz in
            August 2026, on air at ~131 Hz, because the replacement WS-8 has not
            been deployed and the old BeaconBlaster is still transmitting.
        ``ok``
            Measured offset matches the assignment within
            :data:`OFFSET_TOLERANCE_HZ`. The tolerance covers the residual
            scatter of a median over reception reports, each carrying its own
            receiver's frequency error; a GPS-disciplined transmitter genuinely
            on frequency reads within 1 Hz.

        An empty string means no assignment on record, or nothing heard.
        """
        assigned = self.offset_assigned_hz.strip()
        observed = self.observed_offset.get("offset_hz")
        if not assigned or observed is None:
            return ""
        if self.observed_offset.get("spread_hz", 0) >= OFFSET_INCOHERENT_HZ:
            return "incoherent"
        return "ok" if abs(int(assigned) - int(observed)) <= OFFSET_TOLERANCE_HZ else "MISMATCH"


def load(path: Path | str | None = None) -> list[Station]:
    """Read the curated station list.

    Parameters
    ----------
    path : pathlib.Path or str, optional
        Defaults to :data:`DEFAULT_STATIONS_CSV`.

    Returns
    -------
    list of Station

    Raises
    ------
    ValueError
        If a ``station_id`` is duplicated, a ``record_status`` is unrecognised,
        or a non-empty ``grid`` is not a valid Maidenhead locator. All three are
        errors a hand-edited CSV invites, and all three fail silently downstream
        if not caught here -- a bad locator becomes a missing dot on a map.
    """
    path = Path(path) if path is not None else DEFAULT_STATIONS_CSV
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    stations: list[Station] = []
    seen: set[str] = set()
    for line, row in enumerate(rows, start=2):
        row = {k: (v or "").strip() for k, v in row.items()}
        station_id = row["station_id"]
        if station_id in seen:
            raise ValueError(f"{path}:{line}: duplicate station_id {station_id!r}")
        seen.add(station_id)
        if row["record_status"] not in RECORD_STATUS:
            raise ValueError(
                f"{path}:{line}: record_status {row['record_status']!r} not in {RECORD_STATUS}"
            )
        if row["grid"] and not maidenhead.is_valid(row["grid"]):
            raise ValueError(f"{path}:{line}: invalid Maidenhead locator {row['grid']!r}")
        stations.append(Station(**{k: row[k] for k in Station.__dataclass_fields__
                                   if k in row}))
    return stations


def resolve(
    stations: list[Station],
    activities: dict[str, Activity],
    offsets: dict[str, dict],
    as_of: str,
) -> list[Station]:
    """Attach the observed record to each station, in place, and return it.

    Parameters
    ----------
    stations : list of Station
    activities : dict
        Output of :func:`wsprsonde.wsprdaemon.activity`.
    offsets : dict
        Output of :func:`wsprsonde.wsprdaemon.observed_offsets`.
    as_of : str
        UTC timestamp the query was run, ``YYYY-MM-DD HH:MM:SS``, used to age
        the last spot. Passed in rather than read from the clock so that a
        re-run against cached query output gives identical results.

    Returns
    -------
    list of Station

    Notes
    -----
    Observations are matched on **callsign**, but the curated list is keyed on
    station. Where one callsign covers two units -- WB6CXC's two WS-8s at
    Occidental -- both rows receive the same observation, because the spot
    record genuinely cannot tell them apart. The two units transmit the same
    callsign on disjoint band sets, so the only way to separate them is by band,
    and that belongs in the frequency-coordination view rather than here.
    """
    from datetime import datetime

    now = datetime.strptime(as_of, "%Y-%m-%d %H:%M:%S")
    for station in stations:
        station.activity = activities.get(station.call)
        station.observed_offset = offsets.get(station.call, {})
        if station.activity is not None:
            last = datetime.strptime(station.activity.last_spot, "%Y-%m-%d %H:%M:%S")
            station._age_days = round((now - last).total_seconds() / 86400.0, 2)
    return stations
