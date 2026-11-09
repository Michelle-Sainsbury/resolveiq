# ResolveIQ dashboard

A local browser interface for the existing synthetic-ticket assessment and
portfolio functions. There was no dashboard/index.html on the dashboard branch
when implementation started. The UI introduces no risk rules and performs no
operational ticket actions.

## Run

From the repository root, with Python 3.9 or newer:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/serve_dashboard.py --date 2026-11-04
```

Open http://127.0.0.1:8787. Choose Client A, B, C, or the separate unassigned-client
review queue. Use another port with `--port 8788` if needed. Stop with Ctrl-C.
The date is explicit; it is never silently replaced with today's date.

The server invokes the existing scripts/run_brief.py runner to produce actual
brief.json in a temporary directory, reads that JSON, and serves a snapshot.
Source ticket files are never changed. Reload generated data restores that
snapshot; restart the server to regenerate after changing an approved fixture.

An existing generated file can also be used directly:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_brief.py \
  --date 2026-11-04 --out /private/tmp/resolveiq-reports
PYTHONDONTWRITEBYTECODE=1 python3 scripts/serve_dashboard.py \
  --brief /private/tmp/resolveiq-reports/brief.json
```

The dashboard will refuse malformed or inconsistent briefs rather than silently
show made-up fallback data. Opening dashboard/index.html as a file is unsupported:
use the server for its scoped data API. There are no production data connections.

## User flows

- **Dashboard:** Actual classification totals, active-ticket facts, overdue
  findings, owner-information gaps, listed dependencies, intake gaps, and flagged
  tickets. Owner counts distinguish absent, null, blank, and malformed values;
  none establishes whether work is genuinely unassigned. A separate signal calls
  out review tickets that retain a High finding.
- **Ticket intake:** Paste or read a local synthetic JSON/CSV file, choose an
  explicit assessment date, and validate/assess a temporary preview. The server
  uses normalize_json_ticket/normalize_csv_tickets, assess_normalized_ticket, and
  build_portfolio_brief. The selected client scope is applied before results are
  returned. Preview reports use render_brief_markdown/brief_to_json. A preview is
  not persisted and never replaces the original generated dataset. Empty or
  unrelated-client previews produce a visible error. Malformed source records
  can be inspected in the separate queue. Maximum HTTP request: 1 MB; preview
  batch: 1–500 records. UI file limit is 900 KB.
- **Tickets:** Search by ID, title, or owner; filter classification; open a ticket
  for source description, required fields, validation and normalization issues,
  all independent findings, exact evidence values, calculations, and provenance.
  Missing, null, blank, empty dependency lists, and malformed values are distinct.
  Each supported validation issue includes field-specific human clarification
  guidance. Guidance never fills a value or grants operational approval.
  Dependency references can open matching records already in the selected scope,
  with a Back button to return. Duplicate IDs require selecting a specific batch
  record; self-references are labeled. Unavailable references remain unverified,
  and navigation never searches another client's records or retrieves new data.
- **Bottlenecks:** Read supported elevated findings and data-quality review cases.
  Dependency references never imply that the referenced work exists or is blocked.
- **Reports:** Read classification totals and per-ticket explanations, owner/date
  information, dependency references, and review guidance. Expand evidence and
  provenance for each finding, or expand the full assessed record. These views
  present existing assessments; they add no classification or priority rules.
  The full original Markdown is available in a separate expandable section.
  JSON and Markdown downloads use the unchanged Python renderer/serializer and
  contain only the selected client or batch queue. Text is shown literally
  rather than interpreted as HTML. Downloads send no communications.
- **Settings:** Read the actual assessment date/window, approval requirements,
  current rules, and backend limitations.

Client selection clears ticket dialogs, reports, previews, search, and filters.
A late response from a previously selected client cannot replace the new scope.
The client catalogue contains names and assessment settings, but no ticket data.
All ticket/report API responses are scoped on the server, not just hidden in CSS.
Record references retain original batch positions; missing IDs are never invented.

## Data isolation and safeguards

This is a **single-user localhost demo**, not a deployed multi-user service.
The server binds only to 127.0.0.1. It rejects unexpected Host/Origin values,
serves only allowlisted UI files, disables caching, and applies a content security
policy without third-party assets. Source text is rendered with textContent.
The API offers no source-ticket update, assignment, closure, or communications
route. POST /api/intake calculates a preview only. Data-quality review remains
separate from operational approval; every operational action still requires a
human. No approval is granted by this dashboard.

The queue is an explicit batch-review workspace. It is not mixed into a client
report. Client-ID filtering is not user authentication: do not deploy this demo
with real client data without authentication, authorization, TLS, and operational
security review. A user can intentionally select any synthetic client in this demo.

## PRD coverage and remaining backend work

Reference: [final Cycle 4 PRD, including Michelle's November 6 addendum](https://docs.google.com/document/d/1iYFLwFtpr7pozyqauT2cjJV0y0HLzZCE7f_IbXQBJFI/edit).
The November 9 audit distinguishes the agreed synthetic portfolio MVP from
pending proposals and future enhancements. The final PRD defers a full dashboard;
Michelle separately authorized this browser interface and its improvements.
This interface preserves the approved Python rules. Fourteen-day inactivity
belongs to the separate Cycle 2 path, and its integration remains a joint decision.

| PRD area | Status |
| --- | --- |
| Client selector; Dashboard/Tickets/Bottlenecks/Reports/Settings | Implemented, plus Ticket intake |
| Intake completeness and missing-information review | Existing validator, displayed without filling gaps |
| High/Medium/Low/Needs Human Review with exact evidence | Existing assessor; independent findings preserved |
| Due dates, owner, status, dependency references, source provenance | Displayed with explicit unknowns |
| Client-specific portfolio brief and human-review queue | Existing builder/renderer; server-side scoping |
| Human decisions required; no automatic source writes/sends | Preserved |
| 14-day inactivity and activity-derived risks | Not implemented by this backend; missing update timestamps shown as missing |
| Dependency completion, existence, cross-ticket resolution | Not implemented; listed references remain unverified |
| Client ID versus free-text description conflict (T-103) | Outside current rules; no detector is implied |
| Separate Cycle 2 monitoring report / GitHub reader integration | Not connected; monitoring-report button disabled with explanation |
| Intended recipients and targeted communications | No recipient-management backend; displayed as not provided, never sent |
| AI-generated natural-language recommendations | No LLM added; deterministic findings and general human-review guidance only |
| Acceptance-criteria field checks, all PRD contradiction examples | Require a separately approved schema/rule extension |
| Cycle 2 full regression/eval card; timed manual baseline | Not evaluated by this dashboard task; no accuracy/time-saving claim |

The representative fixture has 20 records. At 2026-11-04 and a three-day window,
Client A has 2 High / 1 Medium / 4 Low / 3 Human Review; Client B has 0 / 1 / 2 / 5;
Client C has one Low; T-111 is alone in the separate queue. T-106 belongs under
Human Review for its missing owner and still displays its independent overdue
High finding. These are generated fixture results, not production measurements.

## Tests

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

The HTTP tests bind an ephemeral localhost port. In a sandbox, permission to bind
localhost may be required. Existing validation/risk/brief/runner tests are unchanged.

Real-browser checks are optional development tooling, not runtime dependencies.
With Node, Playwright, and an installed Chrome executable:

```sh
npm install --prefix /private/tmp/resolveiq-browser-tests playwright
PLAYWRIGHT_MODULE=/private/tmp/resolveiq-browser-tests/node_modules/playwright \
  node tests/dashboard_browser.cjs
```

Start the dashboard with the fixture date 2026-11-04 first. Set DASHBOARD_URL for
another port, and CHROME_PATH for a different Chrome executable location. The
browser suite covers navigation, client isolation (including delayed responses),
ticket dialogs, report downloads, intake previews, injection text, filters, and
mobile layout. It also checks owner distinctions, field-specific guidance,
dependency navigation and ambiguity, exact expandable record preservation, and
unchanged Markdown downloads. It intentionally evaluates the UI; it is not a statistical accuracy
or usability study. The default Chrome path is the macOS Applications path.
