# WSPRSonde Management System — Requirements for Discussion

**Status:** Draft 0.2, for collaborator review (change log at the end)
**Date:** 2026-09-02 (Draft 0.1 was 2026-08-13)
**Editor:** Nathaniel A. Frissell, W2NAF (University of Scranton)
**Review list:** Paul Elliott WB6CXC · Rob Robinett AI6VN · Gwyn Griffiths G3ZIL ·
Gary Mikitin AF8A · Michael Hauan AC0G · Hyomin Kim (NJIT) · Gerard Piccini KD2ZHK ·
Majid Mokhtari · David Witten KD0EAG · Phil Karn KA9Q ·
Jonathan D. Rizzo KC3EEY (University of Scranton) · Kristina Collins KD8OXT ·
Dave Larsen KV0S

> **This is a request for comment, not a specification.** Requirements are numbered so
> you can say "R4.2 is wrong because…" rather than re-prosing the whole thing.
> Section 10 lists the questions I most want answered. Section 5 concerns FCC rules and
> is the section I am least confident in — please read it adversarially.
>
> **How to comment.** File an issue at
> <https://github.com/HamSCI/wsprsonde.hamsci.org/issues>, one per point, using the
> *Requirement comment* or *Answer to an open question* template. Issues are how I track
> what has been raised and what has been resolved. Email to the editor works too, but
> anything that changes the document will be turned into an issue so the reasoning is on
> the record. Comments are being collected against **Draft 0.2**; when a requirement is
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
8-band, GPS-disciplined, ~1 W per band, transmitting WSPR and FST4W continuously — as the
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
| **D** | **Positive control** | Give each control operator a means, available to them at all times, of confirming control of and if necessary shutting down their station — and give the transmitter a watchdog that stops it if that link is lost. |

**In scope:** the transmit side of the PSWS network — WSPRSondes and BeaconBlasters,
whether HamSCI-funded or privately owned, worldwide.

**Not in scope:** PSWS receivers (HFRx, magnetometers, VLF), science data processing, and
the WsprDaemon infrastructure itself. Those are separate systems this one reads from.

**Who will build it.** The intent is to offer this system to a team of Computer Science
students at the University of Scranton as a senior capstone project, with the editor as
faculty sponsor and the people on the review list as the customers. That intent shapes the
document: the students need a stable, numbered set of requirements to work from, with the
reasoning attached so they can make design decisions without re-deriving the domain. This
review round exists to settle that baseline before the capstone proposal is written. See §9
for what it implies about phasing.

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
Measuring the on-air offset of every listed callsign against its assignment:

| Callsign | Assigned | Measured | Verdict |
|---|---|---|---|
| WB6CXC (Occidental) | 135 Hz | 135 Hz | ok |
| KH2R | 36 Hz | 36 Hz | ok |
| DP0GVN | 37 Hz | 37 Hz | ok |
| WW0WWV | 50 Hz | 50 Hz | ok |
| TI4JWC | 15 Hz | 16 Hz | ok |
| **KD0EAG** | **80 Hz** | **131 Hz** | **mismatch** |
| **VY0ERC** | 150 Hz | bands disagree by 115 Hz | **not measurable** |
| **N4RVE** | 100 Hz | — | **off the air since 2026-08-09** |

KD0EAG is explicable — the replacement WS-8 configured at 80 Hz has not been deployed and
the old BeaconBlaster is still running — but nothing in the current arrangement would have
surfaced it. N4RVE went silent four days before anyone noticed. VY0ERC is heard by so few
receivers that its channel cannot be verified at all from the spot record, which is itself
a finding worth having.

**2.3 A collision is already on the books.** Paul flagged in the 2026-08-06 thread that
KH2R and DP0GVN sit 1 Hz apart and one should be reassigned. There is no tool that would
have caught that at assignment time, and no tool that would catch the next one.

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

This matters beyond bookkeeping. Any study that wants to use the WSPRSonde network as a
controlled transmitter array must be able to say which spots came from a controlled
transmitter, and right now that is only possible by consulting a spreadsheet.

**2.5 Nobody is watching the transmitters.** DP0GVN and VY0ERC are the two existing polar
PSWS sites and the scientific justification for the McMurdo, South Pole and Palmer
deployments. VY0ERC was heard by 70 receivers over 30 days, against 2,319 for KH2R. Whether
that is propagation, an antenna problem or a sick transmitter, no one is being told.

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

---

## 4. What already exists

Build on these rather than replacing them.

**4.1 MeshCentral (`meshcentral.hamsci.org`).** Every HamSCI WSPRSonde ships with a
Raspberry Pi running a MeshCentral agent that phones home. This already provides remote
terminal and desktop access, device grouping, per-user device delegation, agent
online/offline state, and an event log. Nathaniel's 2026-08-06 deployment plan has Gerard
using it for final configuration and granting each host access to their own Pi.

**Use it for:** device inventory, reachability, remote configuration, and delegated access.

**Do not use it as the transmit interlock.** MeshCentral tells you the *computer* is
reachable. It says nothing about whether the *transmitter* is keying, on what frequency, or
whether a control operator is present. Section 5 needs a mechanism that fails safe when the
network is down, which is precisely when MeshCentral is unavailable.

**4.2 The WsprDaemon archive.** Reachable over the ClickHouse HTTP interface at
`http://wd10.wsprdaemon.org/` with no credentials (mirrors on `wd1`, `wd2`). `wspr.rx`
carries the full WSPRNet record and is the right table for liveness, because a sonde is
heard by whoever happens to be listening. `wsprdaemon.spots` carries calibrated noise from
~5% of receivers and is the right table for science, not for monitoring.

> Note for implementers: `wd1.wsprdaemon.org` also exposes PostgreSQL on 5432 with a `spots`
> hypertable, and it is the obvious thing to poll. As of 2026-08-13 that table is unusable —
> any query fails with `could not open file "pg_tblspc/18143/…"` because a TimescaleDB
> chunk's tablespace is missing. Use the ClickHouse endpoint.

**4.3 Gwyn's `wsprsonde` table** on `wd10.wsprdaemon.org` (PostgreSQL, database `tutorial`).
139 rows of `(tx_call, tx_grid, mode, freq, clock, band, time_start, time_end, code)` at
1 mHz resolution, with validity intervals. **This is the right schema for the frequency
history** and the new system should adopt its shape rather than invent one, then take over
maintaining it.

**4.4 This repository.** `data/wsprsonde_stations.csv` is a first reconciliation of the four
sources above; `src/wsprsonde/` builds a location product from it plus live queries. It is
deliberately a flat file with no runtime dependencies — it is a stopgap and a specification
by example, not the proposed system.

**4.5 hamsci.org.** Gary Mikitin can host a landing page. Rob Robinett and Gary both
favoured GitHub over the HamSCI web server for the underlying files, consistent with the
direction the PSWS instrument pages are already taking. **R4.1** The registry's canonical
form should be a versioned text file in a Git repository, with the web application as a
view and an editor over it — not a database whose history lives only in backups.

---

## 5. Regulatory basis for positive control

> **Not legal advice.** Rule text below was read from the Cornell LII copy of 47 CFR Part 97
> on 2026-08-13 and re-verified against the eCFR (point-in-time version of 2026-08-29) on
> 2026-09-02; the quoted passages match the eCFR text. It should still be reviewed by
> someone who has actually argued these rules — ARRL regulatory counsel would be the right
> destination.

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
whole feature, and it cuts both ways:

- It is **not** satisfied by a web dashboard the operator can visit. A dashboard is a way to
  look; the rule demands that transmission *stop* when the link fails.
- It **is** naturally satisfied by an interlock at the transmitter, because a WSPR
  transmission lasts about 110.6 seconds — under three minutes. If the sonde requires a
  fresh, short-lived authorisation before each transmission slot and refuses to key without
  one, then a control-link failure stops transmission within one slot **by construction**,
  with no timer to get wrong.

That is the mechanism this document proposes (R4). It also happens to give the control
operator the thing they actually want: a single control they can hit from a phone that
demonstrably stops the transmitter.

**5.6 Jurisdiction.** Part 97 governs US stations only. The network already includes
DP0GVN (German licence, Antarctica), VY0ERC (Canada, ISED), TI4JWC (Costa Rica) and VU24JD
(India), and the polar expansion adds more. **R4.9** The control-operator module must be
jurisdiction-aware: record each station's licensing administration, apply the US interlock
rules to US stations, and do not assert compliance with rules that have not been checked
for the others. Where a non-US administration's rules are unknown, the system should say so
rather than defaulting to the FCC's.

---

## 6. Functional requirements

### R1 — Registry

- **R1.1** One record per **unit** (a physical transmitter), keyed by a stable identifier
  independent of callsign. Callsigns change: the Friday Harbor station is recorded as
  WB6CXC in Gwyn's metadata and transmits as N4RVE today.
- **R1.2** Units group into **sites**. A site is one location and one dot on a map; a site
  may hold more than one unit (WB6CXC at CM88mj).
- **R1.3** Each unit record must carry, at minimum: identifier, site, current callsign and
  callsign history, licensee, control operator(s), host, Maidenhead locator with its
  precision, hardware model (BB-6 / WS-6 / WS-8 / successor), GPSDO type, antenna, modes,
  in-service and out-of-service dates, funding source, and free-text notes.
- **R1.4** All history is **interval-valued**, following §4.3's schema. "Where was DP0GVN in
  March 2025" must be answerable, because a study spanning a reconfiguration otherwise
  silently mixes two different stations.
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

- **R2.1** Record, per unit, the **assigned** channel offset (Hz above the bottom of the
  200 Hz WSPR/FST4W window) and the **measured** per-band transmit frequency to 1 mHz,
  following the existing `wsprsonde` table's resolution.
- **R2.2** Support the current allocation scheme: one offset applied to all of a unit's
  bands, allocated on a 10 Hz grid from 1450 Hz upward, with the pre-existing off-sequence
  assignments (TI4JWC 1415, KH2R 1436, DP0GVN 1437, WB6CXC 1535) recorded as exceptions
  rather than errors.
- **R2.3** **Refuse or warn on a colliding assignment** at allocation time, with a
  configurable guard band. Flag existing collisions: KH2R and DP0GVN are 1 Hz apart.
- **R2.4** Check assignments against **non-sonde WSPR activity** in the same window, not
  only against other sondes. The WSPR window is shared with everyone.
- **R2.5** Continuously compare measured against assigned (R3.3) and raise a discrepancy.
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
- **R3.3** Measure the on-air offset per band as a **median over many reception reports** —
  each report carries the receiving station's own frequency error, so a single spot is not a
  measurement. Report the spread across bands: when it exceeds a documented limit, no single
  offset exists and the system must say "not measurable" rather than "wrong frequency".
  VY0ERC is in exactly this state and must not generate a false fault.
- **R3.4** Alert on: reported grid differing from the registry; reported power differing from
  the configured power; a band dropping out while others continue (an antenna, filter or
  combiner fault, and invisible in an all-bands liveness check); and a sudden collapse in
  reporter count while other stations in the region are unaffected.
- **R3.5** Cross-check against MeshCentral agent state, and **distinguish the three
  outcomes**, because they mean different things and need different people:

  | Pi reachable | Being spotted | Meaning |
  |---|---|---|
  | yes | yes | healthy |
  | yes | no | RF fault — transmitter, filter, combiner, antenna, or a bad frequency |
  | no | yes | site network is down; the transmitter is fine and **still radiating** |
  | no | no | site power or connectivity failure |

  The third row is the interesting one: it is the case where the control link is gone and
  the station is still on the air, which is precisely what §97.213(b) addresses.

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
  operator's obligation is engaged). *Immediate* alerts must **escalate**: if the on-duty
  control operator has not acknowledged within a documented interval, the alert goes to the
  other designated control operators for that unit (R4.6) and then to the network operator.
  A control operator who cannot be reached is the situation R4.6 exists to prevent.

### R4 — Positive control

The requirement Nathaniel stated: a control operator should be able to claim, reasonably and
truthfully, that they are at the control point of their WSPRSonde at all times, with the
means of control in their pocket. See §5 for the regulatory reading behind this.

- **R4.1** Every unit has **one or more designated control operators**, each a licensed
  amateur, recorded with licence class and issuing administration.
- **R4.2** A control operator can **inhibit transmission immediately** from a phone, with no
  more than one deliberate action from opening the app, and no dependence on the site's own
  network path being healthy in the transmit direction. A native smartphone app and a
  mobile web application are both acceptable; what is required is that the control point
  fits in a pocket, works on the phone the operator already carries, and can deliver push
  alerts (R3.7, R3.9). The intent is that the control operator can truthfully say they are
  at the control point wherever they happen to be.
- **R4.3** **The interlock lives at the transmitter, not in the web application.** The sonde's
  host computer must require a valid, short-lived authorisation to key the transmitter, and
  must inhibit transmission when it cannot obtain one. This is what makes §97.213(b)
  structural rather than a timer that can be misconfigured: a WSPR transmission is ~110.6 s,
  so refusing to start a slot without fresh authorisation bounds transmission after a
  control-link failure to less than one slot.
- **R4.4** **Fail safe.** Loss of the control link, an expired token, an unreachable server,
  or a clock disagreement must all result in *not transmitting*. The failure mode of a bug in
  this subsystem must be a silent beacon, never an uncontrolled one.
- **R4.5** The control operator must be able to see **live confirmation of the current
  state** — transmitting or inhibited, when the last authorisation was issued and when it
  expires — so that "I am at the control point" is a statement about an observable system and
  not a claim about intent.
- **R4.6** **Delegation, hand-off and a pool of control operators.** A unit's designated
  control operators (R4.1) form a pool that shares responsibility for it. At every moment
  exactly one member of the pool is **on duty** for the unit, visible to everyone with access
  to the unit and recorded in the audit log (R4.7). A control operator must be able to hand
  duty to another pool member for a defined period (a vacation, a hospital stay, a field
  season) with the change logged, and the system must warn the pool and the network operator
  when a duty period is about to lapse with no successor, because a unit with nobody on duty
  is a unit with no control operator. Sites are unattended for months; Antarctic and Arctic
  sites change staff seasonally.
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

### R5 — Access control

- **R5.1** Roles per §3, assigned per unit and per site, not globally.
- **R5.2** A host who is not a licensed amateur can see status and report site changes but
  cannot hold control-operator authority (R3.1).
- **R5.3** Authenticate against something operators already have. Options to weigh:
  MeshCentral accounts (already issued to hosts), a HamSCI SSO if one exists, or LoTW/ARRL
  identity. **Callsign self-assertion is not authentication** and must not be the basis for
  control authority.
- **R5.4** Multi-factor authentication required for any account that can enable transmission.
- **R5.5** Read-only public access to the consented subset (R1.6) without an account.

### R6 — Integrations

- **R6.1** WsprDaemon ClickHouse, read-only, for monitoring (§4.2). Bounded time windows,
  one request at a time, `wd10` by default — these are volunteer-run servers under live load.
- **R6.2** MeshCentral, for agent reachability and remote configuration (§4.1).
- **R6.3** Gwyn's `wsprsonde` PostgreSQL table: import as the frequency-history seed, then
  take over maintenance or keep it synchronised. Gwyn has asked for a curator; this is the
  system that becomes one.
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
- **N4 — The transmit interlock must not depend on the web application being up.** See R4.4.
  If the interlock's availability becomes the network's availability, the cure is worse than
  the disease.
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
   meshcentral ───────▶│                              │
   (agent state)       └───────────────┬──────────────┘
                                       │  short-lived transmit authorisation
                                       ▼
                       ┌──────────────────────────────┐
                       │  WSPRSonde host (Raspberry Pi)│
                       │  ┌────────────────────────┐  │
                       │  │ interlock daemon       │  │  refuses to key without a
                       │  │  · fetches token       │  │  valid unexpired token;
                       │  │  · gates the WS-8      │  │  fails closed  (R4.3, R4.4)
                       │  └────────────────────────┘  │
                       └──────────────────────────────┘
```

Two properties are load-bearing:

1. **The arrow into the Pi is a pull, not a push.** The sonde asks for permission; the server
   never has to reach in. That works behind NAT, needs no inbound firewall rule, and means a
   server outage stops transmission rather than stranding it.
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
| **2 — Monitoring** | Scheduled polling, status classification, offset verification, alerting, MeshCentral cross-check | next |
| **3 — Coordination** | Assignment workflow with collision and §97.203(b) checking; public assignment table | with or after 2 |
| **4 — Positive control** | Interlock daemon on the Pi, token service, operator phone interface, audit log | last, and needs the most review |

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
- **Phase 4 is scoped for the students as a design, a reference implementation of the
  interlock daemon, and a test harness against a bench unit**, with deployment to licensed
  stations gated on a review by the control operators concerned and a settled answer to
  Q1. Students should not be the ones deciding when a transmitter someone else is licensed
  for goes on or off the air.
- **The requirements freeze at Draft 1.0 when the capstone proposal is submitted.**
  Anything raised after that goes into a backlog for the team to weigh, not into the
  baseline they are graded against. This is why the review round is happening now.

---

## 10. Open questions for reviewers

1. **§5 as a whole — is the reading right?** Specifically: is unattended HF WSPR beacon
   operation correctly characterised as remote control under §97.109(c) rather than automatic
   control, given that §97.203(d) does not cover 3.5–28.126 MHz? What is current practice
   among the existing operators, and has anyone had this conversation with the FCC or with
   ARRL? *(Paul, Rob, Michael AC0G, Mark WA4KFZ — you have all run unattended beacons.)*
2. **Is a per-slot authorisation token acceptable to operators**, or is the operational risk
   of a station going quiet because a token did not arrive worse than the problem it solves?
   Would a longer-lived token with a local watchdog be a better trade?
3. **Should the interlock be mandatory for HamSCI-funded units** and optional for privately
   owned ones, or uniform?
4. **Who owns the registry after this is built?** Gwyn has been explicit that he wants a
   curator with hands-on access to the hardware. Is that a named person, a rota, or the
   system itself with the coordinator as backstop?
5. **Callsign suffixes.** Nathaniel proposed `-WS` to mark WSPRSonde transmissions. §2.4
   shows the simultaneity test identifies them without one, so the suffix is no longer
   necessary for detection — but it would make the data self-describing for anyone querying
   WSPRNet without our registry. Worth the disruption to existing callsigns and to Gwyn's
   historical table?
6. **MeshCentral as the identity provider** — is that acceptable and does it scale to
   non-HamSCI participants (R2.7)?
7. **Four unlisted candidates** — DC7TO, ZD7GWM, N9VP, G0PKT. Does anyone recognise these as
   WSPRSondes, BeaconBlasters, or something else? *(Paul, you would know who has hardware.)*
8. **KH2R and DP0GVN are 1 Hz apart.** Which moves, and when? DP0GVN is in Antarctica and
   reconfiguration there is not free.
9. **Non-US jurisdictions** — does anyone know the equivalent Canadian (ISED), German (BNetzA),
   Costa Rican and Indian requirements for unattended beacon operation? *(Michael Hartje
   DK5HH, Pierre Fogal VE3KTB, John Clark TI4JWC.)*
10. **Scope check** — is the transmit side the right boundary, or should this system cover
    PSWS receivers too? Rob's original question was about a "HamSCI monitoring and
    configuration website", which is broader than what is proposed here.
11. **Capstone fit (§9.1).** Is the split of Phases 1–3 for the students and Phase 4 as
    design-plus-bench-prototype the right one? Is anything in R1–R3 unreasonable to ask of
    a student team in one academic year?
12. **Who will act as a customer for the student team?** A capstone works when the
    students can put a question to a real user and get an answer within a week. Which
    reviewers are willing to be named as stakeholders the team may contact, and for which
    roles in §3?

---

## 11. Explicitly out of scope

- PSWS receive instruments (HFRx, magnetometer, VLF) — see Q10.
- Science data processing and archival. This system publishes metadata about transmitters;
  it does not touch spot or noise data beyond reading it for monitoring.
- Replacing WsprDaemon, WSPRNet or MeshCentral.
- WSPRSonde firmware, except for the interlock daemon on the host computer (R4.3).
- Procurement, shipping and inventory finance, beyond the pipeline states in R1.7.

---

## Provenance

Sources consulted 2026-08-13:

- Email thread *"WSPRSonde Shipping List #1"* and *"Currently deployed WSPRSondes?"*,
  2026-07-31 to 2026-08-06 (Frissell, Mikitin, Elliott, Robinett, Griffiths), archived at
  `reference/20260813_wsprsonde_location_email.olm`
- `G3ZIL_WsprSonde_Metadata_V1-1.xlsx`, Griffiths & Elliott, revised 2025-05-11
- `wsprsonde` table, `wd10.wsprdaemon.org` PostgreSQL database `tutorial`, 139 rows
- `wspr.rx`, WsprDaemon ClickHouse endpoint — live queries, 2026-08-13
- 47 CFR §§97.3, 97.109, 97.203, 97.213, via Cornell LII, read 2026-08-13; re-verified
  against the eCFR point-in-time version of 2026-08-29 on 2026-09-02
- <https://hamsci.org/wsprsonde-psws-transmitter>, <https://turnislandsystems.com>
- `polar-psws/docs/wsprdaemon_extended_spots_access.md` (Frissell, 2026-07-28)

Drafted with AI assistance; see `ai/ai_usage_log.md`. All rule citations, measurements and
attributions require human verification before this document is acted upon.

---

## Change log

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
- Review list extended: KA9Q, KC3EEY, KD8OXT, KV0S.

**Draft 0.1, 2026-08-13.** First draft.
