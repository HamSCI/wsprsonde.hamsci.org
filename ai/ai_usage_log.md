# AI Usage Log — wsprsonde.hamsci.org

This log records all substantive AI-assisted sessions for the project
"HamSCI WSPRSonde Network — Registry, Frequency Coordination and Management System".

Required per University of Scranton AI Policy, HamSCI Generative AI Use Agreement, NASA AI guidance, NSF AI guidance, and NSF expectations for awards OPP-2332427 and AGS-2432821–2432824.

---

<!-- Append new entries below this line, newest at the bottom. Use the format produced by the /commit command. -->

## [2026-04-25 13:26 EDT]

- **Tool**: Claude (Anthropic), claude-opus-4-7
- **Session Purpose**: Fix invalid `$schema` URL in `.claude/settings.json` so Claude Code stops rejecting the file (caught while using a downstream project scaffolded from this template).
- **Sections/Files Affected**: `.claude/settings.json`
- **Nature of Contribution**: Bug fix
- **Human Review Status**: Reviewed and verified
- **Git Hash**: 839ee05

## [2026-04-25 13:31 EDT]

- **Tool**: Claude (Anthropic), claude-opus-4-7
- **Session Purpose**: Align template with the `.claude/` folder anatomy described in https://blog.dailydoseofds.com/p/anatomy-of-the-claude-folder — gitignore the personal-override file and scope language-specific rules to relevant file types so they don't load when not applicable.
- **Sections/Files Affected**: `.gitignore` (added `CLAUDE.local.md`), `.claude/rules/latex-writing.md` (added `paths:` frontmatter scoping to `.tex`/`.bib`/`.cls`/`.sty`), `.claude/rules/python-code.md` (added `paths:` frontmatter scoping to `.py`/`pyproject.toml`/`requirements*.txt`)
- **Nature of Contribution**: Configuration / scaffolding refinement
- **Human Review Status**: Reviewed and verified
- **Git Hash**: e229ba5

## [2026-08-13 16:42 EDT]

- **Tool**: Claude (Anthropic), claude-opus-5[1m], via Claude Code
- **Session Purpose**: Instantiate this repository from the `ai_project_template` scaffold for the WSPRSonde project. Two deliverables: (1) reconcile the four scattered records of the WSPRSonde network into a curated registry and build a verified, up-to-date location product for overlay on the `polar-psws` station maps; (2) draft a requirements document for a proposed web-based WSPRSonde management system covering registry, frequency coordination, on-air monitoring and control-operator positive control, for circulation to collaborators.
- **Sections/Files Affected**:
  - Created: `data/wsprsonde_stations.csv` (curated registry, 21 units / 20 sites);
    `src/wsprsonde/{__init__,maidenhead,wsprdaemon,stations,build_locations}.py`;
    `tests/test_{maidenhead,stations,wsprdaemon}.py` (57 tests, all passing);
    `pyproject.toml`; `docs/requirements_wsprsonde_management_system.md`;
    `products/{wsprsonde_locations.csv,wsprsonde_locations_manifest.json,wsprsonde_candidates.csv}` (generated)
  - Rewritten from template placeholders: `CLAUDE.md`, `README.md`, this log
  - Modified: `.gitignore` (added `reference/`)
- **Nature of Contribution**: Data reconciliation from primary sources; code generation with tests; live database querying and analysis; requirements drafting; documentation.
- **Sources consulted**: `reference/20260813_wsprsonde_location_email.olm` (email thread 2026-07-31 to 2026-08-06 and its two attachments: `G3ZIL_WsprSonde_Metadata_V1-1.xlsx` rev. 2025-05-11, and WSPRSonde Shipping List #1); `wsprsonde` table on `wd10.wsprdaemon.org` PostgreSQL (139 rows); live queries against `wspr.rx` on the WsprDaemon ClickHouse endpoint; 47 CFR §§97.3, 97.109, 97.203, 97.213 read from Cornell LII; hamsci.org and turnislandsystems.com public pages.
- **Human Review Status**: **Pending review.** Specific items requiring the PI's verification before circulation or use:
  1. **§5 of the requirements document** (FCC Part 97 analysis, including the conclusion that WSPRSonde HF frequencies fall outside the automatic-control segments of §97.203(d) and therefore operate under remote control). Rule text was read from a secondary source (Cornell LII) because eCFR blocked automated access; it must be re-verified against the current eCFR, and the reading should be reviewed by someone competent in Part 97.
  2. **`data/wsprsonde_stations.csv`** — a reconciliation of four sources that disagree. Approximate dates (recorded where the source said "mid 2023", "Aug-24?"), the N4RVE/WB6CXC callsign attribution at Friday Harbor, and the four city-derived grid squares for pending shipments are all inferences, flagged in the `notes` column.
  3. **`ok_to_list_public`** is `unknown` for most stations because the source column was blank. No station should be published on that basis.
  4. **The four unlisted candidate transmitters** (DC7TO, ZD7GWM, N9VP, G0PKT) are the output of a detection heuristic, not confirmed WSPRSondes.
  5. Personal data (host names, street addresses, emails, phone numbers) was deliberately excluded from all tracked files; `reference/` was gitignored. Confirm nothing leaked before the first push.
- **Git Hash**: a9d7a50 (polar-psws vendored copy: 704bef1)

## 2026-09-02 22:09 UTC
- **Tool**: Claude (Anthropic), claude-fable-5-1, via Claude Code
- **Session Purpose**: Extend the review list of the WSPRSonde management-system requirements document (Draft 0.1) with four additional reviewers named by the PI: Phil Karn KA9Q, Jonathan D. Rizzo KC3EEY, Kristina Collins KD8OXT and Dave Larsen KV0S.
- **Sections/Files Affected**: `docs/requirements_wsprsonde_management_system.md`, header "Review list" only.
- **Nature of Contribution**: Edit. Names and callsigns were supplied by the PI except KA9Q, which the assistant took from the email domain he supplied; email addresses were deliberately not written into the document.
- **Human Review Status**: Reviewed and verified (PI dictated the names and inspected the result before committing).
- **Git Hash**: 0858eba

## 2026-09-02 22:26 UTC
- **Tool**: Claude (Anthropic), claude-fable-5-1, via Claude Code
- **Session Purpose**: Prepare the repository and the requirements draft for circulation to the review list, checking both against the PI's cover email (single management system; frequency coordination and a record for science; regulatory case for remote control with a smartphone control point, automatic alerting and a pool of control operators; delivery as a University of Scranton CS capstone; comments via GitHub issues).
- **Sections/Files Affected**:
  - `docs/requirements_wsprsonde_management_system.md`: bumped to Draft 0.2 with a change log; added "How to comment" (issues) and "Who will build it" (capstone) to the preamble and §1; §5 re-verified against the eCFR point-in-time version of 2026-08-29 and extended (§5.1 framing paragraph on remote vs automatic control, §5.2 NRQZ note on §97.203(e), §5.4 wireline-link sentence from §97.213(a)); **corrected R7.3**, which had cited §97.203(e) for something the rule does not say; added R3.9 (alert severity and escalation); expanded R4.2 (phone app) and R4.6 (pool of control operators, on-duty designation); added §9.1 (capstone delivery) and Q11–Q12.
  - `README.md`: new "Reviewing the requirements" section.
  - `.github/ISSUE_TEMPLATE/{requirement_comment,open_question,config}.yml`: new issue forms.
- **Nature of Contribution**: Edit and drafting of requirements text; regulatory verification (47 CFR §§97.3, 97.109, 97.203, 97.213 fetched from the eCFR API); repository scaffolding. Also reviewed the PI's cover email; one suggested wording change was withdrawn after the PI pointed out that a beacon is an HF station.
- **Human Review Status**: Partially reviewed. The PI reviewed the summary of changes and the regulatory reading before committing; the new requirement text (R3.9, R4.2, R4.6, §9.1, Q11–Q12) is drafted for the PI's review alongside the collaborators'. Flagged and deliberately not changed: personal names in the `notes` column of `data/wsprsonde_stations.csv` in a public repository, contrary to the repo's own data-handling rule; and a quotation from a private email in §2.1.
- **Git Hash**: f0c56f8

## 2026-09-02 22:29 UTC
- **Tool**: Claude (Anthropic), claude-fable-5-1, via Claude Code
- **Session Purpose**: Remove Majid Mokhtari from the review list of the requirements draft, at the PI's instruction, so the list matches the recipients of the cover email.
- **Sections/Files Affected**: `docs/requirements_wsprsonde_management_system.md`, header "Review list" and the Draft 0.2 change log.
- **Nature of Contribution**: Edit.
- **Human Review Status**: Reviewed and verified (PI dictated the change and inspected the result).
- **Git Hash**: bc0d963

## 2026-09-03 14:20 UTC
- **Tool**: Claude (Anthropic), claude-opus-5, via Claude Code
- **Session Purpose**: Answer the first round of review comments on the requirements draft (GitHub issues #1–#4, all from Paul Elliott WB6CXC), verifying each against primary sources, and act on them in the document as Draft 0.3.
- **Sections/Files Affected**:
  - GitHub issues #1–#4: one reply comment each, drafted and shown to the PI before posting, each carrying the A8 attribution trailer and asking the reporter to close the issue if satisfied. The four comments were shortened and re-posted at the PI's direction, to state plainly what changed in the document.
  - `docs/requirements_wsprsonde_management_system.md`: bumped to Draft 0.3 with a change log entry citing each issue. §2.2 N4RVE row and prose corrected (nine-day power-supply outage, returned on its assigned 100 Hz channel); §2.4 and Q10.5 closed against the callsign-suffix proposal; §4.1 gains MeshCentral's role as keep-alive transport with its availability cost; §5.5 and R4.3 rewritten around the WSPRSonde's own dead-man, including the interval arithmetic against a 110.6 s frame and the requirement that the keep-alive be contingent on contact with the control point; R4.5, the §8 sketch, §9.1 and §11 aligned to the same mechanism; Q10.1 and Q10.2 updated; provenance extended.
  - `data/wsprsonde_stations.csv`: removed the stale claim that N4RVE's on-air offset is ~10 Hz, which the spot record contradicts on both sides of the outage.
- **Nature of Contribution**: Analysis and drafting. Live queries against `wspr.rx` on `wd10.wsprdaemon.org` established N4RVE's outage boundaries (2026-08-09 23:20 UTC to 2026-08-18 23:20 UTC) and its present offset (100 Hz median on eight bands, 0 Hz spread). 47 CFR §§97.109, 97.203 and 97.213 re-read from Cornell LII to check the three-minute claim in issue #4, which is §97.213(b), telecommand, rather than a rule of automatic control. WSPR compound-callsign encoding checked against published protocol documentation for issue #2.
- **Human Review Status**: Partially reviewed. The PI read all four draft comments before they were posted and approved the document changes. The interval arithmetic in §5.5 and R4.3 rests on hardware behaviour that is still an open question with the manufacturer. `products/` was rebuilt during the session and then reverted: that rebuild raised a false frequency mismatch for VY0ERC, because the three-day offset window drops weakly-heard bands and so manufactures a single offset where none exists, contrary to R3.3. Pending the PI's decision.
- **Git Hash**: 6f94e3c

## 2026-09-03 15:50 UTC
- **Tool**: Claude (Anthropic), claude-opus-5, via Claude Code
- **Session Purpose**: Act on Paul Elliott's second round of answers (GitHub issues #2 and #3), which supplied the WS-8's serial-number and `CSV` interfaces and the measured behaviour of its dead-man, and revise the requirements to match.
- **Sections/Files Affected**:
  - GitHub issues #2 and #3: one reply comment each, shown to the PI before posting, stating what changed in the document and carrying the A8 attribution trailer.
  - `docs/requirements_wsprsonde_management_system.md`: bumped to Draft 0.4 with a change log entry. §5.5 and R4.3 rewritten around the dead-man's actual behaviour (immediate shutdown, automatic re-arm, 1 to 12,000 minute range tested once a minute, so a 1-minute setting with 2 as the ceiling); the 69-second branch of Draft 0.3 removed. Added R4.11 (the keep-alive daemon owns the command line, since any inbound command re-arms the dead-man and a query cannot be used to read its state) and R3.10 (read the unit's own `CSV` report). Amended R1.1 and R1.3 (24-bit serial as the unit key, enclosure marking recorded separately, firmware version), R2.1 and R2.5 (three-way comparison of assigned, configured and measured), §2.2 (the BeaconBlaster has no dead-man, so the KD0EAG swap is a compliance matter), §4.1 (MeshCentral's remote terminal is a hazard to the interlock) and Q10.2.
  - `data/wsprsonde_stations.csv`: KD0EAG's hardware corrected from `WS-6` to `BB-6`, with the provenance of the change recorded in its notes.
- **Nature of Contribution**: Analysis and drafting. The hardware facts are the manufacturer's, quoted from the issues; the compliance arithmetic (the once-a-minute test interval, the resulting 1-minute setting) and the shared-channel consequence in R4.11 are this session's, derived from those facts and §97.213(b).
- **Human Review Status**: Partially reviewed. The PI approved both draft comments and the document changes before posting. Two items are open with the manufacturer and marked as such: the correct designation for the `WS-6` entries inherited from the G3ZIL metadata, and whether the licence holders accept a MeshCentral outage taking their stations off the air (Q10.2).
- **Git Hash**: bcc30cc

## 2026-09-10 22:49 UTC
- **Tool**: Claude (Anthropic), claude-opus-5, via Claude Code
- **Session Purpose**: Act on Gwyn Griffiths' (G3ZIL) review of Draft 0.4, GitHub issues #5–#10, verifying each claim against the live spot record before acting on it, and revise the requirements to Draft 0.6. Also commit the Draft 0.5 material left pending from the previous session (MIT license, capstone project description).
- **Sections/Files Affected**:
  - GitHub issues #5–#10: one reply comment each, shown to the PI before posting, each carrying the A8 attribution trailer.
  - `docs/requirements_wsprsonde_management_system.md`: bumped to Draft 0.6 with a change log entry citing each issue. §1 corrected to "WSPR **or** FST4W" (#5). §2.2 re-measured 2026-09-10 and given **Mode** and **`code`** columns, with the finding that the code number is a property of the source rather than of the mode (#6, #9); KH2R corrected to 35 Hz measured against a 36 Hz assignment (#10). §2.3 rewritten around a second, live collision: ZD7GWM and N4RVE are co-channel on 100 Hz (#7). §2.4 and Q10.7 record ZD7GWM as identified and W8GPS as post-dating the 2026-08-13 scan (#6, #7). New §4.6 for the WSPRSonde Grafana dashboard, with R6.3 requiring it keep resolving (#8). R1.3, R1.4 and R2.1 carry transmit mode and its code; R2.2 gains a per-band offset override; Q10.8 covers both channel conflicts.
  - `data/wsprsonde_stations.csv`: new `mode_code` column; TI4JWC and DP0GVN corrected from FST4W to WSPR against the measured `code`; KH2R's note records the 35 Hz measurement and its provenance; new rows for ZD7GWM and W8GPS, both carrying `ok_to_list_public = unknown` and no host name or contact detail.
  - `src/wsprsonde/`: `mode_code` added to `Station` and to the product's columns; `MODE_BY_CODE` added to `wsprdaemon.py` as a documented constant recording the measured encoding and the warning that it is source-specific. `tests/test_stations.py` fixtures updated; 57 tests pass.
  - `products/`: rebuilt against `wd10` at 2026-09-10 22:39 UTC. The VY0ERC false mismatch that caused the previous session's rebuild to be reverted did not recur: no VY0ERC band reaches the 20-report floor, so the offset is reported as absent rather than invented, which is R3.3's intended behaviour. The unlisted-candidate list is now DC7TO, N9VP and G0PKT, ZD7GWM and W8GPS having been registered.
  - `LICENSE`, `pyproject.toml`, `docs/project_description.md`, `README.md`: the Draft 0.5 material from the previous session, plus the same KH2R and collision corrections applied to the project description so it does not diverge from §2.
- **Nature of Contribution**: Analysis and drafting. Every claim in the six issues was checked against live queries on `wspr.rx` before being acted on. Three findings are this session's rather than the reviewer's: ZD7GWM and N4RVE share the 100 Hz channel on five bands with a sixth 1 Hz apart; W8GPS came on the air 2026-08-21 and so was invisible to the 2026-08-13 scan; and the `code` value for WSPR-2 is 1 in `wspr.rx` and `wsprdaemon.spots`, against the 2 the reviewer reports from the `wsprsonde` PostgreSQL table, which is the reviewer's own warning borne out and is put back to him rather than resolved here.
- **Human Review Status**: Partially reviewed. The PI read all six draft comments before they were posted and approved the document and registry changes. Two items are open with the reviewer: the encoding of the `code` and `mode` columns in the `wsprsonde` table, and who owns W8GPS and whether its 60 Hz channel was coordinated. Who moves off 100 Hz is open with the frequency coordinator.
- **Git Hash**: 20d8279
