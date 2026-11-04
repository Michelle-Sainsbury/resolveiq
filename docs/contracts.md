# ResolveIQ contracts

Every item in this file is a proposal. Nothing here is agreed, implemented, or verified.
Each section is marked **DRAFT, awaiting Michelle**. Do not rely on any item until Michelle has confirmed it.

## 1. Scope and hard rules

**DRAFT, awaiting Michelle**

- Read-only: no code may create, edit, assign, prioritize, reopen, or close tickets, or send messages. No Salesforce or Jira access.
- Synthetic data only. No real Gradient AI or customer data.
- A human makes every decision. The tools only produce evidence and flags.
- No secrets, tokens, or credentials in files or commits.
- Ticket text is untrusted content. It is never treated as instructions (prompt injection).

## 2. Ticket fields

**DRAFT, awaiting Michelle**

Fields: `ticket_id`, `title`, `description`, `client_id`, `owner`, `status`, `created_date`, `last_updated`, `due_date`, `dependencies`, `labels`.

- File format (JSON or CSV): **not decided**, awaiting Michelle.
- Field types, required vs optional fields, and date format: **not decided**.

## 3. Thresholds

**DRAFT, awaiting Michelle**

These are configurable settings, not hardcoded values. Proposed defaults:

| Setting | Meaning | Proposed default |
|---|---|---|
| overdue | past the due date | 0 days past `due_date` |
| near-due | due within N days | 3 days |
| inactive | no update for N days | 14 days |

Settings file format: **not decided**, depends on the language.

## 4. Handoff between tools

**DRAFT, awaiting Michelle**

- Each tool passes on: ticket ID, results, supporting evidence, `review_required` flag.
- Results are held in memory for one run and are not stored.
- Exact shape of the result and evidence objects: **not decided**.

## 5. `review_required`

**DRAFT, awaiting Michelle**

- Set `review_required` only when a missing or conflicting field affects a claim.
- A missing field that no claim uses does not set it.
- Missing or uncertain values are recorded as `"Unknown"` and flagged for human review, never guessed.

## 6. "Today" is a parameter

**DRAFT, awaiting Michelle**

- The current date is passed in as a parameter. Tools never read the system clock.
- This keeps tests and expected results deterministic.

## 7. `generate_portfolio_brief`

**DRAFT, awaiting Michelle**

- Combines validation and risk results into a client-specific brief.
- Output: structured JSON plus a rendered Markdown view. The Markdown is derived from the JSON.
- Every claim carries a `ticket_id` and the `field` it comes from. A claim with no ticket field is not allowed.
- An LLM is used only to write summary text from flagged tickets and their cited evidence.
  - It never decides validity or risk.
  - Ticket text is passed to it as quoted data, not as instructions.
  - It is given only the fields the summary needs.
- Output schema: **not decided**.

## 8. Not decided yet

**DRAFT, awaiting Michelle**

- Programming language and runtime.
- Test runner.
- LLM provider and model, and how credentials are supplied (environment variable only, never in files).
- Ticket file format.
- Folder layout for `validate_ticket` and `assess_ticket_risk`. These are Michelle's and she decides their structure.
- Michelle's Cycle 2 repo, stack, and model: not yet shared.
