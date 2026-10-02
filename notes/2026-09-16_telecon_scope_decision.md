# 2026-09-16 telecon: Phase 4 scope decision

## Decision (PI, N. A. Frissell W2NAF, on the telecon of 2026-09-16)

> "After reviewing this document, our team believes that automated monitor for the purpose of
> control shutdown is going to be too difficult for an undergraduate team to design and
> implement correctly in the next 6 months. Instead, I propose that this project just make a
> good faith effort towards putting a control point for the WSPRSondes in the control
> operator's pocket (smartphone) or computer. Therefore, let's just scope it this way: The
> requirement will be that the majority of WSPRSonde configurations and the ability to turn on
> and off the transmitter be availble to the control operator through the web app interface."

Status: **accepted as the scope for the capstone.** Verbatim above; wording of the replacement
requirement not yet drafted, pending the clarification in "Open against this decision" below.

**Confirmed on the same call**, when the cut was put back to the PI in the assistant's words:

> "Yes, this cuts down the automated monitoring feature. That is too complex for the initial
> version of this project." — NAF, 2026-09-16

Note "**initial version**". The automated monitor is **deferred, not retired**: it belongs in a
post-capstone backlog rather than in §11 (explicitly out of scope). Confirm with the PI before
Draft 1.0 which of the two it is.

## What it supersedes

To be written into Draft 1.0 once the clarification lands. Provisionally:

- **R4 (positive control)** narrows from an automated interlock to an operator-facing control
  point: configuration and transmit on/off through the web app.
- **Q10.1, Q10.2 and Q10.3** were all framed against the interlock. Q10.2 (keep-alive cadence
  acceptable to operators?) and Q10.3 (interlock mandatory for funded units?) largely dissolve.
  Q10.1 (is §5's reading right?) does **not** dissolve; see below.
- **§9.1's** "Phase 4 as design-plus-bench-prototype" becomes deliverable work rather than a
  design exercise, which is a simplification for the student team.

## Open against this decision

**Does the web-app control point replace the keep-alive daemon (R4.3), or sit alongside it?**

This is the one question that changes what gets built. The two are different things and only one
of them is the hard part:

- The **automated monitor** the PI is cutting is the fault-detection-and-act system: watch the
  spot record, decide a station is misbehaving, shut it down. Correctly scoping "misbehaving" is
  genuinely hard, and cutting it is a sound call for a six-month undergraduate project.
- The **keep-alive daemon** is a heartbeat on the host computer with a three-minute dead-man in
  the WSPRSonde firmware. It is small. §5 of the requirements rests its compliance argument on
  it, via §97.213(b), which bounds the renewal interval over a telecommand control link at three
  minutes.

If the keep-alive goes too, §5 needs rewriting, because the compliance case would then rest on
the control operator being reachable and acting rather than on an automatic provision. That is
the PI's call to make, but it should be made knowingly rather than absorbed into this one.

**Not verified this session.** The §97.213(b) reading above is quoted from §5 of the
requirements document as it stands (primary sources read 2026-08-13). Per the project's rule,
any change to §5 must be re-verified against the current eCFR before it is written.

---

# 2026-09-16 telecon: second decision, frequency coordination simplified

## Decision (review committee, reported by the PI on the same call)

> "Our review committee decided that the question of how to coordinate WSPRSonde frequency
> assignments and how many WSPRSondes the world can support is not at all straightforward.
> Likewise, the scientific conclusions that can be made from looking at received WSPR data will
> be greatly affected by the choices made here, as well as a proper understanding of how the
> WSPR mode propagates and gets decoded. These decisions are out-of-scope for an initial
> prototype website and need to be considered carefully.
>
> Therefore, we need to simplify the requirements for this project as much as possible. We
> simply need the ability to go into the website and make and track frequency assignments.
> Therefore, we are going to use a very simple scheme for frequency assignment: First, try not
> to reuse frequencies. When there are so many wspsondes that you do have to reuse frequencies,
> do so that the reuse is evenly distributed. Make sure re-used frequencies are as
> geographically separate as possible. This is a recommended starting algorithm, but a better
> one could be investigated by an interested student."

Status: **accepted.** Wording for Draft 1.0 pending the PI's confirmation of the restatement
below.

## Restatement for implementation (pending confirmation)

The verbal rule as three ordered steps a student can implement:

1. **Prefer an unassigned channel.** If any channel on the grid has no unit assigned to it,
   assign one of those.
2. **Otherwise pick the least-used channel**, that is, the one with the fewest units currently
   assigned to it. This is the "evenly distributed" clause: it minimises the largest number of
   units sharing any one channel.
3. **Break ties by geographic separation**, choosing the candidate channel whose nearest
   already-assigned unit is furthest away. Distance is great-circle between Maidenhead locator
   centres, which the registry already carries and `src/wsprsonde/maidenhead.py` already
   computes.

Stated assumption, which the decision explicitly puts out of scope: **geographic separation is
used as a proxy for non-interference.** It is not the same thing on HF, because a receiver
between two distant transmitters can hear both. The committee's decision is that getting this
right requires a proper treatment of WSPR propagation and decoding, and that treatment is
deferred. The prototype should say in its interface that the rule is a heuristic.

## What this changes in the requirements

- **R2.2's grid**, **R2.3's guard band** and the whole of the channel-capacity analysis become
  **advisory rather than binding on the prototype**. Technical Note 1 stays as the record of the
  analysis; its proposed changes to R2.2, R2.3 and R2.4 move to the deferred list.
- **The WS-8 drift-over-temperature question is out of scope for the prototype.** It was the
  open item that set the grid step after the measurement floor stopped setting it. It returns
  when the careful consideration happens.
- **Q10.8 is partly decided rather than deferred.** Rule 1, "try not to reuse frequencies",
  says directly that ZD7GWM and N4RVE should not both sit on 100 Hz. One of them moves. Which
  one, and when, is still the coordinator's call, and KH2R/DP0GVN at 1 Hz apart is still open.
- **Channel exhaustion stops being a failure.** The registry has two spare channels against five
  further NSF units; under this algorithm the system reuses gracefully instead of failing to
  allocate. That removes the urgency behind the capacity note's recommendation.
- **R2.1, R2.5, R2.6 and R2.7 are unaffected.** Recording assigned/configured/measured, comparing
  them, the §97.203(b) same-site rule and coordinating non-HamSCI units all stand.
- **R2.4** (check against non-sonde WSPR activity) needs a decision: it is a check the simple
  algorithm does not perform. See the open question below.

## Open against this decision

**Does R2.4 survive?** The simple algorithm coordinates WSPRSondes against each other and
ignores everyone else on the band. R2.4 says check a proposed assignment against all WSPR
activity in the window, and Gwyn's `wd2` dashboard already does it, so adopting it is cheap.
Keeping R2.4 as a **view the coordinator can consult**, rather than as an automatic gate, looks
like the version that survives this simplification. Put to the PI.

---

## Q0 answered: the keep-alive daemon is per-unit configurable

> "Make it a per-wsprsonde configuration option that can be enabled or disabled in the web
> dashboard." — NAF / review committee, 2026-09-16

**Resolution:** R4.3 stays in scope. The keep-alive daemon is built, and whether it is active is
a per-unit setting exposed in the web dashboard alongside the other configuration of the second
scope decision.

**Why this is the right answer rather than a compromise.** §97.213(b) binds **US** stations. A
large part of the network is not US-licensed: ZD7GWM (St Helena), DP0GVN (Antarctica, German
licence), TI4JWC (Costa Rica), VU24JD (India), and others. A single global setting would either
impose a US rule on stations it does not govern, or drop it for stations it does.

**A jurisdiction warning was proposed and declined.** The assistant recommended that the
dashboard warn, and the record flag, when the keep-alive is disabled on a US-licensed station,
naming §97.213(b), since the registry already carries `country` per unit. The PI's decision:

> "No, just leave it as a manual configuration per wsprsonde for now." — NAF, 2026-09-16

**Write it as a plain per-unit manual setting**, with no jurisdiction logic and no warning. Note
for whoever picks this up later: §5 still states what §97.213(b) requires of US stations, and
that text is unchanged, so the rule is on the record in the document even though the prototype
does not enforce or surface it. Setting the toggle correctly is the control operator's
responsibility, which is consistent with where this project puts every other operating decision.

Also agreed on the same call, on the frequency-assignment restatement:

> "I agree with this." — NAF, 2026-09-16, on geographic separation being recorded as an explicit
> proxy for non-interference rather than as the thing itself.

## Still open at the end of this exchange

- **R2.4**: keep the all-WSPR-activity check as a coordinator-consultable view rather than an
  automatic gate? Assistant recommends yes. Awaiting the PI.
- Whether the automated monitor is **deferred or retired** (see the first decision above).
- The §10 open questions, none of which have been answered on the call yet.

---

## Automated monitor: retired, not deferred

> "retire" — NAF, 2026-09-16, asked directly whether the automated monitor was deferred to a
> post-capstone backlog or retired.

**Supersedes** the provisional reading recorded under the first decision above, which had it as
deferred on the strength of the phrase "initial version". It goes to **§11, explicitly out of
scope**, and no backlog item is created. Do not reintroduce it into Draft 1.0 as future work.

---

## R2.4 resolved: kept as a view

> "Keep it as a view (my recommendation)" — NAF, 2026-09-16.

R2.4 stays in Draft 1.0, reworded from a check into a **coordinator-consultable view**: a panel
or link showing the proposed channel against all WSPR activity in the window, opened before an
assignment is confirmed. **Not an automatic gate**, and it does not block an assignment. The
implementation is Gwyn Griffiths' `wd2` co-channel dashboard (§4.6) with the frequency populated
from the registry instead of typed in, which is the proposal he made in issue #8.

---

## §10 open questions answered on the call

**Q10.10, scope boundary: transmit side only.** WSPRSondes only; PSWS receive instruments stay
in §11 as out of scope. Rob Robinett's original framing of a broader "HamSCI monitoring and
configuration website" is noted and not adopted for this project. No extensibility work is to be
done up front against a receiver use case nobody has specified.

**Q10.4, registry ownership: the system is the record, the frequency coordinator is the
backstop.** Hosts and control operators maintain their own entries through the web app; the
coordinator resolves disputes. No named curator role is created.

*This departs from what Gwyn Griffiths asked for.* He was explicit in review that he wanted a
curator with hands-on access to the hardware, and §10 recorded it that way. The decision is the
PI's to make (P8), and it is made; **tell Gwyn directly rather than letting him find it in
Draft 1.0**, since he raised it and the answer went the other way.

**Q10.12, customer for the student team: the PI (W2NAF).** Named as primary customer and first
point of contact.

Practical note for §9.1: the PI is the front door, and the team will still hit questions only
WB6CXC can answer (what a WSPRSonde can be told to do, how assignments are actually issued) and
only G3ZIL can answer (the existing `wsprsonde` table, the spot archive, what the dashboards
already do). Route them through the PI, but both need to be reachable, or those questions stall.

**Q10.12 REVISITED and superseded.** The earlier answer on this call, "the PI is the customer",
is retired. The PI reopened it and replaced it with a team approach:

> "For the contact, we are going to use a team approach:
>
> 1. Paul WB8CXC is going to answer WSPRSonde hardware and firmware questions.
> 2. Gwyn G3ZIL is going to be responsible for data analyis/WSPR/FST4FW modulation questions and
>    database questions.
> 3. Gerard KD2ZHK is going to be responsible for user interface questions.
> 4. Majid Mohktari is going to be responsible for getting students access to hardware. He is the
>    university resaerch and lab engineer.
> 5. Nathaniel Frissell is going to be the on-campus POC that can address other questions as
>    needed. He will work with the computer science faculty who is responsible for the capstone
>    project.
>
> In general, the student can email the "technical team" all at once for design questions, which
> includes Paul, Gwyn, Gerard, and Nathaniel. Majid only needs to be involved if access to
> hardware is required." — NAF, 2026-09-16

**For §3 and §9.1 of Draft 1.0:**

| Contact | Responsible for |
|---|---|
| Paul Elliott **WB6CXC** | WSPRSonde hardware and firmware |
| Gwyn Griffiths G3ZIL | Data analysis, WSPR/FST4W modulation, database |
| Gerard Piccini KD2ZHK | User interface |
| Majid Mokhtari | Student access to hardware (university research and lab engineer) |
| Nathaniel Frissell W2NAF | On-campus POC, everything else; liaison to the CS capstone faculty |

**Routing rule:** design questions go to the **technical team** as one email, meaning Paul, Gwyn,
Gerard and Nathaniel together. Majid is involved only when physical hardware access is needed.

*Two identifiers corrected against the project record when transcribing: the callsign was
dictated as WB8CXC and is **WB6CXC** throughout this project; the surname was dictated
"Mohktari" and is spelled **Mokhtari** in `CLAUDE.md`. The verbatim quote above is left as
dictated (W12); the table carries the corrected forms.*

**Q10.8, the two live channel conflicts: not a project decision.**

> "This is not a decision that is part of the project. It will be addressed when the system is
> actually deployed." — NAF, 2026-09-16

Q10.8 leaves the open-questions list. Neither conflict is for the capstone or for Draft 1.0 to
settle: KH2R/DP0GVN 1 Hz apart by assignment, and ZD7GWM/N4RVE co-channel on 100 Hz within
0.4 Hz on five bands.

**What stays.** §2.3 keeps both collisions as *evidence*, because they are the case for building
the system at all, and §2.2 keeps the measurements. What is removed is any expectation that this
project resolves them. When the system is deployed, the assignment rule of the second decision
above will flag the ZD7GWM/N4RVE pair on its own, which is the right time to act on it.

**Q10.11, capstone fit: R1–R3 stand as written.** No further cuts. With Phase 4 rescoped and the
automated monitor retired, the registry, monitoring and coordination requirements are accepted as
reasonable for one academic year.

**Q10.3 resolved as a side effect.** "Should the interlock be mandatory for HamSCI-funded units
and optional for privately owned ones, or uniform?" is answered by the per-unit keep-alive
toggle: it is neither mandatory nor uniform, it is configured per WSPRSonde by the control
operator. Q10.3 leaves the list.

## State of §10 at the end of the call

| Q | Disposition |
|---|---|
| 10.1 | **Open.** §5's characterisation still matters, since the keep-alive stays for units that enable it. Needs Paul, Rob, AC0G, WA4KFZ. |
| 10.2 | **Open, narrowed.** Whether licence holders accept that a MeshCentral outage takes an enabled station off the air, and how much redundancy the keep-alive path needs. |
| 10.3 | **Closed** by the per-unit toggle. |
| 10.4 | **Closed.** System of record, coordinator as backstop. Departs from G3ZIL's request; tell him. |
| 10.5 | **Open remainder.** Does a WS-8 carry a readable serial number, so R1.1 can use the hardware's own identifier? Paul. |
| 10.6 | **Still unanswered.** MeshCentral as the identity provider: acceptable, and does it scale to non-HamSCI participants (R2.7)? Was put to the room and not reached. |
| 10.7 | **Open.** DC7TO, N9VP, G0PKT unidentified; who issued W8GPS its 60 Hz channel. Paul. |
| 10.8 | **Removed.** Deployment-time operational decision, not a project decision. |
| 10.9 | **Open.** Non-US jurisdictions. DK5HH, VE3KTB, TI4JWC. |
| 10.10 | **Closed.** Transmit side only. |
| 10.11 | **Closed.** R1–R3 stand. |
| 10.12 | **Closed.** Team approach, routed by subject; see the table above. |
| 10.13 | **Open.** Mode-encoding gaps. Rob AI6VN, Dave W0DAS, Hyomin Kim, DK5HH. |

Everything still open is a question for a named person outside this call, with one exception:
**Q10.6 needs this group** and was not reached.

## Q10.6 answered: identity provider becomes a trade study

> "Yes, this should be part of the trade study. I think there is some question as to whether it
> make sense to continue using meshcentral or not. Right now, it is certainly an option, and
> possibly the preferred one." — NAF, 2026-09-16

**R5.3 is upgraded from a list of options into a deliverable.** It already says "Options to
weigh: MeshCentral accounts (already issued to hosts), a HamSCI SSO if one exists, or LoTW/ARRL
identity", with callsign self-assertion excluded. Draft 1.0 turns that into an explicit **trade
study the student team performs and documents**, with MeshCentral named as an option and the
current front-runner, and with whether to continue using MeshCentral at all stated as an open
question rather than an assumption. Q10.6 leaves §10, because it now has a home in R5.

**Scope note for whoever writes the trade study.** Identity is not the only thing MeshCentral is
doing here, and the study should say so plainly. MeshCentral also carries the agent state that
R3.5 cross-checks against the spot record, and it manages the host computer that runs the
keep-alive daemon of R4.3. So "do we keep MeshCentral" is entangled with the control path and
not only with login. A study that weighs it as an identity provider alone will reach a
conclusion the rest of the system cannot act on.

**R5.4 constrains the answer**: multi-factor authentication is required for any account that can
enable transmission, and that requirement now binds harder than it did this morning, because
after the first decision the web app *is* the control point. Any candidate that cannot do MFA is
out regardless of how it scores elsewhere.

---

## MeshCentral required for the control path — SUPERSEDES the R5.3 trade study

The PI asked whether making MeshCentral required would simplify the project, and accepted the
boundary the assistant proposed:

> "If we just make mesh central required, does that simplify things?" […] "Yes, i agree with
> this." — NAF, 2026-09-16, the second quote agreeing to requiring MeshCentral for the control
> path but not for registration.

**This retires the trade-study decision recorded earlier on this same call.** That entry said
R5.3 becomes "a trade study the student team performs and documents". **Do not act on it.**
R5.3 is now decided: MeshCentral is the identity and control transport, and the alternatives
(HamSCI SSO, LoTW/ARRL identity) are not evaluated by this project.

**The decision, in two tiers:**

| Participation | MeshCentral | What they get |
|---|---|---|
| Control operator with transmit on/off authority | **Required**, MFA enabled (R5.4) | Full control point: configuration and transmitter on/off through the web app |
| Registry and coordination only | **Not required** | A registry entry and a frequency assignment, maintained by the coordinator. No control, no agent on their hardware. |

**Why the second tier exists.** R2.7 requires that a non-HamSCI unit be registerable "without
implying HamSCI operates it". Coordinating a channel for ZD7GWM needs a registry row, not remote
access to a volunteer's Pi on St Helena. Requiring the agent for registration would have made
R2.7 unimplementable in practice, and would have made Paul Elliott's outside-HamSCI users
uncoordinatable.

**Why it simplifies, beyond removing the trade study.** The project no longer has to build,
deploy, update and secure its own agent on every host computer in order to reach the keep-alive
daemon and the transmitter. That was among the largest remaining pieces of work. R3.5's
agent-state cross-check also comes free, since MeshCentral is now guaranteed present wherever
control exists.

**Verified this session, because R5.4 could have blocked it.** MeshCentral supports MFA: TOTP
per RFC 6238 (Google Authenticator and compatible), FIDO2, Yubikey OTP, Duo, and push. Sources:
<https://ylianst.github.io/MeshCentral/meshcentral/security/> and
<https://meshcentral2.blogspot.com/2019/01/meshcentral2-two-step-authentication.html>, both read
2026-09-16.

**Accepted risks, recorded so they are not rediscovered as surprises.** A hard dependency on a
third-party open-source project, and the concentration risk already open as Q10.2: a MeshCentral
outage takes every keep-alive-enabled station off the air. The per-unit keep-alive toggle is the
operator's escape from the second one.

---

## Q10.1 decided: remote control under §97.109(c)

> "We are going to state this is remote control because this interface will give control
> operator the facility to control the WSPRSonde's functions, including transmitter on/off, from
> their smartphone or computer. Therefore, the control operator is at the control point of the
> transmitter." — NAF, 2026-09-16

**Re-verified against the current eCFR on 2026-09-16**, per this project's rule that regulatory
claims are verified rather than recalled. Both sections read this session:

- **§97.109(c)**: "When a station is being remotely controlled, the control operator must be at
  the control point. Any station may be remotely controlled." Remote control is defined as the
  use of a control operator who **indirectly manipulates the operating adjustments in the station
  through a control link**. <https://www.ecfr.gov/current/title-47/chapter-I/subchapter-D/part-97/subpart-B/section-97.109>
- **§97.213**: telecommand of a station requires (a) a radio or wireline control link between the
  control point and the station sufficient for the control operator to perform their duties, with
  fibre and other telecommunication services counted as wireline; and **(b) "Provisions are
  incorporated to limit transmission by the station to a period of no more than 3 minutes in the
  event of malfunction in the control link."**
  <https://www.ecfr.gov/current/title-47/chapter-I/subchapter-D/part-97/subpart-C/section-97.213>

**The decision is supported, and the project is what supports it.** The web app is the control
link §97.109(c)'s definition of remote control requires. Before this project there was arguably
no link at all, so the characterisation improves with the system rather than merely being
asserted about it. This is a good argument and Draft 1.0 should make it in §5.

**What it carries with it.** Choosing remote control invokes §97.213, and (b) is not optional.
The three-minute limit on transmission after a control-link malfunction **is** the keep-alive
daemon plus the firmware dead-man. Consequence for the per-unit toggle decision recorded earlier
on this call:

- **US-licensed stations: the keep-alive toggle is required-on.** A US station with it disabled
  has no provision meeting §97.213(b).
- **Non-US stations: genuinely configurable**, since Part 97 does not reach them. Their own
  administrations' rules are Q10.9, still open.

Draft 1.0's §5 states this. **The warning UI is not reopened**; the PI declined it earlier on
this call and that decision stands. The rule is stated in the document; the software does not
enforce or surface it; setting the toggle correctly is the control operator's responsibility.

The document's existing caveat that it is not legal advice stays, unchanged.

---

## Q10.2 answered: keep-alive built, toggle stays optional, redundancy via a control-operator pool

> "We are going to implement keep-alive, but it is still going to be an optional toggle. For the
> first version, we don't need redundancy built-in. For the redundancy, we want the ability to
> assign multiple simultaneous control ops. This way the keepalive can be sent to a pool of
> control ops, where only one positive response is required to keepalive." — NAF, 2026-09-16

**The toggle stays optional, reaffirmed after the §97.213(b) finding.** The assistant raised that
a US station with the keep-alive disabled has no provision meeting §97.213(b); the PI's decision
is that the toggle remains optional in the software regardless. Recorded as the PI's call, not an
oversight. §5 states the rule, the software neither enforces nor surfaces it, and setting the
toggle correctly is the control operator's responsibility. **Do not re-raise this.**

**No redundancy in version 1.**

**New requirement: multiple simultaneous control operators per unit.** A unit may have a pool of
assigned control operators, and the station stays up while **any one** of them responds.

**What counts as a response, asked and answered on the call: automatic, from a logged-in
device.** Any designated control operator's phone or computer with an authenticated session
responds in the background. The pool is redundancy of **reachability**, not a human attention
requirement. No human action in normal operation.

### Design consequence for R4.3, which needs rewriting

This relocates where the keep-alive originates. R4.3 currently describes a keep-alive daemon on
the **host computer**. Under this decision the chain is:

```
control operator's authenticated device  (the control point, §97.109(c))
        -> internet / MeshCentral
        -> host computer
        -> WSPRSonde firmware dead-man (3 minutes, §97.213(b))
```

The heartbeat has to **originate at the control point**, because that is what §97.213(a)'s
control link connects and what makes the operator "at" it. A daemon that keeps the sonde alive
from the host Pi alone would satisfy the firmware timer while proving nothing about any control
operator being reachable. The host-side daemon becomes a relay and validator for a token that
originates in an authenticated control-operator session, and it stops relaying when no member of
the pool is contactable.

**Design note for the student team, not a decision needed now.** A backgrounded or sleeping phone
must still count as reachable, or beacons will drop off the air nightly. That argues for a
server-side session token with a heartbeat the server maintains on the operator's behalf while
the session is valid, rather than requiring the app to be in the foreground. Worth stating in the
requirement so it is not discovered late.

### Architecture settled: the server is the intermediary

> "The server can act as the intermediary. wsprsonde.hamsci.org will keep track of all logged in
> control devices. The wsprsonde pi can then ping wsprsonde.hamsci.org to see if the required
> control is available." — NAF, 2026-09-16

**This supersedes the "heartbeat originates at the control point" sketch above**, which had the
operator's device driving the chain. The settled design:

```
control operator devices  --login/session-->  wsprsonde.hamsci.org
                                                     ^
                                                     | poll: "is a control op available?"
                                              WSPRSonde host Pi
                                                     |
                                              WSPRSonde firmware dead-man (3 min, §97.213(b))
```

1. The server tracks every logged-in control device and therefore knows, per unit, whether any
   member of that unit's control-operator pool is currently reachable.
2. The host Pi **polls the server**, at an interval shorter than the firmware dead-man.
3. A "yes" causes the Pi to feed the dead-man. A "no", or an unreachable server, means the Pi
   stops feeding it and the sonde ceases transmitting within three minutes.

**Why this is the right shape.** The Pi pulling rather than the operator's device pushing means a
Pi that loses its own internet connection stops receiving "yes" and goes quiet by itself, which
is exactly the §97.213(b) behaviour on control-link malfunction. It needs no push
infrastructure, no foreground mobile app, and no open inbound port at the host site.

**Correction to an earlier statement in this record and on the call.** The assistant said that
making MeshCentral required meant a MeshCentral outage would take every keep-alive-enabled
station off the air. **That is not true under this architecture.** The Pi polls
`wsprsonde.hamsci.org` directly; MeshCentral is out of the keep-alive path and remains the
identity provider and remote-administration channel. The dependency moves to our own server.

**Accepted risk, stated once.** `wsprsonde.hamsci.org` becomes a single point of failure for the
whole network: if the server is down, every keep-alive-enabled station stops transmitting within
three minutes. The PI has decided there is no redundancy in version 1. Server uptime therefore
becomes an operational requirement in its own right, and belongs in §7 (non-functional
requirements) rather than being left implicit.

**Design note, no decision needed now.** The poll interval must be comfortably shorter than the
three-minute dead-man, so that a single missed poll does not take a healthy station off the air.
Something near 30 to 60 seconds gives several retries inside the window.

---

## MeshCentral removed from the project entirely — SUPERSEDES the "required for the control path" decision

> "Don't mention meshcentral at all in this project. We may still use it, but should not be in
> scope of this project." — NAF, 2026-09-16

**This retires two earlier decisions from this same call**, in order: the R5.3 trade study, and
then "MeshCentral required for the control path, not for registration" with its two-tier
participation table. **Do not act on either.** The two-tier table is gone with them: if the
project owns identity, there is no reason a registry-only participant cannot simply have a login.

**The project depends on nothing but our own server and software.** MeshCentral may continue in
use operationally by the PSWS team, and that is outside this document.

### What each of MeshCentral's four jobs becomes

| Job | Replacement |
|---|---|
| Identity, login, MFA | Our own authentication in the web app. Better for R2.7: an outside-HamSCI control operator needs no third-party account to log in. |
| Keep-alive and control path | Already ours, per the architecture decision above: the Pi polls `wsprsonde.hamsci.org`. |
| Pi liveness for R3.5 | Free from that same poll, and a better signal than agent state. R3.5's three-outcome table is rebuilt on our own poll data. |
| Remote administration of the host Pi | **Out of scope.** Not replaced, not required. How the PSWS team gets a shell on a Pi is an operational matter this system does not address. |

### Edits required for Draft 1.0 (17 references in the requirements, plus the project description)

- **§4.1** (MeshCentral as an existing system): remove the subsection.
- **§4 architecture diagram** (~line 859): remove the `meshcentral` node.
- **§5.5** (~line 529): the argument that "a script, a diagnostic session, or an open MeshCentral
  terminal all pet the dog" is still a **valid and important** point about keep-alive design. Keep
  the argument, restate it generically as any process on the host able to reach the server.
- **R3.5**: rewrite the three-outcome table against our own poll data instead of agent state.
- **R5.3**: MeshCentral, HamSCI SSO and LoTW/ARRL all leave the options list. Identity is ours.
  R5.4's MFA requirement stands and now falls to us to implement.
- **R6.2**: remove the integration.
- **§9 phasing table** (~line 897): drop the cross-check from Phase 2.
- **§11**: "Replacing WsprDaemon, WSPRNet or MeshCentral" becomes WsprDaemon and WSPRNet.
- **Q10.2 and Q10.6**: both already closed on this call; their MeshCentral wording goes with them.
- **`docs/project_description.md`**: reconcile.

### One exception, recommended

**The change log keeps its existing entries unchanged.** Entries at lines ~1244 and ~1275 record
what Drafts 0.x actually said, including MeshCentral's role as keep-alive transport. Editing them
would falsify the document's own history of how it evolved, which P7 forbids. The forward-looking
content carries no MeshCentral; the historical record of earlier drafts stays accurate, and
Draft 1.0's own change-log entry states that MeshCentral was removed from scope and why. Raise
with the PI if he wants it gone from the history too.

---

## Remaining §10 answers

**§5.5's keep-alive argument: restate generically.** "That is fine." — NAF. Keep the point that a
script or a diagnostic session can satisfy a keep-alive without any control operator paying
attention; drop the MeshCentral example.

**Q10.5: yes, a WS-8 carries a host-readable serial number.** — NAF, 2026-09-16.

R1.1's unit identifier becomes **the hardware's own serial**, not one we invent. This matters
more than it looks: units get re-sited and re-called, and a hardware serial survives both. It
also gives R1.7's shipping pipeline a key that exists before the unit has a callsign or a site.
Q10.5 closes completely; the callsign-suffix half was already closed.

**Q10.7: out of scope for this project description.** — NAF.

The unidentified transmitters (DC7TO, N9VP, G0PKT) and W8GPS's uncoordinated 60 Hz channel leave
§10. As with Q10.8, **§2.4 keeps them as evidence**: they are the case for R3.6 running the
detection scan on a schedule, and W8GPS is the worked example of a unit appearing after a scan.
What is removed is any expectation that this project identifies them.

**Q10.9: US rules only.** — NAF: "Just do US rules for now. Even at that, we are making the keep
alive a toggle-option."

§5 covers 47 CFR Part 97 and does not attempt ISED, BNetzA, Costa Rican or Indian requirements.
Q10.9 leaves §10. §5 should say plainly that it is US-only and that operators outside the US are
responsible for their own administrations' rules, which is consistent with the toggle being a
per-unit setting the control operator owns.

**Q10.13: the PI asked for the question to be explained.** Explanation given on the call; answer
pending. See the next section.

## Q10.13 resolved by splitting it

> "Yes, figuring out historical data is out of scope. But it is in scope to make sure the control
> system sends the correct number." — NAF, 2026-09-16

**Out of scope:** why `wsprdaemon.spots` changed its WSPR-2 encoding three times between July 2024
and March 2026, and whether a second transmitter signs DP0GVN at Neumayer. Q10.13 leaves §10.
R1.4 becomes a one-line requirement: **mode history comes from the unit record**, not from
re-deriving it out of the spot archive. §2.2 keeps the measurements as evidence.

**In scope, and this is the sharper requirement:** when the system writes a mode anywhere, it
must write the encoding that destination uses.

### The requirement this becomes

**Store mode by name; translate at every boundary.** The system's internal representation is the
mode's name (`WSPR-2`, `WSPR-15`, `FST4W-120`, `FST4W-300`). A bare number is never stored as the
mode and never copied between destinations. Every read and every write passes through an explicit
per-destination mapping.

Three encodings are known to be in play, and they disagree:

| Mode | `wspr.rx` / WSPRNet | `wsprdaemon.spots` and the `wsprsonde` table | WSPRSonde firmware |
|---|---|---|---|
| WSPR-2 | 1 | 2 | **unknown** |
| WSPR-15 | 2 | 15 | **unknown** |
| FST4W-120 | 3 | 3 | **unknown** |
| FST4W-300 | 4 | 6 | **unknown** |

The first two columns were measured and are in §2.2 of Draft 0.9. They **agree on FST4W and
disagree on WSPR**, which is what makes a mistake here survive review: it is right about every
FST4W station and wrong about every WSPR one.

This strengthens rather than replaces R1.3, which already says to store the mode by name with
each source's number beside it. Draft 1.0 extends it from reading to writing, and the per-source
codes in `data/wsprsonde_stations.csv` are reframed as a **translation table** rather than as
history.

### New open question, replacing Q10.13

**What encoding does the WSPRSonde firmware itself use for mode?** The control system now
configures the unit, so it has to write a mode value the WS-8 will accept, and the third column
above is blank. This is in scope by the PI's decision and it is the one piece of it nobody here
can answer. *(Paul Elliott WB6CXC.)*
