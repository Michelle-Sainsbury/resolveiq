import copy
import json
import unittest

from resolveiq import validate_ticket


class ValidateTicketTests(unittest.TestCase):
    def setUp(self):
        self.ticket = json.loads('''{
            "ticket_id": "T-100", "client_id": "C-10", "owner": "Synthetic Owner",
            "status": "open", "due_date": "2026-11-30", "dependencies": []
        }''')

    def test_complete_ticket_with_confirmed_no_dependencies(self):
        self.assertEqual(validate_ticket(self.ticket), {
            "valid": True, "requires_human_review": False, "issues": []
        })

    def test_complete_ticket_with_dependency_ids(self):
        self.ticket.update(status="blocked", dependencies=["T-99"])
        self.assertTrue(validate_ticket(self.ticket)["valid"])

    def test_each_required_field_missing(self):
        for field in self.ticket:
            with self.subTest(field=field):
                ticket = {k: v for k, v in self.ticket.items() if k != field}
                self.assertEqual(validate_ticket(ticket)["issues"], [{
                    "field": field, "code": "missing",
                    "message": "Required information is missing or unknown."
                }])
                self.assertTrue(validate_ticket(ticket)["requires_human_review"])

    def test_null_dependencies_are_unknown(self):
        self.ticket["dependencies"] = None
        result = validate_ticket(self.ticket)
        self.assertFalse(result["valid"])
        self.assertTrue(result["requires_human_review"])
        self.assertEqual(result["issues"][0]["field"], "dependencies")
        self.assertEqual(result["issues"][0]["code"], "missing")

    def test_null_required_values(self):
        for field in self.ticket:
            with self.subTest(field=field):
                ticket = dict(self.ticket, **{field: None})
                self.assertEqual(validate_ticket(ticket)["issues"][0]["code"], "missing")

    def test_malformed_string_fields(self):
        for field in ("ticket_id", "client_id", "owner", "status", "due_date"):
            for value in ("", "  ", 123, True, [], {}):
                with self.subTest(field=field, value=value):
                    self.assertFalse(validate_ticket(dict(self.ticket, **{field: value}))["valid"])

    def test_unknown_status(self):
        self.ticket["status"] = "maybe"
        self.assertEqual(validate_ticket(self.ticket)["issues"][0]["code"], "malformed")

    def test_invalid_dates(self):
        for value in ("2026-02-29", "2026-13-01", "20261130", "2026-1-01", "2026-11-30T12:00:00"):
            with self.subTest(value=value):
                self.ticket["due_date"] = value
                self.assertFalse(validate_ticket(self.ticket)["valid"])

    def test_valid_leap_day(self):
        self.ticket["due_date"] = "2028-02-29"
        self.assertTrue(validate_ticket(self.ticket)["valid"])

    def test_malformed_dependencies(self):
        for value in ("none", {}, 12, True, [None], [123], [""], ["  "], [{}]):
            with self.subTest(value=value):
                self.ticket["dependencies"] = value
                self.assertFalse(validate_ticket(self.ticket)["valid"])

    def test_contradictions(self):
        for updates in ({"dependencies": ["T-100"]},
                        {"dependencies": ["T-99", "T-99"]},
                        {"status": "blocked", "dependencies": []}):
            with self.subTest(updates=updates):
                result = validate_ticket(dict(self.ticket, **updates))
                self.assertTrue(result["requires_human_review"])
                self.assertEqual(result["issues"][0]["code"], "contradictory")

    def test_non_object_input(self):
        for value in (None, [], "{}", 123, True):
            with self.subTest(value=value):
                self.assertFalse(validate_ticket(value)["valid"])

    def test_reports_multiple_issues(self):
        result = validate_ticket({"dependencies": None})
        self.assertEqual(len(result["issues"]), 6)

    def test_does_not_mutate_or_invent_values(self):
        self.ticket.update(dependencies=None, extra={"notes": ["synthetic"]})
        del self.ticket["owner"]
        before = copy.deepcopy(self.ticket)
        validate_ticket(self.ticket)
        self.assertEqual(self.ticket, before)


if __name__ == "__main__":
    unittest.main()
