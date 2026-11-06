import copy
from datetime import date, datetime, timedelta
import unittest

from resolveiq import assess_ticket_risk


class AssessTicketRiskTests(unittest.TestCase):
    def setUp(self):
        self.today = date(2026, 11, 5)
        self.ticket = {
            "ticket_id": "T-100", "client_id": "C-10", "owner": "Synthetic Owner",
            "status": "open", "due_date": "2026-11-30", "dependencies": [],
        }

    def assess(self, **updates):
        return assess_ticket_risk(dict(self.ticket, **updates), assessment_date=self.today)

    def test_blocked(self):
        result = self.assess(status="blocked", dependencies=["T-99"])
        self.assertEqual(result["classification"], "High")
        self.assertFalse(result["requires_human_review"])
        self.assertEqual(result["findings"][0]["evidence"], [
            {"field": "status", "present": True, "value": "blocked"},
            {"field": "dependencies", "present": True, "value": ["T-99"]},
        ])

    def test_deadline_boundaries(self):
        for days, expected in [(-1, "High"), (0, "Medium"), (1, "Medium"),
                               (3, "Medium"), (4, "Low")]:
            with self.subTest(days=days):
                due = (self.today + timedelta(days=days)).isoformat()
                result = self.assess(due_date=due)
                self.assertEqual(result["classification"], expected)
                self.assertFalse(result["requires_human_review"])
                finding = result["findings"][0]
                self.assertEqual(finding["calculated"]["days_remaining"], days)
                self.assertIn({"field": "due_date", "present": True, "value": due}, finding["evidence"])
                self.assertEqual(result["assessment_date"], "2026-11-05")

    def test_calendar_days_across_month_and_leap_day(self):
        for start, due in [(date(2026, 12, 30), "2027-01-02"),
                           (date(2028, 2, 27), "2028-03-01")]:
            with self.subTest(start=start):
                result = assess_ticket_risk(dict(self.ticket, due_date=due), assessment_date=start)
                self.assertEqual(result["classification"], "Medium")
                self.assertEqual(result["findings"][0]["calculated"]["days_remaining"], 3)

    def test_completed_and_cancelled_ignore_deadlines(self):
        for status in ("completed", "cancelled"):
            for due in ("2026-11-04", "2026-11-05", "2026-11-08"):
                with self.subTest(status=status, due=due):
                    result = self.assess(status=status, due_date=due)
                    self.assertEqual(result["classification"], "Low")
                    self.assertEqual([f["rule"] for f in result["findings"]], ["inactive"])

    def test_multiple_operational_findings(self):
        for due, rule in [("2026-11-04", "overdue"), ("2026-11-08", "approaching_deadline")]:
            with self.subTest(due=due):
                result = self.assess(status="blocked", dependencies=["T-99"], due_date=due)
                self.assertEqual(result["classification"], "High")
                self.assertEqual([f["rule"] for f in result["findings"]], ["blocked", rule])

    def test_contradictions_take_precedence(self):
        for updates in ({"status": "blocked"}, {"dependencies": ["T-100"]},
                        {"dependencies": ["T-99", "T-99"]}):
            with self.subTest(updates=updates):
                result = self.assess(**updates)
                self.assertEqual(result["classification"], "Needs Human Review")
                self.assertTrue(result["requires_human_review"])
                self.assertEqual(result["validation_issues"][0]["code"], "contradictory")

    def test_missing_and_null_have_distinct_evidence(self):
        ticket = dict(self.ticket, dependencies=None)
        del ticket["owner"]
        result = assess_ticket_risk(ticket, assessment_date=self.today)
        self.assertEqual(result["classification"], "Needs Human Review")
        evidence = [e for f in result["findings"] for e in f["evidence"]]
        self.assertIn({"field": "owner", "present": False}, evidence)
        self.assertIn({"field": "dependencies", "present": True, "value": None}, evidence)

    def test_validation_does_not_hide_supported_signals(self):
        result = self.assess(owner=None, status="blocked", dependencies=["T-99"], due_date="2026-11-04")
        self.assertEqual(result["classification"], "Needs Human Review")
        self.assertEqual([f["rule"] for f in result["findings"]], ["validation_missing", "blocked", "overdue"])

    def test_malformed_fields_do_not_produce_unsupported_findings(self):
        result = self.assess(status=[], due_date="tomorrow")
        self.assertEqual(result["classification"], "Needs Human Review")
        self.assertEqual([f["rule"] for f in result["findings"]], ["validation_malformed"] * 2)
        result = self.assess(status="blocked", dependencies=["T-99"], due_date="tomorrow")
        self.assertEqual([f["rule"] for f in result["findings"]], ["validation_malformed", "blocked"])

    def test_inactive_missing_information_still_needs_review(self):
        self.assertEqual(self.assess(status="completed", owner=None)["classification"], "Needs Human Review")

    def test_non_object(self):
        for ticket in (None, [], "{}", 12):
            with self.subTest(ticket=ticket):
                result = assess_ticket_risk(ticket, assessment_date=self.today)
                self.assertEqual(result["classification"], "Needs Human Review")

    def test_configurable_threshold(self):
        ticket = dict(self.ticket, due_date="2026-11-09")
        result = assess_ticket_risk(ticket, assessment_date=self.today, approaching_deadline_days=4)
        self.assertEqual(result["classification"], "Medium")
        self.assertEqual(result["approaching_deadline_days"], 4)
        result = assess_ticket_risk(ticket, assessment_date=self.today, approaching_deadline_days=0)
        self.assertEqual(result["classification"], "Low")

    def test_invalid_configuration(self):
        for value in (-1, True, 3.5, "3", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                assess_ticket_risk(self.ticket, assessment_date=self.today, approaching_deadline_days=value)
        for value in (None, "2026-11-05", datetime(2026, 11, 5)):
            with self.subTest(value=value), self.assertRaises(TypeError):
                assess_ticket_risk(self.ticket, assessment_date=value)
        with self.assertRaises(TypeError):
            assess_ticket_risk(self.ticket)

    def test_all_outcomes_require_operational_approval(self):
        for updates in ({}, {"due_date": "2026-11-08"}, {"due_date": "2026-11-04"}, {"owner": None}):
            with self.subTest(updates=updates):
                self.assertTrue(self.assess(**updates)["operational_actions_require_human_approval"])

    def test_input_unchanged_and_evidence_independent(self):
        self.ticket.update(status="blocked", dependencies=["T-99"])
        before = copy.deepcopy(self.ticket)
        result = assess_ticket_risk(self.ticket, assessment_date=self.today)
        self.assertEqual(self.ticket, before)
        result["findings"][0]["evidence"][1]["value"].append("T-98")
        self.assertEqual(self.ticket, before)


if __name__ == "__main__":
    unittest.main()
