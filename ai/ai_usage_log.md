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
