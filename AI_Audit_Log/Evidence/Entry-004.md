# AI Audit Entry 004 — Data Analytics, PDR and Ground-Station Storage

## 1. Entry Metadata

- **Entry ID:** ENTRY-004
- **Evidence ID:** EV-004
- **Date and time:** Week 10 (as labelled in the original AI Audit Log; exact date/time not recorded)
- **AI tool and model:** NOT VERIFIED
- **Human operator:** NOT VERIFIED (the source identifies Group 5, Class IA2103, not the individual operator)
- **Interaction type:** PROMPT / RESPONSE / REVIEW / DECISION (interaction details reconstructed from the audit summary)
- **Evidence classification:** RECONSTRUCTED / PARTIALLY VERIFIED
- **Source location:** `AI_Audit_Log.md` — Entry 4; `ADR-003-SQLite-WAL-Dashboard-v1.1.md`

## 2. Objective

Record the AI-assisted work on data analytics and display, especially the packet-delivery-ratio (PDR) calculation, and distinguish it from the separate database architecture decision documented in ADR-003. The original AI Audit Log states that AI generated a PDR script based on SQLite row count divided by software uptime. The team identified a problem when the telemetry sampling interval changed between 1, 5 and 60 seconds, and recorded a sequence-number-based formula as its replacement.

ADR-003 separately documents SQLite in WAL mode for concurrent local storage and dashboard access. ADR-003 supports the ground-station storage context but does not itself confirm the sequence-number PDR formula.

## 3. Project Context Supplied to the AI

The project is an IOT102 Fall 2026 UAV environmental-monitoring system with LoRa telemetry sent from the UAV to a ground station. The ground station stores readings and displays data for research metrics, including PDR, AoI, MAE and RMSE.

The original AI Audit Log states that the UAV can change its sampling interval among 1, 5 and 60 seconds. ADR-003 records the need for offline data storage while the gateway writes incoming telemetry and the Streamlit dashboard reads data to display charts and calculate the four RBL metrics.

## 4. Prompt or Input

**RECONSTRUCTED SUMMARY — not a verbatim prompt.** The supplied AI Audit Log indicates that AI assistance was requested for a script to calculate packet delivery ratio from received database rows and software uptime. The exact prompt, expected-packet model and full interaction are not preserved.

## 5. AI Output

**SUMMARY — original AI response not preserved verbatim.** The AI-generated approach is described in the audit log as counting rows received in SQLite and dividing by the software uptime.

The full generated script, exact formula implementation, and original AI response were not supplied.

## 6. Claims and Recommendations Requiring Verification

| ID | Claim or recommendation | Verification method / source | Status | Notes |
|---|---|---|---|---|
| V-01 | SQLite row count divided by software uptime is a valid PDR calculation for this system. | Compare against transmitted sequence numbers and expected-packet accounting under each sampling interval. | REJECTED BY TEAM | The audit log states the method becomes inaccurate when the sampling interval changes. |
| V-02 | The UAV's sequence number can support a PDR calculation based on received unique sequence values over the sequence-number span. | Inspect transmitted `seq` field, received records, duplicate/loss handling and calculation code; test with known packet loss. | TEAM DECISION RECORDED; TEST ARTIFACT NOT SUPPLIED | The audit log records the formula: unique `seq` count / (`seq max` − `seq min` + 1). |
| V-03 | SQLite is suitable for local offline telemetry storage. | Inspect database integration and test read/write behaviour without network access. | ACCEPTED / IMPLEMENTED AS RECORDED IN ADR-003 | ADR-003 states SQLite was integrated into `gateway.py` and `app.py`. |
| V-04 | SQLite WAL mode allows gateway writes and dashboard reads to proceed concurrently. | Inspect `PRAGMA journal_mode=WAL;` and run concurrent read/write tests. | RECORDED IN ADR-003; TEST OUTPUT NOT SUPPLIED | ADR-003 describes this as the reason for WAL mode. |
| V-05 | The database uses `readings` and `events` tables. | Inspect database schema or migration / initialization code. | RECORDED IN ADR-003 | No database file or schema dump was supplied. |
| V-06 | Dashboard calculates PDR, AoI, MAE and RMSE from stored data. | Inspect `app.py`, calculation functions and test dataset. | RECORDED IN ADR-003; METRIC VALIDATION NOT PROVIDED | ADR-003 states that the dashboard retrieves data to calculate these metrics. |

## 7. Human Review

- **What appears useful:** The AI-generated approach provided an initial implementation direction for PDR. The team identified that a fixed uptime-based denominator does not represent expected packets consistently when the reporting interval changes. ADR-003 also records a database choice suited to an offline ground station with simultaneous ingestion and dashboard access.
- **Potential errors or unsupported assumptions:** Row count divided by uptime is not, by itself, a packet-delivery ratio when packet generation intervals are adaptive. The sequence-based formula also needs careful handling of duplicates, sequence-number wraparound, restarts, and missing start/end context; the supplied records do not describe these cases.
- **Changes made by human reviewer:** The AI Audit Log records adding an incrementing `seq` field from the UAV and calculating PDR at the ground station as the number of unique sequence values divided by (`seq max` − `seq min` + 1). ADR-003 separately records SQLite with WAL mode, `readings` and `events` tables, and integration with `gateway.py` and `app.py`.
- **Independent verification performed:** The AI Audit Log records the sampling-interval issue (1 s, 5 s and 60 s). ADR-003 records the database architecture and integration status. No raw packet trace, known-loss test, PDR comparison, database concurrency log or dashboard screenshot was supplied.

## 8. Team Decision

- **Decision:** ACCEPTED for the sequence-number PDR approach as recorded in `AI_Audit_Log.md`; ACCEPTED for SQLite WAL storage as recorded in ADR-003.
- **Decision evidence:** `AI_Audit_Log.md` — Entry 4 records the sequence-number PDR change. `ADR-003-SQLite-WAL-Dashboard-v1.1.md` records the SQLite WAL decision as Accepted and states it was integrated into `gateway.py` and `app.py` (Streamlit).
- **Participants:** NOT VERIFIED
- **Date:** Week 10 in the AI Audit Log; exact calendar date NOT VERIFIED. ADR-003 version v1.1; approval date is not stated.
- **Conditions and limitations:** The sequence-based formula is the formula recorded by the team; the supplied files do not specify behaviour for sequence-number wraparound, device restart, duplicate packets, or filtering of invalid records. ADR-003 notes that WAL creates `.db-wal` and `.db-shm` files that should be handled by `.gitignore`.

## 9. Implementation and Testing

- **Implementation status:** SQLite WAL: IMPLEMENTED AS RECORDED IN ADR-003. Sequence-number PDR: DECISION RECORDED IN AI AUDIT LOG; implementation status NOT INDEPENDENTLY VERIFIED BY THE SUPPLIED ADR FILES.
- **Test performed:** The audit log reports the sampling-interval issue with the original uptime-based calculation. ADR-003 states SQLite WAL was integrated into `gateway.py` and `app.py`. No controlled packet-loss test or concurrent database read/write test result is supplied.
- **Observed result:** The supplied records describe why the uptime-based calculation was rejected and record the selected sequence-number formula. No measured PDR value, known packet-loss result, query-latency measurement, or database concurrency test output is provided.
- **Test artifact:** `AI_Audit_Log.md` and `ADR-003-SQLite-WAL-Dashboard-v1.1.md`. The source code (`gateway.py`, `app.py`), SQLite database, packet captures and test dataset were not supplied.
- **Limitations:** The database decision and integration status are recorded in ADR-003, but no raw test output is present. The sequence-number PDR formula is documented in the AI Audit Log, not in ADR-003; the two decisions should not be treated as the same evidence.

## 10. Follow-up Actions

| Action | Owner | Due date | Status |
|---|---|---|---|
| Preserve the firmware / gateway code that sends and processes the `seq` field. | NOT ASSIGNED | NOT SET | OPEN |
| Validate PDR using controlled packet loss at 1 s, 5 s and 60 s reporting intervals. | NOT ASSIGNED | NOT SET | OPEN |
| Document handling of duplicates, sequence wraparound and device restart in PDR calculation. | NOT ASSIGNED | NOT SET | OPEN |
| Preserve the SQLite schema and WAL initialization code. | NOT ASSIGNED | NOT SET | OPEN |
| Preserve a concurrent gateway-write / dashboard-read test and sample database. | NOT ASSIGNED | NOT SET | OPEN |

## 11. Provenance and Revision History

- **Prepared on:** 2026-11-16
- **Source fidelity:** SUMMARY / RECONSTRUCTED
- **Reviewer:** NOT VERIFIED
- **Revision notes:** Prepared from the original AI Audit Log and cross-checked against ADR-003. The PDR decision is sourced from the AI Audit Log; SQLite WAL, database tables and dashboard integration are sourced from ADR-003. No unprovided source code or test results are claimed.

---
**Integrity rule:** This entry documents AI assistance and human review; it does not itself prove technical correctness, team approval, implementation, or experimental success.
