# Get started with ResolveIQ

ResolveIQ turns a batch of implementation tickets into evidence-based risk
findings and client portfolio briefs. This walkthrough uses the 20 bundled
synthetic tickets. Use synthetic data only: the dashboard is a single-user
localhost demo. Client selection filters reports but is not an authentication
or access-control system.

## 1. Set up the project

You need Git, Python 3.9 or newer, and a web browser for the dashboard. If the
repository is private, you also need GitHub access and an authorized SSH key
for the clone command below. No Python packages, API keys, or AI services are
required to run the demo. These commands are for macOS with zsh.

```sh
git clone git@github.com:Michelle-Sainsbury/resolveiq.git
cd resolveiq
git switch feature/resolveiq-build
python3 --version
```

Run the remaining commands from the repository root, where the `scripts` and
`data` directories are. If you already have a clone, check for local changes
before switching branches, then fetch and fast-forward:

```sh
git status --short --branch
git fetch origin
git switch feature/resolveiq-build
git pull --ff-only origin feature/resolveiq-build
```

## 2. Load the synthetic tickets

Generate both report formats in a fresh temporary folder:

```sh
report_dir="$(mktemp -d)"
PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_brief.py \
  --date 2026-11-04 --tickets data/tickets/tickets.json --out "$report_dir"
printf 'Reports: %s\n' "$report_dir"
```

The runner reads the [bundled tickets](../data/tickets/tickets.json), a JSON
array, and writes `brief.md` and `brief.json`. It does not change the input.
The explicit date reproduces the demo; the default window is three calendar
days. The CLI accepts JSON only. The dashboard previews JSON and CSV; the
library also normalizes supported records supplied by a separate GitHub issue
reader. ResolveIQ does not fetch live issues.

## 3. Open the dashboard

In the same terminal, serve the generated report:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/serve_dashboard.py \
  --brief "$report_dir/brief.json"
```

Open <http://127.0.0.1:8787> in a browser. Choose **Client A**, then use
**Tickets** to open T-101 and inspect its findings. Choose **Client B** to
inspect T-106. Records without a usable client ID are shown in a separate
batch review queue; select that queue to see T-111. Stop the server with
Ctrl+C.

To generate and serve the bundled dataset in one command instead:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/serve_dashboard.py --date 2026-11-04
```

## 4. Read the risk signals and review flags

| Overall result | Meaning under the current rules |
| --- | --- |
| **High** | A valid active ticket is recorded as blocked or is overdue. |
| **Medium** | A valid active ticket is due today or within three calendar days by default, without a High finding. |
| **Low** | A valid ticket is completed or cancelled, or the rules found no elevated signal. |
| **Needs Human Review** | Validation or normalization flagged missing, invalid, contradictory, or ambiguous information. |

Findings cite the fields and recorded values behind each rule. Where applicable,
they show the date calculation and source provenance. A dependency ID is a
reference; it does not establish that the other ticket exists, is unresolved,
or caused a blocker.

- **T-101** is High because its recorded status is blocked. Its November 6
  deadline also produces a Medium finding, two days from the assessment date.
- **T-106** needs human review because the owner is null. Its separate High
  finding still shows that its November 1 deadline is overdue. Missing owner
  information does not prove the ticket is unassigned.
- **T-111** has no client ID. ResolveIQ puts it in the batch review queue
  without guessing a client.

ResolveIQ preserves missing values and available evidence. A review flag asks
a person to check the information. Every operational action still requires
human approval, regardless of classification. The demo does not update tickets,
assign work, or send messages.

## 5. View or download a report

Open **Reports** with a client or the batch queue selected. Expand a finding
for its evidence and provenance, or expand the full assessed record for more
context. JSON and Markdown downloads cover the selected scope only. The CLI
files from step 2 cover the whole batch: 20 tickets, with 2 High, 2 Medium,
7 Low, and 9 needing human review (including one in the batch queue).

Use JSON for full structured records and dependency lists. Some dependency
references are omitted from the current Markdown report. The
[sample brief](sample/brief.md) can be read without running the application.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Clone fails | Confirm repository access and SSH setup. If HTTPS is already configured, see the [walkthrough](walkthrough.md) for the HTTPS clone command. |
| Python cannot find the script or ticket file | Run from the repository root on `feature/resolveiq-build` and check `python3 --version`. |
| Runner rejects the date or input | Use `YYYY-MM-DD` and a JSON array. Pass CSV text to the dashboard intake or library adapter instead. |
| Runner cannot write both files | Use a fresh writable output directory. The runner refuses to overwrite the input and can leave a partial report set after a write error; check the exit status and both files before using them. |
| Dashboard will not load | Keep the server running and open its localhost URL, not the HTML file directly. If port 8787 is taken, append `--port 8788` to the launch command and open <http://127.0.0.1:8788>. A restricted sandbox may require permission to bind locally. |
| Ticket or report is missing | Select the correct client or batch queue and clear ticket filters. Intake previews are temporary and do not replace the generated batch. |

See the [dashboard guide](dashboard.md) for all views, intake limits, and tests.
The [decision log plan](human-review-decision-log-plan.md) describes future work.
