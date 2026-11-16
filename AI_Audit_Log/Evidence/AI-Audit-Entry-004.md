# AI Audit Entry — IOT102 Fall 2026

> **Record status:** RECONSTRUCTED / APPROXIMATE. The original exact timestamps and meeting records were not available. The date/time below is a proposed timeline aligned with the course week, not a verified historical timestamp. Confirm or replace it before submission.
>
> **Project:** Adaptive IoT-UAV Environmental Monitoring System with Downwash-Aware Sensing and Adaptive Communication  
> **Course / Group:** IOT102 — Group 5, IA2103  
> **AI tool:** ChatGPT  
> **Human operators:** TRAN PHI LONG; NGUYEN BAO PHUC  
> **Source location:** Reconstructed from the team's AI_Audit_Log.md; no original conversation permalink available.

## 1. Entry Metadata

- **Entry ID:** ENTRY-004
- **Evidence ID:** EV-004
- **Date and time:** 2026-11-12, 20:15 (proposed; reconstructed)
- **AI tool and model:** ChatGPT
- **Human operator:** TRAN PHI LONG; NGUYEN BAO PHUC
- **Interaction type:** PROMPT / RESPONSE / REVIEW / DECISION
- **Evidence classification:** RECONSTRUCTED / APPROXIMATE
- **Source location:** Team AI audit summary; original prompt and conversation link not preserved.

## 2. Objective

Review the ground-station Packet Delivery Ratio (PDR) calculation so it remains meaningful when the UAV changes its telemetry sampling interval.

## 3. Project Context Supplied to the AI

The UAV can transmit telemetry at different sampling/reporting intervals, including 1 s, 5 s, and 60 s. The ground station stores received packets in SQLite and evaluates communication performance. The PDR calculation must account for missing packets and variable reporting rates.

## 4. Prompt or Input

**RECONSTRUCTED SUMMARY — not a verbatim prompt:** Ask ChatGPT how to calculate packet delivery performance for telemetry whose transmission interval changes over time, and how the UAV and ground station should identify missing packets.

## 5. AI Output

**SUMMARY:** The team audit summary describes an initial AI-generated approach that estimated PDR by dividing the number of SQLite rows received by application uptime. The team identified that this approach does not account for changing expected packet counts when the reporting interval changes.

## 6. Claims and Recommendations Requiring Verification

| ID | Claim or recommendation | Verification method / source | Status | Notes |
|---|---|---|---|---|
| V-01 | Received-row count divided by uptime is sufficient for PDR | Compare calculation against known sent/received packet sequences | REJECTED | Variable sampling intervals make a fixed expected rate invalid. |
| V-02 | A monotonically increasing sequence number can expose packet gaps | Inspect transmitted payloads and receiver logs | PENDING VERIFICATION | Ensure sequence numbers persist or reset behavior is documented. |
| V-03 | PDR can be calculated as unique received sequence numbers divided by sequence-number span | Validate against controlled packet-loss tests | PROPOSED FORMULA | Define session boundaries and handle duplicates, resets, and out-of-order packets. |

## 7. Human Review

- **What appears useful:** Sequence numbers provide a direct way to identify gaps in a stream of packets, including when the reporting interval changes.
- **Potential errors or unsupported assumptions:** The formula `unique received seq / (max seq - min seq + 1)` is only valid within a clearly defined sequence-number session. It can be misleading if the sequence counter resets, if the capture begins mid-session, or if packets arrive out of order.
- **Changes made by human reviewer:** The team audit summary records adding a monotonically increasing `seq` field to UAV telemetry and calculating PDR at the ground station from the sequence-number range.
- **Independent verification performed:** The source summary describes a revised calculation, but no known-loss test dataset or SQLite export was attached to this reconstructed entry.

## 8. Team Decision

- **Decision:** REPORTED IN TEAM AUDIT SUMMARY
- **Decision evidence:** AI_Audit_Log.md, Entry 4. Original meeting minutes or approval record not available.
- **Participants:** TRAN PHI LONG; NGUYEN BAO PHUC
- **Date:** 2026-11-12 (proposed; reconstructed)
- **Conditions and limitations:** Document session boundaries, duplicate handling, sequence resets, and the exact PDR definition used in the final report.

## 9. Implementation and Testing

- **Implementation status:** REPORTED IN TEAM AUDIT SUMMARY; source code and database evidence not attached here.
- **Test performed:** No controlled packet-loss test is documented in the supplied summary.
- **Observed result:** The source summary identifies a flaw in the uptime-based calculation and records a sequence-number-based revision. No measured PDR result is available in this entry.
- **Test artifact:** Add the UAV payload sample containing `seq`, corresponding ground-station SQLite rows, and a controlled-loss test if available.
- **Limitations:** Do not report a numerical PDR improvement without a reproducible test and verified sent-packet reference.

## 10. Follow-up Actions

| Action | Owner | Due date | Status |
|---|---|---|---|
| Confirm `seq` field in current UAV firmware and ground-station parser | TRAN PHI LONG; NGUYEN BAO PHUC | 2026-11-19 | OPEN |
| Run a controlled packet-loss test and attach SQLite/log evidence | TRAN PHI LONG; NGUYEN BAO PHUC | 2026-11-20 | OPEN |

## 11. Provenance and Revision History

- **Prepared on:** 2026-11-16
- **Source fidelity:** RECONSTRUCTED
- **Reviewer:** TRAN PHI LONG; NGUYEN BAO PHUC
- **Revision notes:** Structured from Entry 4 of AI_Audit_Log.md. Date, time, operator attribution, and verification details are reconstructed and require team confirmation.
