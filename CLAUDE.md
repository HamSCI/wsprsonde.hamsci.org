# wsprsonde.hamsci.org

## Project Overview

This repository supports the tracking, frequency coordination, monitoring and control-operator
compliance of the **HamSCI WSPRSonde network** — the transmit side of the HamSCI Personal Space
Weather Station (PSWS) programme. A WSPRSonde is an 8-band, GPS-disciplined, ~1 W-per-band
WSPR/FST4W beacon built by Turn Island Systems (Paul Elliott, WB6CXC), transmitting continuously
so that the PSWS receiver network observes a *controlled* transmitter rather than whoever happened
to be on the air. Roughly a dozen units are operating worldwide; ten more are NSF-funded for
deployment across North America, the first five of which shipped in August 2026. The repository
holds the reconciled station registry, the code that verifies it against live on-air observations,
and the requirements for a proposed web-based WSPRSonde management system. The audience is the
HamSCI PSWS team, the WSPRSonde host and control-operator community, and NSF programme officers.

**PI**: Nathaniel A. Frissell, W2NAF (University of Scranton)
**Collaborators**: Paul Elliott WB6CXC (Turn Island Systems — designer/manufacturer, frequency
coordinator); Rob Robinett AI6VN (WsprDaemon); Gwyn Griffiths G3ZIL (station metadata and
frequency history); Gary Mikitin AF8A (host recruitment, hamsci.org); Hyomin Kim (NJIT);
Gerard Piccini KD2ZHK, Majid Mokhtari (Scranton — configuration and shipping);
Michael Hauan AC0G; David Witten KD0EAG
**Funder**: U.S. National Science Foundation — OPP-2332427, AGS-2432821, AGS-2432822,
AGS-2432823, AGS-2432824
**Project period**: 2026 — ongoing

## Project Goal

Maintain one authoritative, verifiable record of where every WSPRSonde is, what channel it is
assigned, and whether it is actually transmitting; and specify a management system that keeps that
record true, coordinates frequencies without collisions, alerts when a station fails, and gives
each control operator a positive-control mechanism sufficient to meet their regulatory
obligations.

## Repository Structure

```text
wsprsonde.hamsci.org/
├── CLAUDE.md
├── README.md
├── pyproject.toml
├── .claude/
│   ├── settings.json
│   ├── commands/commit.md              ← /commit workflow
│   └── rules/{ai-governance,python-code}.md
├── ai/ai_usage_log.md                  ← mandatory AI session log
├── data/
│   └── wsprsonde_stations.csv          ← the curated registry (hand-maintained)
├── src/wsprsonde/
│   ├── maidenhead.py                   ← locator ↔ coordinate conversion
│   ├── wsprdaemon.py                   ← read-only WsprDaemon ClickHouse client
│   ├── stations.py                     ← registry loading; administrative ∪ observed join
│   └── build_locations.py              ← CLI: builds products/
├── products/                           ← generated; do not hand-edit
│   ├── wsprsonde_locations.csv         ←   the deliverable consumed by polar-psws
│   ├── wsprsonde_locations_manifest.json
│   └── wsprsonde_candidates.csv
├── tests/
├── docs/
│   └── requirements_wsprsonde_management_system.md
└── reference/                          ← source material; **not tracked** (see below)
```

`data/wsprsonde_stations.csv` is the **administrative** record — what we believe we deployed.
`products/wsprsonde_locations.csv` is that joined to the **observational** record from WsprDaemon.
Keeping both and reporting where they disagree is the point; never overwrite one with the other.

## Working on this repository

- Rebuild the product with `PYTHONPATH=src python3 -m wsprsonde.build_locations`. It queries a
  live volunteer-run server: bounded windows, one request at a time, `wd10` by default.
- Run `python3 -m pytest` after changes. Doctests run as part of the suite.
- No runtime dependencies, deliberately — a collaborator should be able to rebuild the product
  with a stock Python. Do not add one without a strong reason.
- Thresholds that turn data into a judgement (how many days silent is "silent", how many Hz is a
  mismatch) live as named constants in `stations.py` with the reasoning attached. Do not inline
  them into queries.

## Data handling

- **`reference/` is not tracked.** It holds an Outlook mailbox export containing the PI's full
  inbox, and shipping lists with host home addresses and email addresses. None of it may be
  committed.
- Host names, street addresses, phone numbers and email addresses must never appear in
  `data/` or `products/`. Callsign, site label, region and Maidenhead locator are the most
  identifying fields permitted.
- `ok_to_list_public` in the registry carries the consent state inherited from the G3ZIL
  metadata's "OK to list on HamSCI?" column. It is `unknown` for most stations. **Check it before
  publishing any station**, including in figures derived from `products/`.

## AI Governance

All AI-assisted work must comply with the policies in `.claude/rules/ai-governance.md`.
Every substantive AI session must be logged in `ai/ai_usage_log.md` before committing.
Use the `/commit` command to handle logging and committing in the correct order.

Two project-specific cautions:

- **Do not submit the contents of `reference/` to any AI tool** beyond what is needed to extract
  WSPRSonde facts. It is a personal mailbox.
- **Regulatory claims must be verified, not recalled.** §5 of the requirements document cites
  47 CFR Part 97 from primary sources read on 2026-08-13. Any change to that section must be
  re-verified against the current eCFR, and the document's own caveat that it is not legal advice
  must stay.
