"""Pure, in-memory source adapters. No retrieval, persistence, or operational actions."""

import csv
from copy import deepcopy
from io import StringIO
import json
import re

from .risk import assess_ticket_risk
from .validation import REQUIRED_FIELDS, validate_ticket


def _envelope(record, source):
    return {"ticket": {}, "source": deepcopy(source), "raw_record": deepcopy(record),
            "field_provenance": {}, "normalization_issues": []}


def _evidence(path, present, value=None):
    result = {"path": path, "present": present}
    if present:
        result["value"] = deepcopy(value)
    return result


def _issue(envelope, field, code, message, evidence):
    envelope["normalization_issues"].append({
        "field": field, "code": code, "message": message,
        "requires_human_review": True, "evidence": deepcopy(evidence),
    })


def _map(envelope, field, evidence, transformation, *, present=False, value=None):
    envelope["field_provenance"][field] = {
        "transformation": transformation, "evidence": deepcopy(evidence),
    }
    if present:
        envelope["ticket"][field] = deepcopy(value)


def _direct(record, source):
    envelope = _envelope(record, source)
    if not isinstance(record, dict):
        _issue(envelope, "ticket", "malformed", "Expected a decoded JSON object.",
               [_evidence("$", True, record)])
        return envelope
    for field in dict.fromkeys((*REQUIRED_FIELDS, *record)):
        present = field in record
        _map(envelope, field, [_evidence(field, present, record.get(field))],
             "copy", present=present, value=record.get(field))
    return envelope


def normalize_json_ticket(record):
    """Copy a decoded synthetic JSON record, preserving absent/null/blank values."""
    return _direct(record, {"type": "synthetic_json"})


def normalize_csv_tickets(text):
    """Return envelopes for CSV rows using canonical headers.

    Blank cells remain strings; exact `null` means null for dependencies only.
    Nonblank dependency cells must encode a JSON list or null. Structural errors
    reject the entire CSV into one review envelope retaining the original text.
    No file paths are opened. Row locators count logical records, header = 1.
    """
    if not isinstance(text, str):
        raise TypeError("CSV input must be text.")
    try:
        rows = list(csv.reader(StringIO(text, newline=""), strict=True))
        if not rows or not rows[0] or any(not name.strip() for name in rows[0]):
            raise ValueError("CSV requires nonblank column names.")
        headers = rows[0]
        if len(set(headers)) != len(headers):
            raise ValueError("Duplicate CSV column names are not allowed.")
        if len(rows) == 1:
            raise ValueError("CSV contains no ticket records.")
        if any(len(row) != len(headers) for row in rows[1:]):
            raise ValueError("CSV row width does not match the header.")
    except (csv.Error, ValueError) as error:
        envelope = _envelope(text, {"type": "synthetic_csv"})
        _issue(envelope, "ticket", "malformed", str(error), [_evidence("$", True, text)])
        return [envelope]

    envelopes = []
    for row_number, row in enumerate(rows[1:], start=2):
        record = dict(zip(headers, row))
        envelope = _direct(record, {"type": "synthetic_csv", "row": row_number})
        if "dependencies" in record and record["dependencies"].strip():
            raw = record["dependencies"]
            try:
                value = json.loads(raw)
                if value is not None and not isinstance(value, list):
                    raise ValueError("Expected a JSON list or null.")
            except (json.JSONDecodeError, ValueError):
                _issue(envelope, "dependencies", "malformed",
                       "Dependency cell must contain a JSON list or null; original cell retained.",
                       [_evidence("dependencies", True, raw)])
            else:
                _map(envelope, "dependencies", [_evidence("dependencies", True, raw)],
                     "parse_json_dependency_cell", present=True, value=value)
        envelopes.append(envelope)
    return envelopes


def normalize_github_issue(record, *, repository):
    """Adapt an existing Cycle 2 reader dictionary, without importing the reader.

    No client mapping, dependency extraction, closed-state mapping, or milestone
    deadline policy is assumed. Repository context is explicit, never inferred.
    """
    envelope = _envelope(record, {"type": "cycle2_github", "repository": repository})
    if not isinstance(record, dict):
        _issue(envelope, "ticket", "malformed", "Expected a Cycle 2 reader dictionary.",
               [_evidence("$", True, record)])
        return envelope

    def ev(field):
        return _evidence(field, field in record, record.get(field))

    repository_ok = isinstance(repository, str) and re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository)
    number = record.get("number")
    number_ok = type(number) is int and number > 0
    identity_evidence = [_evidence("source.repository", True, repository), ev("number"), ev("url")]
    _map(envelope, "ticket_id", identity_evidence, "qualify_repository_issue_number",
         present=bool(repository_ok and number_ok),
         value=f"{repository}#{number}" if repository_ok and number_ok else None)
    if not repository_ok or not number_ok:
        _issue(envelope, "ticket_id", "malformed", "A repository owner/name and positive issue number are required.", identity_evidence)
    elif record.get("url") is not None:
        expected = f"https://github.com/{repository}/issues/{number}"
        if record["url"] != expected:
            _issue(envelope, "ticket_id", "contradictory", "Issue URL conflicts with supplied repository/number or has an unsupported format.", identity_evidence)
    envelope["source"]["issue_number"] = deepcopy(number)

    assignees = record.get("assignees")
    single = (isinstance(assignees, list) and len(assignees) == 1
              and isinstance(assignees[0], dict)
              and isinstance(assignees[0].get("login"), str)
              and bool(assignees[0]["login"].strip()))
    _map(envelope, "owner", [ev("assignees")], "single_assignee_login",
         present=single, value=assignees[0]["login"] if single else None)
    if not single:
        code = "ambiguous" if isinstance(assignees, list) and len(assignees) > 1 else "missing" if assignees is None or assignees == [] else "malformed"
        _issue(envelope, "owner", code, "Exactly one valid assignee is required to establish an owner.", [ev("assignees")])

    state = record.get("state")
    _map(envelope, "status", [ev("state")], "github_open_state_or_preserve_unsupported",
         present="state" in record, value=state)
    if state != "open":
        _issue(envelope, "status", "ambiguous" if state == "closed" else "malformed",
               "Only open maps directly; closed does not establish completed versus cancelled.", [ev("state")])

    for field in ("client_id", "dependencies"):
        _map(envelope, field, [ev(field)], "unmapped_requires_approved_source_contract")
        _issue(envelope, field, "ambiguous" if field in record else "missing",
               "Cycle 2 reader supplies no approved mapping for this field.", [ev(field)])

    _map(envelope, "due_date", [ev("deadline")], "milestone_deadline_not_assumed")
    _issue(envelope, "due_date", "ambiguous" if record.get("deadline") is not None else "missing",
           "Milestone deadlines are not automatically ticket deadlines; an approved mapping is required.", [ev("deadline")])
    for field in ("title", "description", "labels", "updated_at", "url"):
        if field in record:
            _map(envelope, field, [ev(field)], "copy", present=True, value=record[field])

    # Canonical fields unexpectedly supplied alongside reader fields are not
    # allowed to silently override reader evidence or resolve missing mappings.
    for field in ("ticket_id", "owner", "status", "due_date"):
        if field in record:
            mapped = envelope["ticket"].get(field)
            _issue(envelope, field, "contradictory" if field in envelope["ticket"] and record[field] != mapped else "ambiguous",
                   "Unexpected canonical field requires an approved mapping; no override applied.",
                   [ev(field)] + envelope["field_provenance"][field]["evidence"])
    return envelope


def assess_normalized_ticket(envelope, *, assessment_date, approaching_deadline_days=3):
    """Validate and assess an adapter envelope, with normalization-first gating.

    Intended for envelopes returned by these adapters, not arbitrary serialized
    input. Return independent snapshots and enrich findings with source evidence.
    """
    snapshot = deepcopy(envelope)
    ticket = snapshot["ticket"]
    validation = validate_ticket(ticket)
    risk = assess_ticket_risk(ticket, assessment_date=assessment_date,
                              approaching_deadline_days=approaching_deadline_days)
    for finding in risk["findings"]:
        finding["source_evidence"] = [
            {"field": evidence["field"],
             "provenance": deepcopy(snapshot["field_provenance"].get(evidence["field"].split("[")[0], {}))}
            for evidence in finding["evidence"]
        ]
    if snapshot["normalization_issues"]:
        risk["classification"] = "Needs Human Review"
        risk["requires_human_review"] = True
    risk["normalization_issues"] = deepcopy(snapshot["normalization_issues"])
    return {"normalized": snapshot, "validation": validation, "risk": risk,
            "requires_human_review": risk["requires_human_review"],
            "operational_actions_require_human_approval": True}
