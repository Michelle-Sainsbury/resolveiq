import copy
from datetime import date
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from resolveiq import normalize_json_ticket, assess_normalized_ticket
from resolveiq.brief import build_portfolio_brief, render_brief_markdown
from resolveiq.dashboard import check_brief, scope_brief, intake_preview, records
from scripts.serve_dashboard import make_handler

ROOT = Path(__file__).resolve().parent.parent
DAY = date(2026, 11, 4)


class DashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (ROOT / 'data/tickets/tickets.json').read_bytes()
        cls.tickets = json.loads(cls.raw)
        cls.brief = build_portfolio_brief([
            assess_normalized_ticket(normalize_json_ticket(t), assessment_date=DAY)
            for t in cls.tickets], assessment_date=DAY)
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(cls.brief))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = 'http://127.0.0.1:' + str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        assert (ROOT / 'data/tickets/tickets.json').read_bytes() == cls.raw

    def get(self, path, headers=None):
        with urlopen(Request(self.url + path, headers=headers or {})) as response:
            return response.read(), response.headers

    def post(self, payload, headers=None):
        with urlopen(Request(self.url + '/api/intake', data=json.dumps(payload).encode(),
                             headers={'Content-Type': 'application/json', **(headers or {})})) as response:
            return json.loads(response.read())

    def test_catalog_has_no_ticket_data(self):
        data = json.loads(self.get('/api/clients')[0])
        self.assertEqual(data['clients'], ['Client A', 'Client B', 'Client C'])
        self.assertEqual(data['assessment_date'], '2026-11-04')
        self.assertEqual(data['approaching_deadline_days'], 3)
        self.assertNotIn('T-101', json.dumps(data))

    def test_every_client_scoped_at_server(self):
        for name, total in [('Client A', 10), ('Client B', 8), ('Client C', 1)]:
            with self.subTest(client=name):
                scoped = json.loads(self.get('/api/brief?client=' + name.replace(' ', '%20'))[0])
                self.assertEqual(len(records(scoped)), total)
                self.assertEqual([c['client_id'] for c in scoped['clients']], [name])
                self.assertEqual(scoped['counts']['records_in_batch']['count'], total)
                self.assertEqual(scoped['batch_review_queue']['records'], [])
                for e in records(scoped):
                    self.assertEqual(e['ticket']['client_id'], name)
                forbidden = [t['ticket_id'] for t in self.tickets if t.get('client_id') != name]
                for ticket_id in forbidden:
                    self.assertNotIn('"ticket_id": "' + ticket_id + '"', json.dumps(scoped))

    def test_queue_never_mixed_with_client(self):
        scoped = json.loads(self.get('/api/brief?scope=queue')[0])
        self.assertEqual(scoped['clients'], [])
        self.assertEqual([e['record']['ticket_id'] for e in records(scoped)], ['T-111'])
        self.assertTrue(scoped['requires_human_review'])
        self.assertEqual(scoped['counts']['records_in_client_briefs']['count'], 0)

    def test_reports_scoped_and_use_existing_renderer(self):
        for selection in ('client=Client%20A', 'client=Client%20B', 'scope=queue'):
            with self.subTest(selection=selection):
                scoped = json.loads(self.get('/api/brief?' + selection)[0])
                markdown = self.get('/api/report?' + selection)[0].decode()
                self.assertEqual(markdown, render_brief_markdown(scoped))
                exported = json.loads(self.get('/api/report?' + selection + '&format=json')[0])
                self.assertEqual(exported, scoped)

    def test_independent_findings_and_missing_values_preserved(self):
        scoped = scope_brief(self.brief, 'Client B')
        entry = next(e for e in records(scoped) if e['record']['ticket_id'] == 'T-106')
        original = next(e for e in records(self.brief) if e['record']['ticket_id'] == 'T-106')
        self.assertEqual(entry, original)
        self.assertEqual(entry['classification'], 'Needs Human Review')
        self.assertIsNone(entry['ticket']['owner'])
        self.assertIn('overdue', [f['rule'] for f in entry['findings']])
        self.assertTrue(entry['operational_actions_require_human_approval'])
        self.assertTrue(scoped['operational_actions_require_human_approval'])

    def test_scope_copies_do_not_mutate_source(self):
        before = copy.deepcopy(self.brief)
        scoped = scope_brief(self.brief, 'Client A')
        records(scoped)[0]['findings'].clear()
        self.assertEqual(self.brief, before)

    def test_invalid_scope_does_not_fall_back_to_all_clients(self):
        for selection, status in [('', 400), ('?client=unknown', 404), ('?scope=queue&client=Client%20A', 400),
                                  ('?client=Client%20A&client=Client%20B', 400), ('?scope=all', 400)]:
            with self.subTest(selection=selection), self.assertRaises(HTTPError) as error:
                self.get('/api/brief' + selection)
            self.assertEqual(error.exception.code, status)

    def test_reject_cross_origin_and_untrusted_host(self):
        for headers in ({'Origin': 'https://untrusted.example'}, {'Host': 'untrusted.example'}):
            with self.subTest(headers=headers), self.assertRaises(HTTPError) as error:
                self.get('/api/clients', headers)
            self.assertEqual(error.exception.code, 403)
        with self.assertRaises(HTTPError) as error:
            self.post({}, {'Origin': 'https://untrusted.example'})
        self.assertEqual(error.exception.code, 403)

    def test_assets_allowlisted_not_repository_files(self):
        for path in ('/README.md', '/.git/config', '/data/tickets/tickets.json', '/../README.md', '/api/update-ticket'):
            with self.subTest(path=path), self.assertRaises(HTTPError) as error:
                self.get(path)
            self.assertEqual(error.exception.code, 404)
        _, headers = self.get('/')
        self.assertEqual(headers['Cache-Control'], 'no-store')
        self.assertIn("script-src 'self'", headers['Content-Security-Policy'])

    def test_json_intake_uses_original_pipeline_and_scopes_result(self):
        payload = {'content': self.raw.decode(), 'format': 'json', 'assessment_date': '2026-11-04', 'client': 'Client A'}
        result = self.post(payload)
        self.assertEqual(result['brief'], scope_brief(self.brief, 'Client A'))
        self.assertEqual(result['markdown'], render_brief_markdown(result['brief']))
        self.assertEqual(json.loads(result['json']), result['brief'])

    def test_intake_does_not_persist_or_replace_generated_brief(self):
        ticket = dict(self.tickets[0], ticket_id='PREVIEW', status='open')
        self.post({'content': json.dumps(ticket), 'format': 'json', 'assessment_date': '2026-11-04', 'client': 'Client A'})
        saved = json.loads(self.get('/api/brief?client=Client%20A')[0])
        self.assertNotIn('PREVIEW', json.dumps(saved))
        self.assertEqual(len(records(saved)), 10)

    def test_csv_intake_preserves_empty_and_unknown_dependencies(self):
        text = 'ticket_id,client_id,owner,status,due_date,dependencies\nX,Client A,Owner,open,2026-11-07,[]\nY,Client A,Owner,open,2026-11-07,null\n'
        scoped = intake_preview(text, 'csv', '2026-11-04', 'Client A')
        entries = {e['ticket']['ticket_id']: e for e in records(scoped)}
        self.assertEqual(entries['X']['classification'], 'Medium')
        self.assertEqual(entries['X']['ticket']['dependencies'], [])
        self.assertEqual(entries['Y']['classification'], 'Needs Human Review')
        self.assertIsNone(entries['Y']['ticket']['dependencies'])

    def test_malformed_intake_visible_in_queue_without_invention(self):
        scoped = intake_preview('owner,owner\nA,B\n', 'csv', '2026-11-04', queue=True)
        self.assertTrue(scoped['requires_human_review'])
        self.assertEqual(records(scoped)[0]['ticket'], {})
        self.assertTrue(records(scoped)[0]['normalization_issues'])

    def test_invalid_intake_errors_without_returning_other_clients(self):
        base = {'format': 'json', 'assessment_date': '2026-11-04', 'client': 'Client A'}
        for updates in ({'content': '['}, {'content': '[]'}, {'content': '{}', 'assessment_date': '2026-02-30'},
                        {'content': '{}', 'format': 'xml'}, {'content': json.dumps(self.tickets[4])}):
            with self.subTest(updates=updates), self.assertRaises(HTTPError) as error:
                self.post({**base, **updates})
            self.assertEqual(error.exception.code, 400)

    def test_missing_intake_content_is_rejected(self):
        with self.assertRaises(HTTPError) as error:
            self.post({'format': 'json', 'assessment_date': '2026-11-04', 'client': 'Client A'})
        self.assertEqual(error.exception.code, 400)

    def test_existing_brief_validation_and_tampered_flags(self):
        self.assertEqual(check_brief(self.brief), self.brief)
        for mutate in (lambda b: b.pop('clients'),
                       lambda b: b.update(operational_actions_require_human_approval=False),
                       lambda b: b['clients'][0]['counts']['high'].update(count=99)):
            with self.subTest(mutate=mutate):
                bad = copy.deepcopy(self.brief)
                mutate(bad)
                with self.assertRaises(ValueError):
                    check_brief(bad)

    def test_report_format_rejected(self):
        with self.assertRaises(HTTPError) as error:
            self.get('/api/report?client=Client%20A&format=html')
        self.assertEqual(error.exception.code, 400)

    def test_scoped_reports_remain_valid_independent_briefs(self):
        for client in ('Client A', 'Client B', 'Client C'):
            with self.subTest(client=client):
                check_brief(scope_brief(self.brief, client))
        check_brief(scope_brief(self.brief, queue=True))

    def test_invalid_summary_queue_and_review_flags_rejected(self):
        for mutate in (lambda b: b.pop('summary'),
                       lambda b: b['batch_review_queue']['counts']['total'].update(count=99),
                       lambda b: b['clients'][0].update(requires_human_review=False),
                       lambda b: b.update(requires_human_review=1)):
            with self.subTest(mutate=mutate):
                bad = copy.deepcopy(self.brief)
                mutate(bad)
                with self.assertRaises(ValueError):
                    check_brief(bad)

    def test_empty_generated_brief_is_valid_without_fabricated_window(self):
        empty = build_portfolio_brief([], assessment_date=DAY)
        self.assertIsNone(empty['approaching_deadline_days'])
        check_brief(empty)
        self.assertEqual(records(empty), [])

    def test_no_classification_logic_in_browser(self):
        source = (ROOT / 'dashboard/app.js').read_text()
        self.assertNotIn('innerHTML', source)
        self.assertNotIn('eval(', source)
        self.assertNotIn('Date.now(', source)
        self.assertNotIn('new Date(', source)


if __name__ == '__main__':
    unittest.main()
