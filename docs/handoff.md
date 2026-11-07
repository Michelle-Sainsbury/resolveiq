# Handoff notes

Built, tested, verified, and pending are kept separate. Proposed assumptions are marked as proposals and are not decisions.

## Built

Merged (Michelle):
- Ticket validation, risk assessment, and normalization (PRs #2 and #3).

Merged (Huma):
- 20 synthetic tickets and hand-computed expected results (PR #4).

Portfolio brief (PR #5):
- Merged by Michelle into `feature/resolveiq-build` (merge commit `82fa0ff`).

Runner (`scripts/run_brief.py`):
- On branch `huma/brief-runner`, pushed, tip `d72abd4`.
- Not merged. No pull request yet.
- The branch contains `d72abd4`, a cherry-pick of `6de5243`. That change is now also on `feature/resolveiq-build` through the PR #5 merge, so `d72abd4` duplicates it.

## Tested

Portfolio brief (PR #5):
- 43 tests. 94 passing together with Michelle's 51.

Runner:
- 12 tests.
- On `huma/brief-runner` (tip `d72abd4`), the full suite ran 106 tests: OK.

## Verified

Portfolio brief (PR #5):
- Michelle verified it at `6de5243` against the latest shared base: 94 tests passed, and 20 PASS, 0 FAIL, 0 EXCLUDED.

Runner:
- On the 20 tickets it agrees with the expected results, 20 of 20.
- This checks the code against expected results derived from the rules. It is not independent accuracy.

## Pending

- Michelle's runner test.
- Rebase of `huma/brief-runner` onto `feature/resolveiq-build`, dropping the duplicate `d72abd4`.
- The runner pull request. Michelle asked for no runner pull request until she has tested the branch.
- Update the PRD status lines for the PR #5 merge.
- The independent expected-outcomes check (target Tue Nov 10, not yet confirmed).
- The Cycle 2 independent rerun.
- Final acceptance testing.

## Proposed assumptions

Pending Michelle's confirmation. Owners: Huma and Michelle.

- The brief covers every verified client in a batch (no client selector).
- The assessment date is always passed in explicitly.
- Version 1 does not merge Cycle 2 monitoring reports. The Nov 6 handoff defines the brief's input as the full `assess_normalized_ticket` output.
- Real GitHub issues go to human review, because `client_id`, `due_date`, and `dependencies` have no approved mapping.

## Next

- Integrated run with Michelle on Mon Nov 9.
- Then the independent comparison.
