# resolveiq
ResolveIQ is an AI-powered implementation issue monitoring agent that validates incoming tickets, assesses operational risks using documented evidence, and generates client-specific portfolio briefs with human oversight.


## User Stories

1. **Ticket Validation:** As an Implementation Manager, I want ResolveIQ to identify missing or contradictory ticket information so I can resolve issues before they affect implementation progress.

2. **Risk Assessment:** As a Program Operations Specialist, I want evidence-based risk classifications so I can identify potential blockers and determine which issues require attention.

3. **Human Review:** As an Implementation Manager, I want incomplete or uncertain assessments flagged for human review so I can make informed decisions without relying on unsupported conclusions.

4. **Client Portfolio Briefs:** As a Client Operations Specialist, I want a consolidated, client-specific portfolio brief so I can review implementation status, dependencies, and risks efficiently.

5. **Human Oversight:** As an Implementation Manager, I want final control over ticket updates, priorities, escalations, and communications so ResolveIQ never takes unauthorized actions.

## Status

Implemented locally: `validate_ticket` checks required ticket fields, formats,
and contradictions without inventing values. `assess_ticket_risk` produces
High, Medium, Low, or Needs Human Review outcomes with field-level evidence,
an explicit assessment date, and a configurable 3-calendar-day deadline window.
Data-quality review is separate from human approval for all operational actions.

The foundation suite passed all 29 tests on November 6, 2026, covering
validation, risk classification, deadline boundaries, evidence, and unchanged
inputs. Portfolio brief generation, its reporting runner, and the local browser
dashboard are now implemented. ResolveIQ remains read-only toward operational
systems: these functions do not update tickets or send communications.

## Ticket validation

`from resolveiq import validate_ticket` validates a decoded JSON object using
Python's standard library. Pass `json.loads(...)` when starting with JSON text.
The function returns `valid`, `requires_human_review`, and an `issues` list with
`field`, `code` (`missing`, `malformed`, or `contradictory`), and `message`.
Every issue requires human review. Input values are never changed or filled in.

The initial synthetic ticket schema is:

| Required field | Accepted value |
| --- | --- |
| `ticket_id` | Non-empty string |
| `client_id` | Non-empty string |
| `owner` | Non-empty string |
| `status` | `open`, `in_progress`, `blocked`, `completed`, or `cancelled` |
| `due_date` | Valid calendar date, exactly `YYYY-MM-DD` |
| `dependencies` | List of non-empty ticket ID strings |

Absent fields and `null` values mean missing information. `dependencies: []`
confirms no dependencies; `dependencies: null` means dependencies are unknown.
Self-dependencies, duplicate dependencies, and `blocked` status with an empty
dependency list are flagged for review. The latter is a review heuristic: a
human can clarify blockers that are not ticket dependencies.

Validation checks internal consistency only. It does not verify referenced
tickets exist or are resolved, infer dependency status, or classify past due
dates as malformed. Additional fields are allowed and are not validated.

```python
from resolveiq import validate_ticket

result = validate_ticket({
    "ticket_id": "T-100",
    "client_id": "C-10",
    "owner": "Synthetic Owner",
    "status": "open",
    "due_date": "2026-11-30",
    "dependencies": [],
})
# {"valid": True, "requires_human_review": False, "issues": []}
```

Run the automated tests from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

## Evidence-based risk assessment

`assess_ticket_risk(ticket, *, assessment_date, approaching_deadline_days=3)`
uses an explicit `datetime.date` and a configurable non-negative integer
calendar-day window. It never uses the system clock or changes the ticket.
Invalid assessment arguments raise `TypeError` (date) or `ValueError` (window).

Rules apply in this order:

| Overall classification | Rule |
| --- | --- |
| Needs Human Review | Any missing, malformed, or contradictory information from validation |
| Low | Valid completed or cancelled ticket; deadline rules do not apply |
| High | Valid active ticket is blocked or overdue |
| Medium | Valid active ticket is due today through 3 calendar days away, inclusive (configurable) |
| Low | Valid active ticket has no elevated status signal and falls outside the deadline window |

Exactly 3 days away is Medium; 4 days away is Low under the default window.
All independently supported findings are retained, including both blocked and
overdue signals. Validation issues always determine the overall outcome first;
supported operational findings can still be shown under Needs Human Review.
Malformed status or date values are never used to infer operational signals.

Every result includes the classification, assessment date, configured window,
validation issues, and findings. Each finding names its rule and explanation,
cites field-level evidence, and includes calculated day counts where relevant.
Evidence distinguishes absent fields (`present: false`, no value) from explicit
null (`present: true`, `value: null`). Date calculations use the result's explicit
assessment date and configured window. Contradictory dependency findings also
cite ticket ID, status, and the dependency list to preserve context.

`requires_human_review` indicates data-quality issues only.
`operational_actions_require_human_approval` is always `true`, including for
valid High, Medium, and Low results. Assessments do not approve or execute any
updates, escalations, communications, or other operational actions.

```python
from datetime import date
from resolveiq import assess_ticket_risk

risk = assess_ticket_risk({
    "ticket_id": "T-101", "client_id": "C-10", "owner": "Synthetic Owner",
    "status": "open", "due_date": "2026-11-08", "dependencies": [],
}, assessment_date=date(2026, 11, 5))
# risk["classification"] == "Medium" (3 calendar days remaining)
# risk["requires_human_review"] is False
# risk["operational_actions_require_human_approval"] is True
```

Dependency IDs are references only: their existence and completion are not
verified. A blocked status supports High without claiming a specific dependency
caused it. Low means no elevated risk detected by these limited rules, not a
guarantee of safety. No missing values or external facts are invented.

## In-memory ticket normalization

The normalization milestone passed 51 tests: the original 29 validation/risk
tests plus 22 normalization tests. Run the current full suite with the same
unittest command above.

The standard-library normalization adapters return independent envelopes with
`ticket`, `source`, `raw_record`, `field_provenance`, and `normalization_issues`.
They neither retrieve data nor open files. Source text is data, never instructions.

- `normalize_json_ticket(record)` accepts a decoded synthetic JSON object. It
  copies values without coercion, including extra fields. Absent keys stay
  absent; explicit null stays `None`; blank strings stay blank; empty lists stay
  empty. Invalid object inputs retain their raw value and produce a review issue.
- `normalize_csv_tickets(text)` accepts CSV text and returns a list of envelopes.
  Headers use the canonical field names without trimming or aliases. Ordinary
  cells stay strings (including the literal `null`). Only nonblank dependency
  cells are JSON-decoded and must contain a list or `null`. Use a CSV writer to
  quote dependency lists containing commas or quotes. Blank dependency cells
  remain blank and require validation review; `[]` confirms no dependencies.
  Invalid dependency cells retain the original string and produce review issues.
  Missing columns stay absent. Duplicate/blank headers, inconsistent row widths,
  malformed CSV, empty input, and header-only input reject the entire input into
  one review envelope retaining the original text. Duplicate ticket records are
  not combined. `source.row` counts logical CSV records, with the header at 1,
  so quoted multiline cells do not change record numbering.
- `normalize_github_issue(record, repository="owner/repository")` accepts the
  existing Cycle 2 reader's dictionary shape without importing that reader.
  A positive integer issue number plus explicit repository context establishes
  a qualified ID (`owner/repository#42`). A supplied non-null URL must match the
  corresponding GitHub issue URL exactly; conflicts require review. Exactly one
  nonblank assignee login maps to owner. Zero assignees means missing; multiple
  assignees are ambiguous. Only `open` maps directly to status; `closed` and
  unsupported values are preserved and flagged rather than mapped to completed
  or cancelled. Client and dependency fields have no approved reader mapping and
  stay absent, even if unexpected canonical fields appear in the supplied record.
  Milestone deadlines remain raw evidence and never become ticket due dates.
  Unexpected canonical ticket ID, owner, status, or due date fields produce
  ambiguity/conflict flags without overriding reader evidence. Title,
  description, labels, update timestamp, and URL are copied as extra metadata.

Provenance records the transformation and source paths with `present` flags and
original values. Normalization issues include field, code, explanation,
`requires_human_review: true`, and source evidence. Raw records preserve
contradictory candidates even when a field cannot be mapped. No value is filled
with an invented `"Unknown"` placeholder. The adapter cannot recover distinctions
the Cycle 2 reader already collapsed into empty lists or null.

```python
from datetime import date
from resolveiq import normalize_json_ticket, assess_normalized_ticket

envelope = normalize_json_ticket({
    "ticket_id": "T-102", "client_id": "C-10", "owner": "Synthetic Owner",
    "status": "open", "due_date": "2026-11-08", "dependencies": [],
})
assessment = assess_normalized_ticket(envelope, assessment_date=date(2026, 11, 5))
# assessment["risk"]["classification"] == "Medium"
```

`assess_normalized_ticket` accepts adapter-generated envelopes and returns an
independent normalized snapshot, the unchanged validator's result, and an
enriched risk result. Use this wrapper rather than passing only `ticket` to the
risk function: unresolved normalization issues force the overall classification
to Needs Human Review even when the mapped ticket passes validation. Supported
independent findings remain available; each risk finding gains `source_evidence`
linking internal fields to provenance. Normalization issues are also included in
the risk result. Assessment date and threshold have the existing risk API's
requirements. Arbitrary or tampered envelope structures are not a supported API.

Data-quality `requires_human_review` is distinct from operational approval.
The wrapper and its risk result always report
`operational_actions_require_human_approval: true`. No adapter or wrapper updates
tickets, sends messages, invokes subprocesses, or accesses the network.

Remaining integration decisions: approve a GitHub client/dependency source,
closed-state mapping, and milestone-to-ticket deadline policy before enabling
them. Agree on this evidence handoff with the portfolio brief consumer. Reader
import, live retrieval, and new risk rules are outside the normalization layer.
Portfolio generation is implemented separately in `resolveiq/brief.py`.
GitHub reader records currently require review because
those required-field mappings remain unresolved.

## Browser dashboard

Run the local synthetic-data dashboard from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/serve_dashboard.py --date 2026-11-04
```

Open http://127.0.0.1:8787 and select a client. The server uses actual generated
`brief.json` data and the existing assessment/portfolio functions. It supports
client-isolated ticket views, evidence details, JSON/CSV intake previews, and
scoped report viewing/downloads. No source tickets are changed or messages sent.
See [dashboard usage, tests, and PRD coverage](docs/dashboard.md) for details and
backend limitations. The earlier 29/51-test counts describe historical stages;
portfolio, runner, and dashboard tests are included by the full discovery command.
