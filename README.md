# resolveiq
ResolveIQ is an AI-powered implementation issue monitoring agent that validates incoming tickets, assesses operational risks using documented evidence, and generates client-specific portfolio briefs with human oversight.


## User Stories

1. **Ticket Validation:** As an Implementation Manager, I want ResolveIQ to identify missing or contradictory ticket information so I can resolve issues before they affect implementation progress.

2. **Risk Assessment:** As a Program Operations Specialist, I want evidence-based risk classifications so I can identify potential blockers and determine which issues require attention.

3. **Human Review:** As an Implementation Manager, I want incomplete or uncertain assessments flagged for human review so I can make informed decisions without relying on unsupported conclusions.

4. **Client Portfolio Briefs:** As a Client Operations Specialist, I want a consolidated, client-specific portfolio brief so I can review implementation status, dependencies, and risks efficiently.

5. **Human Oversight:** As an Implementation Manager, I want final control over ticket updates, priorities, escalations, and communications so ResolveIQ never takes unauthorized actions.

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
