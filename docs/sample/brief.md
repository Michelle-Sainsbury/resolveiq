# Portfolio brief

- Assessment date: `"2026-11-04"`
- Approaching-deadline window in days: `3`
- Requires human review: yes
- Operational actions require human approval: yes
- Records in batch: 20 (records: `[{"batch_position": 1, "ticket_id": "T-101"}, {"batch_position": 2, "ticket_id": "T-102"}, {"batch_position": 3, "ticket_id": "T-103"}, {"batch_position": 4, "ticket_id": "T-104"}, {"batch_position": 5, "ticket_id": "T-105"}, {"batch_position": 6, "ticket_id": "T-106"}, {"batch_position": 7, "ticket_id": "T-107"}, {"batch_position": 8, "ticket_id": "T-108"}, {"batch_position": 9, "ticket_id": "T-109"}, {"batch_position": 10, "ticket_id": "T-110"}, {"batch_position": 11, "ticket_id": "T-111"}, {"batch_position": 12, "ticket_id": "T-112"}, {"batch_position": 13, "ticket_id": "T-113"}, {"batch_position": 14, "ticket_id": "T-114"}, {"batch_position": 15, "ticket_id": "T-115"}, {"batch_position": 16, "ticket_id": "T-116"}, {"batch_position": 17, "ticket_id": "T-117"}, {"batch_position": 18, "ticket_id": "T-118"}, {"batch_position": 19, "ticket_id": "T-119"}, {"batch_position": 20, "ticket_id": "T-120"}]`)
- Records in client briefs: 19 (records: `[{"batch_position": 1, "ticket_id": "T-101"}, {"batch_position": 2, "ticket_id": "T-102"}, {"batch_position": 3, "ticket_id": "T-103"}, {"batch_position": 4, "ticket_id": "T-104"}, {"batch_position": 5, "ticket_id": "T-105"}, {"batch_position": 6, "ticket_id": "T-106"}, {"batch_position": 7, "ticket_id": "T-107"}, {"batch_position": 8, "ticket_id": "T-108"}, {"batch_position": 9, "ticket_id": "T-109"}, {"batch_position": 10, "ticket_id": "T-110"}, {"batch_position": 12, "ticket_id": "T-112"}, {"batch_position": 13, "ticket_id": "T-113"}, {"batch_position": 14, "ticket_id": "T-114"}, {"batch_position": 15, "ticket_id": "T-115"}, {"batch_position": 16, "ticket_id": "T-116"}, {"batch_position": 17, "ticket_id": "T-117"}, {"batch_position": 18, "ticket_id": "T-118"}, {"batch_position": 19, "ticket_id": "T-119"}, {"batch_position": 20, "ticket_id": "T-120"}]`)
- Records in batch review queue: 1 (records: `[{"batch_position": 11, "ticket_id": "T-111"}]`)

## Summary

- Client `"Client A"`
  - High: 2 (records: `[{"batch_position": 1, "ticket_id": "T-101"}, {"batch_position": 9, "ticket_id": "T-109"}]`)
  - Medium: 1 (records: `[{"batch_position": 19, "ticket_id": "T-119"}]`)
  - Low: 4 (records: `[{"batch_position": 3, "ticket_id": "T-103"}, {"batch_position": 4, "ticket_id": "T-104"}, {"batch_position": 7, "ticket_id": "T-107"}, {"batch_position": 16, "ticket_id": "T-116"}]`)
  - Human Review: 3 (records: `[{"batch_position": 12, "ticket_id": "T-112"}, {"batch_position": 14, "ticket_id": "T-114"}, {"batch_position": 18, "ticket_id": "T-118"}]`)
- Client `"Client B"`
  - High: 0 (records: `[]`)
  - Medium: 1 (records: `[{"batch_position": 8, "ticket_id": "T-108"}]`)
  - Low: 2 (records: `[{"batch_position": 5, "ticket_id": "T-105"}, {"batch_position": 15, "ticket_id": "T-115"}]`)
  - Human Review: 5 (records: `[{"batch_position": 2, "ticket_id": "T-102"}, {"batch_position": 6, "ticket_id": "T-106"}, {"batch_position": 10, "ticket_id": "T-110"}, {"batch_position": 13, "ticket_id": "T-113"}, {"batch_position": 17, "ticket_id": "T-117"}]`)
- Client `"Client C"`
  - High: 0 (records: `[]`)
  - Medium: 0 (records: `[]`)
  - Low: 1 (records: `[{"batch_position": 20, "ticket_id": "T-120"}]`)
  - Human Review: 0 (records: `[]`)
- Batch review queue: 1 (records: `[{"batch_position": 11, "ticket_id": "T-111"}]`)

## Review items

- Client `"Client A"`, section `"high"`, record `{"batch_position": 1, "ticket_id": "T-101"}`, findings `[{"classification": "High", "fields": ["status", "dependencies"], "rule": "blocked"}, {"classification": "Medium", "fields": ["status", "due_date"], "rule": "approaching_deadline"}]`, normalization issues `[]`
- Client `"Client A"`, section `"high"`, record `{"batch_position": 9, "ticket_id": "T-109"}`, findings `[{"classification": "High", "fields": ["status", "due_date"], "rule": "overdue"}]`, normalization issues `[]`
- Client `"Client A"`, section `"human_review"`, record `{"batch_position": 12, "ticket_id": "T-112"}`, findings `[{"classification": "Needs Human Review", "fields": ["dependencies[0]", "ticket_id", "status", "dependencies"], "rule": "validation_contradictory"}, {"classification": "Low", "fields": ["status", "due_date"], "rule": "outside_deadline_window"}]`, normalization issues `[]`
- Client `"Client A"`, section `"human_review"`, record `{"batch_position": 14, "ticket_id": "T-114"}`, findings `[{"classification": "Needs Human Review", "fields": ["dependencies", "ticket_id", "status"], "rule": "validation_contradictory"}, {"classification": "High", "fields": ["status", "dependencies"], "rule": "blocked"}]`, normalization issues `[]`
- Client `"Client A"`, section `"human_review"`, record `{"batch_position": 18, "ticket_id": "T-118"}`, findings `[{"classification": "Needs Human Review", "fields": ["status"], "rule": "validation_malformed"}]`, normalization issues `[]`
- Client `"Client B"`, section `"human_review"`, record `{"batch_position": 2, "ticket_id": "T-102"}`, findings `[{"classification": "Needs Human Review", "fields": ["owner"], "rule": "validation_missing"}, {"classification": "Needs Human Review", "fields": ["due_date"], "rule": "validation_missing"}, {"classification": "Needs Human Review", "fields": ["dependencies"], "rule": "validation_missing"}]`, normalization issues `[]`
- Client `"Client B"`, section `"human_review"`, record `{"batch_position": 6, "ticket_id": "T-106"}`, findings `[{"classification": "Needs Human Review", "fields": ["owner"], "rule": "validation_missing"}, {"classification": "High", "fields": ["status", "due_date"], "rule": "overdue"}]`, normalization issues `[]`
- Client `"Client B"`, section `"human_review"`, record `{"batch_position": 10, "ticket_id": "T-110"}`, findings `[{"classification": "Needs Human Review", "fields": ["owner"], "rule": "validation_missing"}, {"classification": "Low", "fields": ["status", "due_date"], "rule": "outside_deadline_window"}]`, normalization issues `[]`
- Client `"Client B"`, section `"human_review"`, record `{"batch_position": 13, "ticket_id": "T-113"}`, findings `[{"classification": "Needs Human Review", "fields": ["dependencies[1]", "ticket_id", "status", "dependencies"], "rule": "validation_contradictory"}, {"classification": "Low", "fields": ["status", "due_date"], "rule": "outside_deadline_window"}]`, normalization issues `[]`
- Client `"Client B"`, section `"human_review"`, record `{"batch_position": 17, "ticket_id": "T-117"}`, findings `[{"classification": "Needs Human Review", "fields": ["due_date"], "rule": "validation_malformed"}]`, normalization issues `[]`

## Client `"Client A"`

- Requires human review: yes
- Operational actions require human approval: yes
- Counts:
  - High: 2 (records: `[{"batch_position": 1, "ticket_id": "T-101"}, {"batch_position": 9, "ticket_id": "T-109"}]`)
  - Medium: 1 (records: `[{"batch_position": 19, "ticket_id": "T-119"}]`)
  - Low: 4 (records: `[{"batch_position": 3, "ticket_id": "T-103"}, {"batch_position": 4, "ticket_id": "T-104"}, {"batch_position": 7, "ticket_id": "T-107"}, {"batch_position": 16, "ticket_id": "T-116"}]`)
  - Human Review: 3 (records: `[{"batch_position": 12, "ticket_id": "T-112"}, {"batch_position": 14, "ticket_id": "T-114"}, {"batch_position": 18, "ticket_id": "T-118"}]`)
  - Total: 10 (records: `[{"batch_position": 1, "ticket_id": "T-101"}, {"batch_position": 3, "ticket_id": "T-103"}, {"batch_position": 4, "ticket_id": "T-104"}, {"batch_position": 7, "ticket_id": "T-107"}, {"batch_position": 9, "ticket_id": "T-109"}, {"batch_position": 12, "ticket_id": "T-112"}, {"batch_position": 14, "ticket_id": "T-114"}, {"batch_position": 16, "ticket_id": "T-116"}, {"batch_position": 18, "ticket_id": "T-118"}, {"batch_position": 19, "ticket_id": "T-119"}]`)

### High

- Record `{"batch_position": 1, "ticket_id": "T-101"}`
  - Classification: `"High"`
  - Requires human review: no
  - Operational actions require human approval: yes
  - Source: `{"type": "synthetic_json"}`
  - Validation issues: none
  - Normalization issues: none
  - Findings:
    - Rule `"blocked"`: classification `"High"`. Explanation: `"Recorded status explicitly indicates a blocker."`
      - Evidence: field `"status"`, present yes, value `"blocked"`
      - Evidence: field `"dependencies"`, present yes, value `["T-140"]`
      - Provenance of `"status"`: `{"evidence": [{"path": "status", "present": true, "value": "blocked"}], "transformation": "copy"}`
      - Provenance of `"dependencies"`: `{"evidence": [{"path": "dependencies", "present": true, "value": ["T-140"]}], "transformation": "copy"}`
    - Rule `"approaching_deadline"`: classification `"Medium"`. Explanation: `"Active ticket is within the approaching-deadline window."`
      - Evidence: field `"status"`, present yes, value `"blocked"`
      - Evidence: field `"due_date"`, present yes, value `"2026-11-06"`
      - Calculated: `{"days_remaining": 2}`
      - Provenance of `"status"`: `{"evidence": [{"path": "status", "present": true, "value": "blocked"}], "transformation": "copy"}`
      - Provenance of `"due_date"`: `{"evidence": [{"path": "due_date", "present": true, "value": "2026-11-06"}], "transformation": "copy"}`
- Record `{"batch_position": 9, "ticket_id": "T-109"}`
  - Classification: `"High"`
  - Requires human review: no
  - Operational actions require human approval: yes
  - Source: `{"type": "synthetic_json"}`
  - Validation issues: none
  - Normalization issues: none
  - Findings:
    - Rule `"overdue"`: classification `"High"`. Explanation: `"Active ticket is past its due date."`
      - Evidence: field `"status"`, present yes, value `"open"`
      - Evidence: field `"due_date"`, present yes, value `"2026-11-02"`
      - Calculated: `{"days_overdue": 2, "days_remaining": -2}`
      - Provenance of `"status"`: `{"evidence": [{"path": "status", "present": true, "value": "open"}], "transformation": "copy"}`
      - Provenance of `"due_date"`: `{"evidence": [{"path": "due_date", "present": true, "value": "2026-11-02"}], "transformation": "copy"}`

### Medium

- Record `{"batch_position": 19, "ticket_id": "T-119"}`
  - Classification: `"Medium"`
  - Requires human review: no
  - Operational actions require human approval: yes
  - Source: `{"type": "synthetic_json"}`
  - Validation issues: none
  - Normalization issues: none
  - Findings:
    - Rule `"approaching_deadline"`: classification `"Medium"`. Explanation: `"Active ticket is within the approaching-deadline window."`
      - Evidence: field `"status"`, present yes, value `"open"`
      - Evidence: field `"due_date"`, present yes, value `"2026-11-04"`
      - Calculated: `{"days_remaining": 0}`
      - Provenance of `"status"`: `{"evidence": [{"path": "status", "present": true, "value": "open"}], "transformation": "copy"}`
      - Provenance of `"due_date"`: `{"evidence": [{"path": "due_date", "present": true, "value": "2026-11-04"}], "transformation": "copy"}`

### Low

- Record `{"batch_position": 3, "ticket_id": "T-103"}`
  - Classification: `"Low"`
  - Requires human review: no
  - Operational actions require human approval: yes
  - Source: `{"type": "synthetic_json"}`
  - Validation issues: none
  - Normalization issues: none
  - Findings:
    - Rule `"outside_deadline_window"`: classification `"Low"`. Explanation: `"No elevated risk detected by the status and deadline rules."`
      - Evidence: field `"status"`, present yes, value `"open"`
      - Evidence: field `"due_date"`, present yes, value `"2026-11-20"`
      - Calculated: `{"days_remaining": 16}`
      - Provenance of `"status"`: `{"evidence": [{"path": "status", "present": true, "value": "open"}], "transformation": "copy"}`
      - Provenance of `"due_date"`: `{"evidence": [{"path": "due_date", "present": true, "value": "2026-11-20"}], "transformation": "copy"}`
- Record `{"batch_position": 4, "ticket_id": "T-104"}`
  - Classification: `"Low"`
  - Requires human review: no
  - Operational actions require human approval: yes
  - Source: `{"type": "synthetic_json"}`
  - Validation issues: none
  - Normalization issues: none
  - Findings:
    - Rule `"outside_deadline_window"`: classification `"Low"`. Explanation: `"No elevated risk detected by the status and deadline rules."`
      - Evidence: field `"status"`, present yes, value `"open"`
      - Evidence: field `"due_date"`, present yes, value `"2026-12-15"`
      - Calculated: `{"days_remaining": 41}`
      - Provenance of `"status"`: `{"evidence": [{"path": "status", "present": true, "value": "open"}], "transformation": "copy"}`
      - Provenance of `"due_date"`: `{"evidence": [{"path": "due_date", "present": true, "value": "2026-12-15"}], "transformation": "copy"}`
- Record `{"batch_position": 7, "ticket_id": "T-107"}`
  - Classification: `"Low"`
  - Requires human review: no
  - Operational actions require human approval: yes
  - Source: `{"type": "synthetic_json"}`
  - Validation issues: none
  - Normalization issues: none
  - Findings:
    - Rule `"outside_deadline_window"`: classification `"Low"`. Explanation: `"No elevated risk detected by the status and deadline rules."`
      - Evidence: field `"status"`, present yes, value `"open"`
      - Evidence: field `"due_date"`, present yes, value `"2026-11-08"`
      - Calculated: `{"days_remaining": 4}`
      - Provenance of `"status"`: `{"evidence": [{"path": "status", "present": true, "value": "open"}], "transformation": "copy"}`
      - Provenance of `"due_date"`: `{"evidence": [{"path": "due_date", "present": true, "value": "2026-11-08"}], "transformation": "copy"}`
- Record `{"batch_position": 16, "ticket_id": "T-116"}`
  - Classification: `"Low"`
  - Requires human review: no
  - Operational actions require human approval: yes
  - Source: `{"type": "synthetic_json"}`
  - Validation issues: none
  - Normalization issues: none
  - Findings:
    - Rule `"inactive"`: classification `"Low"`. Explanation: `"Recorded status is inactive; deadline rules do not apply."`
      - Evidence: field `"status"`, present yes, value `"cancelled"`
      - Provenance of `"status"`: `{"evidence": [{"path": "status", "present": true, "value": "cancelled"}], "transformation": "copy"}`

### Human Review

- Record `{"batch_position": 12, "ticket_id": "T-112"}`
  - Classification: `"Needs Human Review"`
  - Requires human review: yes
  - Operational actions require human approval: yes
  - Source: `{"type": "synthetic_json"}`
  - Validation issues:
    - Field `"dependencies[0]"`, code `"contradictory"`, message `"A ticket cannot depend on itself."`
  - Normalization issues: none
  - Findings:
    - Rule `"validation_contradictory"`: classification `"Needs Human Review"`. Explanation: `"A ticket cannot depend on itself."`
      - Evidence: field `"dependencies[0]"`, present yes, value `"T-112"`
      - Evidence: field `"ticket_id"`, present yes, value `"T-112"`
      - Evidence: field `"status"`, present yes, value `"open"`
      - Evidence: field `"dependencies"`, present yes, value `["T-112"]`
      - Provenance of `"dependencies[0]"`: `{"evidence": [{"path": "dependencies", "present": true, "value": ["T-112"]}], "transformation": "copy"}`
      - Provenance of `"ticket_id"`: `{"evidence": [{"path": "ticket_id", "present": true, "value": "T-112"}], "transformation": "copy"}`
      - Provenance of `"status"`: `{"evidence": [{"path": "status", "present": true, "value": "open"}], "transformation": "copy"}`
      - Provenance of `"dependencies"`: `{"evidence": [{"path": "dependencies", "present": true, "value": ["T-112"]}], "transformation": "copy"}`
    - Rule `"outside_deadline_window"`: classification `"Low"`. Explanation: `"No elevated risk detected by the status and deadline rules."`
      - Evidence: field `"status"`, present yes, value `"open"`
      - Evidence: field `"due_date"`, present yes, value `"2026-11-15"`
      - Calculated: `{"days_remaining": 11}`
      - Provenance of `"status"`: `{"evidence": [{"path": "status", "present": true, "value": "open"}], "transformation": "copy"}`
      - Provenance of `"due_date"`: `{"evidence": [{"path": "due_date", "present": true, "value": "2026-11-15"}], "transformation": "copy"}`
- Record `{"batch_position": 14, "ticket_id": "T-114"}`
  - Classification: `"Needs Human Review"`
  - Requires human review: yes
  - Operational actions require human approval: yes
  - Source: `{"type": "synthetic_json"}`
  - Validation issues:
    - Field `"dependencies"`, code `"contradictory"`, message `"Blocked status with confirmed no dependencies needs review."`
  - Normalization issues: none
  - Findings:
    - Rule `"validation_contradictory"`: classification `"Needs Human Review"`. Explanation: `"Blocked status with confirmed no dependencies needs review."`
      - Evidence: field `"dependencies"`, present yes, value `[]`
      - Evidence: field `"ticket_id"`, present yes, value `"T-114"`
      - Evidence: field `"status"`, present yes, value `"blocked"`
      - Provenance of `"dependencies"`: `{"evidence": [{"path": "dependencies", "present": true, "value": []}], "transformation": "copy"}`
      - Provenance of `"ticket_id"`: `{"evidence": [{"path": "ticket_id", "present": true, "value": "T-114"}], "transformation": "copy"}`
      - Provenance of `"status"`: `{"evidence": [{"path": "status", "present": true, "value": "blocked"}], "transformation": "copy"}`
    - Rule `"blocked"`: classification `"High"`. Explanation: `"Recorded status explicitly indicates a blocker."`
      - Evidence: field `"status"`, present yes, value `"blocked"`
      - Evidence: field `"dependencies"`, present yes, value `[]`
      - Provenance of `"status"`: `{"evidence": [{"path": "status", "present": true, "value": "blocked"}], "transformation": "copy"}`
      - Provenance of `"dependencies"`: `{"evidence": [{"path": "dependencies", "present": true, "value": []}], "transformation": "copy"}`
- Record `{"batch_position": 18, "ticket_id": "T-118"}`
  - Classification: `"Needs Human Review"`
  - Requires human review: yes
  - Operational actions require human approval: yes
  - Source: `{"type": "synthetic_json"}`
  - Validation issues:
    - Field `"status"`, code `"malformed"`, message `"Unrecognized status; see the documented schema."`
  - Normalization issues: none
  - Findings:
    - Rule `"validation_malformed"`: classification `"Needs Human Review"`. Explanation: `"Unrecognized status; see the documented schema."`
      - Evidence: field `"status"`, present yes, value `"done"`
      - Provenance of `"status"`: `{"evidence": [{"path": "status", "present": true, "value": "done"}], "transformation": "copy"}`

## Client `"Client B"`

- Requires human review: yes
- Operational actions require human approval: yes
- Counts:
  - High: 0 (records: `[]`)
  - Medium: 1 (records: `[{"batch_position": 8, "ticket_id": "T-108"}]`)
  - Low: 2 (records: `[{"batch_position": 5, "ticket_id": "T-105"}, {"batch_position": 15, "ticket_id": "T-115"}]`)
  - Human Review: 5 (records: `[{"batch_position": 2, "ticket_id": "T-102"}, {"batch_position": 6, "ticket_id": "T-106"}, {"batch_position": 10, "ticket_id": "T-110"}, {"batch_position": 13, "ticket_id": "T-113"}, {"batch_position": 17, "ticket_id": "T-117"}]`)
  - Total: 8 (records: `[{"batch_position": 2, "ticket_id": "T-102"}, {"batch_position": 5, "ticket_id": "T-105"}, {"batch_position": 6, "ticket_id": "T-106"}, {"batch_position": 8, "ticket_id": "T-108"}, {"batch_position": 10, "ticket_id": "T-110"}, {"batch_position": 13, "ticket_id": "T-113"}, {"batch_position": 15, "ticket_id": "T-115"}, {"batch_position": 17, "ticket_id": "T-117"}]`)

### High

None.

### Medium

- Record `{"batch_position": 8, "ticket_id": "T-108"}`
  - Classification: `"Medium"`
  - Requires human review: no
  - Operational actions require human approval: yes
  - Source: `{"type": "synthetic_json"}`
  - Validation issues: none
  - Normalization issues: none
  - Findings:
    - Rule `"approaching_deadline"`: classification `"Medium"`. Explanation: `"Active ticket is within the approaching-deadline window."`
      - Evidence: field `"status"`, present yes, value `"in_progress"`
      - Evidence: field `"due_date"`, present yes, value `"2026-11-07"`
      - Calculated: `{"days_remaining": 3}`
      - Provenance of `"status"`: `{"evidence": [{"path": "status", "present": true, "value": "in_progress"}], "transformation": "copy"}`
      - Provenance of `"due_date"`: `{"evidence": [{"path": "due_date", "present": true, "value": "2026-11-07"}], "transformation": "copy"}`

### Low

- Record `{"batch_position": 5, "ticket_id": "T-105"}`
  - Classification: `"Low"`
  - Requires human review: no
  - Operational actions require human approval: yes
  - Source: `{"type": "synthetic_json"}`
  - Validation issues: none
  - Normalization issues: none
  - Findings:
    - Rule `"outside_deadline_window"`: classification `"Low"`. Explanation: `"No elevated risk detected by the status and deadline rules."`
      - Evidence: field `"status"`, present yes, value `"open"`
      - Evidence: field `"due_date"`, present yes, value `"2026-11-30"`
      - Calculated: `{"days_remaining": 26}`
      - Provenance of `"status"`: `{"evidence": [{"path": "status", "present": true, "value": "open"}], "transformation": "copy"}`
      - Provenance of `"due_date"`: `{"evidence": [{"path": "due_date", "present": true, "value": "2026-11-30"}], "transformation": "copy"}`
- Record `{"batch_position": 15, "ticket_id": "T-115"}`
  - Classification: `"Low"`
  - Requires human review: no
  - Operational actions require human approval: yes
  - Source: `{"type": "synthetic_json"}`
  - Validation issues: none
  - Normalization issues: none
  - Findings:
    - Rule `"inactive"`: classification `"Low"`. Explanation: `"Recorded status is inactive; deadline rules do not apply."`
      - Evidence: field `"status"`, present yes, value `"completed"`
      - Provenance of `"status"`: `{"evidence": [{"path": "status", "present": true, "value": "completed"}], "transformation": "copy"}`

### Human Review

- Record `{"batch_position": 2, "ticket_id": "T-102"}`
  - Classification: `"Needs Human Review"`
  - Requires human review: yes
  - Operational actions require human approval: yes
  - Source: `{"type": "synthetic_json"}`
  - Validation issues:
    - Field `"owner"`, code `"missing"`, message `"Required information is missing or unknown."`
    - Field `"due_date"`, code `"missing"`, message `"Required information is missing or unknown."`
    - Field `"dependencies"`, code `"missing"`, message `"Required information is missing or unknown."`
  - Normalization issues: none
  - Findings:
    - Rule `"validation_missing"`: classification `"Needs Human Review"`. Explanation: `"Required information is missing or unknown."`
      - Evidence: field `"owner"`, present yes, value `null`
      - Provenance of `"owner"`: `{"evidence": [{"path": "owner", "present": true, "value": null}], "transformation": "copy"}`
    - Rule `"validation_missing"`: classification `"Needs Human Review"`. Explanation: `"Required information is missing or unknown."`
      - Evidence: field `"due_date"`, present yes, value `null`
      - Provenance of `"due_date"`: `{"evidence": [{"path": "due_date", "present": true, "value": null}], "transformation": "copy"}`
    - Rule `"validation_missing"`: classification `"Needs Human Review"`. Explanation: `"Required information is missing or unknown."`
      - Evidence: field `"dependencies"`, present yes, value `null`
      - Provenance of `"dependencies"`: `{"evidence": [{"path": "dependencies", "present": true, "value": null}], "transformation": "copy"}`
- Record `{"batch_position": 6, "ticket_id": "T-106"}`
  - Classification: `"Needs Human Review"`
  - Requires human review: yes
  - Operational actions require human approval: yes
  - Source: `{"type": "synthetic_json"}`
  - Validation issues:
    - Field `"owner"`, code `"missing"`, message `"Required information is missing or unknown."`
  - Normalization issues: none
  - Findings:
    - Rule `"validation_missing"`: classification `"Needs Human Review"`. Explanation: `"Required information is missing or unknown."`
      - Evidence: field `"owner"`, present yes, value `null`
      - Provenance of `"owner"`: `{"evidence": [{"path": "owner", "present": true, "value": null}], "transformation": "copy"}`
    - Rule `"overdue"`: classification `"High"`. Explanation: `"Active ticket is past its due date."`
      - Evidence: field `"status"`, present yes, value `"open"`
      - Evidence: field `"due_date"`, present yes, value `"2026-11-01"`
      - Calculated: `{"days_overdue": 3, "days_remaining": -3}`
      - Provenance of `"status"`: `{"evidence": [{"path": "status", "present": true, "value": "open"}], "transformation": "copy"}`
      - Provenance of `"due_date"`: `{"evidence": [{"path": "due_date", "present": true, "value": "2026-11-01"}], "transformation": "copy"}`
- Record `{"batch_position": 10, "ticket_id": "T-110"}`
  - Classification: `"Needs Human Review"`
  - Requires human review: yes
  - Operational actions require human approval: yes
  - Source: `{"type": "synthetic_json"}`
  - Validation issues:
    - Field `"owner"`, code `"missing"`, message `"Required information is missing or unknown."`
  - Normalization issues: none
  - Findings:
    - Rule `"validation_missing"`: classification `"Needs Human Review"`. Explanation: `"Required information is missing or unknown."`
      - Evidence: field `"owner"`, present yes, value `null`
      - Provenance of `"owner"`: `{"evidence": [{"path": "owner", "present": true, "value": null}], "transformation": "copy"}`
    - Rule `"outside_deadline_window"`: classification `"Low"`. Explanation: `"No elevated risk detected by the status and deadline rules."`
      - Evidence: field `"status"`, present yes, value `"open"`
      - Evidence: field `"due_date"`, present yes, value `"2026-11-24"`
      - Calculated: `{"days_remaining": 20}`
      - Provenance of `"status"`: `{"evidence": [{"path": "status", "present": true, "value": "open"}], "transformation": "copy"}`
      - Provenance of `"due_date"`: `{"evidence": [{"path": "due_date", "present": true, "value": "2026-11-24"}], "transformation": "copy"}`
- Record `{"batch_position": 13, "ticket_id": "T-113"}`
  - Classification: `"Needs Human Review"`
  - Requires human review: yes
  - Operational actions require human approval: yes
  - Source: `{"type": "synthetic_json"}`
  - Validation issues:
    - Field `"dependencies[1]"`, code `"contradictory"`, message `"Dependency is listed more than once."`
  - Normalization issues: none
  - Findings:
    - Rule `"validation_contradictory"`: classification `"Needs Human Review"`. Explanation: `"Dependency is listed more than once."`
      - Evidence: field `"dependencies[1]"`, present yes, value `"T-160"`
      - Evidence: field `"ticket_id"`, present yes, value `"T-113"`
      - Evidence: field `"status"`, present yes, value `"open"`
      - Evidence: field `"dependencies"`, present yes, value `["T-160", "T-160"]`
      - Provenance of `"dependencies[1]"`: `{"evidence": [{"path": "dependencies", "present": true, "value": ["T-160", "T-160"]}], "transformation": "copy"}`
      - Provenance of `"ticket_id"`: `{"evidence": [{"path": "ticket_id", "present": true, "value": "T-113"}], "transformation": "copy"}`
      - Provenance of `"status"`: `{"evidence": [{"path": "status", "present": true, "value": "open"}], "transformation": "copy"}`
      - Provenance of `"dependencies"`: `{"evidence": [{"path": "dependencies", "present": true, "value": ["T-160", "T-160"]}], "transformation": "copy"}`
    - Rule `"outside_deadline_window"`: classification `"Low"`. Explanation: `"No elevated risk detected by the status and deadline rules."`
      - Evidence: field `"status"`, present yes, value `"open"`
      - Evidence: field `"due_date"`, present yes, value `"2026-11-18"`
      - Calculated: `{"days_remaining": 14}`
      - Provenance of `"status"`: `{"evidence": [{"path": "status", "present": true, "value": "open"}], "transformation": "copy"}`
      - Provenance of `"due_date"`: `{"evidence": [{"path": "due_date", "present": true, "value": "2026-11-18"}], "transformation": "copy"}`
- Record `{"batch_position": 17, "ticket_id": "T-117"}`
  - Classification: `"Needs Human Review"`
  - Requires human review: yes
  - Operational actions require human approval: yes
  - Source: `{"type": "synthetic_json"}`
  - Validation issues:
    - Field `"due_date"`, code `"malformed"`, message `"Expected a valid calendar date in YYYY-MM-DD format."`
  - Normalization issues: none
  - Findings:
    - Rule `"validation_malformed"`: classification `"Needs Human Review"`. Explanation: `"Expected a valid calendar date in YYYY-MM-DD format."`
      - Evidence: field `"due_date"`, present yes, value `"11/06/2026"`
      - Provenance of `"due_date"`: `{"evidence": [{"path": "due_date", "present": true, "value": "11/06/2026"}], "transformation": "copy"}`

## Client `"Client C"`

- Requires human review: no
- Operational actions require human approval: yes
- Counts:
  - High: 0 (records: `[]`)
  - Medium: 0 (records: `[]`)
  - Low: 1 (records: `[{"batch_position": 20, "ticket_id": "T-120"}]`)
  - Human Review: 0 (records: `[]`)
  - Total: 1 (records: `[{"batch_position": 20, "ticket_id": "T-120"}]`)

### High

None.

### Medium

None.

### Low

- Record `{"batch_position": 20, "ticket_id": "T-120"}`
  - Classification: `"Low"`
  - Requires human review: no
  - Operational actions require human approval: yes
  - Source: `{"type": "synthetic_json"}`
  - Validation issues: none
  - Normalization issues: none
  - Findings:
    - Rule `"outside_deadline_window"`: classification `"Low"`. Explanation: `"No elevated risk detected by the status and deadline rules."`
      - Evidence: field `"status"`, present yes, value `"open"`
      - Evidence: field `"due_date"`, present yes, value `"2026-12-01"`
      - Calculated: `{"days_remaining": 27}`
      - Provenance of `"status"`: `{"evidence": [{"path": "status", "present": true, "value": "open"}], "transformation": "copy"}`
      - Provenance of `"due_date"`: `{"evidence": [{"path": "due_date", "present": true, "value": "2026-12-01"}], "transformation": "copy"}`

### Human Review

None.

## Batch review queue

- Criteria: `"Records without a verified client_id (absent, null, blank, or malformed)."`
- Requires human review: yes
- Operational actions require human approval: yes
- Records: 1 (records: `[{"batch_position": 11, "ticket_id": "T-111"}]`)

- Record `{"batch_position": 11, "ticket_id": "T-111"}`
  - Classification: `"Needs Human Review"`
  - Requires human review: yes
  - Operational actions require human approval: yes
  - Source: `{"type": "synthetic_json"}`
  - Client evidence: `{"field": "client_id", "present": false}`
  - Validation issues:
    - Field `"client_id"`, code `"missing"`, message `"Required information is missing or unknown."`
  - Normalization issues: none
  - Findings:
    - Rule `"validation_missing"`: classification `"Needs Human Review"`. Explanation: `"Required information is missing or unknown."`
      - Evidence: field `"client_id"`, present no, no value
      - Provenance of `"client_id"`: `{"evidence": [{"path": "client_id", "present": false}], "transformation": "copy"}`
    - Rule `"outside_deadline_window"`: classification `"Low"`. Explanation: `"No elevated risk detected by the status and deadline rules."`
      - Evidence: field `"status"`, present yes, value `"open"`
      - Evidence: field `"due_date"`, present yes, value `"2026-11-12"`
      - Calculated: `{"days_remaining": 8}`
      - Provenance of `"status"`: `{"evidence": [{"path": "status", "present": true, "value": "open"}], "transformation": "copy"}`
      - Provenance of `"due_date"`: `{"evidence": [{"path": "due_date", "present": true, "value": "2026-11-12"}], "transformation": "copy"}`
