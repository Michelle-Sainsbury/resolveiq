"""Deterministic portfolio brief built from assess_normalized_ticket outputs.

Facts only. The brief regroups what the assessments already say: it adds no
interpretation, no new risk rules, and no claim without a finding behind it.
It uses the standard library only, with no network, LLM, clock, environment, or
file access. The assessment date is passed in, never read from the system.

Input: a list of complete assess_normalized_ticket outputs and a datetime.date.
Output: a JSON-serializable dict (see brief_to_json), plus a Markdown view that
render_brief_markdown generates from that dict alone.

Grouping: a record joins a client's brief only when its normalized ticket has a
present, non-blank string client_id and no validation or normalization issue
names client_id. Every other record goes to the batch-level review queue. No
client is inferred from any text, and client_id is never trimmed or changed.

Within a client, a record that needs human review appears in the human_review
section and is not counted as High, Medium, or Low.

Record references: batch_position (1-based position in the input list), plus
ticket_id only when the normalized ticket has a non-empty string ticket_id.
Counts list the references of the records counted and nothing else.

Summary: a block at the top of the JSON and the Markdown with, per client, the
High, Medium, Low, and Human Review counts, and the size of the batch review
queue. Each count carries the records counted, like every other count.

Review items: for each client, the High tickets and then the Human Review
tickets, each as a record reference with the rule names from its own findings
(High findings for a High ticket, Needs Human Review findings for a Human Review
ticket) and the field and code of any normalization issue. No free text.

Ordering: clients are sorted by client_id; records keep batch order. In the JSON,
summary and review_items come first and all other keys are sorted.
"""

import json
from copy import deepcopy
from datetime import date

_LEVEL_KEYS = {"High": "high", "Medium": "medium", "Low": "low"}
_REVIEW = "Needs Human Review"
_TOP_KEYS = ("normalized", "validation", "risk", "requires_human_review",
             "operational_actions_require_human_approval")
_NORMALIZED_KEYS = ("ticket", "source", "raw_record", "field_provenance", "normalization_issues")
_RISK_KEYS = ("classification", "assessment_date", "approaching_deadline_days",
              "requires_human_review", "operational_actions_require_human_approval", "findings")
_FINDING_KEYS = ("rule", "classification", "evidence")
_SECTIONS = (("high", "High"), ("medium", "Medium"), ("low", "Low"), ("human_review", "Human Review"))
_TOP_FIRST = ("summary", "review_items")


def build_portfolio_brief(assessments, *, assessment_date):
    """Return the brief dict for a list of assess_normalized_ticket outputs."""
    if type(assessment_date) is not date:
        raise TypeError("assessment_date must be a datetime.date (not a datetime).")
    if type(assessments) is not list:
        raise TypeError("assessments must be a list of assess_normalized_ticket outputs.")
    iso_date = assessment_date.isoformat()

    window = None
    entries = []
    client_entries = {}
    queue = []
    for position, assessment in enumerate(assessments, start=1):
        entry, client_id, entry_window = _read(position, assessment, iso_date)
        if position > 1 and entry_window != window:
            raise ValueError(
                f"Assessment at batch position {position} used a different approaching_deadline_days.")
        window = entry_window
        entries.append(entry)
        if client_id is None:
            entry["client_id_evidence"] = _client_evidence(assessment["normalized"]["ticket"])
            queue.append(entry)
        else:
            client_entries.setdefault(client_id, []).append(entry)

    clients = []
    for client_id in sorted(client_entries):
        members = client_entries[client_id]
        sections = {key: [] for key, _ in _SECTIONS}
        for entry in members:
            key = "human_review" if entry["requires_human_review"] else _LEVEL_KEYS[entry["classification"]]
            sections[key].append(entry)
        counts = {key: _count(sections[key]) for key, _ in _SECTIONS}
        counts["total"] = _count(members)
        clients.append({
            "client_id": client_id,
            "requires_human_review": any(e["requires_human_review"] for e in members),
            "operational_actions_require_human_approval": True,
            "counts": counts,
            "sections": sections,
        })

    in_clients = sorted((e for members in client_entries.values() for e in members),
                        key=lambda e: e["record"]["batch_position"])
    return {
        "summary": {
            "clients": [{"client_id": client["client_id"],
                         **{key: deepcopy(client["counts"][key]) for key, _ in _SECTIONS}}
                        for client in clients],
            "batch_review_queue": _count(queue),
        },
        "review_items": _review_items(clients),
        "assessment_date": iso_date,
        "approaching_deadline_days": window,
        "requires_human_review": any(e["requires_human_review"] for e in entries),
        "operational_actions_require_human_approval": True,
        "counts": {
            "records_in_batch": _count(entries),
            "records_in_client_briefs": _count(in_clients),
            "records_in_batch_review_queue": _count(queue),
        },
        "clients": clients,
        "batch_review_queue": {
            "criteria": "Records without a verified client_id (absent, null, blank, or malformed).",
            "requires_human_review": any(e["requires_human_review"] for e in queue),
            "operational_actions_require_human_approval": True,
            "counts": {"total": _count(queue)},
            "records": queue,
        },
    }


def brief_to_json(brief):
    """Serialize a brief so equal briefs give identical text.

    Keys are sorted at every level, except that the top level starts with
    summary and review_items.
    """
    return json.dumps(_ordered(brief, top=True), indent=2, ensure_ascii=True) + "\n"


def render_brief_markdown(brief):
    """Render the Markdown view from the brief dict only.

    Every value that came from a ticket is shown as a JSON literal inside inline
    code, so ticket text cannot add headings, links, or other Markdown structure.
    """
    lines = ["# Portfolio brief", ""]
    counts = brief["counts"]
    lines += [
        f"- Assessment date: {_code(brief['assessment_date'])}",
        f"- Approaching-deadline window in days: {_code(brief['approaching_deadline_days'])}",
        f"- Requires human review: {_yes_no(brief['requires_human_review'])}",
        "- Operational actions require human approval: "
        + _yes_no(brief["operational_actions_require_human_approval"]),
        f"- Records in batch: {_counted(counts['records_in_batch'])}",
        f"- Records in client briefs: {_counted(counts['records_in_client_briefs'])}",
        f"- Records in batch review queue: {_counted(counts['records_in_batch_review_queue'])}",
        "",
        "## Summary",
        "",
    ]
    for client in brief["summary"]["clients"]:
        lines.append(f"- Client {_code(client['client_id'])}")
        for key, title in _SECTIONS:
            lines.append(f"  - {title}: {_counted(client[key])}")
    lines += [f"- Batch review queue: {_counted(brief['summary']['batch_review_queue'])}", "",
              "## Review items", ""]
    if brief["review_items"]:
        for item in brief["review_items"]:
            lines.append(
                f"- Client {_code(item['client_id'])}, section {_code(item['section'])}, "
                f"record {_code(item['record'])}, rules {_code(item['rules'])}, "
                f"normalization issues {_code(item['normalization_issues'])}")
    else:
        lines.append("None.")
    lines.append("")
    for client in brief["clients"]:
        lines += [f"## Client {_code(client['client_id'])}", "",
                  f"- Requires human review: {_yes_no(client['requires_human_review'])}",
                  "- Operational actions require human approval: "
                  + _yes_no(client["operational_actions_require_human_approval"]),
                  "- Counts:"]
        for key, title in _SECTIONS:
            lines.append(f"  - {title}: {_counted(client['counts'][key])}")
        lines.append(f"  - Total: {_counted(client['counts']['total'])}")
        lines.append("")
        for key, title in _SECTIONS:
            lines += [f"### {title}", ""]
            lines += _entries(client["sections"][key])
            lines.append("")
    queue = brief["batch_review_queue"]
    lines += ["## Batch review queue", "",
              f"- Criteria: {_code(queue['criteria'])}",
              f"- Requires human review: {_yes_no(queue['requires_human_review'])}",
              "- Operational actions require human approval: "
              + _yes_no(queue["operational_actions_require_human_approval"]),
              f"- Records: {_counted(queue['counts']['total'])}", ""]
    lines += _entries(queue["records"])
    lines.append("")
    return "\n".join(lines)


def _invalid(position, reason):
    return ValueError(
        f"Assessment at batch position {position} is not a complete "
        f"assess_normalized_ticket output: {reason}.")


def _read(position, assessment, iso_date):
    if not isinstance(assessment, dict):
        raise _invalid(position, "expected a dict")
    for key in _TOP_KEYS:
        if key not in assessment:
            raise _invalid(position, f"missing {key!r}")
    normalized, validation, risk = assessment["normalized"], assessment["validation"], assessment["risk"]
    if not isinstance(normalized, dict) or not isinstance(validation, dict) or not isinstance(risk, dict):
        raise _invalid(position, "normalized, validation, and risk must be dicts")
    for key in _NORMALIZED_KEYS:
        if key not in normalized:
            raise _invalid(position, f"normalized is missing {key!r}")
    for key in _RISK_KEYS:
        if key not in risk:
            raise _invalid(position, f"risk is missing {key!r}")
    if not isinstance(normalized["ticket"], dict):
        raise _invalid(position, "normalized ticket must be a dict")
    if not isinstance(validation.get("issues"), list):
        raise _invalid(position, "validation is missing an issues list")
    if not isinstance(normalized["normalization_issues"], list):
        raise _invalid(position, "normalization_issues must be a list")
    if not isinstance(risk["findings"], list):
        raise _invalid(position, "risk findings must be a list")
    for finding in risk["findings"]:
        if not isinstance(finding, dict) or any(key not in finding for key in _FINDING_KEYS):
            raise _invalid(position, "a finding is missing rule, classification, or evidence")
    if risk["assessment_date"] != iso_date:
        raise ValueError(
            f"Assessment at batch position {position} was made for a different assessment date.")
    if (assessment["operational_actions_require_human_approval"] is not True
            or risk["operational_actions_require_human_approval"] is not True):
        raise _invalid(position, "operational_actions_require_human_approval must be true")
    classification = risk["classification"]
    if classification not in _LEVEL_KEYS and classification != _REVIEW:
        raise _invalid(position, "unrecognized classification")
    review = assessment["requires_human_review"]
    if type(review) is not bool or review != (classification == _REVIEW):
        raise _invalid(position, "requires_human_review disagrees with the classification")

    ticket = normalized["ticket"]
    record = {"batch_position": position}
    if isinstance(ticket.get("ticket_id"), str) and ticket["ticket_id"].strip():
        record["ticket_id"] = ticket["ticket_id"]
    entry = {
        "record": record,
        "classification": classification,
        "requires_human_review": review,
        "operational_actions_require_human_approval": True,
        "ticket": deepcopy(ticket),
        "raw_record": deepcopy(normalized["raw_record"]),
        "source": deepcopy(normalized["source"]),
        "field_provenance": deepcopy(normalized["field_provenance"]),
        "validation": deepcopy(validation),
        "findings": deepcopy(risk["findings"]),
        "normalization_issues": deepcopy(normalized["normalization_issues"]),
    }
    client_id = _verified_client(ticket, validation["issues"], normalized["normalization_issues"])
    return entry, client_id, risk["approaching_deadline_days"]


def _verified_client(ticket, validation_issues, normalization_issues):
    """Return client_id only when it is present, a non-blank string, and not flagged."""
    value = ticket.get("client_id")
    if not isinstance(value, str) or not value.strip():
        return None
    for issue in (*validation_issues, *normalization_issues):
        if isinstance(issue, dict) and issue.get("field") == "client_id":
            return None
    return value


def _review_items(clients):
    items = []
    for client in clients:
        for section, classification in (("high", "High"), ("human_review", _REVIEW)):
            for entry in client["sections"][section]:
                items.append({
                    "client_id": client["client_id"],
                    "section": section,
                    "record": deepcopy(entry["record"]),
                    "rules": [finding["rule"] for finding in entry["findings"]
                              if finding["classification"] == classification],
                    "normalization_issues": [{"field": issue.get("field"), "code": issue.get("code")}
                                             for issue in entry["normalization_issues"]],
                    "requires_human_review": entry["requires_human_review"],
                    "operational_actions_require_human_approval": True,
                })
    return items


def _ordered(value, top=False):
    """Copy value with sorted dict keys (summary and review_items first at the top)."""
    if isinstance(value, dict):
        keys = sorted(value)
        if top:
            first = [key for key in _TOP_FIRST if key in value]
            keys = first + [key for key in keys if key not in first]
        return {key: _ordered(value[key]) for key in keys}
    if isinstance(value, list):
        return [_ordered(item) for item in value]
    return value


def _client_evidence(ticket):
    evidence = {"field": "client_id", "present": "client_id" in ticket}
    if evidence["present"]:
        evidence["value"] = deepcopy(ticket["client_id"])
    return evidence


def _count(entries):
    return {"count": len(entries), "records": [deepcopy(entry["record"]) for entry in entries]}


def _code(value):
    text = json.dumps(value, sort_keys=True, ensure_ascii=True)
    return "`" + text.replace("`", "\\u0060") + "`"


def _yes_no(value):
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return _code(value)


def _counted(count):
    return f"{count['count']} (records: {_code(count['records'])})"


def _entries(entries):
    if not entries:
        return ["None."]
    lines = []
    for entry in entries:
        lines += [
            f"- Record {_code(entry['record'])}",
            f"  - Classification: {_code(entry['classification'])}",
            f"  - Requires human review: {_yes_no(entry['requires_human_review'])}",
            "  - Operational actions require human approval: "
            + _yes_no(entry["operational_actions_require_human_approval"]),
            f"  - Source: {_code(entry['source'])}",
        ]
        if "client_id_evidence" in entry:
            lines.append(f"  - Client evidence: {_code(entry['client_id_evidence'])}")
        lines += _issue_lines("Validation issues", entry["validation"]["issues"])
        lines += _issue_lines("Normalization issues", entry["normalization_issues"])
        lines += _finding_lines(entry["findings"])
    return lines


def _issue_lines(title, issues):
    if not issues:
        return [f"  - {title}: none"]
    lines = [f"  - {title}:"]
    for issue in issues:
        lines.append(f"    - Field {_code(issue.get('field'))}, code {_code(issue.get('code'))}, "
                     f"message {_code(issue.get('message'))}")
    return lines


def _finding_lines(findings):
    if not findings:
        return ["  - Findings: none"]
    lines = ["  - Findings:"]
    for finding in findings:
        lines.append(f"    - Rule {_code(finding['rule'])}: classification "
                     f"{_code(finding['classification'])}. Explanation: {_code(finding.get('explanation'))}")
        for item in finding["evidence"]:
            if item.get("present") is True:
                lines.append(f"      - Evidence: field {_code(item.get('field'))}, present yes, "
                             f"value {_code(item.get('value'))}")
            else:
                lines.append(f"      - Evidence: field {_code(item.get('field'))}, present "
                             f"{_yes_no(item.get('present'))}, no value")
        if finding.get("calculated"):
            lines.append(f"      - Calculated: {_code(finding['calculated'])}")
        for item in finding.get("source_evidence", []):
            lines.append(f"      - Provenance of {_code(item.get('field'))}: {_code(item.get('provenance'))}")
    return lines
