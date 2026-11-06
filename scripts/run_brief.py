"""Run the portfolio brief on a tickets file and write brief.json and brief.md.

    python3 scripts/run_brief.py --date 2026-11-04 --out OUTPUT_DIR [--tickets FILE]

Read-only toward tickets: it only reads the tickets file. It normalizes each
record with normalize_json_ticket, assesses it with assess_normalized_ticket for
the assessment date given by --date (never read from the clock), builds the
brief, and writes brief.json and brief.md. Nothing is written outside --out.
Standard library only; no network; no LLM.

Exit codes: 0 on success, 1 when the tickets file or the output directory cannot
be used, 2 for bad command-line arguments.
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from resolveiq import assess_normalized_ticket, normalize_json_ticket  # noqa: E402
from resolveiq.brief import brief_to_json, build_portfolio_brief, render_brief_markdown  # noqa: E402

DEFAULT_TICKETS = _ROOT / "data" / "tickets" / "tickets.json"


def _iso_date(text):
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", text):
        raise argparse.ArgumentTypeError("expected a date in YYYY-MM-DD format")
    try:
        return date.fromisoformat(text)
    except ValueError:
        raise argparse.ArgumentTypeError("not a valid calendar date")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Build a deterministic portfolio brief from a tickets JSON file.",
        allow_abbrev=False)
    parser.add_argument("--date", required=True, type=_iso_date,
                        help="assessment date, YYYY-MM-DD (never read from the clock)")
    parser.add_argument("--out", required=True, type=Path,
                        help="directory for brief.json and brief.md (created if missing)")
    parser.add_argument("--tickets", type=Path, default=DEFAULT_TICKETS,
                        help="JSON array of ticket records (default: data/tickets/tickets.json)")
    args = parser.parse_args(argv)

    try:
        records = json.loads(args.tickets.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        print(f"Cannot read tickets from {args.tickets}: {error}", file=sys.stderr)
        return 1
    if type(records) is not list:
        print(f"Tickets file {args.tickets} must contain a JSON array.", file=sys.stderr)
        return 1

    assessments = [assess_normalized_ticket(normalize_json_ticket(record), assessment_date=args.date)
                   for record in records]
    brief = build_portfolio_brief(assessments, assessment_date=args.date)

    try:
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "brief.json").write_text(brief_to_json(brief), encoding="utf-8")
        (args.out / "brief.md").write_text(render_brief_markdown(brief), encoding="utf-8")
    except OSError as error:
        print(f"Cannot write to {args.out}: {error}", file=sys.stderr)
        return 1
    print(f"Wrote {args.out / 'brief.json'}")
    print(f"Wrote {args.out / 'brief.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
