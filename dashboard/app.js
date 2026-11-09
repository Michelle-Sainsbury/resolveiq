/* Presentation only. All validation, risk and portfolio facts come from Python. */
"use strict";
const $ = (id) => document.getElementById(id);
const titles = {
  dashboard: [
    "Client overview",
    "Understand what needs attention, with evidence behind every finding.",
  ],
  intake: [
    "Ticket intake",
    "Inspect synthetic JSON or CSV without changing your source tickets.",
  ],
  tickets: [
    "Ticket workspace",
    "Review status, intake gaps and the evidence supporting each classification.",
  ],
  bottlenecks: [
    "Bottlenecks & review",
    "Recorded blockers and supported risk signals, including those on review tickets.",
  ],
  reports: [
    "Client portfolio brief",
    "An evidence-backed report for the selected scope. Human decisions required.",
  ],
  settings: [
    "Assessment settings",
    "Explicit assessment settings and the limits of the current backend.",
  ],
};
const state = {
  catalog: null,
  brief: null,
  page: "dashboard",
  filter: "",
  search: "",
  report: "",
  preview: null,
  generation: 0,
};
const levels = ["High", "Medium", "Low", "Needs Human Review"];
const tone = (level) =>
  ({
    High: "high",
    Medium: "medium",
    Low: "low",
    "Needs Human Review": "review",
  })[level] || "neutral";
const el = (tag, text, cls) => {
  const n = document.createElement(tag);
  if (text !== undefined) n.textContent = text;
  if (cls) n.className = cls;
  return n;
};
const append = (parent, ...children) => {
  children.forEach((c) => parent.append(c));
  return parent;
};
const button = (label, action, cls = "secondary") => {
  const b = el("button", label, cls);
  b.type = "button";
  b.addEventListener("click", action);
  return b;
};
const badge = (level) => el("span", level, `badge ${tone(level)}`);
const json = (value) => JSON.stringify(value, null, 2);
const shown = (obj, key) =>
  !Object.hasOwn(obj, key)
    ? "Missing · not provided"
    : obj[key] === null
      ? "Unknown · null"
      : typeof obj[key] === "string" && !obj[key].trim()
        ? "Blank · needs review"
        : typeof obj[key] === "object"
          ? json(obj[key])
          : String(obj[key]);
const rows = () =>
  !state.brief
    ? []
    : [
        ...state.brief.clients.flatMap((c) => Object.values(c.sections).flat()),
        ...state.brief.batch_review_queue.records,
      ];
const queueSelected = () => $("client").value === "queue";
const selectedClient = () =>
  $("client").value.startsWith("client:") ? $("client").value.slice(7) : null;
const query = () =>
  queueSelected()
    ? "?scope=queue"
    : `?client=${encodeURIComponent(selectedClient())}`;
const scopeLabel = () =>
  queueSelected() ? "Unassigned-client review queue" : selectedClient();
function issueList(entry) {
  return [...entry.validation.issues, ...entry.normalization_issues];
}
function setError(message) {
  $("error").textContent = message;
  $("error").hidden = !message;
}
async function request(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    let message = `Request failed (${response.status}).`;
    try {
      message = (await response.json()).error || message;
    } catch {}
    throw new Error(message);
  }
  return response;
}
function clearScope() {
  state.brief = null;
  state.preview = null;
  state.report = "";
  state.filter = "";
  state.search = "";
  $("ticket-dialog").close();
  $("ticket-body").replaceChildren();
  $("content").replaceChildren();
  $("view-report").disabled = true;
}
function status(text) {
  $("status").textContent = text;
}
async function loadScope() {
  const generation = ++state.generation;
  clearScope();
  setError("");
  render();
  if (!$("client").value) {
    status("Choose a client to load its generated assessment.");
    return;
  }
  status("Loading selected scope…");
  try {
    const b = await (await request("/api/brief" + query())).json();
    if (generation !== state.generation) return;
    state.brief = b;
    $("view-report").disabled = false;
    status(
      "Generated brief loaded. Only this scope is returned by the server.",
    );
    render();
  } catch (error) {
    if (generation !== state.generation) return;
    status("Data could not be loaded.");
    setError(error.message);
  }
}
function header() {
  const [title, subtitle] = titles[state.page];
  $("page-title").textContent = title;
  $("page-subtitle").textContent = subtitle;
  $("breadcrumb").textContent =
    state.page === "dashboard" ? "Dashboard" : title;
  document.querySelectorAll("nav a").forEach((a) => {
    if (a.dataset.page === state.page) a.setAttribute("aria-current", "page");
    else a.removeAttribute("aria-current");
  });
}
function heading(title, note, action) {
  const box = el("div", undefined, "panel-heading");
  const label = el("div");
  append(label, el("h2", title), el("p", note));
  append(box, label);
  if (action) box.append(action);
  return box;
}
function empty(title, description) {
  return append(
    el("div", undefined, "empty"),
    el("h2", title),
    el("p", description),
  );
}
function factsSummary(entries) {
  const active = entries.filter((e) =>
    ["open", "in_progress", "blocked"].includes(e.ticket.status),
  ).length;
  const overdue = entries.filter((e) =>
    e.findings.some((f) => f.rule === "overdue"),
  ).length;
  const owners = { missing: 0, null: 0, blank: 0, malformed: 0 };
  for (const entry of entries) {
    const value = entry.ticket.owner;
    if (!Object.hasOwn(entry.ticket, "owner")) owners.missing++;
    else if (value === null) owners.null++;
    else if (typeof value !== "string") owners.malformed++;
    else if (!value.trim()) owners.blank++;
  }
  const ownerGaps = Object.values(owners).reduce(
    (sum, count) => sum + count,
    0,
  );
  const withDependencies = entries.filter(
    (e) =>
      Array.isArray(e.ticket.dependencies) && e.ticket.dependencies.length > 0,
  ).length;
  const missing = entries.filter((e) =>
    issueList(e).some((i) => i.code === "missing" || i.code === "malformed"),
  ).length;
  return { active, overdue, ownerGaps, owners, withDependencies, missing };
}
function overview() {
  const all = rows(),
    cards = el("div", undefined, "cards");
  for (const level of levels) {
    const count = all.filter((e) => e.classification === level).length;
    const c = button(
      "",
      () => {
        state.filter = level;
        location.hash = "tickets";
      },
      `card ${tone(level)}`,
    );
    append(
      c,
      el("span", "", "card-line"),
      el("span", level, "card-title"),
      el("span", String(count), "card-number"),
      el(
        "span",
        level === "Needs Human Review"
          ? "Data quality needs clarification"
          : "View tickets and cited evidence →",
        "card-note",
      ),
    );
    cards.append(c);
  }
  $("content").append(cards);
  const grid = el("div", undefined, "grid-two"),
    left = el("section", undefined, "panel"),
    right = el("section", undefined, "panel");
  left.append(
    heading("Portfolio signals", "Facts from the selected generated brief."),
  );
  const metrics = factsSummary(all),
    metricGrid = el("div", undefined, "metrics");
  for (const [title, key] of [
    ["Active tickets", "active"],
    ["Overdue findings", "overdue"],
    ["Owner information gaps", "ownerGaps"],
    ["Listed dependencies", "withDependencies"],
  ])
    append(
      metricGrid,
      append(
        el("div", undefined, "metric"),
        el("span", title),
        el("strong", String(metrics[key])),
      ),
    );
  append(left, metricGrid);
  const ownerBreakdown = el(
    "p",
    `Owner information: ${metrics.owners.missing} missing · ${metrics.owners.null} null · ${metrics.owners.blank} blank · ${metrics.owners.malformed} malformed. These values do not establish whether a ticket is genuinely unassigned.`,
    "text-small",
  );
  ownerBreakdown.id = "owner-breakdown";
  left.append(ownerBreakdown);
  append(
    left,
    el(
      "p",
      `${metrics.missing} ticket(s) have missing or malformed intake information. Listed dependencies are references; their completion is not verified.`,
      "text-small",
    ),
  );
  right.append(
    heading(
      "Human review comes first",
      "Counts reflect overall classification, not every underlying signal.",
    ),
  );
  const highReview = all.filter(
    (e) =>
      e.requires_human_review &&
      e.findings.some((f) => f.classification === "High"),
  );
  append(
    right,
    el(
      "div",
      `${highReview.length} review ticket(s) retain an independently supported High finding.`,
      "notice",
    ),
    el(
      "p",
      "Read the evidence before deciding next steps. No assignments, updates or messages are sent.",
      "text-small",
    ),
    button("Review bottlenecks →", () => (location.hash = "bottlenecks")),
  );
  const monitoring = button("Generate Monitoring Report", () => {});
  monitoring.disabled = true;
  monitoring.title =
    "The separate Cycle 2 monitoring report is not connected to this backend.";
  append(
    left,
    monitoring,
    el(
      "p",
      "Cycle 2 monitoring report integration is not available in this workspace.",
      "text-small",
    ),
  );
  append(grid, left, right);
  $("content").append(grid);
  const section = el("section");
  section.append(
    heading(
      "Flagged tickets",
      "High, Medium and Human Review tickets within this scope.",
      button("View all tickets →", () => {
        state.filter = "";
        location.hash = "tickets";
      }),
    ),
  );
  section.append(ticketTable(all.filter((e) => e.classification !== "Low")));
  $("content").append(section);
}
function ticketTable(entries) {
  if (!entries.length)
    return empty(
      "No matching tickets",
      "No ticket in this scope matches the current view.",
    );
  const wrap = el("div", undefined, "table-wrap"),
    table = el("table"),
    head = el("thead"),
    tr = el("tr");
  for (const h of [
    "Ticket / request",
    "Classification",
    "Owner",
    "Due date",
    "Intake",
    "Dependencies",
  ]) {
    const th = el("th", h);
    th.scope = "col";
    tr.append(th);
  }
  head.append(tr);
  table.append(head);
  const body = el("tbody");
  for (const entry of entries) {
    const t = entry.ticket,
      row = el("tr"),
      cell = el("td");
    append(
      cell,
      button(
        entry.record.ticket_id || `Record ${entry.record.batch_position}`,
        () => openTicket(entry),
        "link",
      ),
      el(
        "small",
        Object.hasOwn(t, "title") ? shown(t, "title") : "No title provided",
      ),
    );
    row.append(cell);
    const classification = el("td");
    classification.append(badge(entry.classification));
    row.append(classification);
    for (const value of [shown(t, "owner"), shown(t, "due_date")])
      row.append(el("td", value));
    row.append(
      el(
        "td",
        issueList(entry).length
          ? `${issueList(entry).length} issue(s) · review`
          : "Required fields complete",
      ),
    );
    const deps = !Object.hasOwn(t, "dependencies")
      ? "Missing"
      : t.dependencies === null
        ? "Unknown"
        : Array.isArray(t.dependencies)
          ? t.dependencies.length
            ? `${t.dependencies.length} listed · unverified`
            : "Confirmed none"
          : "Malformed";
    row.append(el("td", deps));
    body.append(row);
  }
  append(table, body);
  wrap.append(table);
  return wrap;
}
function ticketView(bottlenecks = false) {
  const all = rows();
  const toolbar = el("div", undefined, "toolbar"),
    searchLabel = el("label", "Search tickets"),
    search = el("input");
  search.type = "search";
  search.placeholder = "Ticket ID, title or owner";
  search.value = state.search;
  search.id = "ticket-search";
  searchLabel.append(search);
  const filterLabel = el("label", "Classification"),
    filter = el("select");
  filter.id = "risk-filter";
  for (const level of ["", ...levels]) {
    const o = el("option", level || "All classifications");
    o.value = level;
    filter.append(o);
  }
  filter.value = state.filter;
  filterLabel.append(filter);
  append(toolbar, searchLabel, filterLabel);
  $("content").append(toolbar);
  const target = el("div");
  $("content").append(target);
  const update = () => {
    state.search = search.value;
    state.filter = filter.value;
    const list = all.filter(
      (e) =>
        (!bottlenecks ||
          e.requires_human_review ||
          e.findings.some(
            (f) =>
              f.classification === "High" || f.rule === "approaching_deadline",
          )) &&
        (!state.filter || e.classification === state.filter) &&
        (!state.search ||
          [e.record.ticket_id, e.ticket.title, e.ticket.owner].some(
            (v) =>
              typeof v === "string" &&
              v.toLowerCase().includes(state.search.toLowerCase()),
          )),
    );
    target.replaceChildren(ticketTable(list));
  };
  search.addEventListener("input", update);
  filter.addEventListener("change", update);
  if (bottlenecks)
    $("content").append(
      el(
        "p",
        "Unverified dependencies do not automatically mean a blocker. A review classification can retain a High operational finding.",
        "text-small",
      ),
    );
  update();
}
// Guidance explains existing issues; it never supplies or changes ticket values.
function reviewGuidance(issue) {
  const field = issue.field.split("[")[0];
  if (issue.code === "contradictory" && field === "dependencies")
    return "Check the recorded ticket ID, status and dependency list with the source owner. Clarify self-references, repeated IDs, or blocked status with an empty list; do not remove or invent dependencies automatically.";
  if (issue.code === "ambiguous" || issue.code === "contradictory")
    return `Ask a human to resolve the competing ${field} evidence and confirm an approved source mapping. Do not choose a candidate automatically.`;
  const guidance = {
    owner:
      "Confirm the responsible owner with a human. Missing, null and blank owner information does not establish whether work is genuinely unassigned; do not assign someone automatically.",
    due_date:
      "Ask a human to confirm the ticket deadline as a valid YYYY-MM-DD calendar date. Do not infer a date from text or a milestone.",
    dependencies:
      "Ask a human to confirm the dependency list: [] explicitly means none; null means unknown. Each reference must be a nonblank ticket ID. Do not infer existence or completion.",
    client_id:
      "Verify the client identifier against the source before grouping this record. Do not infer a client from the description.",
    ticket_id:
      "Confirm a nonblank ticket identifier from the source. Do not generate a replacement identifier.",
    status:
      "Confirm the recorded status with a human: open, in_progress, blocked, completed or cancelled. Do not convert unsupported or conflicting states automatically.",
    ticket:
      "Check the original input structure and submit a supported JSON object or canonical CSV record for another preview. Preserve the original evidence.",
  };
  return (
    guidance[field] ||
    `Ask a human to verify ${issue.field} against the original source. Keep missing or malformed information unchanged until clarified.`
  );
}

function issueView(issue) {
  const section = el("section", undefined, "review-guidance");
  append(
    section,
    el("h4", `${issue.field} · ${issue.code}`),
    el("p", issue.message),
    el("p", reviewGuidance(issue), "guidance"),
  );
  if (issue.evidence) {
    const detail = el("details");
    append(
      detail,
      el("summary", `Source evidence · ${issue.field}`),
      el("pre", json(issue.evidence)),
    );
    section.append(detail);
  }
  return section;
}

function dependencyView(entry, history = []) {
  const box = el("section", undefined, "dependency-references");
  append(
    box,
    el("h3", "Dependency references"),
    el(
      "p",
      "References only. Existence, completion and any causal link to a blocker are not verified. Navigation stays within the selected scope.",
      "text-small",
    ),
  );
  const dependencies = entry.ticket.dependencies;
  if (!Array.isArray(dependencies)) {
    box.append(el("p", shown(entry.ticket, "dependencies"), "text-small"));
    return box;
  }
  if (!dependencies.length) {
    box.append(el("p", "Confirmed none · []", "text-small"));
    return box;
  }
  const list = el("ul");
  for (const id of dependencies) {
    const item = el("li");
    item.append(el("span", json(id), "dependency-id"));
    // Never search another client's data or request a dependency from the server.
    const matches =
      typeof id === "string" && id.trim()
        ? rows().filter((e) => e.record.ticket_id === id)
        : [];
    if (id === entry.record.ticket_id)
      item.append(
        el("span", "Self-reference · requires clarification.", "text-small"),
      );
    if (!matches.length)
      item.append(
        el(
          "span",
          "Not available in selected scope. Existence and completion remain unverified.",
          "text-small",
        ),
      );
    else {
      for (const match of matches) {
        const label =
          matches.length > 1
            ? `Open ${id} · record ${match.record.batch_position}`
            : `Open ${id}`;
        item.append(
          button(label, () => openTicket(match, [...history, entry])),
        );
      }
      if (matches.length > 1)
        item.append(
          el(
            "span",
            "Multiple records share this ID; select a record to inspect. No identity is assumed.",
            "text-small",
          ),
        );
    }
    list.append(item);
  }
  box.append(list);
  return box;
}

function findingView(finding) {
  const section = el("section", undefined, "finding");
  append(
    section,
    append(el("h3"), el("span", finding.rule), badge(finding.classification)),
    el("p", finding.explanation || "No explanation supplied."),
  );
  const detail = el("details");
  detail.className = "finding-evidence";
  append(
    detail,
    el(
      "summary",
      `Evidence & provenance · ${finding.evidence.length} supporting field(s)`,
    ),
  );
  const evidence = el("dl");
  for (const item of finding.evidence)
    append(
      evidence,
      el("dt", item.field),
      el(
        "dd",
        item.present === false
          ? "Missing · not provided"
          : item.value === null
            ? "Unknown · null"
            : json(item.value),
      ),
    );
  detail.append(evidence);
  if (finding.calculated && Object.keys(finding.calculated).length)
    detail.append(el("pre", json(finding.calculated)));
  for (const item of finding.source_evidence || [])
    append(
      detail,
      el("h4", `Source provenance · ${item.field}`),
      el("pre", json(item.provenance)),
    );
  section.append(detail);
  return section;
}

function openTicket(entry, history = []) {
  const body = $("ticket-body");
  body.replaceChildren();
  if (history.length) {
    const previous = history[history.length - 1];
    body.append(
      button(
        `Back to ${previous.record.ticket_id || "record " + previous.record.batch_position}`,
        () => openTicket(previous, history.slice(0, -1)),
      ),
    );
  }
  const t = entry.ticket;
  const title = el(
    "h2",
    entry.record.ticket_id || `Record ${entry.record.batch_position}`,
    "detail-title",
  );
  title.id = "ticket-title";
  append(
    body,
    title,
    badge(entry.classification),
    el("p", shown(t, "title"), "text-small"),
  );
  const facts = el("div", undefined, "detail-facts");
  for (const [label, key] of [
    ["Client", "client_id"],
    ["Owner", "owner"],
    ["Status", "status"],
    ["Due date", "due_date"],
    ["Last update", "updated_at"],
    ["Dependencies", "dependencies"],
  ])
    append(
      facts,
      append(
        el("div", undefined, "fact"),
        el("small", label),
        el("span", shown(t, key)),
      ),
    );
  body.append(facts);
  if (Object.hasOwn(t, "description"))
    append(
      body,
      el("h3", "Source description"),
      el("p", shown(t, "description"), "text-small"),
    );
  append(body, el("h3", "Intake validation"));
  const issues = issueList(entry);
  if (!issues.length)
    body.append(
      el(
        "p",
        "Required fields are complete. No validation or normalization issues.",
        "text-small",
      ),
    );
  issues.forEach((issue) => body.append(issueView(issue)));
  body.append(dependencyView(entry, history));
  body.append(el("h3", "Classification findings & supporting evidence"));
  entry.findings.forEach((finding) => body.append(findingView(finding)));
  const source = el("details");
  append(
    source,
    el("summary", "Original record and source information"),
    el(
      "pre",
      json({
        source: entry.source,
        raw_record: entry.raw_record,
        field_provenance: entry.field_provenance,
      }),
    ),
  );
  body.append(source);
  append(
    body,
    el(
      "p",
      "Human decisions required. Clarify flagged fields with the source owner and review supported findings before deciding any follow-up. No operational approval has been granted.",
      "safeguard",
    ),
  );
  if (!$("ticket-dialog").open) $("ticket-dialog").showModal();
  $("close-dialog").focus();
}

// A readable presentation of the supplied brief, not a second reporting engine.
function readableReport() {
  const report = el("div", undefined, "readable-report");
  report.id = "portfolio-report";
  append(
    report,
    el("h2", "Portfolio brief"),
    el(
      "p",
      `${scopeLabel()} · ${rows().length} record(s) · assessment ${state.brief.assessment_date} · deadline window ${state.brief.approaching_deadline_days} days`,
      "text-small",
    ),
  );
  const counts = el("ul", undefined, "report-counts");
  for (const level of levels)
    counts.append(
      el(
        "li",
        `${level}: ${rows().filter((e) => e.classification === level).length}`,
      ),
    );
  report.append(counts);
  append(
    report,
    el(
      "p",
      "These are overall classifications, not approved work priorities. Review cases can retain independent High, Medium or Low findings. All operational actions require human approval.",
      "notice",
    ),
  );
  for (const level of levels) {
    const entries = rows().filter((e) => e.classification === level);
    const section = el("section", undefined, "report-section");
    section.append(el("h3", `${level} · ${entries.length}`));
    if (!entries.length)
      section.append(
        el("p", "No records in this classification.", "text-small"),
      );
    for (const entry of entries) {
      const card = el("article", undefined, "report-ticket");
      append(
        card,
        button(
          entry.record.ticket_id || `Record ${entry.record.batch_position}`,
          () => openTicket(entry),
          "link",
        ),
        badge(entry.classification),
      );
      if (Object.hasOwn(entry.ticket, "title"))
        card.append(el("p", shown(entry.ticket, "title"), "text-small"));
      append(
        card,
        el(
          "p",
          `Owner: ${shown(entry.ticket, "owner")} · Due date: ${shown(entry.ticket, "due_date")}`,
          "text-small",
        ),
      );
      card.append(dependencyView(entry));
      const issues = issueList(entry);
      issues.forEach((issue) => card.append(issueView(issue)));
      entry.findings.forEach((finding) => card.append(findingView(finding)));
      const full = el("details");
      full.className = "record-evidence";
      append(
        full,
        el("summary", "Full assessed record, evidence & source provenance"),
        el("pre", json(entry)),
      );
      card.append(full);
      section.append(card);
    }
    report.append(section);
  }
  return report;
}

async function reportView() {
  const generation = state.generation;
  const panel = el("section", undefined, "panel");
  panel.append(
    heading(
      `${scopeLabel()} · Portfolio brief`,
      "Summaries from generated portfolio data. Original reports use the Python renderer.",
    ),
  );
  panel.append(
    el(
      "p",
      "Intended recipients: not provided. Recipient management is not connected.",
      "text-small",
    ),
  );
  panel.append(
    el(
      "p",
      "This is a local review copy. Downloading a report does not send it or approve any ticket action.",
      "text-small",
    ),
  );
  const report = readableReport();
  const original = el("details");
  original.className = "original-report";
  const markdown = el("pre", "Loading report…", "report-text");
  markdown.id = "original-markdown";
  append(
    original,
    el("summary", "Full original Markdown report (unchanged)"),
    markdown,
  );
  const actions = el("div", undefined, "actions");
  const mdButton = button("Download Markdown", () =>
    download(state.report, "portfolio.md", "text/markdown"),
  );
  const jsonButton = button("Download JSON", async () => {
    try {
      const value = state.preview
        ? state.preview.json
        : await (
            await request("/api/report" + query() + "&format=json")
          ).text();
      if (generation !== state.generation) return;
      download(value, "portfolio.json", "application/json");
    } catch (e) {
      setError(e.message);
    }
  });
  mdButton.disabled = true;
  append(actions, mdButton, jsonButton);
  append(panel, actions, report, original);
  $("content").append(panel);
  try {
    const text = state.preview
      ? state.preview.markdown
      : await (await request("/api/report" + query())).text();
    if (generation !== state.generation || state.page !== "reports") return;
    state.report = text;
    markdown.textContent = text;
    mdButton.disabled = false;
  } catch (e) {
    if (generation !== state.generation) return;
    markdown.textContent = "Report unavailable.";
    setError(e.message);
  }
}
function download(text, filename, mime) {
  const url = URL.createObjectURL(new Blob([text], { type: mime }));
  const a = el("a");
  a.href = url;
  a.download = filename;
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function intakeView() {
  const panel = el("section", undefined, "panel intake-form");
  append(
    panel,
    heading(
      "Review a synthetic intake batch",
      "JSON object/array or CSV with the existing canonical fields.",
    ),
  );
  panel.append(
    el(
      "p",
      "Preview only: no input file is uploaded to storage and no source record is changed. Results are restricted to your selected client or queue. Reload generated data to return to the original brief.",
      "notice",
    ),
  );
  const form = el("form");
  form.id = "intake-form";
  const formatLabel = el("label", "Format"),
    format = el("select");
  format.id = "intake-format";
  for (const value of ["json", "csv"]) {
    const o = el("option", value.toUpperCase());
    o.value = value;
    format.append(o);
  }
  formatLabel.htmlFor = "intake-format";
  append(form, formatLabel, format);
  const dateLabel = el("label", "Assessment date"),
    day = el("input");
  day.type = "date";
  day.required = true;
  day.id = "intake-date";
  day.value = state.brief.assessment_date;
  dateLabel.htmlFor = day.id;
  append(form, dateLabel, day);
  const label = el("label", "Synthetic ticket data"),
    text = el("textarea");
  text.id = "intake-data";
  text.required = true;
  label.htmlFor = text.id;
  text.placeholder =
    "Paste synthetic JSON or CSV here. No values will be filled in for you.";
  append(form, label, text);
  const fileLabel = el("label", "Or read a local synthetic file"),
    file = el("input");
  file.type = "file";
  file.id = "intake-file";
  file.accept = ".json,.csv";
  fileLabel.htmlFor = file.id;
  append(form, fileLabel, file);
  file.addEventListener("change", async () => {
    if (!file.files.length) return;
    const item = file.files[0];
    if (item.size > 900000) {
      setError("Choose a synthetic file smaller than 900 KB.");
      return;
    }
    text.value = await item.text();
    format.value = item.name.toLowerCase().endsWith(".csv") ? "csv" : "json";
  });
  const submit = el("button", "Validate & assess preview", "primary");
  submit.type = "submit";
  const actions = el("div", undefined, "actions");
  actions.append(submit);
  form.append(actions);
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    setError("");
    if (text.value.length > 900000) {
      setError("Intake must be smaller than 900 KB.");
      return;
    }
    const generation = state.generation;
    submit.disabled = true;
    status("Assessing synthetic intake…");
    try {
      const result = await (
        await request("/api/intake", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            content: text.value,
            format: format.value,
            assessment_date: day.value,
            client: selectedClient(),
            queue: queueSelected(),
          }),
        })
      ).json();
      if (generation !== state.generation) return;
      state.preview = result;
      state.brief = result.brief;
      state.filter = "";
      state.search = "";
      status(
        "In-memory intake preview. Original generated brief and source tickets are unchanged.",
      );
      location.hash = "tickets";
    } catch (e) {
      if (generation !== state.generation) return;
      setError(e.message);
      status("Intake preview could not be completed.");
    } finally {
      submit.disabled = false;
    }
  });
  panel.append(form);
  $("content").append(panel);
}
function settingsView() {
  const panel = el("section", undefined, "panel");
  append(
    panel,
    heading("Assessment contract", "These values come from the loaded report."),
  );
  for (const [label, value] of [
    ["Assessment date", state.brief.assessment_date],
    [
      "Approaching deadline",
      `${state.brief.approaching_deadline_days} calendar days, inclusive`,
    ],
    ["Operational actions", "Always require human approval"],
    [
      "Source mode",
      "Synthetic local data; no live GitHub, Jira or Salesforce connection",
    ],
  ]) {
    const row = el("div", undefined, "stat-row");
    append(row, el("span", label), el("strong", value));
    panel.append(row);
  }
  append(
    panel,
    el("h3", "Backend limitations"),
    el(
      "p",
      "The current backend does not implement 14-day inactivity monitoring, dependency resolution, description/client conflict detection, intended-recipient management, or a separate Cycle 2 monitoring report. No timing or accuracy improvement is claimed.",
      "notice",
    ),
    el(
      "p",
      "High: valid active blocked or overdue tickets. Medium: valid active tickets due within the configured window. Low: no elevated signal under these rules, or inactive completed/cancelled tickets. Missing or contradictory required information takes precedence as Needs Human Review.",
      "text-small",
    ),
  );
  $("content").append(panel);
}
function render() {
  header();
  $("content").replaceChildren();
  if (!state.brief) {
    $("content").append(
      empty(
        "Choose your client workspace",
        "Select a client above. Records without a verified client ID are available only in the separate review queue.",
      ),
    );
    return;
  }
  if (state.page === "dashboard") overview();
  else if (state.page === "tickets") ticketView();
  else if (state.page === "bottlenecks") ticketView(true);
  else if (state.page === "reports") reportView();
  else if (state.page === "intake") intakeView();
  else settingsView();
}
function navigate() {
  const name = location.hash.slice(1) || "dashboard";
  state.page = Object.hasOwn(titles, name) ? name : "dashboard";
  setError("");
  render();
}
window.addEventListener("hashchange", navigate);
$("client").addEventListener("change", loadScope);
$("reload").addEventListener("click", loadScope);
$("view-report").addEventListener("click", () => (location.hash = "reports"));
$("close-dialog").addEventListener("click", () => $("ticket-dialog").close());
async function init() {
  navigate();
  try {
    const catalog = await (await request("/api/clients")).json();
    state.catalog = catalog;
    for (const client of catalog.clients) {
      const option = el("option", client);
      option.value = "client:" + client;
      $("client").append(option);
    }
    if (catalog.queue_available) {
      const option = el("option", "Unassigned-client review queue");
      option.value = "queue";
      $("client").append(option);
    }
    $("assessment-info").textContent =
      `Assessment: ${catalog.assessment_date} · ${catalog.approaching_deadline_days}-day deadline window`;
    $("reload").disabled = false;
    status("Choose a client. No ticket records have been loaded.");
  } catch (e) {
    status("No generated data is available.");
    setError(
      e.message +
        " Start the Python dashboard server; opening index.html directly is not supported.",
    );
  }
}
init();
