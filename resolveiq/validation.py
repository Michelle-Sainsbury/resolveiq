"""Validate decoded JSON tickets without filling in or changing their values."""

import re
from datetime import date


STATUSES = frozenset({"open", "in_progress", "blocked", "completed", "cancelled"})
REQUIRED_FIELDS = ("ticket_id", "client_id", "owner", "status", "due_date", "dependencies")


def validate_ticket(ticket):
    """Return validation and human-review flags for a decoded JSON ticket.

    Dependencies are ticket ID strings, not embedded tickets. This function
    checks one ticket's internal consistency, not external ticket existence.
    Unknown extra fields are preserved by leaving the input untouched.
    """
    issues = []

    def flag(field, code, message):
        issues.append({"field": field, "code": code, "message": message})

    def result():
        return {"valid": not issues, "requires_human_review": bool(issues), "issues": issues}

    if not isinstance(ticket, dict):
        flag("ticket", "malformed", "Expected a decoded JSON object.")
        return result()

    for field in REQUIRED_FIELDS:
        if field not in ticket or ticket[field] is None:
            flag(field, "missing", "Required information is missing or unknown.")
        elif field != "dependencies":
            value = ticket[field]
            if not isinstance(value, str) or not value.strip():
                flag(field, "malformed", "Expected a non-empty string.")
            elif field == "status" and value not in STATUSES:
                flag(field, "malformed", "Unrecognized status; see the documented schema.")
            elif field == "due_date":
                try:
                    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
                        raise ValueError
                    date.fromisoformat(value)
                except ValueError:
                    flag(field, "malformed", "Expected a valid calendar date in YYYY-MM-DD format.")

    dependencies = ticket.get("dependencies")
    if dependencies is not None:
        if not isinstance(dependencies, list):
            flag("dependencies", "malformed", "Expected a list of ticket ID strings, or null if unknown.")
        else:
            seen = set()
            for index, dependency in enumerate(dependencies):
                field = f"dependencies[{index}]"
                if not isinstance(dependency, str) or not dependency.strip():
                    flag(field, "malformed", "Expected a non-empty ticket ID string.")
                    continue
                if dependency == ticket.get("ticket_id"):
                    flag(field, "contradictory", "A ticket cannot depend on itself.")
                if dependency in seen:
                    flag(field, "contradictory", "Dependency is listed more than once.")
                seen.add(dependency)
            if ticket.get("status") == "blocked" and not dependencies:
                flag("dependencies", "contradictory", "Blocked status with confirmed no dependencies needs review.")

    return result()
