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
**Institution**: The University of Scranton
**Funder**: U.S. National Science Foundation — OPP-2332427, AGS-2432821, AGS-2432822,
AGS-2432823, AGS-2432824
**Project period**: 2026 — ongoing

## Project Goal

Maintain one authoritative, verifiable record of where every WSPRSonde is, what channel it is
assigned, and whether it is actually transmitting; and specify a management system that keeps that
record true, coordinates frequencies without collisions, alerts when a station fails, and gives
each control operator a positive-control mechanism sufficient to meet their regulatory
obligations.

## Standing Rules

These two are binding on every HamSCI project and are imported here so they load into context
automatically:

@.claude/rules/ai-governance.md
@.claude/rules/hamsci-data.md

`.claude/rules/python-code.md` is scoped by its own `paths:` frontmatter to `.py`,
`pyproject.toml` and `requirements*.txt`. The template's LaTeX rule was removed because this
project has no LaTeX.

## Repository Structure

```text
wsprsonde.hamsci.org/
├── CLAUDE.md
├── README.md
├── LICENSE
├── CITATION.cff                        ← citation metadata
├── pyproject.toml
├── .gitignore
├── .claude/
│   ├── settings.json
│   ├── commands/commit.md              ← /commit workflow (branch, commit, PR)
│   └── rules/{ai-governance,hamsci-data,python-code}.md
├── .github/ISSUE_TEMPLATE/             ← requirement comment, open question, bug, feature, question
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
│   ├── requirements_wsprsonde_management_system.md  ← the requirements, for review
│   ├── project_description.md          ← the capstone project description
│   └── technical_note_channel_capacity.md           ← advisory since Draft 0.95
├── notes/                              ← one dated file per working session
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

## Working Conventions

**Session notes.** Keep one dated notes file per working session in `notes/`, named
`YYYY-MM-DD_<topic>.md`, recording what was decided, why, what it depends on, and what is still
open. Write them for a reader with no context.

**Commits.** Use the `/commit` command. It logs the AI session, then commits on a feature branch
and opens a pull request. Prefix AI-assisted commits with `[AI-assisted]`. Reference tracking
issues (`refs #N`, or `closes #N` only when completion is yours to declare).

**Every change goes through a pull request.** Branch from `origin/main`, commit on the branch,
push the branch, and open a PR with `gh pr create`. A human maintainer reviews and merges.
Claude never commits or pushes directly to `main` and never merges.

**Pushing a feature branch and opening its PR is standing permission** once the user has approved
the commit. Any other push needs explicit instruction. Never force-push or hard-reset. Fetch and
verify remote state before any push.

**Project boards and issue status are human-curated.** Read them freely; propose changes and
name the exact command rather than running it.

## AI Governance

Every substantive AI session is logged in `ai/ai_usage_log.md` **before** the work is committed.
Use `/commit`, which enforces the ordering. The full policy stack is in
`.claude/rules/ai-governance.md`, which is imported above.

Two project-specific cautions:

- **Do not submit the contents of `reference/` to any AI tool** beyond what is needed to extract
  WSPRSonde facts. It is a personal mailbox.
- **Regulatory claims must be verified, not recalled.** §5 of the requirements document cites
  47 CFR Part 97 from primary sources read on 2026-08-13 and re-verified against the
  current eCFR on 2026-09-16. Any change to that section must be
  re-verified against the current eCFR, and the document's own caveat that it is not legal advice
  must stay.
