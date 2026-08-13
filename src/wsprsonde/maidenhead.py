"""Maidenhead locator conversion.

WSPRSonde positions reach us as Maidenhead grid squares, never as coordinates,
so every map of the network is really a map of grid-cell centres. The precision
that costs is worth stating explicitly, because it is the dominant position
error for most of these stations:

============  ==================  =========================
Locator       Cell size           Worst-case centre error
============  ==================  =========================
4-character   2 deg lon x 1 lat   ~78 km at 40 deg latitude
6-character   5 min lon x 2.5 lat ~3.3 km at 40 deg latitude
============  ==================  =========================

Two stations in this network show why that matters. KH2R is on record in the
G3ZIL metadata as ``FN21us`` (Kerhonkson, NY) but reports only ``FN21`` to
WSPRNet, whose cell centre lands about 65 km away near Scranton, PA. VY0ERC has
only a 4-character locator on record at 80 deg N, where a 1-degree tall cell
straddles the boundary the polar-cap classification turns on.

So: prefer the 6-character locator from the curated station list over the
4-character one the spot record carries, and record which one was used.
"""

from __future__ import annotations

import re
import string

#: A 4-, 6- or 8-character Maidenhead locator. Case-insensitive on input; the
#: canonical form is upper/digit/lower/digit.
LOCATOR_RE = re.compile(
    r"^[A-Ra-r]{2}[0-9]{2}(?:[A-Xa-x]{2}(?:[0-9]{2})?)?$"
)

_FIELD = string.ascii_uppercase[:18]      # A-R
_SUBSQUARE = string.ascii_lowercase[:24]  # a-x


def is_valid(locator: str | None) -> bool:
    """Return whether ``locator`` is a syntactically valid Maidenhead locator.

    Examples
    --------
    >>> is_valid("FN21us"), is_valid("FN21US"), is_valid("EQ79")
    (True, True, True)
    >>> is_valid("FN21z"), is_valid(""), is_valid(None)
    (False, False, False)
    """
    return bool(locator) and bool(LOCATOR_RE.match(locator.strip()))


def normalise(locator: str) -> str:
    """Return ``locator`` in canonical Maidenhead case.

    Examples
    --------
    >>> normalise("fn21US")
    'FN21us'
    """
    loc = locator.strip()
    if not is_valid(loc):
        raise ValueError(f"not a Maidenhead locator: {locator!r}")
    out = loc[:2].upper() + loc[2:4]
    if len(loc) >= 6:
        out += loc[4:6].lower()
    if len(loc) >= 8:
        out += loc[6:8]
    return out


def to_latlon(locator: str) -> tuple[float, float]:
    """Return the (latitude, longitude) of a locator's **cell centre**, in degrees.

    Parameters
    ----------
    locator : str
        4-, 6- or 8-character Maidenhead locator, any case.

    Returns
    -------
    tuple of float
        ``(lat, lon)`` in degrees, north and east positive.

    Raises
    ------
    ValueError
        If ``locator`` is not a valid Maidenhead locator.

    Examples
    --------
    >>> lat, lon = to_latlon("FN21")          # 4-char: centre of a 2x1 deg cell
    >>> f"{lat:.4f} {lon:.4f}"
    '41.5000 -75.0000'
    >>> lat, lon = to_latlon("FN21us")        # 6-char: the real Kerhonkson site
    >>> f"{lat:.4f} {lon:.4f}"
    '41.7708 -74.2917'
    >>> lat, lon = to_latlon("IB59ui")        # DP0GVN, Neumayer III
    >>> f"{lat:.4f} {lon:.4f}"
    '-70.6458 -8.2917'
    """
    loc = normalise(locator)

    lon = (_FIELD.index(loc[0]) * 20.0) - 180.0
    lat = (_FIELD.index(loc[1]) * 10.0) - 90.0
    lon += int(loc[2]) * 2.0
    lat += int(loc[3]) * 1.0
    size_lon, size_lat = 2.0, 1.0

    if len(loc) >= 6:
        lon += _SUBSQUARE.index(loc[4]) * (2.0 / 24.0)
        lat += _SUBSQUARE.index(loc[5]) * (1.0 / 24.0)
        size_lon, size_lat = 2.0 / 24.0, 1.0 / 24.0

    if len(loc) >= 8:
        lon += int(loc[6]) * (size_lon / 10.0)
        lat += int(loc[7]) * (size_lat / 10.0)
        size_lon, size_lat = size_lon / 10.0, size_lat / 10.0

    return lat + size_lat / 2.0, lon + size_lon / 2.0


def from_latlon(lat: float, lon: float, precision: int = 6) -> str:
    """Return the Maidenhead locator containing a coordinate.

    Parameters
    ----------
    lat, lon : float
        Degrees, north and east positive.
    precision : {4, 6, 8}, optional
        Number of locator characters.

    Returns
    -------
    str

    Examples
    --------
    >>> from_latlon(41.7708, -74.2917)
    'FN21us'
    >>> from_latlon(41.7708, -74.2917, precision=4)
    'FN21'
    """
    if precision not in (4, 6, 8):
        raise ValueError(f"precision must be 4, 6 or 8, got {precision}")
    if not -90.0 <= lat <= 90.0 or not -180.0 <= lon <= 180.0:
        raise ValueError(f"coordinate out of range: {lat}, {lon}")

    adj_lon, adj_lat = lon + 180.0, lat + 90.0
    out = _FIELD[min(int(adj_lon // 20), 17)] + _FIELD[min(int(adj_lat // 10), 17)]
    adj_lon %= 20.0
    adj_lat %= 10.0
    out += str(int(adj_lon // 2)) + str(int(adj_lat // 1))
    if precision == 4:
        return out

    adj_lon %= 2.0
    adj_lat %= 1.0
    out += _SUBSQUARE[int(adj_lon // (2.0 / 24.0))] + _SUBSQUARE[int(adj_lat // (1.0 / 24.0))]
    if precision == 6:
        return out

    adj_lon %= 2.0 / 24.0
    adj_lat %= 1.0 / 24.0
    out += str(int(adj_lon // (2.0 / 240.0))) + str(int(adj_lat // (1.0 / 240.0)))
    return out


def precision_of(locator: str) -> int:
    """Return the character count of a locator, as a precision indicator.

    Examples
    --------
    >>> precision_of("EQ79"), precision_of("FN21us")
    (4, 6)
    """
    return len(normalise(locator))
