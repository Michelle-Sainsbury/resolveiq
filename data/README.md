# Test data (DRAFT, awaiting Michelle)

- **Synthetic only.** Every ticket is invented. There is no real Gradient AI or customer data.
- **Draft.** `data/tickets/tickets.json` (a JSON array, so it cannot carry a marker itself) and `data/expected/expected_results.json` are both DRAFT, awaiting Michelle.
- **Tickets are inputs only.** The expected results are in a separate file. They were written by hand from the implemented contract (five statuses; required fields `ticket_id`, `client_id`, `owner`, `status`, `due_date`, `dependencies`) before any run. **Michelle must review the expected results independently.** Nothing here has been run or verified.
- **Assessment date** is 2026-11-04 with a 3-day window. Pass it in as a `datetime.date`.
- **Pending Michelle, excluded from pass or fail:** the owner-null tickets (T-102's owner issue, T-106, T-110). Whether a null owner is a missing-field issue or an unassigned state is her call.
- **Known limitation:** T-103 names Client B in its description while `client_id` is Client A. As implemented nothing compares them, so the expected result is Low. Client-versus-description detection is a separate enhancement, and T-103 is excluded from contradiction scoring.
- **Not in the contract:** a 14-day inactivity flag is not scored.
- T-111 has no `client_id` on purpose.
