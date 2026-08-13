# wsprsonde.hamsci.org

Registry, frequency coordination and on-air verification for the **HamSCI WSPRSonde network** —
the transmit side of the HamSCI Personal Space Weather Station programme.

A WSPRSonde is an 8-band, GPS-disciplined, ~1 W-per-band WSPR/FST4W beacon built by
[Turn Island Systems](https://turnislandsystems.com/) and deployed by
[HamSCI](https://hamsci.org/wsprsonde-psws-transmitter) so that the PSWS receiver network observes
a *controlled* transmitter — known position, known power, GPS-locked frequency, continuous
operation — instead of whoever happened to be on the air.

This repository holds two things:

1. **A reconciled station registry and the code that checks it against reality.** Four partial
   records of the network existed as of August 2026 — a spreadsheet, a database table, an email
   thread and a shipping list. `data/wsprsonde_stations.csv` merges them;
   `src/wsprsonde/` verifies the result against live WsprDaemon observations and writes
   `products/wsprsonde_locations.csv`, which `polar-psws` overlays on its station maps.
2. **[Requirements for a WSPRSonde management system](docs/requirements_wsprsonde_management_system.md)**
   — a draft for collaborator review covering registry, frequency coordination, monitoring, and
   control-operator positive control.

## Quick start

No dependencies beyond a stock Python 3.10+.

```bash
PYTHONPATH=src python3 -m wsprsonde.build_locations
python3 -m pytest
```

`build_locations` queries the WsprDaemon ClickHouse endpoint at `wd10.wsprdaemon.org` and writes
three files to `products/`:

| File | Contents |
| --- | --- |
| `wsprsonde_locations.csv` | One row per unit: position, on-air status, assigned vs. measured frequency offset |
| `wsprsonde_locations_manifest.json` | Provenance — when it ran, what windows, what thresholds, resulting counts |
| `wsprsonde_candidates.csv` | Transmitters that look like WSPRSondes but are not in the registry |

## What the product tells you

Two status columns, deliberately kept apart:

- **`record_status`** — what the project believes: `deployed`, `retired`, `in_transit`,
  `pending_shipment`, `unknown`.
- **`on_air_status`** — what the radio is doing: `active`, `intermittent`, `silent`.

Rows where these disagree are the useful ones. A `deployed` station that is `silent` is a work
item, not a datum.

Likewise `offset_assigned_hz` (what the frequency coordinator allocated) against
`offset_observed_hz` (what receivers measure), with `offset_check` reporting `ok`, `MISMATCH`, or
`incoherent` when the bands disagree too much for a single offset to exist.

## Identifying a WSPRSonde in the spot record

A constant frequency offset does **not** identify one — an ordinary WSJT-X station band-hopping
with a fixed TX audio tone looks identical. What does work is **simultaneity**: a WSPRSonde keys
every band in the same 2-minute slot, which no band-hopping station can imitate. See
`wsprsonde.wsprdaemon.simultaneity`. The method needs someone to have *heard* several bands at
once, so a hit is strong evidence and a miss is no evidence — weakly-heard polar sites fall below
the threshold.

## Data handling

`reference/` is **not tracked** and must not be committed: it holds a mailbox export and shipping
lists containing host home addresses. Host names, addresses, phone numbers and email addresses
must never appear in `data/` or `products/`.

The `ok_to_list_public` column carries the publication consent inherited from the G3ZIL station
metadata. It is `unknown` for most stations. **Check it before publishing any station**, including
in figures built from `products/`.

## Positions

Positions are Maidenhead cell centres, not surveyed coordinates. A 4-character locator is about
78 km across at 40° latitude. KH2R reports `FN21` to WSPRNet but is really at `FN21us`, 65 km
away; VY0ERC has only a 4-character locator at 80° N. `grid_precision` in the product says which
you are looking at.

## Acknowledgements

Supported by the U.S. National Science Foundation under awards OPP-2332427, AGS-2432821,
AGS-2432822, AGS-2432823 and AGS-2432824. WSPRSonde hardware by Paul Elliott, WB6CXC
(Turn Island Systems). Spot data from [WsprDaemon](https://wsprdaemon.org) (Rob Robinett, AI6VN)
and [WSPRNet](https://wsprnet.org). Station metadata and frequency history originally compiled by
Gwyn Griffiths, G3ZIL.

Portions of this repository were produced with AI assistance; see [`ai/ai_usage_log.md`](ai/ai_usage_log.md).
