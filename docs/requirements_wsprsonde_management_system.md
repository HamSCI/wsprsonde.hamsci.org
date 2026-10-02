# WSPRSonde Management System — Requirements for Discussion

**Status:** Draft 0.96, for collaborator review (change log at the end)
**Date:** 2026-10-02 (Draft 0.95 was 2026-09-16; Drafts 0.2 to 0.9 were 2026-09-02 to
2026-09-14; Draft 0.1 was 2026-08-13)
**Editor:** Nathaniel A. Frissell, W2NAF (University of Scranton)
**Review list:** Paul Elliott WB6CXC · Rob Robinett AI6VN · Gwyn Griffiths G3ZIL ·
Gary Mikitin AF8A · Michael Hauan AC0G · Hyomin Kim (NJIT) · Gerard Piccini KD2ZHK ·
David Witten KD0EAG · Phil Karn KA9Q · Jonathan D. Rizzo KC3EEY (University of Scranton) ·
Kristina Collins KD8OXT · Dave Larsen KV0S

> **This is a request for comment, not a specification.** Requirements are numbered so
> you can say "R4.2 is wrong because…" rather than re-prosing the whole thing.
> Section 10 lists the questions I most want answered. Section 5 concerns FCC rules and
> is the section I am least confident in — please read it adversarially.
>
> **Draft 0.95 is a scope reduction, despite the modest version number.** The review committee met on 2026-09-16 and cut this
> back to what a student team can build correctly in one academic year. Automated fault
> monitoring, the channel-capacity question and third-party infrastructure dependencies all
> left the document. If you reviewed an earlier draft, read the change log first: several
> requirements you commented on are gone rather than changed.
>
> **How to comment.** File an issue at
> <https://github.com/HamSCI/wsprsonde.hamsci.org/issues>, one per point, using the
> *Requirement comment* or *Answer to an open question* template. Issues are how I track
> what has been raised and what has been resolved. Email to the editor works too, but
> anything that changes the document will be turned into an issue so the reasoning is on
> the record. Comments are being collected against **Draft 0.96**; when a requirement is
> changed as a result, the change log at the end will say which issue drove it.

---

## Contents

1. [Purpose and scope](#1-purpose-and-scope)
2. [Why now — the evidence](#2-why-now--the-evidence)
3. [Stakeholders and roles](#3-stakeholders-and-roles)
4. [What already exists](#4-what-already-exists)
5. [Regulatory basis for positive control](#5-regulatory-basis-for-positive-control)
6. [Functional requirements](#6-functional-requirements)
7. [Non-functional requirements](#7-non-functional-requirements)
8. [Architecture sketch](#8-architecture-sketch)
9. [Phasing](#9-phasing)
10. [Open questions for reviewers](#10-open-questions-for-reviewers)
11. [Explicitly out of scope](#11-explicitly-out-of-scope)

---

## 1. Purpose and scope

The HamSCI Personal Space Weather Station programme is deploying WSPRSonde transmitters —
8-band, GPS-disciplined, ~1 W per band, transmitting WSPR or FST4W continuously — as the
controlled transmit side of a distributed ionospheric sounding network. Roughly a dozen are
on the air today; ten more are NSF-funded for deployment across North America, of which the
first five shipped in August 2026.

The network has outgrown the way it is being tracked. This document proposes a web-based
**WSPRSonde Management System** covering four functions:

| | Function | One-line statement |
|---|---|---|
| **A** | **Registry** | One authoritative record of which sonde is where, run by whom, on what hardware. |
| **B** | **Frequency coordination** | Assign, publish and *verify* each unit's channel so sondes do not collide with each other or with ordinary WSPR traffic. |
| **C** | **Monitoring** | Detect automatically when a sonde stops transmitting, drifts off its assigned channel, or reports the wrong grid or power. |
| **D** | **Positive control** | Put a control point in each control operator's pocket: the ability to configure their WSPRSonde and to turn its transmitter on and off from a phone or computer, with a watchdog that stops the transmitter when that link is lost. |

**In scope:** the transmit side of the PSWS network — WSPRSondes and BeaconBlasters,
whether HamSCI-funded or privately owned, worldwide.

**Not in scope:** PSWS receivers (HFRx, magnetometers, VLF), science data processing, and
the WsprDaemon infrastructure itself. Those are separate systems this one reads from. §11
carries the full list, which Draft 0.10 extended considerably.

**What this document is deliberately not trying to settle.** How many WSPRSondes the world can
support, and how frequency assignments should be optimised, are open scientific and engineering
questions. They depend on how WSPR propagates and decodes, and the answers will shape what
science the received data can support. The review committee's position is that these need
careful consideration and are out of scope for an initial prototype. This document therefore
specifies a **simple, stated, replaceable** assignment rule (R2.2) rather than a good one, and
says so plainly where it matters.

**Who will build it.** The intent is to offer this system to a team of Computer Science
students at the University of Scranton as a senior capstone project, with the editor as
faculty sponsor and the people on the review list as the customers. That intent shapes the
document: the students need a stable, numbered set of requirements to work from, with the
reasoning attached so they can make design decisions without re-deriving the domain. This
review round settles the draft the student team starts from. The final version is the one the
student team and the WSPRSonde team agree on together (§9.1). See §9 for what it implies about
phasing.

---

## 2. Why now — the evidence

Everything in this section came out of a single afternoon's work on 2026-08-13 using the
existing sources. It is offered as evidence that the problem is real and measurable, not as
criticism of anyone — the current arrangement has been maintained generously by volunteers
and has simply reached its limit.

**2.1 There is no single list, and the ones we have disagree.** The network is currently
recorded in at least four places: Gwyn Griffiths' `G3ZIL_WsprSonde_Metadata_V1-1.xlsx`
(last revised 2025-05-11), the `wsprsonde` table on `wd10.wsprdaemon.org`, Paul Elliott's
offset assignments circulated by email on 2026-08-06, and Gary Mikitin's shipping lists.
None of them is wrong; they are simply four partial views maintained at four different
times, and reconciling them is manual work nobody owns. Gwyn said as much on 2026-07-31:
the table "does need updating, and a curator rather than me".

**2.2 The assigned frequency and the transmitted frequency are not the same thing.**
Measuring the on-air offset and the transmitted mode of every listed callsign against its
assignment. Offsets are medians over the three days to 2026-09-11 18:14 UTC, taken from
`products/wsprsonde_locations.csv`; modes are from the 14 days to 2026-09-10, and the two
`code` columns are the same mode as numbered by `wspr.rx` and by `wsprdaemon.spots` over the
three days to 2026-09-11:

| Callsign | Mode | `code`, `wspr.rx` | `code`, `wsprdaemon.spots` | Assigned | Measured | Verdict |
|---|---|---|---|---|---|---|
| WB6CXC (Occidental) | FST4W | 3 | 3 | 135 Hz | 135 Hz | ok |
| **KH2R** | FST4W | 3 | 3 | **36 Hz** | **35 Hz** | **1 Hz below assignment** |
| DP0GVN | WSPR | 1 | 2 | 37 Hz | 37 Hz | ok |
| WW0WWV | WSPR | 1 | 2 | 50 Hz | 50 Hz | ok |
| TI4JWC | WSPR | 1 | 2 | 15 Hz | 16 Hz | ok |
| **KD0EAG** | FST4W | 3 | 3 | **80 Hz** | **128 Hz** | **mismatch** |
| **VY0ERC** | FST4W | 3 | (none heard) | 150 Hz | withheld | **not measurable** |
| N4RVE | FST4W | 3 | 3 | 100 Hz | 100 Hz | ok, after a **nine-day outage** |
| **W8GPS** | FST4W | 3 | 3 | **none on record** | 60 Hz | **unassigned** |
| **ZD7GWM** | WSPR | 1 | 2 | 100 Hz nominal, **uncoordinated** | 100 Hz, 1 Hz on 28 MHz | **collides with N4RVE** |

**Mode belongs in the table, and so does its code, because the two are different facts.**
Gwyn Griffiths raised both
([issue #6](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/6),
[issue #9](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/9)): a unit transmits WSPR
**or** FST4W, several have changed over their lives, and a query has to select on a number
rather than on the mode name. Which number depends on which table is being queried, because
two encodings are in use. WSPRNet's encoding is what `wspr.rx` carries. WsprDaemon's own
encoding is what its PostgreSQL tables carry in a column named `mode`. The ClickHouse table
`wsprdaemon.spots` carries that same encoding in a column named `code` (Gwyn Griffiths,
issue #6, confirmed on `wd10`, `wd1` and `wd2` on 2026-09-11). WsprDaemon publishes the
mapping at <https://wspr.live/>:

| Mode | `wspr.rx` `code`, from 2023-01-16 | `wspr.rx` `code`, before 2023-01-16 | `wsprdaemon.spots` `code`, and WsprDaemon PostgreSQL `mode` |
|---|---|---|---|
| WSPR-2 | 1 | 1 | 2 |
| WSPR-15 | 2 | 2 | 15 |
| FST4W-120 | 3 | 1 | 3 |
| FST4W-300 | 4 | 4 | 6 |
| FST4W-900 | 5 | 1 | 16 |
| FST4W-1800 | 8 | 8 | 31 |

**The two encodings agree on FST4W-120 and disagree on WSPR-2**, and that is what makes the
trap subtle: a system that confuses them is right about every FST4W station and wrong about
every WSPR one, so it looks half correct. This document fell into it twice. Drafts 0.6 and
0.7 said WSPR-2 reads `1` in `wsprdaemon.spots`; that was the `wspr.rx` value carried over
without being measured, and Gwyn Griffiths' query on 2026-09-11 showed the table reads `2`.
R1.3 therefore stores the mode by name and each source's number beside it, and
`data/wsprsonde_stations.csv` carries both numbers so the disagreement is visible in the data
rather than buried in a query.

**Which table to measure mode from.** `wspr.rx` is the one, because its `code` has been
uniform since 2023-01-16: month by month from July 2024 to September 2026, WW0WWV reads `1`
throughout and the five FST4W sondes read `3` throughout. `wsprdaemon.spots` has switched
encoding at least three times over the same span: WW0WWV reads `1` from July 2024 to April
2025, `2` from May to October 2025, `1` again from November 2025 to February 2026, and `2`
from March 2026 on, with ZD7GWM and DP0GVN following the same pattern. The cause was not
established; the switches may line up with WsprDaemon client releases or with the move of the
spots table from TimescaleDB to ClickHouse, which is a question for Gwyn and Rob. Until it is,
only readings from `wsprdaemon.spots` dated March 2026 or later count as evidence of mode.

**One historical limit belongs with it.** Before 2023-01-16, `wspr.rx` `code` did not separate
WSPR-2 from FST4W-120: both were reported as `1`. Mode history reaching back past that date
has to come from the unit record or the curator's table, never from the spot archive, which is
a constraint on R1.4 rather than a preference.

**TI4JWC changed mode in July 2026, and the record shows why mode has to be interval-valued.**
In `wspr.rx` it reads `3` (FST4W) in every month from July 2024 to June 2026, both codes in
July 2026, and `1` (WSPR) alone from August 2026. The G3ZIL metadata, which lists it as FST4W,
and Gwyn's list in issue #6, which lists it as WSPR, were each right on the day they were
written. Draft 0.6 recorded the change as a correction to the registry; it was a change of
state, and the registry now records both intervals.

DP0GVN's record raises a different question. In `wspr.rx` it reads `1` in every month, and it
also reads `3` in substantial numbers from January to September 2025 and from December 2025 to
February 2026 (in March 2025, 110,072 spots against 107,524), with the last `3` at 2026-02-07
23:36 UTC. A WSPRSonde transmits one mode, so
either a second transmitter signs DP0GVN or the unit was reconfigured band by band. The per-band
breakdown that would settle it had not returned from `db1` at the time of writing, and the
question is put to Gwyn in issue #6.

KD0EAG is explicable, because the replacement WS-8 configured at 80 Hz has not been deployed
and the old BeaconBlaster is still running, and nothing in the current arrangement would have
surfaced it. Its bands still disagree by 23 Hz, which is what put the median at 128 Hz here
and 131 Hz in Draft 0.3. The BeaconBlaster has no dead-man
([issue #3](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/3)), so completing that
swap now settles a compliance question as well as a frequency one (§5.5, R4.3).

KH2R transmits 1 Hz below its assignment. Gwyn Griffiths measured 35 Hz at W2NAF-2 on
3.5 MHz ground wave and has used that value in the `wsprsonde` table
([issue #10](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/10)); the spot record
agrees, giving a median of 35 Hz on all seven measurable bands with 0 Hz spread, and W2NAF-2
alone gives 35 Hz over 1,015 reports on 80 m. The coordinator's list of 2026-08-06 assigns
1436 Hz.

Draft 0.8 explained the leftover hertz as the resolution limit of a crowd-sourced median. That
was wrong, and Gwyn corrected it
([issue #8](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/8)): the limit belongs to the
table rather than to the crowd. `wspr.rx` stores frequency as whole hertz, and the median of
whole numbers is a whole number however many reports go into it. `wsprdaemon.spots` carries the
same spots to 0.1 Hz in its `frequency_mhz` column. Re-measured there over the three days to
2026-09-14, KH2R reads **34.9 to 35.2 Hz on all eight bands**, a spread of 0.3 Hz over 102,000
reports. The station is on 35 Hz and the list assigns 1436, so the disagreement is real rather
than an artefact of rounding, and R2.1 keeps the assigned, configured and measured values in
three separate columns for exactly this case. A ground-wave reference receiver remains worth
having, because it is the only leg that does not depend on the crowd at all.

The same column settles TI4JWC, which Draft 0.8 reported as wandering: three measurements across
10 and 11 September read 16, then 15, then 16 Hz against a 15 Hz assignment. At 0.1 Hz resolution
TI4JWC reads 15.0 to 15.3 Hz on seven bands and holds still. The wander was `wspr.rx`'s
whole-hertz median stepping across a boundary as the receiving population changed from day to
day. Both stations are on frequency. What moved was the measurement, and now we can see by how
much.

**VY0ERC's row is the one to read carefully, because it has been wrong twice.** On 2026-09-10
seven of its bands fell below the twenty-report floor, the eighth read 50 Hz, and the prototype
reported a confident 50 Hz with 0 Hz spread against a 150 Hz assignment, which is a fault report
that would have sent somebody to Ellesmere Island. The spread test cannot catch this, because one
surviving band has a spread of zero by construction. The prototype withholds an offset measured
on fewer than three bands and returns *not measurable*, which is what R3.3 asked for.

Moving to the sub-hertz source brought the same failure back by a different route, which is why
R3.3c exists. In `wsprdaemon.spots` VY0ERC clears twenty reports on all eight bands, but four of
those bands are one receiver reporting several hundred times, and a single receiver's median
measures that receiver. Qualifying bands on distinct receivers instead leaves VY0ERC with three:
50.3 Hz on 30 m, 50.8 Hz on 15 m and 112.7 Hz on 17 m. The product now reads *incoherent* with a
62.4 Hz spread, which is the honest answer. The station's bands genuinely disagree, and no single
offset exists to compare against the 150 Hz assignment. A monitoring system's worst failure is
not silence; it is confident invention, and it is worth noticing that the same invention arrived
twice from opposite directions.

N4RVE was off the air for nine days, from 2026-08-09 23:20 UTC to
2026-08-18 23:20 UTC, and nobody was told; Paul Elliott reported the cause as a power supply
failure and the station returned on its assigned 100 Hz channel on all eight bands
([issue #1](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/1), measurements re-run
2026-09-03). It is the clearest case in this table for R3.2 and R3.7: a well-heard site, a
known and fixable cause, and no alert to anyone for nine days. VY0ERC is heard by so few
receivers that its channel cannot be verified at all from the spot record, which is itself
a finding worth having.

**2.3 Two collisions are on the books, and one of them is live.** Paul flagged in the
2026-08-06 thread that KH2R and DP0GVN sit 1 Hz apart by assignment, 1436 and 1437 Hz, and
that one should be reassigned; on the air they are now 2 Hz apart, because KH2R transmits at
35 Hz (§2.2).

The second is not a near miss. ZD7GWM, the privately owned St Helena sonde Gwyn identified
([issue #7](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/7)), transmits on 100 Hz,
which is N4RVE's assigned channel. Over the three days to 2026-09-10 the two measured the same
100 Hz on five common bands, 3.5, 7, 14, 18 and 21 MHz, with a sixth, 24 MHz, one hertz apart.
Two GPS-disciplined 1 W beacons are sharing a channel across most of HF. Nobody did anything wrong: ZD7GWM was never in a list the coordinator could check
against, which is R2.7's case for registering non-HamSCI units and R2.3's case for checking
an assignment against everything on the air rather than against our own roster.

**Measured to 0.1 Hz the collision is tighter than the whole-hertz figures showed.** Over the
five days to 2026-09-14, `wsprdaemon.spots` puts the two within **0.4 Hz on every one of the
five common bands**, and the 24 MHz pair that read one hertz apart in `wspr.rx` is 0.7 Hz apart:
99.7 Hz for N4RVE against 100.4 Hz for ZD7GWM. That separation sits well below the tone spacing
of either mode, so the two signals occupy the same slice of the sub-band rather than merely the
same 200 Hz window. Gwyn has plotted it from the `wd2` dashboard (§4.5) with W1XP as the
receiver on 14 MHz, showing ZD7GWM's WSPR reports against N4RVE's FST4W reports inside a
1 Hz bandwidth ([issue #8](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/8)). One pair
of spots from that check, both at 2026-09-12 01:12 UTC into W1XP, reads 14.0970996 MHz for
N4RVE and 14.0970998 MHz for ZD7GWM: 0.2 Hz apart in a single receiver at a single minute.

There is no tool that would have caught either at assignment time, and no tool that would
catch the next one.

**2.4 "Which of these is a WSPRSonde?" has no answer in the data.** Nathaniel asked this
on 2026-07-31 and suggested a callsign suffix such as `-WS`. Two detection methods were
tested against `wspr.rx` on 2026-08-13:

- *Constant frequency offset* — **does not work.** An ordinary WSJT-X station band-hopping
  with a fixed TX audio tone produces an identical signature; a scan on this criterion
  returned 46 stations, most of them not sondes.
- *Simultaneous multi-band transmission* — **works.** Grouping spots by `(tx_sign, time)`
  and counting distinct bands per 2-minute slot cleanly separates a sonde, which keys every
  band at once, from a band-hopper, which cannot. A 3-day scan returned nine stations, of
  which five are known sondes and four are candidates nobody has on a list: **DC7TO**,
  **ZD7GWM** (St Helena), **N9VP** and **G0PKT**.

  The method's limitation is not fixable from the spot record: it needs someone to have
  *heard* several bands in the same slot, so weakly-heard sondes — the polar sites
  especially — fall below the threshold. A hit is strong evidence; a miss is no evidence.

**Two of those candidates now have answers, and a ninth station appeared after the scan.**
ZD7GWM is a privately owned WSPRSonde on St Helena, confirmed by Gwyn Griffiths, who has
added it to the `wsprsonde` table and holds the control operator's contact details
([issue #7](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/7)). W8GPS is a WSPRSonde
Gwyn lists that no scan here has ever reported, for a simple reason: it was first heard on
2026-08-21, on four bands, and went to eight on 2026-08-29, both after the 2026-08-13 scan.
It transmits FST4W on 60 Hz with 0 Hz spread across eight bands and has no assignment on
record. A one-off scan is therefore worth about as much as a one-off frequency measurement,
which is the case for running R3.6 on a schedule rather than by hand.

**The suffix idea is closed.** Paul Elliott reports that neither the WSPRSonde nor the
BeaconBlaster supports extended callsigns
([issue #2](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/2)), so a `-WS` marker
would require a firmware change on every unit in the field. The protocol forbids it
independently: WSPR carries a compound callsign only in the Type 2 and Type 3 message pair,
whose permitted add-on forms are a prefix of up to three characters (`xxx/callsign`), a
single letter or digit (`callsign/x`), or a two-digit number from 10 to 99 (`callsign/dd`),
and those messages cost two transmission slots each. A two-letter suffix is not encodable.
Identification therefore rests on the simultaneity scan as the finder (R3.6) and the
registry as the authority (R1.1). The related question of a hardware identifier is settled: a
WS-8 carries a host-readable serial number, so R1.1 keys on the hardware's own rather than on
one we invent.

This matters beyond bookkeeping. Any study that wants to use the WSPRSonde network as a
controlled transmitter array must be able to say which spots came from a controlled
transmitter, and right now that is only possible by consulting a spreadsheet.

**2.5 Nobody is watching the transmitters.** DP0GVN and VY0ERC are the two existing polar
PSWS sites, and no new polar WSPRSonde deployments are currently planned, so those two are
the network's whole polar transmit capability. They are also the hardest sites to service and
the ones where a fault costs the most. VY0ERC was heard by 70 receivers over 30 days, against
2,319 for KH2R. Whether that is propagation, an antenna problem or a sick transmitter, no one
is being told.

---

## 3. Stakeholders and roles

The system should model these as distinct roles with distinct permissions, because they
carry genuinely different responsibilities and liabilities.

| Role | Who | Needs to be able to |
|---|---|---|
| **Control operator** | The licensed amateur responsible for a station's transmissions | See their station's state; inhibit or enable transmission immediately, from a phone; receive alerts |
| **Station host** | The person whose property the sonde sits on — often but *not always* the control operator | See status; report site changes; be contacted |
| **Frequency coordinator** | Paul Elliott WB6CXC today | Allocate and reassign channels; see the whole assignment map; be warned of collisions |
| **Network operator** | HamSCI PSWS team (Scranton/NJIT) | See fleet health; manage the deployment pipeline from shipment to on-air; export data products |
| **Data curator** | Currently Gwyn Griffiths G3ZIL, by his own account looking to hand over | Correct the registry; manage the historical record of who transmitted what, where, when |
| **Scientist** | Anyone using the data | Get an authoritative machine-readable list of controlled transmitters with positions and validity intervals |
| **Public** | HamSCI community, prospective hosts | See a map and status of the network, subject to consent (R1.6) |

A single person will hold several of these. **R3.1** The system must not assume they are
the same person: a host who is not a licensed amateur must not inherit control-operator
authority, and a control operator who is not the host must still be able to shut the
station down.

**3.1 The technical team the student developers work with.** Settled on 2026-09-16, replacing
the earlier intent that the PI alone act as customer. Questions are routed by subject, and a
capstone team that knows who to ask does not lose its first month finding out.

| Contact | Answers questions about |
|---|---|
| Paul Elliott WB6CXC | WSPRSonde hardware and firmware |
| Gwyn Griffiths G3ZIL | Data analysis, WSPR and FST4W modulation, databases |
| Gerard Piccini KD2ZHK | User interface |
| Majid Mokhtari | Student access to hardware (University of Scranton research and lab engineer) |
| Nathaniel Frissell W2NAF | On-campus point of contact for everything else; liaison to the Computer Science capstone faculty |

**How to use it.** Design questions go to the **technical team** as a single email: Paul, Gwyn,
Gerard and Nathaniel together. Majid is involved only when physical access to hardware is
required. One email to four people beats four guesses about which one to ask.

---

## 4. What already exists

Build on these rather than replacing them.

**4.1 The WsprDaemon archive.** Reachable over the ClickHouse HTTP interface at
`http://wd10.wsprdaemon.org/` with no credentials (mirrors on `wd1`, `wd2`). `wspr.rx`
carries the full WSPRNet record and is the right table for liveness, because a sonde is
heard by whoever happens to be listening. `wsprdaemon.spots` carries calibrated noise from
~5% of receivers and is the right table for science, not for monitoring.

> Note for implementers: `wd1.wsprdaemon.org` also exposes PostgreSQL on 5432 with a `spots`
> hypertable, and it is the obvious thing to poll. As of 2026-08-13 that table is unusable —
> any query fails with `could not open file "pg_tblspc/18143/…"` because a TimescaleDB
> chunk's tablespace is missing. Use the ClickHouse endpoint.

**4.2 Gwyn's `wsprsonde` table** on `wd10.wsprdaemon.org` (PostgreSQL, database `tutorial`).
139 rows of `(tx_call, tx_grid, mode, freq, clock, band, time_start, time_end, code)` at
1 mHz resolution, with validity intervals. **This is the right schema for the frequency
history** and the new system should adopt its shape rather than invent one, then take over
maintaining it.

**4.3 This repository.** `data/wsprsonde_stations.csv` is a first reconciliation of the four
sources above; `src/wsprsonde/` builds a location product from it plus live queries. It is
deliberately a flat file with no runtime dependencies — it is a stopgap and a specification
by example, not the proposed system.

**4.4 hamsci.org.** Gary Mikitin can host a landing page. Rob Robinett and Gary both
favoured GitHub over the HamSCI web server for the underlying files, consistent with the
direction the PSWS instrument pages are already taking. **R4.1** The registry's canonical
form should be a versioned text file in a Git repository, with the web application as a
view and an editor over it — not a database whose history lives only in backups.

**4.5 Gwyn's WSPRSonde Grafana dashboard**, at `wd10.wsprdaemon.org:3000`
(`/d/dfagb9m7nn5s0f/wsprsonde-ch`), joins the `wsprsonde` table of §4.2 to the spot record
and plots Doppler shift, derived signal level and clock metadata per transmitter
([issue #8](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/8)). It reads with the
shared read-only `wdread` account that WsprDaemon publishes on <https://wsprdaemon.org>; the
password is public but is not transcribed here, so that this repository holds no credential
string of any kind.

**It is the strongest available argument for the registry's frequency record.** The Doppler
plot works only because the transmit frequency is known to 1 mHz from the table rather than
inferred from the spot, so R2.1's measured leg is a science product and not only a
coordination check. Two consequences for this document: the system must keep feeding
whatever the dashboard reads rather than diverging from it (R6.3), and the dashboard is the
presentation layer for per-station status that R7.2 would otherwise have to build from
nothing.

**A second, prototype dashboard on `wd2` is the collision check already built.** At
`wd2.wsprdaemon.org:3000/d/dopAJDLIk/a9e4d43` it shows the signal-to-noise ratio of a wanted
transmitter at a chosen receiver alongside every other station heard within a user-set
bandwidth of it, which is how a human would gauge co-channel interference
([issue #8](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/8)). The transmitter need not
be a WSPRSonde, so it answers R2.4's question as well as R2.3's. Today the frequency and
bandwidth are typed in by hand; Gwyn Griffiths proposes populating them from the WSPRSonde
frequency record, which is the same join this system exists to make. **Adopt it rather than
rebuild it**, and point it at the registry. The §2.3 collision is the case it would have shown:
two 1 W beacons on one channel, visible as one plot.

**It has now shown it.** Gwyn ran the dashboard on 2026-09-12 with W1XP as the receiver, ZD7GWM
as the wanted transmitter on 14 MHz, and a bandwidth of 1 Hz. The panel returns N4RVE's FST4W
reports alongside ZD7GWM's WSPR reports and the other co-channel traffic, checked against the
underlying rows (§2.3). That is the check of R2.3 and R2.4 running against a real collision, on
existing infrastructure, with the frequency typed in by hand. Supplying that frequency from the
registry is the whole of the remaining work.

---

## 5. Regulatory basis for positive control

> **Not legal advice.** Rule text below was read from the Cornell LII copy of 47 CFR Part 97
> on 2026-08-13, re-verified against the eCFR (point-in-time version of 2026-08-29) on
> 2026-09-02, and §97.109 and §97.213 re-verified against the current eCFR again on
> 2026-09-16 when the committee adopted the remote-control determination of §5.3; the quoted
> passages match the eCFR text. It should still be reviewed by someone who has actually argued
> these rules — ARRL regulatory counsel would be the right destination.
>
> **This section covers US stations only.** The committee decided on 2026-09-16 not to attempt
> the Canadian, German, Costa Rican or Indian equivalents. See §5.6.

**5.1 A WSPRSonde is a beacon.** §97.3(a)(9): *"An amateur station transmitting
communications for the purposes of observation of propagation and reception or other related
experimental activities."* That is exactly what a WSPRSonde does, and §97.203(g) confirms a
beacon may transmit one-way communications.

The claim this document makes is therefore **not** that a WSPRSonde is something other than
a beacon. It is that a WSPRSonde on HF is a beacon under **remote control** (a control
operator at a control point, reached through a control link) rather than under **automatic
control** (no control operator present), because automatic control of a beacon is permitted
only on the segments listed in §97.203(d), and none of the WSPR frequencies below 10 m is
among them. Reviewers should argue with that reading, not with the word "beacon".

**5.2 Beacon-specific limits we already satisfy — but should verify automatically.**

- §97.203(c): transmitter power must not exceed 100 W. A WSPRSonde runs ~1 W per band. ✔
- §97.203(b): *"A beacon must not concurrently transmit on more than 1 channel in the same
  amateur service frequency band, from the same station location."* A WSPRSonde-8 transmits
  one channel in each of eight *different* bands, so it complies. **But this becomes a live
  constraint the moment a site gets a second unit.** WB6CXC runs two WS-8s at Occidental
  (CM88mj) on disjoint band sets — 80–10 m and 160/6 m — which is compliant, and would stop
  being compliant if either were reconfigured. This is a rule a computer should check, not a
  person. → **R2.6**
- §97.203(e): a licensee must notify the National Radio Astronomy Observatory before
  establishing an *automatically controlled* beacon in the National Radio Quiet Zone, or
  changing its frequency, power or antenna. It is written for automatic control and no
  current site is in the Quiet Zone, but the registry should flag any US site whose
  locator falls inside it so the question is asked at registration rather than afterwards.

**5.3 The part that actually constrains us: automatic control is not available on these
frequencies.** §97.109(d) permits operation without a control operator at the control point
only for stations "specifically designated elsewhere in this part". For beacons, §97.203(d)
designates: **28.20–28.30 MHz, 50.06–50.08 MHz, 144.275–144.300 MHz, 222.05–222.06 MHz,
432.300–432.400 MHz, and the 33 cm and shorter bands.**

Measured WSPRSonde transmit frequencies (from `wspr.rx`, 2026-08-13) are 3.570, 5.366,
7.040, 10.140, 14.097, 18.106, 21.096, 24.926, 28.126 and 50.294 MHz. **None falls in an
automatic-control segment** — 10 m WSPR at 28.126 MHz sits below the 28.20 MHz threshold,
and 6 m WSPR at 50.294 MHz is above 50.08 MHz.

**Consequence:** a US WSPRSonde running unattended is operating under **remote control**
(§97.109(c)), which states the control operator *must be at the control point*. §97.3(a)(39)
defines remote control as *"the use of a control operator who indirectly manipulates the
operating adjustments in the station through a control link"*, and §97.3(a)(14) defines the
control point as *"the location at which the control operator function is performed"*.

**The review committee adopted this reading on 2026-09-16, and the system is what makes it
true.** The determination rests on the interface this document specifies: the control operator
is given the facility to control the WSPRSonde's functions, including transmitter on and off,
from a smartphone or computer, and is therefore at a control point of the transmitter. That is
the definition of remote control in §97.3(a)(39) satisfied by construction, through a control
link that did not exist before this system. The argument improves with the system rather than
being asserted about it.

**5.4 §97.213 sets the conditions, and one of them is a hard number.** An amateur station
within 50 km of the Earth's surface may be under telecommand where:

- **(a)** there is a radio or wireline control link between the control point and the
  station sufficient for the control operator to perform their function. The rule adds that
  *"a control link using a fiber optic cable or another telecommunication service is
  considered wireline"*, so an internet or cellular path from a phone to the sonde is a
  wireline control link and needs no auxiliary radio station;
- **(b)** *"Provisions are incorporated to limit transmission by the station to a period of
  no more than 3 minutes in the event of malfunction in the control link."*
- **(c)** the station is protected against making unauthorized transmissions, willfully or
  negligently;
- **(d)** a photocopy of the station license and a label with the name, address and telephone
  number of the licensee and at least one designated control operator is posted conspicuously
  at the station location.

**5.5 What this means for the design.** Paragraph (b) is the requirement that shapes the
whole feature. A web dashboard the operator can visit does not satisfy it: a dashboard is a
way to look, and the rule demands that transmission *stop* when the link fails. What
satisfies it is an interlock at the transmitter, and the WSPRSonde already has one.

**The mechanism is the WSPRSonde's dead-man**, and its behaviour is now on the record from
its designer ([issue #3](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/3)). A WS-8
can be configured to shut its transmitters down after an interval with no inbound
command-line traffic. When it fires the transmissions stop immediately, with no frame
overhang, and it re-arms the moment inbound activity resumes, so a network outage costs one
dead-man interval of downtime and needs no site visit. The interval ranges from 1 to 12,000
minutes, 0 disables it, and the condition is tested once a minute. No "ask for permission to
transmit" feature is needed in the sonde, and no timer in the web application can be
misconfigured into non-compliance.

**One minute is the setting.** Because the test runs once a minute, the worst case is the
configured interval plus up to another minute, so a 1-minute interval stops transmission
within two minutes of the last keep-alive and 2 minutes is the ceiling that still fits inside
§97.213(b). The keep-alive should therefore be sent every 15 to 30 s, which leaves room for a
retry before the transmitters drop.

**The keep-alive must be conditional on the control link, and this is the load-bearing
detail.** Paragraph (b) is triggered by a malfunction in the *control link*, so a keep-alive
the host generates on its own would cover a host or software failure and miss the case the
rule is written for: the site's network path is down, the transmitter is healthy, and it is
still radiating with the control operator unable to reach it. That is the third row of
R3.5's table. The host must therefore feed the serial keep-alive only while it is in contact
with the control point, and stop feeding it when that contact lapses. The interval that has
to stay under three minutes is consequently the **renewal interval over the control link**,
not merely the dead-man timeout at the transmitter.

**The architecture that delivers this was settled on 2026-09-16, and the server is the
intermediary.** `wsprsonde.hamsci.org` tracks every logged-in control device and therefore knows,
per unit, whether any member of that unit's control-operator pool is currently reachable. The
host Pi **polls the server** and feeds the dead-man only while the answer is yes:

```
control operator devices  ──login/session──▶  wsprsonde.hamsci.org
                                                      ▲
                                                      │  poll: "is a control op reachable?"
                                               WSPRSonde host Pi
                                                      │  serial keep-alive, only on "yes"
                                                      ▼
                                               WSPRSonde dead-man  (§97.213(b))
```

**The Pi pulls; the server never reaches in.** A host that loses its own network path stops
receiving "yes" and goes quiet by itself, which is exactly the behaviour paragraph (b)
prescribes on control-link malfunction. It needs no push infrastructure, no mobile app running
in the foreground, and no inbound firewall rule at the host site. The cost, accepted openly, is
that `wsprsonde.hamsci.org` becomes a single point of failure for every keep-alive-enabled
station; see N4.

**Two consequences follow from how the dead-man is fed.** Any inbound command re-arms it, so
the keep-alive is indistinguishable from ordinary traffic on the same port: a monitoring script,
a diagnostic session, or any other process on the host that can reach the unit's command line
all pet the dog equally, and one left running is an indefinite authorisation nobody issued. Outbound traffic is safe to read,
because the per-frame reports the WS-8 emits carry the text `Watchdog shutdown` when it has
tripped, which gives R4.5 an observable state with no query. **R4.11** covers both.

**The BeaconBlaster has no dead-man.** Its interlock cannot be retrofitted in software, and
Paul Elliott's preference is to replace the remaining unit with a WS-8 rather than revise the
older firmware. A BeaconBlaster at a US site therefore cannot satisfy R4.3, which makes
KD0EAG's replacement a compliance question rather than only the frequency question of §2.2.

That is the mechanism this document proposes (R4.3). It also happens to give the control
operator the thing they actually want: a single control they can hit from a phone that
demonstrably stops the transmitter.

**5.6 Jurisdiction: this section is US-only, by decision.** Part 97 governs US stations only.
The network already includes DP0GVN (German licence, Antarctica), VY0ERC (Canada, ISED), TI4JWC
(Costa Rica) and VU24JD (India), so it spans four licensing administrations beyond the FCC.

The review committee decided on 2026-09-16 to **do US rules only for now**, and not to research
the ISED, BNetzA, Costa Rican or Indian requirements for unattended beacon operation. That
question leaves the document.

**R4.9** Record each station's licensing administration. Apply the US rules of this section to US
stations, and **do not assert compliance with rules that have not been checked**. Where an
administration's requirements are unknown, the system says so rather than defaulting to the
FCC's. Operators outside the US are responsible for their own administrations' rules, which is
consistent with the keep-alive being a per-unit setting the control operator owns (R4.3).

---

## 6. Functional requirements

### R1 — Registry

- **R1.1** One record per **unit** (a physical transmitter), keyed by a stable identifier
  independent of callsign. Callsigns change: the Friday Harbor station is recorded as
  WB6CXC in Gwyn's metadata and transmits as N4RVE today. **Use the hardware's own
  identifier.** Every WS-8 carries a unique 24-bit serial number, derived from its
  microcontroller's, readable over the command line (Paul Elliott,
  [issue #2](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/2)). The number written on
  the enclosure is unrelated to it, so record that separately and never key on it.
- **R1.2** Units group into **sites**. A site is one location and one dot on a map; a site
  may hold more than one unit (WB6CXC at CM88mj).
- **R1.3** Each unit record must carry, at minimum: identifier, site, current callsign and
  callsign history, licensee, control operator(s), host, Maidenhead locator with its
  precision, hardware model (BeaconBlaster / WS-8 / successor), hardware serial number,
  enclosure marking, firmware version, GPSDO type, antenna, **transmit mode and its numeric
  code**, in-service and out-of-service dates, funding source, and free-text notes.
  A unit transmits WSPR **or** FST4W, several have changed mode over their lives, and a
  query selects on a number rather than on the name (Gwyn Griffiths,
  [issue #9](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/9)).
- **R1.3a** **Store mode by name; translate at every boundary.** The system's internal
  representation of transmit mode is its name (`WSPR-2`, `WSPR-15`, `FST4W-120`, `FST4W-300`).
  A bare number is never stored as the mode, and a number is never copied from one destination
  to another. Every read and every write passes through an explicit mapping for that specific
  destination.

  This binds on **writing** as much as on reading, which is the half Draft 0.9 left implicit.
  The system now configures units (R4.12), so it emits mode values as well as consuming them,
  and it must emit the encoding the receiving system expects:

  | Mode | `wspr.rx` / WSPRNet | `wsprdaemon.spots` and the `wsprsonde` table | WSPRSonde firmware |
  |---|---|---|---|
  | WSPR-2 | 1 | 2 | **unknown, Q10.3** |
  | WSPR-15 | 2 | 15 | **unknown, Q10.3** |
  | FST4W-120 | 3 | 3 | **unknown, Q10.3** |
  | FST4W-300 | 4 | 6 | **unknown, Q10.3** |

  The first two columns were measured (§2.2). They **agree on FST4W and disagree on WSPR**, so
  a system that confuses them is right about every FST4W station and wrong about every WSPR
  one, which is the hardest kind of wrong to notice. The third column is not yet known and is
  the one the system must get right in order to configure a unit at all.
- **R1.4** All history is **interval-valued**, following §4.2's schema. "Where was DP0GVN in
  March 2025" must be answerable, because a study spanning a reconfiguration otherwise silently
  mixes two different stations. Mode is one of the interval-valued fields: TI4JWC has run both
  WSPR and FST4W, and a study that assumes one mode across a span gets the wrong integration
  time.

  **History comes from the unit record, not from the spot archive.** The system records what a
  unit was configured to do and when it changed, and it imports Gwyn Griffiths' existing history
  as the seed (R6.3). It does **not** attempt to reconstruct past configuration by mining spots.

  That is a decision of 2026-09-16, and §2.2 records why it is the right one: `wsprdaemon.spots`
  changed its encoding of WSPR-2 at least three times between July 2024 and March 2026, and
  before 2023-01-16 `wspr.rx` reported WSPR-2 and FST4W-120 alike as `1`, so early history is not
  recoverable from spots at any price. Explaining those archive changes is out of scope (§11).
  Recording configuration correctly going forward is the requirement.
- **R1.5** Positions are Maidenhead locators, and **locator precision must be stored and
  displayed**. A 4-character locator is ~78 km across at 40° latitude. KH2R reports `FN21`
  to WSPRNet but is really at `FN21us`, 65 km away; VY0ERC has only a 4-character locator at
  80° N, where a 1° cell straddles the polar-cap boundary. Accepting a true coordinate where
  the host is willing to give one is preferable.
- **R1.6** Every record carries an explicit **publication-consent** flag per field group
  (position, operator name, contact). Gwyn's spreadsheet already has an "OK to list on
  HamSCI?" column and it is blank for most stations. Default must be *not published*. Host
  street addresses and email addresses must never appear in an exported product.
- **R1.7** Deployment pipeline states, so a unit can be tracked before it is on the air:
  `in_stock → configured → shipped → installed → on_air → retired`, plus `in_transit`
  (VU24JD has been in Indian customs since at least 2026-08-06).
- **R1.8** Export the registry as CSV and JSON at a stable URL, versioned and with a
  provenance manifest stating when it was generated and from what. Downstream consumers —
  the `polar-psws` station maps are the first — must be able to cite a version.

### R2 — Frequency coordination

- **R2.1** Record, per unit, three things that are usually assumed to agree and sometimes do
  not: the **assigned** channel offset (Hz above the bottom of the 200 Hz WSPR/FST4W window),
  the **configured** frequency list read from the unit itself (R3.10), and the **measured**
  per-band transmit frequency to 1 mHz, following the existing `wsprsonde` table's resolution.
  Carry the mode and its code alongside all three (R1.3), because §4.2's schema keys on them
  and the dashboard of §4.5 selects on them.
- **R2.2** **The assignment rule, stated simply and meant to be replaced.** Decided by the
  review committee on 2026-09-16. Applied in order:

  1. **Prefer an unassigned channel.** If any channel on the grid has no unit on it, assign one
     of those. In short: try not to reuse frequencies.
  2. **Otherwise pick the least-used channel**, the one with the fewest units currently assigned
     to it, so that reuse is spread evenly rather than piling onto one channel.
  3. **Break ties by geographic separation**, choosing the candidate channel whose nearest
     already-assigned unit is furthest away. Distance is great-circle between Maidenhead locator
     centres, which the registry already carries (R1.5).

  **Stated assumption, which the reader must not mistake for a finding: geographic separation is
  used here as a proxy for non-interference, and on HF it is not the same thing.** A receiver
  between two distant transmitters hears both. Getting this right needs a proper treatment of how
  WSPR propagates and decodes, which the committee placed out of scope (§1, §11). The interface
  must present this rule as a heuristic rather than as an optimum, and **a better algorithm is
  explicitly invited** as work for an interested student.

  Support the existing allocation scheme underneath it: one offset applied to all of a unit's
  bands, on a 10 Hz grid from 1450 Hz upward, with the pre-existing off-sequence assignments
  (TI4JWC 1415, KH2R 1436, DP0GVN 1437, WB6CXC 1535) recorded as exceptions rather than errors.
  **Allow a per-band override.** ZD7GWM runs 100 Hz on seven bands and 0 Hz on 28 MHz
  ([issue #7](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/7)), which this
  repository's one-offset-per-unit model reports as an incoherent unit rather than as a
  deliberate configuration. A unit whose bands legitimately differ must be recordable as
  such, so that R2.5 compares each band against its own assignment and R3.3 raises a fault
  only where the disagreement is unexplained.
- **R2.3** **Refuse or warn on a colliding assignment** at allocation time, with a
  configurable guard band. Flag existing collisions: KH2R and DP0GVN are 1 Hz apart.
- **R2.4** **A view, not a gate.** Before confirming an assignment the coordinator must be able
  to see the proposed channel against **all WSPR activity** in that window, not only against
  other sondes, because the 200 Hz window is shared with everyone. This **does not block** an
  assignment and the rule of R2.2 does not consult it; it is there so a human can notice an
  occupied channel before issuing it.

  Gwyn Griffiths' co-channel dashboard on `wd2` already is this view: it shows the
  signal-to-noise ratio of a wanted transmitter at a chosen receiver together with every other
  station within a user-set bandwidth of it (§4.5). **Adopt it rather than rebuild it**, and
  populate the frequency from the registry instead of by hand, which is the proposal he made in
  [issue #8](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/8). He has since run it
  against the live §2.3 collision, so what it shows is known rather than assumed.
- **R2.5** Continuously compare all three legs of R2.1 and raise a discrepancy. Assigned
  against configured catches a unit that was never reconfigured; configured against measured
  catches a unit that is not doing what it was told. §2.2's KD0EAG row is the first case and
  would have been visible the day the assignment was made.
- **R2.6** Enforce §97.203(b) for US stations: no two units at the same site may be assigned
  channels in the same band. See §5.2.
- **R2.7** The coordinator role must be able to issue assignments for units **outside**
  HamSCI. Paul Elliott ships WSPRSondes to people not in the PSWS programme and asked
  specifically to keep coordinating with HamSCI rather than run a parallel scheme. A
  non-HamSCI unit must be registerable for coordination purposes without implying HamSCI
  operates it.

### R3 — Monitoring

- **R3.1** Poll the WsprDaemon archive on a schedule and record, per unit: last spot time,
  distinct reporters, distinct bands, reported grid and reported power.
- **R3.2** Classify on-air state as **active / intermittent / silent** against a documented
  threshold, and treat "not heard" as *evidence of nothing being received*, not as proof the
  transmitter is dead. A single quiet day at a remote site is normal; two consecutive days at
  a station that is normally heard is a signal.
- **R3.3** Measure the on-air offset per band as a **median over many reception reports**.
  Each report carries the receiving station's own frequency error, so a single spot is not a
  measurement. Report the spread across bands: when it exceeds a documented limit, no single
  offset exists and the system must say "not measurable" rather than "wrong frequency".
  VY0ERC is in exactly this state and must not generate a false fault.
- **R3.3a** Take the offset from **`wsprdaemon.spots.frequency_mhz`, which resolves 0.1 Hz**,
  and fall back to `wspr.rx` only where a station is heard by too few WsprDaemon sites
  (issue #8). The choice of table sets the precision of the answer: `wspr.rx` stores whole
  hertz, and a median of whole numbers is a whole number no matter how many reports go into it,
  so no amount of additional receivers will resolve a 1 Hz question there. The trade is
  resolution against ears, and R3.2's liveness check keeps `wspr.rx` for the same reason it
  always did. Record which table each measurement came from, because a 35 Hz reading and a
  34.9 Hz reading are not the same claim.
- **R3.3c** Qualify a band on **distinct receivers**, not on a count of reports. A report floor
  is the wrong test against `wsprdaemon.spots`: one WsprDaemon site near a transmitter reports
  every two-minute slot and clears a twenty-report floor by itself, and a single receiver's
  median is that receiver's frequency error rather than the transmitter's offset. VY0ERC cleared
  twenty reports on all eight bands on 2026-09-14, four of them from **one** receiver reporting
  between 200 and 2,158 times. Five receivers separates the current registry cleanly: VY0ERC,
  KD0EAG and ZD7GWM each have a band down at one, and every other station sits at six or above.
- **R3.3b** Never use `wsprdaemon.spots.frequency`, the integer column, for a frequency
  measurement. Measured over 582,198 spots on 14 MHz in the day to 2026-09-14, it is the
  **floor** of `frequency_mhz` rather than its rounding: the difference falls in 0 to 0.9 Hz
  and averages 0.43 Hz. A system that reads the integer column reports every station about
  half a hertz low, consistently enough that the error looks like a calibration offset.
- **R3.4** Alert on: reported grid differing from the registry; reported power differing from
  the configured power; a band dropping out while others continue (an antenna, filter or
  combiner fault, and invisible in an all-bands liveness check); and a sudden collapse in
  reporter count while other stations in the region are unaffected.
- **R3.5** Cross-check **host reachability against on-air evidence**, and distinguish the four
  outcomes, because they mean different things and need different people:

  | Host polling us | Being spotted | Meaning |
  |---|---|---|
  | yes | yes | healthy |
  | yes | no | RF fault: transmitter, filter, combiner, antenna, or a bad frequency |
  | no | yes | site network is down; the transmitter is fine and **still radiating** |
  | no | no | site power or connectivity failure |

  The third row is the interesting one: the control link is gone and the station is still on
  the air, which is precisely what §97.213(b) addresses and what the keep-alive stops.

  **Host reachability is free, and comes from the keep-alive poll itself.** The Pi contacts
  `wsprsonde.hamsci.org` every 15 to 30 seconds (§5.5), so the server already knows when a host
  last checked in, to the second, with no separate agent and no third-party system to query.
  This is a better signal than an external agent's online state, because it is the *same* path
  the control link runs over: if it is healthy, the control link is healthy by definition.

- **R3.6** Run the simultaneity scan (§2.4) periodically to surface unregistered
  WSPRSonde-like transmitters, and present them as **candidates for a human to confirm**,
  never as automatic registry entries.
- **R3.7** Alerts go to the control operator and the network operator, by a channel the
  recipient chose (email at minimum; push and SMS desirable). Alerts must be de-duplicated
  and rate-limited — an alerting system that cries wolf gets muted, and a muted alerting
  system is worse than none.
- **R3.8** Retain the monitoring history. "How much of 2026 was this station actually on the
  air" is a question the science will ask, and it cannot be reconstructed later.
- **R3.9** Alerts carry a **severity** that says what the recipient is expected to do:
  *informational* (a band dropped out; look when convenient), *attention* (silent for longer
  than the threshold; investigate), and *immediate* (transmitting on a channel other than
  the assigned one, transmitting while inhibited, or any condition where the control
  operator's obligation is engaged). *Immediate* alerts must **escalate**: if no control
  operator has acknowledged within a documented interval, the alert goes to every designated
  control operator for that unit (R4.6) and then to the network operator. A unit whose whole
  control-operator pool is unreachable is the situation R4.6 exists to prevent.
- **R3.10** **Read the unit's own report.** A WS-8 answers a `CSV` command over its command
  line with a comma-delimited line carrying its serial number, software version, configured
  transmit frequency list and status, and it emits a report of the same kind after each frame
  (Paul Elliott, [issue #2](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/2)). Record
  it per unit and use it for the configured leg of R2.1, for firmware inventory, and for the
  dead-man state in R4.11. Reading the outbound stream is passive; issuing the command is
  not, so this traffic goes through the daemon of R4.11 like everything else.

### R4 — Positive control

**Rescoped on 2026-09-16.** The review committee judged that an automated monitor deciding when
to shut a station down was too complex to design and implement correctly in six months, and
retired it (§11). What remains is a good-faith control point in the control operator's pocket:

> The requirement will be that the majority of WSPRSonde configurations and the ability to turn
> on and off the transmitter be available to the control operator through the web app interface.

That is the whole of R4. A control operator should be able to claim, reasonably and truthfully,
that they are at the control point of their WSPRSonde at all times, with the means of control in
their pocket. See §5 for the regulatory reading behind it.

- **R4.1** Every unit has **one or more designated control operators**, each a licensed
  amateur, recorded with licence class and issuing administration.
- **R4.2** A control operator can **inhibit transmission immediately** from a phone, with no
  more than one deliberate action from opening the app, and no dependence on the site's own
  network path being healthy in the transmit direction. A native smartphone app and a
  mobile web application are both acceptable; what is required is that the control point
  fits in a pocket, works on the phone the operator already carries, and can deliver push
  alerts (R3.7, R3.9). The intent is that the control operator can truthfully say they are
  at the control point wherever they happen to be.
- **R4.3** **The interlock lives in the transmitter, and it is a per-unit option.**
  Transmission depends on the WSPRSonde's own dead-man, set to **1 minute** and never above 2,
  which bounds transmission after the last keep-alive at two to three minutes once the
  once-a-minute test is counted (§5.5, §97.213(b)). The host feeds the keep-alive **only while
  the server reports a control operator reachable**, and stops the moment that lapses; a
  keep-alive generated locally satisfies nothing, because the condition the rule cares about is
  a control-link malfunction. A unit with no dead-man cannot meet this requirement, which today
  means the BeaconBlaster at KD0EAG.

  **Enabling the keep-alive is a per-unit setting in the dashboard**, decided 2026-09-16. It is
  neither mandatory nor uniform; the control operator configures it for their own station. The
  reason it is per-unit rather than global is jurisdiction: Part 97 reaches US stations, and
  DP0GVN, VY0ERC, TI4JWC, VU24JD and ZD7GWM are licensed elsewhere (§5.6). A single global
  setting would either impose a US rule on stations it does not govern or drop it for stations
  it does.

  **What §97.213(b) requires of a US station is unchanged by the toggle.** A US station with the
  keep-alive disabled has no provision limiting transmission on control-link malfunction. The
  system does not enforce or warn on this: the committee decided on 2026-09-16 to leave it as a
  plain manual setting. Setting it correctly is the control operator's responsibility, in common
  with every other operating decision in this document.
- **R4.4** **Fail safe.** Loss of the control link, an expired token, an unreachable server,
  or a clock disagreement must all result in *not transmitting*. The failure mode of a bug in
  this subsystem must be a silent beacon, never an uncontrolled one.
- **R4.5** The control operator must be able to see **live confirmation of the current
  state**: transmitting or inhibited, the dead-man's armed or tripped state as the sonde
  itself reports it where that is readable, and when the last authorisation was issued and
  when it expires. "I am at the control point" should be a statement about an observable
  system.
- **R4.6** **Multiple simultaneous control operators, and the pool is the redundancy.** A unit
  may have several designated control operators (R4.1) assigned at once, and the station stays
  up while **any one of them is reachable**. The server tracks logged-in control devices and
  answers the host's poll (§5.5) with a single yes or no for the unit.

  **What counts as reachable is automatic, not a human acknowledgment.** Any designated control
  operator's phone or computer with a valid authenticated session answers in the background. No
  member of the pool performs any action in normal operation. The pool is redundancy of
  *reachability*: a rota requiring a human to respond every few minutes around the clock is not
  possible and is not what this asks for.

  This is the committee's answer of 2026-09-16 to how the control path gets redundancy without
  building any into version 1. Sites are unattended for months and Antarctic and Arctic sites
  change staff seasonally, so the pool must be editable and every change recorded in the audit
  log (R4.7).

  **Design note.** A backgrounded or sleeping phone must still count as reachable, or beacons
  will drop off the air nightly. That argues for a server-side session the server maintains on
  the operator's behalf while it remains valid, rather than requiring an app in the foreground.
- **R4.7** **Audit log**, append-only: every inhibit, enable, delegation, authorisation lapse
  and configuration change, with actor and timestamp. This is the record that answers a
  regulatory enquiry, and it must be exportable.
- **R4.8** A **network-wide emergency stop** for the network operator, for the case where a
  systematic problem — a bad firmware push, an interference complaint affecting many
  stations — needs every HamSCI sonde off the air at once.
- **R4.9** Jurisdiction-aware, per §5.6. Do not apply or assert FCC rules for non-US stations.
- **R4.10** Hold the material §97.213(d) requires posted at the station — station licence
  copy, licensee and control-operator name, address and telephone — so a host can print a
  correct label rather than assemble one. The system stores it; the human still has to put it
  on the wall.
- **R4.11** **The keep-alive daemon owns the command line.** Any inbound command re-arms the
  dead-man, so every other path to the unit's serial port has to run through the daemon, which
  withholds all traffic while it lacks authorisation. Interactive access for configuration and
  diagnosis must be brokered the same way, because a session left open is an authorisation
  nobody issued and one that outlives the operator's attention. Sessions must therefore expire.
  The system must read the dead-man's tripped state from the outbound per-frame report rather
  than by querying the unit, since a query is itself a keep-alive. Where a unit has the
  keep-alive enabled (R4.3), the system must **verify that the dead-man is actually armed** and
  treat a `0` interval as a fault at *immediate* severity (R3.9).
- **R4.12** **Configuration through the web app.** The majority of a WSPRSonde's configuration
  must be settable by its control operator through the web interface, alongside the transmitter
  on/off of R4.2. This is the committee's statement of what Phase 4 delivers, and it is the half
  of R4 that is not about compliance: the operator should not need a terminal, a serial cable or
  a site visit to change what their own station is doing.

  Configuration writes go through the daemon of R4.11 like all other command-line traffic, and
  any mode value written must use the firmware's own encoding rather than another system's
  (R1.3a). **Which fields are in "the majority" is for the student team to propose and the
  technical team (§3.1) to confirm**, against what the `CSV` report of R3.10 shows a WS-8
  actually exposes.

### R5 — Access control

- **R5.1** Roles per §3, assigned per unit and per site, not globally.
- **R5.2** A host who is not a licensed amateur can see status and report site changes but
  cannot hold control-operator authority (R3.1).
- **R5.3** **The system owns its own identity.** Accounts, authentication and session
  management belong to this application and depend on no third-party service. Decided
  2026-09-16, replacing Draft 0.9's list of external identity providers to weigh.

  Two reasons it came out this way. First, R2.7 requires coordinating units outside HamSCI, and
  an outside control operator should not need an account on somebody else's infrastructure in
  order to log in to a website. Second, the server is already the control point's counterparty
  (§5.5): it has to know who is logged in to answer the host's poll at all, so identity is not a
  thing that can be delegated elsewhere without delegating the control path with it.

  **Callsign self-assertion is not authentication** and must not be the basis for control
  authority. How a callsign is verified against a licence is a real question and is left to the
  team, with the technical team (§3.1) to confirm the approach.
- **R5.4** Multi-factor authentication required for any account that can enable transmission.
- **R5.5** Read-only public access to the consented subset (R1.6) without an account.

### R6 — Integrations

- **R6.1** WsprDaemon ClickHouse, read-only, for monitoring (§4.1). Bounded time windows,
  one request at a time, `wd10` by default — these are volunteer-run servers under live load.
- **R6.3** Gwyn's `wsprsonde` PostgreSQL table: import as the frequency-history seed, then
  take over maintenance or keep it synchronised. Gwyn has asked for a curator; this is the
  system that becomes one. The Grafana dashboard of §4.5 reads that table, so a divergence
  breaks a working scientific product rather than only a metadata record; whatever the
  system does with the table, the dashboard must keep resolving.
- **R6.4** Publish a stable machine-readable feed for `polar-psws` and other consumers
  (R1.8).
- **R6.5** Optional and low priority: WSPRNet directly. WsprDaemon already mirrors it and is
  more pleasant to query.

### R7 — Public presentation

- **R7.1** A map of the network — deployed, pending and retired, with status — at a
  hamsci.org URL, showing only consented records.
- **R7.2** A per-station page suitable for linking from the existing PSWS instrument pages.
- **R7.3** A public frequency-assignment table, so operators outside HamSCI can see what is
  in use before choosing a channel. Part 97 does not require this (§97.203(e), which Draft
  0.1 cited here, concerns the National Radio Quiet Zone), but it is how a shared 200 Hz
  window stays usable, and it is good manners regardless.

---

## 7. Non-functional requirements

- **N1 — Open source, in the HamSCI GitHub organisation.** Rob and Gary both argued for
  GitHub over the HamSCI web server, and "the fewer sites the better" (Rob, 2026-08-06).
- **N2 — The registry is a versioned text file**, with the application as a view over it
  (R4.1). Survivability matters more than elegance here: this data must outlive the web
  application, and a CSV in Git can be read in twenty years by anyone.
- **N3 — Monitoring must degrade gracefully.** If WsprDaemon is unreachable the system
  reports "unknown", never "silent". A monitoring system that manufactures faults during its
  own outages will be ignored.
- **N4 — The interlock is in the transmitter; the *authorisation* depends on the server, by
  design.** Draft 0.9 stated that the transmit interlock must not depend on the web application
  being up. The architecture settled on 2026-09-16 (§5.5) makes the host poll
  `wsprsonde.hamsci.org`, so for keep-alive-enabled units **server availability is transmit
  availability**, and this requirement is restated rather than carried forward unchanged.

  The trade was made knowingly and it fails in the safe direction: a server outage stops
  transmission rather than stranding it, and the dead-man re-arms by itself when the server
  returns, so an outage costs minutes of downtime and no site visit. The committee decided
  against building redundancy into version 1. Two consequences follow, and they are requirements
  rather than observations:

  1. **Server uptime is an operational requirement of this system**, not an assumption about it.
     It needs monitoring, and its own outages need alerting that does not run on it.
  2. **The failure of any component other than the server must not stop transmission.** The
     interlock stays in the transmitter, so a crash of the web front end, the database or the
     monitoring subsystem is survivable as long as the poll endpoint answers.
- **N5 — Privacy.** Host addresses, emails and phone numbers are collected for shipping and
  for §97.213(d). They must be access-controlled, never exported, and never published.
- **N6 — Modest operational burden.** This will be maintained by a small academic team with
  student turnover. Prefer boring, well-documented technology over anything requiring a
  specialist.
- **N7 — Documented thresholds.** Every threshold that turns data into a judgement — how many
  days silent is "silent", how many Hz is a mismatch — must be a named, documented constant,
  not a number buried in a query.
- **N8 — Attribution and licensing** for the data products, so downstream science can cite
  the network. NSF award numbers OPP-2332427, AGS-2432821–2432824 apply to the HamSCI-funded
  units.

---

## 8. Architecture sketch

Offered to make the discussion concrete, not because it is decided.

```
                       ┌──────────────────────────────┐
   registry (Git) ────▶│  WSPRSonde Management System │◀──── operators (web + phone)
   CSV/JSON, PR-based  │                              │
                       │  registry · coordination     │
   wd10 ClickHouse ───▶│  monitoring · control        │────▶ public map, hamsci.org
   (wspr.rx)           │                              │────▶ data products (polar-psws)
                       │                              │
                       └───────────────┬──────────────┘
                                       │  poll: "is a control operator reachable?"
                                       ▼
                       ┌──────────────────────────────┐
                       │  WSPRSonde host (Raspberry Pi)│
                       │  ┌────────────────────────┐  │
                       │  │ keep-alive daemon      │  │  feeds the sonde's dead-man
                       │  │  · polls the server    │  │  only while the server answers
                       │  │  · feeds WS dead-man   │  │  yes; the WS drops the
                       │  └───────────┬────────────┘  │  transmitters when the
                       │      serial  ▼               │  keep-alive stops
                       │  ┌────────────────────────┐  │  (R4.3, R4.4)
                       │  │ WSPRSonde: dead-man    │  │
                       │  └────────────────────────┘  │
                       └──────────────────────────────┘
```

Two properties are load-bearing:

1. **The arrow into the Pi is a pull, not a push.** The host asks whether a control operator
   is reachable; the server never has to reach in. That works behind NAT, needs no inbound
   firewall rule, no mobile app in the foreground, and means a server outage stops transmission
   rather than stranding it. The transmitters are stopped by the sonde's own dead-man, so the
   daemon's failure mode is the same as its silence.
2. **The registry is upstream of the application.** Changes arrive as commits — reviewable,
   attributable, revertible — and the web UI is a convenient way to author them.

---

## 9. Phasing

Each phase is independently useful, so the effort can stop or pause at any boundary without
leaving something half-built.

| Phase | Delivers | Roughly |
|---|---|---|
| **0 — done** | Reconciled station list, live location product, verified detection method (this repo) | complete 2026-08-13 |
| **1 — Registry** | Canonical versioned registry, import from all four current sources, public export, map | first |
| **2 — Monitoring** | Scheduled polling, status classification, offset verification, alerting, host-reachability cross-check | next |
| **3 — Coordination** | Assignment workflow with collision and §97.203(b) checking; public assignment table | with or after 2 |
| **4 — Positive control** | Keep-alive daemon on the Pi feeding the WS dead-man, the poll endpoint, operator phone interface with configuration and transmit on/off, audit log | last, and needs the most review |

Phase 4 deliberately comes last. It touches transmitters people are licensed for, it is the
part where a bug has consequences beyond a wrong number on a web page, and §5 should be
settled before anyone writes code for it.

**9.1 Delivery as a capstone project.** The plan (§1) is to hand this to a University of
Scranton Computer Science capstone team, which means roughly one academic year of part-time
effort by three to five students with faculty supervision and no prior amateur-radio
background. Three consequences:

- **Phases 1–3 are the capstone.** Registry, monitoring and coordination are conventional
  web-application work with clear acceptance tests (the registry round-trips the four
  current sources; the monitor reproduces the §2.2 table; the coordinator refuses the KH2R /
  DP0GVN collision). They fit the format.
- **Phase 4 is now deliverable work rather than a design exercise**, because the committee
  removed the hard part. Retiring the automated monitor (§11) leaves a control point: the
  keep-alive daemon, the poll endpoint, and an operator interface for configuration and
  transmit on/off. Deployment to licensed stations is still gated on a review by the control
  operators concerned. Students should not be the ones deciding when a transmitter someone
  else is licensed for goes on or off the air.
- **The requirements become final when the student team and the WSPRSonde team agree on
  them.** Decided by the editor on 2026-10-02:

  > "nothing is final until the actual student comes to an agreement with the WSPRSonde team."

  This draft is the scope-reduced baseline the team starts from, and reviewing it with the
  technical team (§3.1) is part of the capstone. The revision they agree on is the baseline
  they build against and are graded against. Anything raised after that agreement goes into a
  backlog for the team to weigh. The review round is happening now so that the starting draft
  is as sound as the reviewers can make it.

---

## 10. Open questions for reviewers

The review committee met on 2026-09-16 and settled most of what this section used to carry. Ten
of the thirteen questions in Draft 0.9 are closed, removed as out of scope, or folded into a
requirement; the change log says which went where. **Three remain, and each needs one named
person rather than a discussion.**

1. **Is §5's reading right?** The committee adopted the remote-control determination of §5.3 on
   2026-09-16: a WSPRSonde is under remote control under §97.109(c), because this system puts a
   control point in the operator's pocket. §97.109 and §97.213 were re-verified against the
   current eCFR the same day and the quoted text matches. What is still wanted is the judgement
   of someone who has argued these rules in practice: **has anyone had this conversation with
   the FCC or with ARRL**, and does the reading survive contact with someone who has?
   *(Paul WB6CXC, Rob AI6VN, Michael AC0G, Mark WA4KFZ — you have all run unattended beacons.)*
   This is the section to read adversarially.

2. **How much redundancy does the control path need, beyond the operator pool?** R4.6 gives
   redundancy of *people*: the station stays up while any designated control operator is
   reachable. It gives none against `wsprsonde.hamsci.org` itself, and the committee decided
   against building any into version 1 (N4). The open question is whether the licence holders
   accept that a server outage takes their keep-alive-enabled stations off the air for its
   duration. *(The control operators, for their own stations.)*

3. **What encoding does the WSPRSonde firmware use for transmit mode?** R1.3a requires the
   system to write the encoding each destination expects, and the firmware column of its table
   is blank. This became load-bearing when R4.12 put configuration in scope: the system cannot
   set a unit's mode without it. Three encodings are already known to be in play and two of them
   disagree, so guessing is not available. *(Paul Elliott WB6CXC.)*

---

## 11. Explicitly out of scope

Draft 0.95 extended this list considerably. Everything below was in an earlier draft or was
proposed and declined; the change log says when and why. **These are retired, not deferred: they
are not backlog items for the capstone team to pick up if time allows.**

**Removed by the review committee on 2026-09-16:**

- **Automated monitoring for the purpose of control shutdown.** A system that watches the spot
  record, decides a station is misbehaving and shuts it down. The committee judged it too
  complex for an undergraduate team to design and implement correctly in six months, and the
  hard part is not the plumbing but defining "misbehaving" well enough to act on automatically.
  Monitoring that *reports and alerts* stays (R3); monitoring that *acts on the transmitter*
  is gone. R4's control point is a human one.
- **How many WSPRSondes the world can support, and how assignments should be optimised.** These
  depend on how WSPR propagates and decodes, and the answers shape what science the received
  data can support, so they need careful consideration rather than a prototype's best guess.
  R2.2 specifies a simple stated rule instead, and invites a better one as student work.
  Technical Note 1 in this repository records the capacity analysis and is advisory; its
  proposed changes to R2.2, R2.3 and R2.4 are not adopted.
- **Explaining the spot archive's historical mode record.** Why `wsprdaemon.spots` changed its
  encoding of WSPR-2 at least three times between July 2024 and March 2026, and whether a second
  transmitter signs DP0GVN at Neumayer. Recording configuration correctly going forward is in
  scope (R1.3a, R1.4); reconstructing the past from somebody else's archive is not.
- **Identifying the unlisted transmitters.** DC7TO, N9VP and G0PKT remain unidentified, and
  W8GPS's 60 Hz channel has no coordinator assignment behind it. §2.4 keeps them as the evidence
  for running R3.6 on a schedule. Resolving them is not this project's work.
- **Resolving the two live channel conflicts.** KH2R and DP0GVN 1 Hz apart, and ZD7GWM and N4RVE
  co-channel on 100 Hz. §2.3 keeps both as evidence, because they are the case for building the
  system at all. They are operational decisions for the coordinator when the system is deployed,
  and R2.2's rule will flag the second one by itself.
- **Non-US regulatory requirements.** ISED, BNetzA, Costa Rican and Indian rules for unattended
  beacon operation. §5 is US-only and says so; R4.9 requires the system to decline to assert
  compliance it has not checked.
- **Third-party infrastructure as a dependency.** The system depends on our own server and
  software. Remote administration of host computers, however the PSWS team chooses to do it, is
  an operational matter this system does not address and does not require.

**Out of scope since earlier drafts:**

- PSWS receive instruments (HFRx, magnetometer, VLF). Confirmed 2026-09-16: the transmit side is
  the right boundary, and no extensibility work is to be done against a receiver use case nobody
  has specified.
- Science data processing and archival. This system publishes metadata about transmitters; it
  does not touch spot or noise data beyond reading it for monitoring.
- Replacing WsprDaemon or WSPRNet.
- WSPRSonde firmware, including the dead-man itself. The keep-alive daemon on the host computer
  is in scope (R4.3).
- Procurement, shipping and inventory finance, beyond the pipeline states in R1.7.

---

## Provenance

Added 2026-09-16, for Draft 0.95:

- **Review committee telecon, 2026-09-16** (Frissell, chairing). Eleven scope decisions,
  recorded verbatim with their analysis and supersessions in
  `notes/2026-09-16_telecon_scope_decision.md`. That file is authoritative for *why* a decision
  was made and what it retired; this document is authoritative for what the requirements now say.
- 47 CFR §97.109 and §97.213, re-verified against the **current eCFR on 2026-09-16** when the
  committee adopted the remote-control determination of §5.3:
  <https://www.ecfr.gov/current/title-47/chapter-I/subchapter-D/part-97/subpart-B/section-97.109>
  and
  <https://www.ecfr.gov/current/title-47/chapter-I/subchapter-D/part-97/subpart-C/section-97.213>.
  Quoted passages match.

Sources consulted 2026-08-13:

- Email thread *"WSPRSonde Shipping List #1"* and *"Currently deployed WSPRSondes?"*,
  2026-07-31 to 2026-08-06 (Frissell, Mikitin, Elliott, Robinett, Griffiths), archived at
  `reference/20260813_wsprsonde_location_email.olm`
- `G3ZIL_WsprSonde_Metadata_V1-1.xlsx`, Griffiths & Elliott, revised 2025-05-11
- `wsprsonde` table, `wd10.wsprdaemon.org` PostgreSQL database `tutorial`, 139 rows
- `wspr.rx`, WsprDaemon ClickHouse endpoint — live queries, 2026-08-13
- 47 CFR §§97.3, 97.109, 97.203, 97.213, via Cornell LII, read 2026-08-13; re-verified
  against the eCFR point-in-time version of 2026-08-29 on 2026-09-02, and §§97.109, 97.203,
  97.213 re-read from Cornell LII on 2026-09-03
- <https://hamsci.org/wsprsonde-psws-transmitter>, <https://turnislandsystems.com>
- `polar-psws/docs/wsprdaemon_extended_spots_access.md` (Frissell, 2026-07-28)

Added 2026-09-03, for Drafts 0.3 and 0.4:

- Reviewer comments, GitHub issues
  [#1](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/1),
  [#2](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/2),
  [#3](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/3) and
  [#4](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/4) (Paul Elliott WB6CXC),
  including his answers of 2026-09-03 on the WS-8 serial number and `CSV` command (#2) and on
  the dead-man's behaviour, range and hardware coverage (#3)
- `wspr.rx`, WsprDaemon ClickHouse endpoint: live queries for N4RVE, 2026-09-03
- WSPR message types and compound-callsign forms, <https://dxplorer.net/wspr/msgtypes.html>
- ARRL, *Link & Remote Control*, <http://www.arrl.org/link-remote-control>

Added 2026-09-10, for Draft 0.6:

- Reviewer comments, GitHub issues
  [#5](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/5),
  [#6](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/6),
  [#7](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/7),
  [#8](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/8),
  [#9](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/9) and
  [#10](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/10) (Gwyn Griffiths G3ZIL)
- `wspr.rx`, WsprDaemon ClickHouse endpoint: live queries 2026-09-10 for per-band offsets and
  per-callsign `code` values over 3 and 14 day windows, and for the first appearance of W8GPS
- WSPRSonde Grafana dashboard, `wd10.wsprdaemon.org:3000/d/dfagb9m7nn5s0f/wsprsonde-ch`, and
  the prototype co-channel dashboard, `wd2.wsprdaemon.org:3000/d/dopAJDLIk/a9e4d43`

Added 2026-09-11, for Draft 0.7:

- Gwyn Griffiths' answers of 2026-09-11 in issues
  [#6](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/6) (the `wsprsonde` table's mode
  encoding; W8GPS is operated by N8UR) and
  [#8](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/8) (the co-channel dashboard)
- WSPR/FST4W mode and code mapping table, <https://wspr.live/>, read 2026-09-11

Added 2026-09-11, for Draft 0.8:

- Gwyn Griffiths' comment of 2026-09-11 16:47 UTC in issue
  [#6](https://github.com/HamSCI/wsprsonde.hamsci.org/issues/6): `wsprdaemon.spots` reads
  `code = 2` for TI4JWC, and his proposal to renumber the `wsprsonde` table's `code` to match
- `wsprdaemon.spots` on `wd10`, `wd1` and `wd2`, and `wspr.rx` on `db1.wspr.live`: live
  queries 2026-09-11 for per-callsign `code` over the three days to 2026-09-11 and month by
  month from July 2024 for WW0WWV, TI4JWC, DP0GVN, ZD7GWM, KD0EAG and WB6CXC

Drafted with AI assistance; see `ai/ai_usage_log.md`. All rule citations, measurements and
attributions require human verification before this document is acted upon.

---

## Change log

**Draft 0.96, 2026-10-02.** One decision by the editor, recorded in
`notes/2026-10-02_student_overview_and_requirements_finality.md`. Changes from Draft 0.95:

- **The Draft 1.0 freeze is retired.** Draft 0.95's §9.1 froze the requirements at Draft 1.0
  when the capstone proposal was submitted, and sent anything later to a backlog. The
  requirements now become final when the student team and the WSPRSonde team agree on them, and
  that review is part of the capstone. §1's "Who will build it" and §9.1 are rewritten to match.
  No requirement changed.

**Draft 0.95, 2026-09-16.** A scope reduction decided by the review committee on a telecon, and
the largest revision this document has had. Eleven decisions, recorded verbatim in
`notes/2026-09-16_telecon_scope_decision.md`. Changes from Draft 0.9:

**Scope removed.** Each of these is **retired, not deferred**, and §11 now says so:

- **Automated monitoring for control shutdown is gone.** "Too complex for the initial version of
  this project." Monitoring that reports and alerts stays (R3); monitoring that acts on the
  transmitter is retired. This is what made Phase 4 deliverable rather than a design exercise.
- **Frequency-assignment optimisation and the channel-capacity question are gone**, because they
  depend on how WSPR propagates and decodes and will shape what science the data supports. **R2.2
  is rewritten as a simple stated rule**: prefer an unassigned channel; otherwise the least-used
  one; break ties by great-circle separation. It records explicitly that geographic separation is
  a *proxy* for non-interference and not the same thing on HF, and invites a better algorithm as
  student work. Technical Note 1 becomes advisory.
- **Historical mode archaeology is gone**, and **R1.4 is rewritten**: mode history comes from the
  unit record, seeded from Gwyn Griffiths' table, rather than being re-derived from spots.
- **Q10.7 and Q10.8 leave §10** as deployment-time and identification matters. §2.3 and §2.4 keep
  both as evidence, since they are the case for building the system.
- **Non-US regulatory research is gone.** §5 is US-only and says so.

**Scope changed.**

- **R4 is rescoped to a control point**, in the committee's words: the majority of WSPRSonde
  configurations and transmitter on/off available to the control operator through the web app.
  **New R4.12** carries the configuration half.
- **§5.3 records the committee's remote-control determination**, adopted on the strength of that
  interface: the operator has the facility to control the transmitter from a phone or computer
  and is therefore at a control point. §97.109 and §97.213 were **re-verified against the current
  eCFR on 2026-09-16** and the quoted text matches.
- **R4.3: the keep-alive becomes a per-unit toggle**, because Part 97 reaches US stations and
  five units are licensed elsewhere. The requirement records that §97.213(b) is unchanged by the
  toggle and that the system does not enforce or warn on it, which was proposed and declined.
- **R4.6 becomes a pool of simultaneous control operators**, replacing the on-duty rota. Any one
  member's authenticated session keeps the station up, automatically, with no human action in
  normal operation.
- **§5.5 and §8 carry the settled architecture**: the server tracks logged-in control devices and
  the host Pi polls it, feeding the dead-man only while the answer is yes. The Pi pulls and the
  server never reaches in, so a host that loses its network path goes quiet by itself.
- **N4 is restated rather than carried forward.** Draft 0.9 said the interlock must not depend on
  the web application being up; the settled architecture makes server availability into transmit
  availability for enabled units. The trade fails safe and was made knowingly, and server uptime
  becomes an operational requirement with two consequences stated as requirements.
- **R2.4 survives as a view rather than a gate**, implemented as Gwyn's `wd2` dashboard with the
  frequency populated from the registry.
- **R1.3a is new**: store mode by name and translate at every boundary, on writes as well as
  reads, now that the system configures units. Its table carries three encodings, two of which
  disagree on WSPR and agree on FST4W.
- **R3.5 is rebuilt on our own poll data**, which is a better signal than an external agent's
  state because it is the same path the control link runs over.
- **R5.3: the system owns its own identity.** Draft 0.9 listed external identity providers to
  weigh; a trade study was set up on this call and then retired within the hour when the
  committee removed third-party infrastructure from scope entirely.
- **§3.1 is new**: the technical team the student developers work with, routed by subject, with
  one email address for design questions. This replaces the earlier intent that the PI alone act
  as customer.
- **§4.1 was removed and §4.2 to §4.6 renumbered to §4.1 to §4.5.** Cross-references in the body
  were updated; **change-log entries below keep the numbers they were written with**, because
  they describe the document as it stood at the time and editing them would falsify its history.
- **Q10.5 closed**: a WS-8 carries a host-readable serial number, so R1.1 keys on the hardware's
  own identifier.
- **§10 falls from thirteen questions to three**, each needing one named person: whether §5's
  reading survives someone who has argued these rules, whether the licence holders accept a
  server outage taking their stations off the air, and what encoding the WSPRSonde firmware uses
  for transmit mode.


**Draft 0.9, 2026-09-14.** One correction from Gwyn Griffiths about which table a frequency
measurement should come from, and what it changes. Changes from Draft 0.8:

- **§2.2's explanation of KH2R's leftover hertz was wrong and is rewritten** (issue #8). Draft
  0.8 blamed "the resolution limit of a crowd-sourced median". The limit belongs to the table:
  `wspr.rx` stores whole hertz, so its median is a whole number however many receivers report.
  `wsprdaemon.spots.frequency_mhz` resolves 0.1 Hz, and re-measured there KH2R reads **34.9 to
  35.2 Hz on all eight bands** over 102,000 reports. The assigned-against-measured disagreement
  is real and now carries a number that can be argued with.
- **TI4JWC was not wandering** (same measurement). Draft 0.8 reported it reading 16, 15 and then
  16 Hz on successive days. At 0.1 Hz it holds 15.0 to 15.3 Hz across seven bands; the wander was
  `wspr.rx`'s whole-hertz median stepping across a boundary as the receiving population changed.
- **§2.3's collision is tighter than the whole-hertz figures showed.** ZD7GWM and N4RVE sit
  within **0.4 Hz on all five common bands**, and the 24 MHz pair that read one hertz apart is
  0.7 Hz apart. That is well below the tone spacing of either mode, so the signals share a slice
  of the sub-band and not merely the 200 Hz window.
- **New R3.3a and R3.3b.** R3.3a requires the offset to come from
  `wsprdaemon.spots.frequency_mhz`, with `wspr.rx` as the fallback where a station is heard by
  too few WsprDaemon sites, and requires recording which table each measurement came from. R3.3b
  forbids `wsprdaemon.spots.frequency`, the integer column: measured over 582,198 spots on
  14 MHz, it is the **floor** of `frequency_mhz` rather than its rounding, averaging 0.43 Hz low,
  which is consistent enough to pass for a calibration offset.
- **§4.6** records that the `wd2` co-channel dashboard has now been run against the §2.3
  collision, with W1XP as the receiver on 14 MHz at 1 Hz bandwidth, and checked against the
  underlying rows (issue #8).
- **Issue #6 is settled.** Gwyn has changed the `wsprsonde` table's `code` to 2 for WSPR-2, so it
  matches `wsprdaemon.spots`. The three questions Draft 0.8 raised from the month-by-month read
  are answered as far as he can answer them: W0DAS and AI6VN are the people who would know why
  `wsprdaemon.spots` changed encoding mid-archive, his table already carries start and end dates
  for TI4JWC's mode change, and he has no first-hand knowledge of a second transmitter at DP0GVN.
  Q10.13 carries the two that remain open.
- **New R3.3c: qualify a band on distinct receivers rather than on a count of reports.** This
  came out of making the switch. `wsprdaemon.spots` reproduces the VY0ERC false-confidence
  failure of Draft 0.7 by a different route, because one nearby WsprDaemon site reports every
  slot and clears a report floor alone. §2.2's VY0ERC paragraph now records both versions of the
  failure, and the station reads *incoherent* with a 62.4 Hz spread across the three bands that
  survive the receiver floor.
- **`products/` is now built from `wsprdaemon.spots.frequency_mhz`**, with `wspr.rx` as the R3.3a
  fallback, and gains an **`offset_source`** column naming the table per station. Every measured
  offset in the product moved to one decimal place; none of the verdicts changed except VY0ERC's,
  from *not measurable* to *incoherent*.
- `src/wsprsonde/wsprdaemon.py` gains `observed_offsets_subhz`, `OFFSET_MIN_RECEIVERS`,
  `BAND_METRES` and `BAND_BASE_HZ_BY_METRES`, and a module warning about the two tables'
  frequency columns and their two different band keyings. `build_locations.py` gains
  `measure_offsets`, which runs the sub-hertz query and falls back for thin stations.
- **The channel-capacity note is reconciled** (§7 and open question 5): it argued that a 6 Hz
  grid with a 0.1 Hz guard band left no margin against a one-hertz measurement floor. The floor
  is 0.1 Hz. The case for a wider step now rests on transmitter drift and Doppler, which nobody
  has measured for the WS-8.

**Draft 0.8, 2026-09-11.** Gwyn Griffiths' third answer in issue #6, which corrects this
document a second time, and what re-measuring on his finding turned up. Changes from Draft 0.7:

- **§2.2 and R1.3: `wsprdaemon.spots` carries WsprDaemon's encoding, so WSPR-2 reads `2`
  there** (issue #6). Drafts 0.6 and 0.7 said `1`, which was the `wspr.rx` value carried over
  without being measured. Gwyn's query showed `2`, and it is `2` on all three mirrors. The §2.2
  measurement table now carries both tables' numbers side by side, and the mapping table is
  extended to the six modes and the pre-2023 column that R1.4's limit rests on.
- **§2.2 and R1.4: measured mode comes from `wspr.rx`, and from `wsprdaemon.spots` only from
  March 2026.** Reading the two tables back to July 2024 for the known sondes showed `wspr.rx`
  uniform and `wsprdaemon.spots` switching encoding at least three times (WW0WWV: `1`, `2`, `1`,
  `2`). The cause is open with Gwyn and Rob.
- **§2.2 and R1.4: TI4JWC changed from FST4W to WSPR in July 2026.** Draft 0.6 had recorded
  this as a registry correction. The G3ZIL metadata (FST4W) and Gwyn's issue #6 list (WSPR) were
  each right when written, and `data/wsprsonde_stations.csv` now records both intervals in the
  TI4JWC row.
- `src/wsprsonde/wsprdaemon.py`: `MODE_BY_CODE` is now documented as `wspr.rx` only,
  `MODE_BY_WD_MODE` as covering `wsprdaemon.spots` `code` as well, and
  `WD_SPOTS_CODE_STABLE_DATE = "2026-03-01"` records the boundary. No query in the prototype
  reads `code`, so the product is unaffected.

**Draft 0.7, 2026-09-11.** Gwyn Griffiths' answers to the questions Draft 0.6 put back to him,
and a correction those answers forced. Changes from Draft 0.6:

- **§2.2's mode and code paragraph was wrong and is rewritten** (issue #6). Draft 0.6 said Gwyn
  records WSPR as `2` in the `wsprsonde` table's **`code`** column. He records it as `2` in the
  **`mode`** column; `code` follows the `wspr.rx` convention. WsprDaemon publishes the full
  mapping at <https://wspr.live/> and it is now quoted as a table. The two encodings **agree on
  FST4W and disagree on WSPR**, so a system that confuses them looks half correct, and that is
  the reason R1.3 asks for both numbers rather than one.
- **A historical limit, new to the document** (same source): before 2023-01-16, `code` reported
  WSPR-2 and FST4W-120 alike as `1`. Mode history earlier than that cannot come from the spot
  archive, which constrains R1.4 and argues for importing Gwyn's history rather than re-deriving
  it.
- `data/wsprsonde_stations.csv` now carries `mode_code_wsprrx` and `mode_code_wd` in place of the
  single `mode_code` column Draft 0.6 added, so the disagreement is visible in the data.
- **§4.6 gains the prototype co-channel dashboard on `wd2`** (issue #8), which plots a wanted
  transmitter against everything else within a chosen bandwidth of it. That is R2.3 and R2.4's
  check, already built; **R2.4 now says adopt it and point it at the registry** rather than build
  another. The §2.3 collision is exactly what it would have shown.
- **Q10.7** records W8GPS as N8UR's, at a site that is not his home address, which narrows the
  open question to its uncoordinated 60 Hz channel.
- **A prototype bug fixed, and it is the one R3.3 was written against.** Rebuilding the product
  on 2026-09-10 reported VY0ERC as transmitting 100 Hz from its assignment, on the strength of a
  single band that cleared the twenty-report floor while seven others did not. One band has a
  spread of 0 Hz by construction, so the incoherence test could not fire. `stations.py` gains
  `OFFSET_MIN_BANDS = 3`, the verdict *not measurable*, and a product that withholds the number
  rather than publishing it. §2.2 records the incident, because a monitoring system's worst
  failure is confident invention rather than silence.

**Draft 0.6, 2026-09-10.** Gwyn Griffiths' review of Draft 0.4, issues #5 to #10, and the
measurements it prompted. Changes from Draft 0.5:

- **§1 corrected** (issue #5): a WSPRSonde transmits WSPR **or** FST4W, not both.
- **§2.2 gains mode and code columns** (issues #6 and #9) and was re-measured on 2026-09-10.
  The code number is a property of the source rather than of the mode: WSPR-2 reads `1` in
  `wspr.rx` and `wsprdaemon.spots`, `2` in the `wsprsonde` table, and the neighbouring `mode`
  column numbers it differently again, so R1.3 stores the mode by name and the code per
  source. `data/wsprsonde_stations.csv` gains a `mode_code` column, and TI4JWC and DP0GVN
  were corrected from FST4W to WSPR.
- **§2.2 KH2R corrected to 35 Hz** (issue #10). Gwyn's ground-wave measurement at W2NAF-2 and
  the spot record agree; the coordinator's list assigns 36 Hz, so the row now shows the
  disagreement instead of hiding it.
- **§2.3 rewritten** (issue #7): ZD7GWM and N4RVE are both transmitting on 100 Hz across six
  common bands. That is a live co-channel collision between a HamSCI unit and a private one,
  and the first real case for R2.7.
- **R2.2 gains a per-band override** (issue #7). ZD7GWM's 0 Hz on 28 MHz against 100 Hz
  elsewhere is a deliberate configuration, and this repository's one-offset-per-unit model
  reports it as an incoherent unit.
- **§2.4 and Q10.7** (issues #6 and #7): ZD7GWM is confirmed as a private WSPRSonde on
  St Helena. W8GPS came on the air on 2026-08-21, after the scan that produced the candidate
  list, which is the argument for running R3.6 on a schedule. Both are now in
  `data/wsprsonde_stations.csv`.
- **Added §4.6** (issue #8): Gwyn's WSPRSonde Grafana dashboard on `wd10`, which plots
  Doppler shift from the known transmit frequency. R6.3 now requires that the dashboard keep
  resolving through whatever the new system does to the table underneath it.
- **R1.3, R1.4 and R2.1** carry transmit mode and its code, with mode interval-valued.
- **Q10.8** now covers both channel conflicts.

**Draft 0.5, 2026-09-03.** Two corrections from the PI, and the capstone proposal this document
was written to support. Changes from Draft 0.4:

- **§2.5 corrected.** Draft 0.4 said the two polar sites were "the scientific justification for
  the McMurdo, South Pole and Palmer deployments," which read as planned WSPRSonde deployments.
  No new polar WSPRSonde deployments are currently planned. DP0GVN and VY0ERC are the whole of
  the polar transmit capability, which raises rather than lowers the value of monitoring them.
- **§5.6 corrected** for the same reason: the jurisdiction requirement now rests on the four
  administrations the network already spans.
- The capstone project description is now written, at
  [docs/project_description.md](project_description.md). It draws its evidence from §2, its
  requirement table from §6, and its phasing from §9.1, and it is the document students and the
  course instructor will read. This document stays the reference the requirements are cited
  from.

**Draft 0.4, 2026-09-03.** Paul Elliott's answers to the questions Draft 0.3 put back to him.
Changes from Draft 0.3:

- **§5.5 and R4.3 now carry measured hardware behaviour** (issue #3). The WS-8 dead-man stops
  transmission immediately when it fires, re-arms by itself when inbound command-line traffic
  resumes, and accepts 1 to 12,000 minutes with the condition tested once a minute. The
  setting is therefore **1 minute**, 2 being the ceiling that still fits §97.213(b) once the
  test interval is counted, and the 69-second branch of Draft 0.3 is gone. The BeaconBlaster
  has no dead-man and cannot be brought into compliance in software, which makes the KD0EAG
  replacement a compliance matter (§2.2).
- **Added R4.11** (issue #3): the keep-alive daemon owns the command line. Any inbound command
  re-arms the dead-man, so an open MeshCentral terminal is an authorisation nobody issued;
  interactive access must be brokered and time-limited, a `0` interval is an *immediate* fault,
  and the tripped state is read from the outbound per-frame report rather than by a query,
  since a query is itself a keep-alive. §4.1 carries the same warning.
- **Added R3.10 and amended R2.1 and R2.5** (issue #2): the WS-8's `CSV` command returns its
  serial number, software version, configured frequency list and status. Frequency
  coordination therefore has three legs to compare, assigned against configured against
  measured, where Draft 0.3 had two. KD0EAG would have been visible on the day of assignment.
- **R1.1 and R1.3** (issue #2): the unit key is the WS-8's 24-bit serial number, with the
  enclosure marking recorded separately and never keyed on. The record gains serial number,
  enclosure marking and firmware version. The model list drops `WS-6`, which the manufacturer
  says does not exist; `data/wsprsonde_stations.csv` had KD0EAG recorded under it and now
  reads `BB-6`, with the provenance noted.
- **Q10.2** narrows again: automatic re-arming means an outage costs downtime rather than a
  truck roll, leaving the question of how much redundancy the keep-alive path needs.

**Draft 0.3, 2026-09-03.** First round of reviewer comments, all from Paul Elliott WB6CXC.
Changes from Draft 0.2:

- **§2.2 corrected** (issue #1): N4RVE was off the air for nine days from a power supply
  failure, 2026-08-09 to 2026-08-18, and returned on its assigned 100 Hz channel on all
  eight bands. Its table row now reads `ok`. Measurements re-run against `wspr.rx` on
  2026-09-03. The stale "on-air offset is still ~10 Hz" note was removed from
  `data/wsprsonde_stations.csv` in the same pass.
- **§2.4 and Q10.5 closed** (issue #2): the hardware does not support extended callsigns and
  the WSPR message format cannot encode a two-letter suffix, so the `-WS` proposal is
  retired. Identification rests on R3.6 and R1.1.
- **§5.5 and R4.3 rewritten** (issue #3): the interlock is now the WSPRSonde's own dead-man
  rather than a per-slot authorisation feature the hardware does not have. Added the
  condition that decides whether it satisfies §97.213(b), namely that the keep-alive must be
  contingent on contact with the control point rather than generated locally, and recorded
  the open hardware questions. §4.1 gains MeshCentral's role as keep-alive transport with its
  availability cost; the §8 sketch and R4.5 follow the same change.
- **Q10.1 and Q10.2 updated** (issues #3, #4): the three-minute limit is recorded as
  §97.213(b), telecommand, rather than a rule of automatic control, which is confined to the
  §97.203(d) segments. Q10.2's remaining content is the availability question.

**Draft 0.2, 2026-09-02.** Circulated to the review list. Changes from Draft 0.1:

- Added *How to comment* (GitHub issues) to the preamble, and *Who will build it* to §1.
- §5: re-verified all quoted rule text against the eCFR. Added the framing paragraph to §5.1
  (a WSPRSonde remains a beacon; the claim concerns the type of control). Added §97.203(e)
  (National Radio Quiet Zone) to §5.2. Added the "another telecommunication service is
  considered wireline" sentence of §97.213(a) to §5.4.
- **Corrected R7.3**, which cited §97.203(e) for something the rule does not say.
- Added R3.9 (alert severity and escalation). Expanded R4.2 (phone app) and R4.6 (pool of
  control operators with an on-duty designation).
- Added §9.1 (delivery as a capstone project) and Q11–Q12.
- Review list extended: KA9Q, KC3EEY, KD8OXT, KV0S. Majid Mokhtari removed.

**Draft 0.1, 2026-08-13.** First draft.
