# Human-review decision log plan

**Status: PLANNED — not implemented.** ResolveIQ currently shows review flags,
findings, and evidence. It does not persist reviewer decisions, grant approval,
or execute follow-up actions.

## Intended user and workflow

An implementation manager or client operations reviewer would use the log to
record how they evaluated a ticket that ResolveIQ flagged. The reviewer would
inspect the original evidence and any independent risk findings, then record
a decision such as **request clarification**, **defer review**, or **close
review without action**. Closing a review would not close the source ticket.
A second reviewer could see what was decided and what evidence was available
at the time.

## Proposed fields

| Field | Purpose |
| --- | --- |
| Decision ID and prior decision reference | Give each entry a stable ID and link corrections to earlier entries. |
| Ticket and report references | Record the source and ticket ID when available; otherwise retain a report and batch-position reference. Do not invent a ticket or client ID. |
| Client or batch-queue scope | Keep decisions for unverified clients in the batch queue until a human verifies the association. |
| Assessment context | Record the assessment date, deadline window, original classification, and relevant rule and evidence references. |
| Reviewer identity and timestamp | Attribute the recorded decision to an authenticated reviewer and record when it was made. |
| Disposition and rationale | Record the decision, why it was made, and what still needs clarification. |
| Proposed operational action and approval reference | If applicable, record the specific proposed action and a reference to an explicit approval in an authorized workflow. Keep approval separate from the review disposition. |

## Human approval, privacy, and audit

A review entry would never authorize or trigger a source-ticket update,
assignment, closure, or communication. An authorized human would approve any
operational action separately. The log would keep ResolveIQ's original
classification and evidence alongside the human judgment.

Start with synthetic data. Before any real-data use, agree on authentication,
client-scoped authorization, restricted access to the batch queue, and a
retention and deletion policy. Store evidence references where possible instead
of copying ticket bodies. Keep credentials and unnecessary personal data out of
rationales and exports. Audit decision creation, corrections, and access as
appropriate; make corrections traceable rather than silently replacing entries.
The current localhost demo does not provide these controls.

## Future acceptance criteria

- An authorized reviewer can save a disposition and rationale with source,
  assessment, reviewer, and timestamp references and retrieve it later.
- A review entry preserves the original classification and all relevant
  independent findings. A missing ID remains missing.
- A correction retains the original entry and records who corrected it, when,
  and why.
- Unauthorized users cannot read or write another client's entries or the
  restricted batch queue. Exports respect the same permissions.
- Saving, correcting, or closing a review never changes the source ticket or
  sends a communication. Operational approval remains a separate human step.
- Synthetic acceptance tests cover missing IDs, a review ticket with an
  overdue finding, cross-client access denial, and traceable corrections.

See the [getting started guide](getting-started.md) for the current workflow.
