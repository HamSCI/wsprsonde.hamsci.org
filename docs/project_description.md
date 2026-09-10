# A Management System for the HamSCI WSPRSonde Transmitter Network

**Computer Science Senior Capstone Project (two semesters)**

| | |
|---|---|
| **Project advisor** | Dr. Nathaniel A. Frissell, W2NAF, Department of Physics and Engineering, The University of Scranton (nathaniel.frissell@scranton.edu) |
| **Primary stakeholders** | Paul Elliott, WB6CXC, Turn Island Systems: designer and manufacturer of the WSPRSonde, and the network's frequency coordinator. Gwyn Griffiths, G3ZIL: keeper of the station metadata and frequency history, who has asked for a successor |
| **Additional mentors** | HamSCI Personal Space Weather Station team (Scranton and NJIT); Rob Robinett, AI6VN (WsprDaemon); Gary Mikitin, AF8A (host recruitment); HamSCI volunteer software community; The University of Scranton Amateur Radio Club (W3USR) |
| **Team size** | 3–5 students (Computer Science) |
| **Duration** | Two semesters (Fall 2026 – Spring 2027) |
| **Disciplines** | Full-stack web development, REST API design, database and schema design, data engineering against a live archive, device integration over a serial port, fail-safe design, DevOps, software testing |

*This description is written for computer science students with no amateur radio or physics
background. Radio and regulatory terms are defined where they first appear and collected in the
glossary (section 11). The full requirements document that accompanies this proposal is
[docs/requirements_wsprsonde_management_system.md](requirements_wsprsonde_management_system.md),
and it carries the reasoning behind every requirement summarized here.*

---

## 1. Background

About a dozen small radio transmitters, scattered from Antarctica to the Arctic to Costa Rica,
beacon continuously on eight shortwave bands so that scientists can measure how the upper
atmosphere bends radio waves. Ten more are funded and being deployed. Nobody can currently say
with confidence where all of them are, what channel each is supposed to use, whether each one is
actually transmitting, or who is legally responsible for it at this moment. This project builds
the system that can: a registry, a frequency coordinator, a monitor, and a control mechanism that
lets a licensed operator shut a transmitter down from a phone. The rest of this section explains
the network and defines the terms.

The Ham Radio Science Citizen Investigation (HamSCI, [hamsci.org](https://hamsci.org)) is an
international collaboration of amateur radio operators, scientists, and students who use the
amateur radio service as a distributed scientific instrument. Its flagship effort is the
**Personal Space Weather Station (PSWS)** network: volunteer-hosted receivers that record radio
signals continuously, so that changes in the received signals can be turned into measurements of
the ionosphere, the electrically charged layer of the upper atmosphere that reflects shortwave
radio around the world.

A receiver alone measures a path, not a medium. To turn a reception report into physics you must
know what was transmitted: from where, at what power, on exactly what frequency, and when.
Ordinary amateur transmissions do not come with those guarantees, so the PSWS programme deploys
its own transmitters, and those are the subject of this project.

**The WSPRSonde.** A WSPRSonde is a purpose-built beacon designed and manufactured by Paul
Elliott, WB6CXC, of [Turn Island Systems](https://turnislandsystems.com). The current model, the
WS-8, transmits about one watt on each of eight shortwave bands at once, continuously, day and
night. Its frequency is locked to a GPS-derived reference, which means the transmitted frequency
is known to a fraction of a hertz rather than merely to the dial setting. In radio regulation a
transmitter of this kind is a **beacon**: a station that transmits for the purpose of observing
propagation rather than to communicate with anyone.

**What it transmits.** WSPRSondes use **WSPR** (Weak Signal Propagation Reporter) and its
successor **FST4W**, digital modes designed to be decoded at signal levels far below the noise
floor. A WSPR transmission occupies a 110.6-second slot beginning on an even minute, and carries
just three things: the transmitting station's callsign, its Maidenhead grid square, and its
transmitter power. Receivers worldwide decode these automatically and upload each decode to a
public database as a **spot**: a record that receiver A heard station B at a given time,
frequency, and signal-to-noise ratio.

**The 200 Hz window, and why coordination is needed.** All WSPR activity on a band is packed into
a window only 200 Hz wide. Every station picks a spot in that window, and a WSPRSonde is
configured with one **channel offset**, in hertz above the bottom of the window, applied to all
of its bands. Two stations on the same offset interfere with each other, so somebody has to
allocate offsets and keep a list. That somebody is currently WB6CXC, by email.

**Two archives already exist and this project reads both.**
[WSPRNet](https://wsprnet.org) collects the spots. [WsprDaemon](https://wsprdaemon.org), run by
Rob Robinett, AI6VN, mirrors and extends them and exposes the whole archive over a ClickHouse
database interface: the `wspr.rx` table holds over twelve billion rows. Every HamSCI WSPRSonde
also ships with a Raspberry Pi host computer running a **MeshCentral** agent, which gives the
programme remote terminal access to the host and reports whether it is online.

**The legal dimension, which is what makes this project unusual.** In the United States an
amateur station transmitting unattended is still the responsibility of a licensed human, the
**control operator**, and Part 97 of the FCC's rules constrains how that works. Automatic control
of a beacon, meaning operation with no control operator present, is permitted only on a short
list of frequency segments that does not include any of the bands a WSPRSonde uses. These
stations therefore operate under **remote control**, and §97.213(b) requires that "provisions are
incorporated to limit transmission by the station to a period of no more than 3 minutes in the
event of malfunction in the control link." A web dashboard does not satisfy that rule. Something
has to stop the transmitter. The WS-8 has the necessary hardware feature, a **dead-man** timer
that shuts the transmitters down when the host computer stops talking to it, and no software
currently feeds it in a way that is tied to the operator's actual reachability.

**Scale and stakes.** Roughly a dozen WSPRSondes are on the air worldwide today. Ten more are
funded by the U.S. National Science Foundation for deployment across North America, of which the
first five shipped in August 2026. Two of the existing sites are polar, DP0GVN at Neumayer
Station III in Antarctica and VY0ERC at Eureka in the Canadian Arctic, and this system has to
support them as they are: no new polar WSPRSonde deployments are currently planned, so those two
are the network's entire polar transmit capability. A transmitter that fails at a polar site can
wait months for a human visit, so learning promptly that it failed has real value.

## 2. The Gap This Project Fills

**The network has outgrown its bookkeeping, and this is measurable rather than a matter of
opinion.** Everything in this section came out of a single afternoon's work on 13 August 2026,
querying the existing archives against the existing records. The scripts that produced it are in
this repository, which means the team can re-run every one of these findings on day one.

**There is no single list, and the lists that exist disagree.** As of August 2026 the network was
recorded in four places: a spreadsheet maintained by G3ZIL, a database table on a WsprDaemon
server, an email thread of channel assignments from WB6CXC, and shipping lists from AF8A. None of
them is wrong. They are four partial views maintained at four different times, and reconciling
them is manual work that nobody owns. G3ZIL has said the table "does need updating, and a curator
rather than me."

**The assigned frequency and the transmitted frequency are not the same thing.** Measuring the
on-air channel offset of every listed station against its assignment, on 13 August 2026,
produced this:

| Callsign | Assigned | Measured | Verdict |
|---|---|---|---|
| WB6CXC (Occidental) | 135 Hz | 135 Hz | ok |
| **KH2R** | **36 Hz** | **35 Hz** | **1 Hz below assignment** |
| DP0GVN | 37 Hz | 37 Hz | ok |
| WW0WWV | 50 Hz | 50 Hz | ok |
| TI4JWC | 15 Hz | 16 Hz | ok |
| **KD0EAG** | **80 Hz** | **131 Hz** | **mismatch** |
| **VY0ERC** | 150 Hz | bands disagree by 115 Hz | **not measurable** |
| N4RVE | 100 Hz | 100 Hz | ok, after a nine-day outage |

Each row is a finding. KD0EAG has an explanation, because a replacement unit configured for the
right channel was never deployed and the old one is still running, but nothing in the current
arrangement would have surfaced it. VY0ERC is heard by so few receivers that its channel cannot
be verified at all from the spot record, which is itself worth knowing. N4RVE went off the air on
9 August 2026 and stayed off for nine days, and the outage was discovered by a script rather than
by a person. KH2R's row is the kind of finding a repeat measurement produces: the crowd-sourced
median read 36 Hz in August and 35 Hz in September, and a ground-wave measurement by G3ZIL settled
it at 35 Hz. One hertz is the resolution limit of the method, which is why the system records the
assigned and the measured value separately rather than reconciling them into one number.

**Frequency collisions are already on the books.** KH2R and DP0GVN are assigned one hertz apart.
WB6CXC flagged it by email in August 2026 and one of them should move. Worse, a privately owned
WSPRSonde on St Helena transmits on the channel assigned to a HamSCI unit in Washington State, and
both were measured on the same channel on five common bands in September 2026; it was never in a
list anyone could check against. No tool would have caught either at assignment time, and no tool would catch the
next one.

**"Which of these transmitters is a WSPRSonde?" has no answer in the data.** A scan of the spot
archive on 13 August 2026 identified nine transmitters keying many bands in the same two-minute
slot, a signature no ordinary station can imitate. Five were known WSPRSondes. Four were stations
nobody had on any list. A repeat of the same scan on 3 September 2026 returned six unlisted
stations, and a ninth WSPRSonde came on the air on 21 August 2026, after the first scan and
invisible to it. Any study that wants to use this network as a controlled transmitter array must be able
to say which spots came from a controlled transmitter, and today that means consulting a
spreadsheet.

**Nobody is watching the transmitters.** Over one 30-day window, VY0ERC was heard by 70 receivers
and KH2R by 2,319. Whether that difference is propagation, an antenna problem, or a failing
transmitter, no one is being told either way.

**No control operator can currently demonstrate control.** Each of these stations has a licensed
amateur responsible for its transmissions, and none of them has a mechanism that would stop the
transmitter if their link to the site failed, nor a way to inhibit it on demand from wherever they
happen to be. The hardware can do it. Nothing drives the hardware.

**None of this criticizes anyone.** The current arrangement has been maintained generously by
volunteers, and it worked while the network was a handful of stations. It does not work at the
twenty-two now deployed or funded, it concentrates in individuals, and it cannot answer the
questions the science and the regulations both ask. This project builds the machine that does the
mechanical part.

## 3. Project Objective

Design, build, test, and deploy **wsprsonde.hamsci.org**: a web platform that holds one
authoritative record of the HamSCI WSPRSonde network, coordinates channel assignments without
collisions, verifies continuously that each station is transmitting where and as it should, alerts
the responsible people when it is not, and gives every control operator a means of positive
control that fits in a pocket.

At the end of the project, a control operator should be able to open a phone, see that their
station is transmitting on its assigned channel, and inhibit it with one deliberate action; a
frequency coordinator should be unable to issue a colliding assignment by accident; a scientist
should be able to fetch a machine-readable list of controlled transmitters with positions and
validity intervals; and the whole network's health should be visible on one page.

**This system will be used, and two properties follow from that.**

1. **The interlock must fail safe, and must not become the network's weak point.** A bug in the
   control subsystem must result in a silent beacon, never an uncontrolled one. Equally, if the
   web application's availability becomes the network's availability, the cure is worse than the
   disease. Both constraints are design inputs from the first week, not tests at the end.
2. **The record must outlive the application.** The registry is the network's institutional
   memory, and it must be readable in twenty years by someone with a text editor. The canonical
   form is a versioned text file in Git, with the web application as a view and an editor over it.

## 4. System Concept

```
   Control operators and hosts                        Scientists and the public
   phone: state, inhibit, alerts                      map, station pages, exports
              │                                                  ▲
              ▼                                                  │
 ┌───────────────────────────────────────────────────────────────┴─────────┐
 │                        wsprsonde.hamsci.org                             │
 │                                                                         │
 │   Registry ──────────── units, sites, callsign history, consent flags   │
 │   Coordination ──────── channel assignment, collision and rule checks   │
 │   Monitoring ────────── liveness, channel verification, alerting        │
 │   Positive control ──── authorisation service, audit log, emergency stop│
 │   Products ──────────── versioned CSV and JSON feed, public map         │
 └──▲────────────▲───────────────────▲───────────────────────┬─────────────┘
    │            │                   │                       │ short-lived
    │ registry   │ spots             │ agent state           │ authorisation
    │ (Git)      │ (ClickHouse)      │ (MeshCentral)         ▼
 ┌──┴──────┐ ┌───┴──────────┐ ┌──────┴───────┐   ┌─────────────────────────┐
 │ CSV and │ │ WsprDaemon   │ │ MeshCentral  │   │ WSPRSonde host          │
 │ JSON in │ │ wspr.rx      │ │ agent on     │   │ (Raspberry Pi)          │
 │ Git     │ │ 12e9 rows    │ │ every host   │   │   keep-alive daemon     │
 └─────────┘ └──────────────┘ └──────────────┘   │        │ serial         │
                                                 │        ▼                │
                                                 │   WS-8 transmitter      │
                                                 │   dead-man: 1 minute    │
                                                 │   8 bands, ~1 W each    │
                                                 └─────────────────────────┘
```

**Registry.** One record per physical transmitter, keyed by the unit's own 24-bit serial number,
which the WS-8 will report over its serial port. Callsigns change and units move, so all history
is interval-valued: "where was DP0GVN in March 2025" must be answerable, because a study spanning
a reconfiguration otherwise silently mixes two different stations.

**Coordination.** Channel assignment with the checks a human cannot reliably do: refuse a
colliding assignment, warn when a proposed channel sits on top of ordinary WSPR traffic, and
enforce the FCC rule that forbids two beacons at one site from occupying the same band.

**Monitoring.** Scheduled polling of the WsprDaemon archive, and a per-band measurement of each
station's actual transmit frequency. Cross-referenced against MeshCentral, this distinguishes
outcomes that need different people: a healthy station, a radio fault with a reachable computer,
and the interesting case where the site's network is down while the transmitter is still
radiating.

**Positive control.** A short-lived authorisation the host computer must hold in order to keep
feeding the transmitter's dead-man timer. When the operator inhibits the station, or when the
control link fails, the authorisation stops arriving, the keep-alive stops, and the dead-man
stops the transmitter within about two minutes. Nothing in that chain depends on the web
application staying up: its failure mode is the same as its silence.

**Products.** A versioned, citable data feed for downstream consumers. The `polar-psws` station
maps already consume the prototype version of exactly this file.

## 5. Draft Technical Requirements

These are the advisor's and stakeholders' targets, drawn from the accompanying requirements
document, which is under collaborator review and freezes at Draft 1.0 when this proposal is
submitted. Refining them into a complete, testable specification, with each stakeholder need
traced to a requirement, is the team's first deliverable.

| # | Requirement (initial target) |
|---|---|
| R1 | **Unit and site registry.** One record per physical transmitter, keyed on the hardware's own serial number, grouped into sites. Carries callsign and callsign history, licensee, control operators, host, position with stated precision, hardware model, firmware version, antenna, modes, in-service dates, funding source, and deployment pipeline state from `in_stock` through `on_air` to `retired`. |
| R2 | **Interval-valued history.** Every fact about a unit is valid over a time interval, and any past state must be reconstructable. The canonical store is a versioned text file in Git; the application is a view and an editor over it. |
| R3 | **Publication consent per field group.** Every record carries an explicit consent flag for position, operator name, and contact details, defaulting to *not published*. Host street addresses, emails, and phone numbers must never appear in any exported product. |
| R4 | **Channel coordination.** Record assigned channel offsets, refuse or warn on a colliding assignment with a configurable guard band, check proposed channels against non-WSPRSonde traffic in the same window, and enforce the one-channel-per-band-per-site rule. Assignments must be issuable for units outside HamSCI, because the manufacturer ships to people who are not in the programme. |
| R5 | **Three-way channel verification.** Compare the **assigned** offset, the **configured** offset read from the unit itself, and the **measured** offset derived from reception reports. Raise a discrepancy on any disagreement. Assigned against configured catches a unit nobody reconfigured; configured against measured catches a unit that is not doing what it was told. |
| R6 | **On-air monitoring.** Poll the WsprDaemon archive on a schedule, record per unit the last spot, reporter count, bands, reported grid, and reported power, and classify state as active, intermittent, or silent against documented thresholds. Treat "not heard" as evidence of nothing being received rather than proof that a transmitter is dead. |
| R7 | **Fault detection and alerting.** Alert on a reported grid or power that disagrees with the registry, on a single band dropping out while others continue, and on a collapse in reporter count that regional stations do not share. Alerts carry a severity that says what the recipient must do, are de-duplicated and rate-limited, escalate when unacknowledged, and go out by a channel the recipient chose. |
| R8 | **Device integration.** Read each unit's own status report over its serial port through the host computer: serial number, firmware version, configured frequency list, and running state. Cross-check host reachability against MeshCentral agent state and distinguish a radio fault from a network fault. |
| R9 | **Positive control.** A control operator can inhibit transmission immediately from a phone, see live confirmation of the current state, and hand duty to another designated operator with the change logged. An append-only audit log records every inhibit, enable, delegation, and authorisation lapse. A network-wide emergency stop exists for a systemic problem. |
| R10 | **The interlock lives in the transmitter.** The host computer holds a short-lived authorisation obtained over the control link and feeds the WS-8's dead-man timer only while it holds one. The dead-man is set to one minute. Loss of the link, an expired authorisation, an unreachable server, or a clock disagreement must all result in not transmitting. The daemon owns the serial port exclusively, because any traffic to the unit resets its timer. |
| R11 | **Roles, authentication, and access control.** Roles assigned per unit and per site rather than globally: control operator, host, frequency coordinator, network operator, curator, scientist, public. A host who is not a licensed amateur can see status but cannot hold control authority. Authenticate against something operators already have, and require multi-factor authentication for any account that can enable transmission. Callsign self-assertion is not authentication. |
| R12 | **Public presentation and data products.** A public network map and per-station pages showing only consented records; a public channel-assignment table so operators outside the programme can see what is in use; and a documented, versioned machine-readable feed with a provenance manifest, which downstream consumers can cite. |
| R13 | **Deployment, degradation, and handoff.** Runs on HamSCI infrastructure, reproducibly deployable from a documented procedure, with automated tests and continuous integration. When the WsprDaemon archive is unreachable the system reports "unknown" rather than "silent". Maintainable by volunteers after the team graduates: a runbook, a backup and restore procedure, and a monitored health check. |

**On R5 and R6, the requirement most easily designed past.** A single reception report is not a
measurement. Each one carries the receiving receiver's own frequency error, so individual spots
scatter by several hertz even from a GPS-locked transmitter, and only a median across many
receivers is stable to about one hertz. The trap has a worked example waiting in this repository:
the existing prototype measures each band over a three-day window and keeps only bands with at
least twenty reports, and for a weakly-heard station that silently drops the bands that disagree
and manufactures a confident, wrong answer. Rediscovering that bug, and fixing it properly, is a
good first week.

**On R6 and the data volume.** The `wspr.rx` table holds over twelve billion rows on a
volunteer-run server carrying live operational load. Every query must be bounded in time, issued
one at a time, and directed at the mirror the WsprDaemon team prefers. Read this as a systems
requirement and an etiquette requirement at once: the team does not own this archive, and a
careless polling loop is a real cost to somebody else's project.

**On R10, and what students are and are not asked to decide.** This requirement touches
transmitters that other people hold licences for, and a bug here has consequences beyond a wrong
number on a web page. The team's scope is the design, a reference implementation of the keep-alive
daemon, and a test harness proving the behaviour against a WSPRSonde on the bench. Deploying it
to a licensed station is gated on review by the control operator concerned. Students should never
be the ones deciding when someone else's transmitter goes on or off the air.

**On R3 and R11.** The consent flag inherited from the existing metadata is `unknown` for most
stations, which means *not publishable* until a human asks the host. Personal data must be kept
out of the schema's public surface from the first design, because retrofitting that boundary
after addresses have spread through a database is far harder than drawing it correctly at the
start.

### Success tiers

The requirements above define the full system. The two-semester plan targets the objective tier;
the threshold tier alone is a complete, successful capstone.

- **Threshold (a successful capstone).** Registry, monitoring, and alerting, deployed to a staging
  environment (R1, R2, R3, R6, R7, R11 at prototype level). **The acceptance test is a replay.**
  Load the archived spot record for August and September 2026 and have the system reproduce, on
  its own, the verification table in section 2: the same eight verdicts, the KD0EAG mismatch, the
  refusal to state a channel for VY0ERC, the unlisted candidate stations, and an alert on N4RVE's
  outage raised within 48 hours of its start. Reproducing a known-good human analysis is how the
  team proves the monitor is right.
- **Objective (the project goal).** The threshold system in production at wsprsonde.hamsci.org,
  with the coordination workflow in use by the frequency coordinator, alerts reaching real control
  operators, the public map and channel table live, the machine-readable feed consumed by the
  `polar-psws` maps, and the device integration of R8 reading real units (adds R4, R5, R8, R12,
  with R13 in force once the site is public). Positive control is delivered at this tier as a
  design, a reference daemon, and a bench demonstration: cut the control link and show the
  transmitter stop within two minutes, with the audit log to prove it.
- **Stretch (beyond expectations).** The interlock deployed to volunteer United States stations
  with their control operators' sign-off; the jurisdiction-aware handling that non-US stations
  need; automatic enrolment of candidate transmitters after human confirmation; and uptime
  analytics that answer "how much of 2026 was this station actually on the air" for the science.

Everything above the threshold is upside. Because the project is grant funded, significant
resources are available to help the team reach the upper tiers, beyond what is normally available
to capstone projects (section 10).

## 6. Two-Semester Plan

**One fixed date drives the schedule.** The 2027 HamSCI Workshop is on 17–18 April 2027, hosted at
the University of Scranton, and the team presents there. It falls about a month before the
course's own final deadline, so semester 2 is planned backward from it.

| Date | Event | Role in the project |
|---|---|---|
| Through the project | Remaining NSF-funded units configured, shipped, and installed | Live test of the deployment pipeline in R1 |
| 17–18 April 2027 | [HamSCI Workshop](https://hamsci.org/hamsci2027), University of Scranton | Present the work |

The first row is the schedule risk worth naming early, and it carries no dates because there is
no deployment schedule to hold it to. Units are configured, shipped, and installed as hosts,
customs, and travel allow; one has been sitting in Indian customs since August 2026; and stations
come on the air when they come on the air. The registry has to be usable throughout, which is why
the deployment pipeline states sit in the threshold tier rather than being deferred.

### Semester 1 (Fall 2026): Requirements, Design, and the Registry and Monitor

- Requirements elicitation with WB6CXC, G3ZIL, AI6VN, and the PSWS team. Freeze the specification
  at Draft 1.0. The requirements document already carries the reasoning; the work is turning it
  into a testable specification with traceability, and resolving the questions its section 10
  leaves open.
- Data investigation: query the real archive, measure it, and design the schema and storage
  strategy against what was measured rather than against an estimate. Re-derive the section 2
  findings from scratch as the first exercise.
- Technology selection, justified in a written trade study: language and framework, database,
  mapping and visualization libraries, hosting and deployment model. Maintainability by volunteers
  after handoff is an explicit criterion, weighted accordingly.
- Build the registry with its interval-valued history and consent model, the import of all four
  existing sources, the monitoring pipeline, and the alerting path.
- **Replay validation** against the archived record, the threshold acceptance test. This milestone
  needs no live deployment and no hardware, which is what makes it the right first-semester
  target.
- **Milestones:** requirements review (mid-semester), architecture and design review, threshold
  system demonstrated on staging, replay validation passed.

### Semester 2 (Spring 2027): Coordination, Control, Deploy, Demonstrate

- Coordination workflow with collision and rule checking, put in front of the frequency
  coordinator and used for a real assignment.
- Device integration: read a real unit's own status report through its host computer, and land the
  three-way channel comparison of R5.
- Positive control, in the order the risk demands: design review first, then the reference
  keep-alive daemon, then the bench harness against a WSPRSonde and a Raspberry Pi in the lab.
  Demonstrate the dead-man stopping the transmitter when the link is cut, and produce the audit
  log for it.
- Deploy to wsprsonde.hamsci.org on HamSCI infrastructure; security review; accessibility audit;
  publish the public map, the channel table, and the machine-readable feed.
- Handoff: runbook, backup and restore rehearsal, volunteer maintainer walkthrough, open-source
  release to the HamSCI GitHub organization.
- Present at the **[2027 HamSCI Workshop](https://hamsci.org/hamsci2027)**, 17–18 April 2027, in
  front of the scientists and volunteer operators who will use the system.
- **Milestones:** coordination in use, device integration demonstrated, interlock bench
  demonstration, production readiness review, workshop presentation, final report and poster,
  open-source release.

**Why the interlock is second-semester work.** It is the only part of this system whose failure
puts a transmitter on the air when it should not be, and the regulatory reading behind it is still
being argued among the reviewers. The team should have a working registry and monitor, and a
settled specification, before writing code that keys a radio.

## 7. Deliverables

1. Requirements specification at Draft 1.0 or later, with traceability from stakeholder needs to
   requirements and the open questions resolved (semester 1).
2. Technology trade study and architecture design document.
3. Working platform deployed at wsprsonde.hamsci.org.
4. Documented, versioned data feed and API with a published schema, data dictionary, and
   provenance manifest, citable by downstream consumers.
5. Automated test suite and continuous integration configuration.
6. Operations runbook: deployment, backup and restore, monitoring, and incident response, written
   for a volunteer maintainer.
7. Validation report: the replay against the archived record, and the faults the live system
   caught in service.
8. Positive-control package: design document, reference keep-alive daemon, bench test harness, and
   a demonstration report showing transmission stopping within the required interval.
9. Final capstone report, poster, and public demonstration.
10. Open-source release to the HamSCI GitHub organization under the MIT license, and a
    presentation at the [2027 HamSCI Workshop](https://hamsci.org/hamsci2027).

## 8. What You Will Learn

This project spans the full arc of a production system inside an active, NSF-funded research
collaboration, with real users, real hardware, and a regulatory constraint that a design has to
satisfy rather than argue with.

- **Full-stack development:** interactive frontend with maps and live status, backend services,
  REST API design, authentication and role-based authorization, audit logging.
- **Data engineering:** schema design for interval-valued history, ETL against a twelve-billion-row
  archive you do not own, statistical aggregation where a single sample is not a measurement, and
  the discipline of reporting "unknown" instead of inventing a value.
- **Device and systems integration:** talking to real hardware over a serial port, through a
  remote host, across a network that fails; distinguishing three kinds of failure from two
  signals; and designing a watchdog chain whose failure mode is silence.
- **Requirements and compliance engineering:** turning a written regulation into a testable
  system property, and defending the design to the people whose licences depend on it. This is
  rare experience for a new graduate and it transfers directly to regulated industries.
- **Working with real users:** an international volunteer organization, hardware in Antarctica,
  and stakeholders who will tell you plainly when a requirement is wrong. Several already have.
- **Open-source collaboration** on software that stays in service after the semester ends.

This is also a deliberate career investment. The stack the project exercises, full-stack web, API
design, data pipelines at volume, device integration, deployment, CI/CD, and testing, is precisely
what software engineering interviews are built around. A capstone that put a public, documented,
tested system into production for a real organization, with the commit history to show for it, is
a concrete answer to the interview question every new graduate faces.

An amateur radio license is helpful and the club (W3USR) will happily get you licensed, but it is
optional. Anyone working on the control subsystem will understand it better with one, and the club
can put you on the air with a licensed operator regardless.

## 9. Team Roles (3–5 students)

- **Frontend and visualization lead:** operator-facing interface, phone experience for the control
  operator, network map, station pages, accessibility.
- **Backend and data lead:** schema and history model, the WsprDaemon ETL, channel measurement and
  verification, the public feed and API.
- **Device and control lead:** host-side daemon, serial integration with the WSPRSonde, the
  interlock design and its bench harness, the audit log.
- **Platform and quality lead:** deployment, CI, testing strategy, monitoring, security and privacy
  review, documentation and handoff. In a three-person team these duties are shared.

**Expanding the team.** Capstone students are expected to carry the majority of the project work
and its management. Within that, the team is encouraged to expand as needed and appropriate:
members of the HamSCI volunteer software community, who have very significant industry experience,
and underclassmen.

## 10. Resources Provided

This project is grant funded. Significant resources are available to help students, beyond what is
normally available to capstone projects:

- **Real stakeholders and a written baseline.** The requirements document accompanying this
  proposal is the product of a collaborator review round with the manufacturer, the frequency
  coordinator, and the data curator, and it records the reasoning behind each requirement. The
  reviewers are available to the team as customers.
- **A working prototype to start from.** This repository already holds the reconciled registry, a
  read-only WsprDaemon client, the channel-measurement code, the WSPRSonde detection method, and
  the data product that `polar-psws` consumes. It is a specification by example, and the team is
  free to keep, replace, or improve any of it.
- **Read access to the archives:** the WsprDaemon ClickHouse endpoint, the historical frequency
  table, and MeshCentral for the HamSCI fleet.
- **Hardware for bench work:** a WSPRSonde and a Raspberry Pi host in the Scranton lab, for the
  device integration and the interlock harness.
- **Hosting on HamSCI infrastructure**, with the wsprsonde.hamsci.org domain and a staging
  environment.
- **Access to the manufacturer.** WB6CXC has answered detailed questions about the hardware's
  serial interface and dead-man behaviour during the requirements review, on the record in this
  repository's issue tracker.
- Appropriate resources through the advisor's grant funding for hosting, services, and tooling.
- Mentorship from the advisor and from HamSCI volunteer software engineers.
- Claude Code accounts for each team member, for use in design, software development, and
  documentation. AI use must follow University of Scranton academic integrity policy and the course
  instructor's rules, including disclosure of AI assistance in project reports.

## 11. Glossary

| Term | Meaning |
|---|---|
| **Automatic control** | Operation with no control operator at the control point. Permitted for beacons only on the frequency segments listed in §97.203(d), none of which a WSPRSonde uses. |
| **Beacon** | In FCC terms, "an amateur station transmitting communications for the purposes of observation of propagation and reception or other related experimental activities." A WSPRSonde is one. |
| **BeaconBlaster** | The WSPRSonde's predecessor, still in service at one site. It has no dead-man timer, which is why it cannot meet the control requirement in R10. |
| **Callsign** | A station's government-issued identifier, such as W2NAF or DP0GVN. Public by convention. |
| **Channel offset** | A WSPRSonde's position within the 200 Hz WSPR window, in hertz above the bottom of it. One offset applies to all of a unit's bands, and the coordinator allocates them. |
| **ClickHouse** | The column-oriented database whose HTTP interface exposes the WsprDaemon spot archive. |
| **Control operator** | The licensed amateur responsible for a station's transmissions. May or may not be the person whose property the station sits on. |
| **Control point** | The location at which the control operator function is performed. The claim this system supports is that a phone can be one. |
| **Dead-man** | A timer in the WS-8 that shuts its transmitters down after a set interval with no traffic from the host computer, and re-arms when traffic resumes. Also called a watchdog. |
| **FST4W** | A newer digital mode, successor to WSPR, used by WSPRSondes for the same purpose. |
| **GPSDO** | GPS-disciplined oscillator. The reference that locks a WSPRSonde's transmit frequency to within a fraction of a hertz. |
| **Grid square** | A Maidenhead locator: a four- or six-character code such as `FN21` or `CN88ln` that encodes latitude and longitude. Four characters is about 78 km across at mid-latitudes, which matters at a polar site. |
| **MeshCentral** | The remote management server HamSCI runs. Every WSPRSonde host computer runs an agent that reports to it and permits remote access. |
| **Part 97** | Title 47, Part 97 of the U.S. Code of Federal Regulations: the amateur radio service rules. Sections §97.109, §97.203, and §97.213 constrain this project. |
| **PSWS** | Personal Space Weather Station. HamSCI's network of volunteer-hosted scientific radio receivers, of which the WSPRSondes are the transmit side. |
| **Remote control** | Operation in which a control operator at a control point manipulates the station through a control link. §97.213(b) requires that transmission stop within three minutes if that link malfunctions. |
| **Spot** | A report that receiver A decoded station B at a given time, frequency, and signal-to-noise ratio. The raw material of all monitoring in this project. |
| **UTC** | Coordinated Universal Time. Every timestamp in this domain is UTC, and mixing in local time is a recurring source of bugs. |
| **WSPR** | Weak Signal Propagation Reporter. A digital mode whose 110.6-second transmission carries a callsign, grid square, and power, decodable far below the noise floor. |
| **WSPRNet** | The public database that collects WSPR spots worldwide. |
| **WsprDaemon** | Rob Robinett's system that mirrors and extends the WSPR spot record, and exposes it over ClickHouse. The archive this project monitors from. |
| **WSPRSonde** | The purpose-built HamSCI beacon: eight bands, about one watt each, GPS-locked, transmitting continuously. Current model WS-8. |

## 12. References

1. HamSCI WSPRSonde PSWS transmitter: https://hamsci.org/wsprsonde-psws-transmitter
2. Requirements for a WSPRSonde management system, this repository:
   [docs/requirements_wsprsonde_management_system.md](requirements_wsprsonde_management_system.md)
3. This repository, including the reconciled registry and the verification code:
   https://github.com/HamSCI/wsprsonde.hamsci.org
4. Manufacturer's answers on the WS-8 serial interface and dead-man behaviour, issue tracker:
   https://github.com/HamSCI/wsprsonde.hamsci.org/issues
5. Turn Island Systems, WSPRSonde hardware: https://turnislandsystems.com
6. WsprDaemon: https://wsprdaemon.org
7. WSPRNet: https://wsprnet.org
8. WSJT-X, the software family that implements WSPR and FST4W: https://wsjt.sourceforge.io
9. WSPR message types and callsign encoding: https://dxplorer.net/wspr/msgtypes.html
10. 47 CFR Part 97, amateur radio service, via Cornell Legal Information Institute:
    https://www.law.cornell.edu/cfr/text/47/part-97 (§97.109 station control, §97.203 beacon
    station, §97.213 telecommand)
11. MeshCentral: https://meshcentral.com
12. HamSCI Personal Space Weather Station: https://hamsci.org/psws
13. 2027 HamSCI Workshop, 17–18 April 2027, University of Scranton: https://hamsci.org/hamsci2027

---

*Interested students should contact Dr. Frissell (nathaniel.frissell@scranton.edu).*

*This project supports the HamSCI Personal Space Weather Station effort. The WSPRSonde deployment
is funded by the U.S. National Science Foundation under awards OPP-2332427, AGS-2432821,
AGS-2432822, AGS-2432823, and AGS-2432824.*
