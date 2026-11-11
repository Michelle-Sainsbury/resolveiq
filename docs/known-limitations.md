# Known limitations

This page lists what ResolveIQ does not do or does not do well, written from the
code and tests on `feature/resolveiq-build` at commit `482cb7e`. No item below
has been fixed. Line numbers refer to that commit and may move.

Each item carries one label:

- **VERIFIED IN CODE** – read in the code and, where stated, reproduced on the 20
  synthetic tickets or with a small in-memory call.
- **REPORTED IN PRD, NOT RE-VERIFIED** – reported in the team's PRD. A section
  number in parentheses says where. It has not been re-checked here, except where
  the item says so.

## Scope and safeguards

- **Synthetic data only.** Every ticket in `data/tickets/` is invented
  ([data/README.md](../data/README.md), line 3). No real customer or company data
  is used. VERIFIED IN CODE.
- **Advisory only.** ResolveIQ does not create, edit, assign, prioritize, reopen,
  or close tickets and does not send messages. The runner writes only
  `brief.json` and `brief.md` into the folder you give it
  ([scripts/run_brief.py](../scripts/run_brief.py), lines 88-90). The dashboard
  server offers one POST route, an in-memory intake preview
  ([scripts/serve_dashboard.py](../scripts/serve_dashboard.py), `do_POST`).
  `operational_actions_require_human_approval` is always `true`
  ([resolveiq/risk.py](../resolveiq/risk.py), line 87). A person decides every
  follow-up. VERIFIED IN CODE.
- **The dashboard is a single-user localhost demo, not an access-control
  system.** The server binds to `127.0.0.1`
  ([scripts/serve_dashboard.py](../scripts/serve_dashboard.py), line 131) and
  checks the Host and Origin headers. Selecting a client filters what is shown. It
  is not authentication, and anyone using the demo can select any synthetic
  client. See [docs/dashboard.md](dashboard.md). VERIFIED IN CODE.
- **No LLM.** Classification is rule-based. The code under `resolveiq/` and
  `scripts/` imports only the Python standard library and makes no network or LLM
  calls. `http.server` and `urllib.parse` are used only for the local dashboard
  server. VERIFIED IN CODE.

## Limitations

### 1. An empty intake request gets a misleading error message

**VERIFIED IN CODE.** `POST /api/intake` with an empty body (or no body) is
rejected with HTTP 413 and the message `Intake must be at most 1 MB.` One check
handles both cases: any `Content-Length` that is not greater than 0 and at most
1,000,000 gets that same message
([scripts/serve_dashboard.py](../scripts/serve_dashboard.py), lines 97-99). For an
empty body the message is wrong, because nothing exceeds the limit. The request is
still rejected before anything is processed. Reproduced with an in-memory server:
an empty body and a missing body both returned 413 with this message. A body over
1,000,000 bytes would get the same status and message, because the same single
branch handles it. That follows from the code and was not reproduced here. No test in
[tests/test_dashboard.py](../tests/test_dashboard.py) covers the empty-body case.

### 2. Some standalone validation findings may lack evidence objects

**REPORTED IN PRD, NOT RE-VERIFIED.** The reported gap is that some standalone
validation findings lack evidence objects in the expected report sections. It has
not been located or confirmed here. What was checked: the entries in
`validation.issues` carry only `field`, `code`, and `message` (11 entries across
the 20 demo tickets, none with an evidence object); the evidence for each issue is
attached to the matching `validation_*` finding
([resolveiq/risk.py](../resolveiq/risk.py), lines 24-51). In the 20-ticket demo
(29 findings) and in eight in-memory edge inputs (non-object records, empty and
null fields, wrong types, empty and header-only CSV text), every finding had at
least one evidence object, so a finding without one could not be reproduced.

### 3. Some dependency references are in the JSON report but not the Markdown

**VERIFIED IN CODE.** `brief.json` keeps each ticket's full `dependencies` list.
`brief.md` shows a dependency only where a finding's evidence cites it, because
[resolveiq/brief.py](../resolveiq/brief.py) has no dependency-specific rendering.
In the demo, T-107 (`T-170`) and T-108 (`T-150`) have dependencies in `brief.json`
that appear nowhere in `brief.md`. T-101, T-112, and T-113 show theirs in
`brief.md` because a finding cites them. Use `brief.json` for the full lists. See
also the [walkthrough](walkthrough.md) and the
[sample brief](sample/brief.md).

### 4. A failed Markdown write can leave a partial output

**VERIFIED IN CODE.** The runner creates the output folder, writes `brief.json`,
then writes `brief.md`, all in one `try` block
([scripts/run_brief.py](../scripts/run_brief.py), lines 87-93). If the second write
fails, the runner prints `Cannot write to …`, exits with code 1, and leaves
`brief.json` behind. Reproduced by making `brief.md` a directory in the output
folder: exit code 1 and a `brief.json` present. No test in
[tests/test_run_brief.py](../tests/test_run_brief.py) covers this. Check the exit
status and both files before using the output.

### 5. T-103's description and client ID conflict is not detected

**VERIFIED IN CODE.** T-103 has `client_id` Client A, but its description names
Client B. Validation and risk assessment never read `description`, so nothing
compares the two. T-103 is classified Low (`outside_deadline_window`) in Client A.
The same limitation is recorded in [data/README.md](../data/README.md), line 8.

### 6. Dependency references are not checked for existence or for blocking

**VERIFIED IN CODE.** Validation checks only the shape of a dependency list: a
list of non-empty strings, with no self-dependency, no duplicates, and no blocked
status together with an empty list
([resolveiq/validation.py](../resolveiq/validation.py), lines 47-64). Validation
and risk assessment each look at one ticket at a time and never look up another
ticket. In the demo, T-101 depends on `T-140`, T-107 on `T-170`, T-108 on
`T-150`, and T-113 on `T-160`. None of those IDs is among the 20 tickets, and
nothing flags them. A `blocked` status supports a High finding without naming a
dependency as the cause.

### 7. Needs Human Review and High/Medium are different things

**VERIFIED IN CODE.** `requires_human_review` marks missing, malformed, or
contradictory data ([resolveiq/risk.py](../resolveiq/risk.py), lines 77 and 86).
High and Medium are operational risk signals. They are not interchangeable. A
ticket flagged for review is counted only as Needs Human Review
([resolveiq/brief.py](../resolveiq/brief.py), line 87), but it can still carry a
High finding: in the demo, T-106 (overdue) and T-114 (blocked). That is why
Client B shows High: 0 although T-106 has an overdue High finding. Read the
review items and findings, not only the counts. Neither value approves any
action.

### 8. Evaluation scope

**REPORTED IN PRD (SECTION 14), NOT RE-VERIFIED.** A teammate compared
ResolveIQ's classifications with human labels on 20 tickets (12 new records and
8 reused development fixtures) and reported 12 of 20 (60%) in agreement: 4 of 12
on the new records and 8 of 8 on the reused fixtures. One label (T-104) was
corrected from Medium to Low after the comparison; before that correction,
agreement was 11 of 20 (55%). ResolveIQ classified T-104 as Low, so the correction
turned a disagreement into an agreement. This is an internal comparison by a
teammate. It is
not external or independent validation, and agreement is not accuracy. The
labels, the data, and the method are not in this repository and have not been
re-checked here. The result does not support any statement about accuracy,
production performance, or time saved.
