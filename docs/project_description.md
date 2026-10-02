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
Ordinary amateur transmissions do not come with those guarantees, so the PSWS program deploys
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
also ships with a Raspberry Pi host computer, connected to the transmitter by a serial cable, and
that computer is where this project's control software runs.

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
on-air channel offset of every listed station against its assignment, on 11 September 2026,
produced this:

| Callsign | Assigned | Measured | Verdict |
|---|---|---|---|
| WB6CXC (Occidental) | 135 Hz | 135 Hz | ok |
| **KH2R** | **36 Hz** | **35 Hz** | **1 Hz below assignment** |
| DP0GVN | 37 Hz | 37 Hz | ok |
| WW0WWV | 50 Hz | 50 Hz | ok |
| TI4JWC | 15 Hz | 16 Hz | ok |
| **KD0EAG** | **80 Hz** | **128 Hz** | **mismatch** |
| **VY0ERC** | 150 Hz | withheld | **not measurable** |
| N4RVE | 100 Hz | 100 Hz | ok, after a nine-day outage |
| **W8GPS** | **none on record** | 60 Hz | **unassigned** |
| **ZD7GWM** | 100 Hz nominal, **uncoordinated** | 100 Hz | **collides with N4RVE** |

Each row is a finding. KD0EAG has an explanation, because a replacement unit configured for the
right channel was never deployed and the old one is still running, but nothing in the current
arrangement would have surfaced it. VY0ERC is heard by so few receivers that its channel cannot
be verified at all from the spot record, which is itself worth knowing. N4RVE went off the air on
9 August 2026 and stayed off for nine days, and the outage was discovered by a script rather than
by a person. KH2R's row shows what the choice of data source is worth. The whole-hertz archive read
36 Hz in August and 35 Hz in September, and a ground-wave measurement by G3ZIL put it at 35 Hz.
Re-measured from a table that resolves 0.1 Hz, it reads 34.9 to 35.2 Hz on all eight bands, so
its 1 Hz disagreement with the assignment is real. That is why the system keeps the assigned and
the measured value as separate records. The last
two rows are stations that were on the air with no coordinated assignment at all, and one of them
is sharing a channel with a HamSCI unit.

**VY0ERC's row is the one to read carefully, because the prototype got it wrong twice.** On
10 September seven of its bands fell below the minimum report count while the eighth read 50 Hz,
and the prototype published a confident 50 Hz against a 150 Hz assignment: a fault report that
would have sent somebody to Ellesmere Island. A spread test cannot catch this, because one
surviving band has a spread of zero by construction. The prototype now counts distinct receivers
per band, and it reports VY0ERC as incoherent: its bands genuinely disagree, so no single offset
exists to compare against the assignment. **A monitoring system's worst failure is confident
invention**, and this project is full of places to make that mistake.

**Frequency collisions are already on the books.** KH2R and DP0GVN are assigned one hertz apart.
WB6CXC flagged it by email in August 2026 and one of them should move. Worse, a privately owned
WSPRSonde on St Helena transmits on the channel assigned to a HamSCI unit in Washington State, and
both were measured on the same channel on five common bands in September 2026. It was never in a
list anyone could check against. No tool would have caught either at assignment time, and no tool
would catch the next one.

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

1. **The interlock must fail safe.** A bug in the control subsystem must result in a silent
   beacon, never an uncontrolled one. The settled design ties each keep-alive-enabled station to
   the server, so a server outage takes those stations off the air until it returns. That trade
   was made knowingly, and it makes server uptime an operational requirement with monitoring of
   its own. Both are design inputs from the first week.
2. **The record must outlive the application.** The registry is the network's institutional
   memory, and it must be readable in twenty years by someone with a text editor. The canonical
   form is a versioned text file in Git, with the web application as a view and an editor over it.

## 4. System Concept

```
   Control operators and hosts                        Scientists and the public
   phone: state, configure, on/off, alerts            map, station pages, exports
              │                                                  ▲
              ▼                                                  │
 ┌───────────────────────────────────────────────────────────────┴─────────┐
 │                        wsprsonde.hamsci.org                             │
 │                                                                         │
 │   Registry ──────────── units, sites, callsign history, consent flags   │
 │   Coordination ──────── channel assignment, collision and rule checks   │
 │   Monitoring ────────── liveness, channel verification, alerting        │
 │   Positive control ──── operator pool, poll endpoint, audit log, e-stop │
 │   Products ──────────── versioned CSV and JSON feed, public map         │
 └──▲────────────▲───────────────────────────────────────────▲─────────────┘
    │            │                      poll: "is a control  │
    │ registry   │ spots                operator reachable?" │
    │ (Git)      │ (ClickHouse)                              │
 ┌──┴──────┐ ┌───┴──────────┐                    ┌───────────┴─────────────┐
 │ CSV and │ │ WsprDaemon   │                    │ WSPRSonde host          │
 │ JSON in │ │ spot tables  │                    │ (Raspberry Pi)          │
 │ Git     │ │ 12e9 rows    │                    │   keep-alive daemon     │
 └─────────┘ └──────────────┘                    │        │ serial         │
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
colliding assignment, show a proposed channel against ordinary WSPR traffic, and enforce the FCC
rule that forbids two beacons at one site from occupying the same band. Channels are chosen by a
simple stated rule (prefer an unassigned channel, then the least-used one, breaking ties by
distance), and the requirements invite a better algorithm.

**Monitoring.** Scheduled polling of the WsprDaemon archive, and a per-band measurement of each
station's actual transmit frequency. Cross-referenced against each host computer's own
check-ins with the server, this distinguishes outcomes that need different people: a healthy
station, a radio fault with a reachable computer, and the interesting case where the site's
network is down while the transmitter is still radiating.

**Positive control.** Each unit has a pool of designated control operators. The host computer
polls the server every 15 to 30 seconds, asking whether any of them is reachable, and feeds the
transmitter's dead-man timer only while the answer is yes. When the operator switches the station
off, or when the control link fails, the keep-alive stops and the dead-man stops the transmitter
within two to three minutes. The keep-alive is a per-unit setting, because Part 97 governs US
stations and five units are licensed elsewhere. The same interface lets the operator change most
of the unit's configuration without a terminal or a site visit.

**Products.** A versioned, citable data feed for downstream consumers. The `polar-psws` station
maps already consume the prototype version of exactly this file, and two Grafana dashboards
maintained by G3ZIL read the same record. One plots per-station Doppler shift from the known
transmit frequency. The other shows a wanted transmitter against every station within a chosen
bandwidth of it, which is the collision view of R2 in working form. Both are constraints as much
as resources: they must keep working through whatever the team does to the table underneath
them.

## 5. Draft Technical Requirements

These are the advisor's and stakeholders' targets, summarized from Draft 0.96 of the
accompanying requirements document, which is under collaborator review. The numbering follows
that document, so R4 here is R4 there. They are a starting draft. The final requirements are the
ones the student team and the WSPRSonde team agree on together, and reaching that agreement,
with each stakeholder need traced to a testable requirement, is the team's first deliverable.

| # | Requirement (initial target) |
|---|---|
| R1 | **Registry.** One record per physical transmitter, keyed on the hardware's own serial number, grouped into sites. Carries callsign history, licensee, control operators, host, position with its precision, hardware, firmware, antenna, transmit mode, in-service dates, and deployment pipeline state from `in_stock` through `on_air` to `retired`. Every fact is valid over a time interval, so any past state can be reconstructed. Mode is stored by name and translated to each system's own numeric code at every boundary, because those codes disagree. Every record carries a publication-consent flag per field group, defaulting to *not published*, and host street addresses, emails and phone numbers never appear in an exported product. |
| R2 | **Frequency coordination.** Record each unit's **assigned**, **configured** and **measured** channel offset, and raise a discrepancy when any two disagree. Assign channels by a simple stated rule: prefer an unassigned channel, otherwise the least-used one, breaking ties by geographic separation. The rule is a placeholder, and a better algorithm is invited. Refuse or warn on a colliding assignment, enforce the one-channel-per-band-per-site rule for US stations, allow per-band overrides, and issue assignments for units outside HamSCI. Before an assignment is confirmed, show the proposed channel against all WSPR traffic, using G3ZIL's existing dashboard. |
| R3 | **Monitoring.** Poll the WsprDaemon archive on a schedule, record per unit the last spot, receivers, bands, reported grid and reported power, and classify each unit as active, intermittent or silent. Measure each band's offset as a median from the table that resolves 0.1 Hz, counting a band only when at least five distinct receivers heard it. Alert on a grid or power mismatch, a single band dropping out, or a collapse in receivers, with severities, de-duplication, rate limiting and escalation. Read each unit's own status report over its serial port, tell a radio fault from a network fault using the host's check-ins, and present unregistered WSPRSonde-like transmitters as candidates for a human to confirm. |
| R4 | **Positive control.** Every unit has one or more designated control operators, and the station stays up while any one of them is reachable. A control operator can switch the transmitter off from a phone with one deliberate action, see live confirmation of its state, and set most of its configuration through the web app. The host feeds the WS-8's one-minute dead-man only while the server reports a control operator reachable, and any failure results in not transmitting. The keep-alive is a per-unit setting. An append-only audit log records every action, and a network-wide emergency stop exists. |
| R5 | **Access control.** Roles assigned per unit and per site: control operator, host, frequency coordinator, network operator, curator, scientist, public. A host who is not a licensed amateur can see status but cannot hold control authority. The system owns its own accounts and authentication, with multi-factor authentication for any account that can enable transmission. Callsign self-assertion is not authentication. |
| R6 | **Integrations.** Read-only WsprDaemon access, bounded and one query at a time. Import G3ZIL's frequency-history table as the seed, and keep the Grafana dashboard built on it working. Publish a stable feed for `polar-psws` and other consumers. |
| R7 | **Public presentation.** A public network map and per-station pages showing only consented records, and a public channel-assignment table so operators outside the program can see what is in use. |
| N1–N8 | **Non-functional.** Open source in the HamSCI GitHub organization. The registry is a versioned text file in Git, with the application as a view over it. When the archive is unreachable the system reports "unknown", never "silent". Server uptime is an operational requirement. Personal data is access-controlled and never exported. Prefer boring, well-documented technology a volunteer can maintain. Every threshold is a named, documented constant. Data products carry attribution and a license. |

**On R3, the requirement most easily designed past.** A single reception report is not a
measurement. Each one carries the receiving station's own frequency error, so individual spots
scatter by several hertz even from a GPS-locked transmitter. The prototype in this repository
fell into that trap twice. It first reported a confident 50 Hz for VY0ERC from the one band that
survived a twenty-report floor. On a finer data source, a single receiver reporting hundreds of
times then cleared the floor by itself, and its own error became the station's measurement. The
fix, now in the prototype, is to qualify each band on distinct receivers. Rediscovering that
history from the data is a good first week.

**On R3 and R6, and the data volume.** The `wspr.rx` table holds over twelve billion rows on a
volunteer-run server carrying live operational load. Every query must be bounded in time, issued
one at a time, and directed at the mirror the WsprDaemon team prefers. Read this as a systems
requirement and an etiquette requirement at once: the team does not own this archive, and a
careless polling loop is a real cost to somebody else's project.

**On R4, and what students are and are not asked to decide.** This requirement touches
transmitters that other people hold licenses for, and a bug here has consequences beyond a wrong
number on a web page. The team's scope is the control point: the keep-alive daemon, the poll
endpoint and the operator interface, proven against a WSPRSonde on the bench. Deploying it to a
licensed station is gated on review by the control operator concerned. Students should never be
the ones deciding when someone else's transmitter goes on or off the air.

**On R1 and R5.** The consent flag inherited from the existing metadata is `unknown` for most
stations, which means *not publishable* until a human asks the host. Personal data must be kept
out of the schema's public surface from the first design, because retrofitting that boundary
after addresses have spread through a database is far harder than drawing it correctly at the
start.

**What is out of scope.** Section 11 of the requirements lists what the review committee removed
on 16 September 2026, including automated monitoring that shuts a station down, optimizing
channel assignments, and dependence on third-party infrastructure. Those items are retired, and
they are not backlog for the team to pick up if time allows.

### Success tiers

The requirements above define the full system. The two-semester plan targets the objective tier;
the threshold tier alone is a complete, successful capstone.

- **Threshold (a successful capstone).** Registry and monitoring, deployed to a staging
  environment (R1, R3 and R5 at prototype level). **The acceptance test is a replay.** Load the
  archived spot record for August and September 2026 and have the system reproduce, on its own,
  the verification table in section 2: the same verdicts, the KD0EAG mismatch, the refusal to
  state a single channel for VY0ERC, the unlisted candidate stations, and an alert on N4RVE's
  outage raised within 48 hours of its start. Reproducing a known-good human analysis is how the
  team proves the monitor is right.
- **Objective (the project goal).** The threshold system in production at wsprsonde.hamsci.org,
  with the coordination workflow in use by the frequency coordinator (R2), alerts reaching real
  control operators, the public map and channel table live (R7), and the machine-readable feed
  consumed by the `polar-psws` maps (R6). R4's control point is delivered: the keep-alive daemon,
  the poll endpoint, and the operator interface for configuration and on/off. Demonstrate it on
  the bench by cutting the control link and showing the transmitter stop within the two to three
  minutes R4 allows, with the audit log to prove it. The non-functional requirements are in force
  once the site is public.
- **Stretch (beyond expectations).** The control point deployed to volunteer United States
  stations with their control operators' sign-off; a better channel-assignment algorithm than
  R2's placeholder rule, which the requirements explicitly invite; and uptime analytics over the
  retained monitoring history that answer "how much of 2026 was this station actually on the air"
  for the science.

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

- Requirements review with the WSPRSonde technical team (WB6CXC, G3ZIL, KD2ZHK and the advisor)
  and the other reviewers, including AI6VN and the PSWS team. The requirements document already
  carries the reasoning. The work is turning it into a testable specification with
  traceability, resolving the questions its section 10 leaves open, and agreeing on a revision
  with the WSPRSonde team. That agreed revision is the baseline the team builds against.
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
- **Milestones:** requirements agreed with the WSPRSonde team (mid-semester), architecture and
  design review, threshold system demonstrated on staging, replay validation passed.

### Semester 2 (Spring 2027): Coordination, Control, Deploy, Demonstrate

- Coordination workflow with collision and rule checking, put in front of the frequency
  coordinator and used for a real assignment.
- Device integration: read a real unit's own status report through its host computer, and land the
  three-way channel comparison of R2.
- Positive control, in the order the risk demands: design review first, then the keep-alive
  daemon and the poll endpoint, then the operator interface for configuration and on/off, then
  the bench harness against a WSPRSonde and a Raspberry Pi in the lab. Demonstrate the dead-man
  stopping the transmitter when the link is cut, and produce the audit log for it.
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
puts a transmitter on the air when it should not be. The review committee adopted its reading of
the regulations in September 2026, and that reading still awaits the judgement of someone who has
argued these rules in practice. The team should have a working registry and monitor, and an
agreed specification, before writing code that keys a radio.

## 7. Deliverables

1. Requirements specification agreed with the WSPRSonde team, with traceability from
   stakeholder needs to requirements and the open questions resolved (semester 1).
2. Technology trade study and architecture design document.
3. Working platform deployed at wsprsonde.hamsci.org.
4. Documented, versioned data feed and API with a published schema, data dictionary, and
   provenance manifest, citable by downstream consumers.
5. Automated test suite and continuous integration configuration.
6. Operations runbook: deployment, backup and restore, monitoring, and incident response, written
   for a volunteer maintainer.
7. Validation report: the replay against the archived record, and the faults the live system
   caught in service.
8. Positive-control package: design document, keep-alive daemon, poll endpoint, operator
   interface for configuration and on/off, bench test harness, and a demonstration report showing
   transmission stopping within the required interval.
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
  system property, and defending the design to the people whose licenses depend on it. This is
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

- **Real stakeholders and a written starting draft.** The requirements document accompanying
  this proposal is the product of a collaborator review round with the manufacturer, the frequency
  coordinator, and the data curator, and it records the reasoning behind each requirement. The
  reviewers are available to the team as customers.
- **A technical team for design questions**, reached in one email: Paul Elliott WB6CXC (hardware
  and firmware), Gwyn Griffiths G3ZIL (data analysis, WSPR and FST4W, databases), Gerard Piccini
  KD2ZHK (user interface) and the advisor. Majid Mokhtari, the University's research and lab
  engineer, arranges access to hardware.
- **A working prototype to start from.** This repository already holds the reconciled registry, a
  read-only WsprDaemon client, the channel-measurement code, the WSPRSonde detection method, and
  the data product that `polar-psws` consumes. It is a specification by example, and the team is
  free to keep, replace, or improve any of it.
- **Read access to the archives:** the WsprDaemon ClickHouse endpoint, the historical frequency
  table, and two Grafana dashboards built over it (per-station Doppler, and a co-channel view that
  is the collision check in working form).
- **Hardware for bench work:** a WSPRSonde and a Raspberry Pi host in the Scranton lab, for the
  device integration and the interlock harness.
- **Hosting on HamSCI infrastructure**, with the wsprsonde.hamsci.org domain and a staging
  environment.
- **Access to the manufacturer.** WB6CXC has answered detailed questions about the hardware's
  serial interface and dead-man behavior during the requirements review, on the record in this
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
| **BeaconBlaster** | The WSPRSonde's predecessor, still in service at one site. It has no dead-man timer, which is why it cannot meet the control requirement in R4. |
| **Callsign** | A station's government-issued identifier, such as W2NAF or DP0GVN. Public by convention. |
| **Channel offset** | A WSPRSonde's position within the 200 Hz WSPR window, in hertz above the bottom of it. One offset applies to all of a unit's bands, and the coordinator allocates them. |
| **ClickHouse** | The column-oriented database whose HTTP interface exposes the WsprDaemon spot archive. |
| **Control operator** | The licensed amateur responsible for a station's transmissions. May or may not be the person whose property the station sits on. |
| **Control point** | The location at which the control operator function is performed. The claim this system supports is that a phone can be one. |
| **Dead-man** | A timer in the WS-8 that shuts its transmitters down after a set interval with no traffic from the host computer, and re-arms when traffic resumes. Also called a watchdog. |
| **FST4W** | A newer digital mode, successor to WSPR, used by WSPRSondes for the same purpose. |
| **GPSDO** | GPS-disciplined oscillator. The reference that locks a WSPRSonde's transmit frequency to within a fraction of a hertz. |
| **Keep-alive** | Traffic from the host computer that re-arms the WS-8's dead-man. In this system the host sends it only while the server reports a control operator reachable. |
| **Grid square** | A Maidenhead locator: a four- or six-character code such as `FN21` or `CN88ln` that encodes latitude and longitude. Four characters is about 78 km across at mid-latitudes, which matters at a polar site. |
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
4. Manufacturer's answers on the WS-8 serial interface and dead-man behavior, issue tracker:
   https://github.com/HamSCI/wsprsonde.hamsci.org/issues
5. Turn Island Systems, WSPRSonde hardware: https://turnislandsystems.com
6. WsprDaemon: https://wsprdaemon.org
7. WSPRNet: https://wsprnet.org
8. WSJT-X, the software family that implements WSPR and FST4W: https://wsjt.sourceforge.io
9. WSPR message types and callsign encoding: https://dxplorer.net/wspr/msgtypes.html
10. 47 CFR Part 97, amateur radio service, via Cornell Legal Information Institute:
    https://www.law.cornell.edu/cfr/text/47/part-97 (§97.109 station control, §97.203 beacon
    station, §97.213 telecommand)
11. HamSCI Personal Space Weather Station: https://hamsci.org/psws
12. 2027 HamSCI Workshop, 17–18 April 2027, University of Scranton: https://hamsci.org/hamsci2027

---

*Interested students should contact Dr. Frissell (nathaniel.frissell@scranton.edu).*

*This project supports the HamSCI Personal Space Weather Station effort. The WSPRSonde deployment
is funded by the U.S. National Science Foundation under awards OPP-2332427, AGS-2432821,
AGS-2432822, AGS-2432823, and AGS-2432824.*
