# Proposal: show why a Needs Human Review ticket also needs attention

**Status: PROPOSED. Not built, not tested, and not yet reviewed by Michelle.**
Author: Huma Ali. Written November 11, 2026. Nothing in this document changes
ResolveIQ's behavior. It becomes a plan only after Michelle confirms the design
and retests the change from a fresh clone.

## The gap

A ticket with missing or conflicting information gets the overall label
**Needs Human Review**, even when it is also blocked or overdue. ResolveIQ still
shows that blocked or overdue finding next to the ticket. But the client summary
counts the ticket under Needs Human Review and not under High, so a specialist who
reads only the totals can miss it.

Evidence, from running `scripts/run_brief.py` on the 20 synthetic tickets with
assessment date 2026-11-04 (code unchanged since `482cb7e`, README-only commits
since):

| Client | Needs Human Review | Of those, also blocked or overdue | High count shown |
| --- | --- | --- | --- |
| Client A | 3 | 1 (T-114, blocked) | 2 |
| Client B | 5 | 1 (T-106, overdue) | 0 |

These counts come from our own runner output and are not an independent check. We
did not check whether the batch review queue (T-111) has a blocked or overdue
finding.

How it was found: by using ResolveIQ ourselves. It was first raised as an open
question on the walkthrough pull request (#7). Peer testing surfaced a different
gap, first-time-user onboarding, which is the team's top usability priority. We
also considered the real-data gap (real GitHub issues currently all go to human
review because client ID, dependencies and due date have no approved mapping). We
chose the summary gap first because it affects every ticket under review and is
visible in the information a specialist reads first.

## Proposal

Add one line to each client summary, for example:

- Client A: 3 tickets need review; 1 is also blocked (T-114).
- Client B: 5 tickets need review; 1 is also overdue (T-106).

The count covers blocked and overdue findings only. Tickets that are only due
within three days (Medium findings) are left out, to keep the line short.

## Label decision

The line names the reason, "blocked" or "overdue", and not "High finding".
Specialists know what blocked and overdue mean. "High" is an internal level, and
using it could suggest the ticket is classified High when its overall label stays
Needs Human Review. A short note under the line would say: tickets needing review
keep their overall label, and any blocked or overdue issues are shown separately for
visibility.

## What would not change

- Overall classifications and the rules that produce them.
- The totals for the 20 synthetic tickets: 2 High, 2 Medium, 7 Low, 9 Needs Human
  Review.
- `operational_actions_require_human_approval`, which stays true.
- ResolveIQ would still not rank tickets or decide what to work on first.

## Who would do what (proposed, not agreed)

- **Huma:** the summary change in the portfolio brief (JSON and Markdown), the
  runner, tests for T-106 and T-114, and the regenerated sample brief.
- **Michelle:** review the design, make any dashboard count changes, and retest the
  result independently from a fresh clone.

## How we would know it works

- The summary shows the correct line for Client A and Client B.
- The totals above are unchanged.
- New tests for T-106 and T-114 pass, and the existing 136 Python checks and 32
  browser checks still pass.
- The sample brief is regenerated and its JSON and Markdown output are checked.
- Michelle retests from a fresh clone.

The gap is not closed when the code changes. It is closed only when the change is
built, the tests pass, and Michelle has retested it.

## Timing and open questions

The Showcase is November 11, so implementation would follow it, once Michelle
agrees the design.

- Which version does Michelle prefer: a count line in each summary, or a tag on each
  review ticket?
- Should the batch review queue be covered?
