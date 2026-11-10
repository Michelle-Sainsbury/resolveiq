"""Local, read-only presentation of generated portfolio briefs.

Classification and rendering belong to the existing assessment/brief modules.
Client scoping happens on the server before data leaves the process. This is a
single-user localhost demo, not a multi-user authorization boundary.
"""
from copy import deepcopy
from datetime import date
import json

from .brief import build_portfolio_brief
from .normalization import normalize_csv_tickets, normalize_json_ticket, assess_normalized_ticket

LEVELS = ("High", "Medium", "Low", "Needs Human Review")
SECTIONS = ("high", "medium", "low", "human_review")


def parse_date(value):
    if not isinstance(value, str):
        raise ValueError("An explicit YYYY-MM-DD assessment date is required.")
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        raise ValueError("Use a valid calendar date in YYYY-MM-DD format.") from None
    if parsed.isoformat() != value:
        raise ValueError("Use YYYY-MM-DD format.")
    return parsed


def records(brief):
    return [entry for client in brief["clients"] for section in SECTIONS
            for entry in client["sections"][section]] + brief["batch_review_queue"]["records"]


def check_brief(brief):
    """Fail visibly on incomplete/tampered reports; never invent sample results."""
    try:
        parse_date(brief["assessment_date"])
        window = brief["approaching_deadline_days"]
        entries = records(brief)
        if (type(window) is not int or window < 0) and not (window is None and not entries):
            raise ValueError
        if brief["operational_actions_require_human_approval"] is not True:
            raise ValueError
        positions = [e["record"]["batch_position"] for e in entries]
        if len(set(positions)) != len(positions) or any(type(p) is not int or p < 1 for p in positions):
            raise ValueError
        if brief["counts"]["records_in_batch"]["count"] != len(entries):
            raise ValueError
        client_ids = [c["client_id"] for c in brief["clients"]]
        if len(set(client_ids)) != len(client_ids):
            raise ValueError
        queue = brief["batch_review_queue"]
        if queue["counts"]["total"] != counted(queue["records"]):
            raise ValueError
        if queue["operational_actions_require_human_approval"] is not True:
            raise ValueError
        if type(queue["requires_human_review"]) is not bool or queue["requires_human_review"] != any(e["requires_human_review"] for e in queue["records"]):
            raise ValueError
        for entry in queue["records"]:
            cid = entry["ticket"].get("client_id")
            flagged = any(i.get("field") == "client_id" for i in entry["validation"]["issues"] + entry["normalization_issues"])
            if isinstance(cid, str) and cid.strip() and not flagged:
                raise ValueError
        grouped = sorted([e for c in brief["clients"] for section in SECTIONS for e in c["sections"][section]], key=lambda e: e["record"]["batch_position"])
        if brief["counts"]["records_in_client_briefs"] != counted(grouped) or brief["counts"]["records_in_batch_review_queue"] != counted(queue["records"]):
            raise ValueError
        if brief["summary"]["batch_review_queue"] != counted(queue["records"]):
            raise ValueError
        if type(brief["requires_human_review"]) is not bool or brief["requires_human_review"] != any(e["requires_human_review"] for e in entries):
            raise ValueError
        expected_summary = []
        for client in brief["clients"]:
            members = sorted([e for section in SECTIONS for e in client["sections"][section]], key=lambda e: e["record"]["batch_position"])
            if client["counts"]["total"] != counted(members) or client["operational_actions_require_human_approval"] is not True:
                raise ValueError
            if type(client["requires_human_review"]) is not bool or client["requires_human_review"] != any(e["requires_human_review"] for e in members):
                raise ValueError
            expected_summary.append({"client_id": client["client_id"], **{key: client["counts"][key] for key in SECTIONS}})
            if not isinstance(client["client_id"], str) or not client["client_id"].strip():
                raise ValueError
            for section in SECTIONS:
                members = client["sections"][section]
                if client["counts"][section] != counted(members):
                    raise ValueError
                for entry in members:
                    if entry["ticket"].get("client_id") != client["client_id"]:
                        raise ValueError
                    if entry["classification"] != LEVELS[SECTIONS.index(section)]:
                        raise ValueError
        if brief["summary"]["clients"] != expected_summary or not isinstance(brief["review_items"], list):
            raise ValueError
        for entry in entries:
            if entry["classification"] not in LEVELS:
                raise ValueError
            if type(entry["requires_human_review"]) is not bool or entry["requires_human_review"] != (entry["classification"] == "Needs Human Review"):
                raise ValueError
            if entry["operational_actions_require_human_approval"] is not True:
                raise ValueError
            for key in ("ticket", "validation", "findings", "source", "field_provenance", "raw_record", "normalization_issues"):
                entry[key]
    except (KeyError, TypeError, AttributeError, ValueError):
        raise ValueError("The brief is incomplete or inconsistent. Generate it with scripts/run_brief.py.") from None
    return brief


def counted(entries):
    return {"count": len(entries), "records": [deepcopy(e["record"]) for e in entries]}


def scope_brief(brief, client=None, queue=False):
    """Return a complete, independently renderable brief for exactly one scope."""
    if queue == (client is not None):
        raise ValueError("Select exactly one client or the unassigned-client review queue.")
    scoped = deepcopy(brief)
    if queue:
        scoped["clients"] = []
        scoped["summary"]["clients"] = []
        scoped["review_items"] = []
    else:
        selected = [c for c in scoped["clients"] if c["client_id"] == client]
        if len(selected) != 1:
            raise KeyError("Client not found.")
        scoped["clients"] = selected
        scoped["summary"]["clients"] = [s for s in scoped["summary"]["clients"] if s["client_id"] == client]
        scoped["review_items"] = [i for i in scoped["review_items"] if i["client_id"] == client]
        scoped["batch_review_queue"]["records"] = []
        scoped["batch_review_queue"]["counts"]["total"] = counted([])
        scoped["batch_review_queue"]["requires_human_review"] = False
    grouped = sorted([e for c in scoped["clients"] for section in SECTIONS for e in c["sections"][section]], key=lambda e: e["record"]["batch_position"])
    waiting = scoped["batch_review_queue"]["records"]
    scoped["summary"]["batch_review_queue"] = counted(waiting)
    scoped["counts"] = {"records_in_batch": counted(grouped + waiting),
                        "records_in_client_briefs": counted(grouped),
                        "records_in_batch_review_queue": counted(waiting)}
    scoped["requires_human_review"] = any(e["requires_human_review"] for e in grouped + waiting)
    return scoped


def intake_preview(content, source_format, assessment_date, client=None, queue=False):
    """Assess synthetic intake in memory; return only explicitly selected scope."""
    day = parse_date(assessment_date)
    if not isinstance(content, str):
        raise ValueError("Provide synthetic ticket text.")
    if source_format == "json":
        try:
            decoded = json.loads(content)
        except ValueError:
            raise ValueError("Invalid JSON. Use a ticket object or an array of ticket objects.") from None
        raw_records = decoded if isinstance(decoded, list) else [decoded]
        envelopes = [normalize_json_ticket(record) for record in raw_records]
    elif source_format == "csv":
        envelopes = normalize_csv_tickets(content)
    else:
        raise ValueError("Supported intake formats are JSON and CSV.")
    if not envelopes or len(envelopes) > 500:
        raise ValueError("Provide between 1 and 500 synthetic ticket records.")
    assessed = [assess_normalized_ticket(e, assessment_date=day) for e in envelopes]
    brief = build_portfolio_brief(assessed, assessment_date=day)
    if not queue and client not in [c["client_id"] for c in brief["clients"]]:
        raise ValueError("No tickets belong to the selected client. Review the client_id fields or choose the unassigned-client queue.")
    return scope_brief(brief, client, queue)
