"""Serve the localhost dashboard with server-scoped generated brief data."""
import argparse
import contextlib
import io
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
import tempfile
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from resolveiq.dashboard import check_brief, scope_brief, intake_preview, parse_date
from resolveiq.brief import brief_to_json, render_brief_markdown
from scripts.run_brief import main as generate_brief

ASSETS = {"/": ("index.html", "text/html"), "/index.html": ("index.html", "text/html"),
          "/app.js": ("app.js", "text/javascript"), "/styles.css": ("styles.css", "text/css")}


def make_handler(brief):
    check_brief(brief)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass  # Never log submitted ticket contents.

        def trusted(self):
            # Block DNS rebinding and cross-origin browser requests. Local demo only.
            if self.headers.get("Host") not in {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}:
                self.respond(403, {"error": "Localhost requests only."})
                return False
            origin = self.headers.get("Origin")
            if origin and origin not in {f"http://127.0.0.1:{self.server.server_port}", f"http://localhost:{self.server.server_port}"}:
                self.respond(403, {"error": "Cross-origin requests are not allowed."})
                return False
            return True

        def respond(self, status, payload, content_type="application/json", download=None):
            body = json.dumps(payload).encode() if content_type == "application/json" else payload.encode() if isinstance(payload, str) else payload
            self.send_response(status)
            self.send_header("Content-Type", content_type + "; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; object-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
            if download:
                self.send_header("Content-Disposition", 'attachment; filename="' + download + '"')
            self.end_headers()
            self.wfile.write(body)

        def selection(self, query):
            client = query.get("client", [None])
            scope = query.get("scope", ["client"])
            if len(client) != 1 or len(scope) != 1 or scope[0] not in ("client", "queue"):
                raise ValueError("Invalid scope selection.")
            return client[0], scope[0] == "queue"

        def do_GET(self):
            if not self.trusted():
                return
            parsed = urlsplit(self.path)
            try:
                if parsed.path in ASSETS:
                    filename, mime = ASSETS[parsed.path]
                    return self.respond(200, (ROOT / "dashboard" / filename).read_bytes(), mime)
                if parsed.path == "/api/clients":
                    return self.respond(200, {"clients": [c["client_id"] for c in brief["clients"]],
                        "assessment_date": brief["assessment_date"], "approaching_deadline_days": brief["approaching_deadline_days"],
                        "queue_available": bool(brief["batch_review_queue"]["records"])})
                if parsed.path in ("/api/brief", "/api/report"):
                    query = parse_qs(parsed.query, keep_blank_values=True)
                    scoped = scope_brief(brief, *self.selection(query))
                    if parsed.path == "/api/brief":
                        return self.respond(200, scoped)
                    formats = query.get("format", ["markdown"])
                    if len(formats) != 1 or formats[0] not in ("markdown", "json"):
                        raise ValueError("Choose markdown or json.")
                    if formats[0] == "json":
                        return self.respond(200, brief_to_json(scoped), "text/plain", "portfolio.json")
                    return self.respond(200, render_brief_markdown(scoped), "text/plain")
                return self.respond(404, {"error": "Not found."})
            except KeyError:
                self.respond(404, {"error": "Client not found."})
            except ValueError as error:
                self.respond(400, {"error": str(error)})

        def do_POST(self):
            if not self.trusted():
                return
            if self.path != "/api/intake":
                return self.respond(404, {"error": "Not found."})
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                return self.respond(415, {"error": "Use application/json."})
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 1_000_000:
                    return self.respond(413, {"error": "Intake must be at most 1 MB."})
                body = json.loads(self.rfile.read(length))
                if not isinstance(body, dict) or type(body.get("queue", False)) is not bool:
                    raise ValueError("Invalid intake request.")
                result = intake_preview(body.get("content"), body.get("format"), body.get("assessment_date"),
                                        body.get("client"), body.get("queue", False))
                self.respond(200, {"brief": result, "markdown": render_brief_markdown(result), "json": brief_to_json(result)})
            except (ValueError, UnicodeDecodeError) as error:
                self.respond(400, {"error": str(error)})

    return Handler


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--date", help="Generate actual brief.json from synthetic tickets for YYYY-MM-DD.")
    mode.add_argument("--brief", type=Path, help="Read an existing runner-generated brief.json.")
    parser.add_argument("--tickets", type=Path, default=ROOT / "data/tickets/tickets.json")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args(argv)
    try:
        if args.brief:
            brief = check_brief(json.loads(args.brief.read_text(encoding="utf-8")))
        else:
            parse_date(args.date)
            with tempfile.TemporaryDirectory(prefix="resolveiq-dashboard-") as directory:
                with contextlib.redirect_stdout(io.StringIO()):
                    code = generate_brief(["--date", args.date, "--tickets", str(args.tickets), "--out", directory])
                if code:
                    return code
                brief = check_brief(json.loads((Path(directory) / "brief.json").read_text()))
        server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(brief))
    except (OSError, ValueError) as error:
        print(f"Cannot start dashboard: {error}", file=sys.stderr)
        return 1
    print(f"ResolveIQ: http://127.0.0.1:{server.server_port} • assessment {brief['assessment_date']}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
