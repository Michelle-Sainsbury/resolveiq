"""Deterministic risk signals backed by ticket evidence; no operational actions."""

from copy import deepcopy
from datetime import date

from .validation import validate_ticket


def assess_ticket_risk(ticket, *, assessment_date, approaching_deadline_days=3):
    """Assess a decoded JSON ticket using an explicit datetime.date.

    Validation issues take precedence over operational signals. Findings retain
    independently supported signals even when the overall outcome needs review.
    No result authorizes an operational action.
    """
    if type(assessment_date) is not date:
        raise TypeError("assessment_date must be a datetime.date (not a datetime).")
    if type(approaching_deadline_days) is not int or approaching_deadline_days < 0:
        raise ValueError("approaching_deadline_days must be a non-negative integer.")

    validation = validate_ticket(ticket)
    findings = []

    def evidence(field):
        if field == "ticket":
            return {"field": field, "present": True, "value": deepcopy(ticket)}
        root = field.split("[")[0]
        present = isinstance(ticket, dict) and root in ticket
        item = {"field": field, "present": present}
        if present:
            value = ticket[root]
            if "[" in field:
                value = value[int(field.split("[")[1].rstrip("]"))]
            item["value"] = deepcopy(value)
        return item

    def add(rule, classification, explanation, fields, **calculated):
        findings.append({
            "rule": rule, "classification": classification,
            "explanation": explanation,
            "evidence": [evidence(field) for field in fields],
            "calculated": calculated,
        })

    for issue in validation["issues"]:
        # Include the ticket ID when it establishes a self-dependency conflict.
        fields = [issue["field"]]
        if issue["code"] == "contradictory":
            fields = list(dict.fromkeys(fields + ["ticket_id", "status", "dependencies"]))
        add("validation_" + issue["code"], "Needs Human Review",
            issue["message"], fields)

    status = ticket.get("status") if isinstance(ticket, dict) else None
    status_valid = isinstance(status, str) and status in {
        "open", "in_progress", "blocked", "completed", "cancelled"
    }
    if status_valid:
        if status in {"completed", "cancelled"}:
            add("inactive", "Low", "Recorded status is inactive; deadline rules do not apply.", ["status"])
        else:
            if status == "blocked":
                add("blocked", "High", "Recorded status explicitly indicates a blocker.", ["status", "dependencies"])
            date_invalid = any(issue["field"] == "due_date" for issue in validation["issues"])
            if not date_invalid:
                remaining = (date.fromisoformat(ticket["due_date"]) - assessment_date).days
                fields = ["status", "due_date"]
                if remaining < 0:
                    add("overdue", "High", "Active ticket is past its due date.", fields,
                        days_remaining=remaining, days_overdue=-remaining)
                elif remaining <= approaching_deadline_days:
                    add("approaching_deadline", "Medium", "Active ticket is within the approaching-deadline window.",
                        fields, days_remaining=remaining)
                elif status != "blocked":
                    add("outside_deadline_window", "Low", "No elevated risk detected by the status and deadline rules.",
                        fields, days_remaining=remaining)

    needs_review = validation["requires_human_review"]
    classification = "Needs Human Review" if needs_review else max(
        (finding["classification"] for finding in findings),
        key={"Low": 0, "Medium": 1, "High": 2}.__getitem__,
    )
    return {
        "classification": classification,
        "assessment_date": assessment_date.isoformat(),
        "approaching_deadline_days": approaching_deadline_days,
        "requires_human_review": needs_review,
        "operational_actions_require_human_approval": True,
        "validation_issues": deepcopy(validation["issues"]),
        "findings": findings,
    }
