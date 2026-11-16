# AI Audit Entry — IOT102 Fall 2026

> **Record status:** RECONSTRUCTED / APPROXIMATE. The original exact timestamps and meeting records were not available. The date/time below is a proposed timeline aligned with the course week, not a verified historical timestamp. Confirm or replace it before submission.
>
> **Project:** Adaptive IoT-UAV Environmental Monitoring System with Downwash-Aware Sensing and Adaptive Communication  
> **Course / Group:** IOT102 — Group 5, IA2103  
> **AI tool:** ChatGPT  
> **Human operators:** TRAN PHI LONG; NGUYEN BAO PHUC  
> **Source location:** Reconstructed from the team's AI_Audit_Log.md; no original conversation permalink available.

## 1. Entry Metadata

- **Entry ID:** ENTRY-001
- **Evidence ID:** EV-001
- **Date and time:** 2026-10-01, 19:30 (proposed; reconstructed)
- **AI tool and model:** ChatGPT
- **Human operator:** TRAN PHI LONG; NGUYEN BAO PHUC
- **Interaction type:** PROMPT / RESPONSE / REVIEW / DECISION
- **Evidence classification:** RECONSTRUCTED / APPROXIMATE
- **Source location:** Team AI audit summary; original prompt and conversation link not preserved.

## 2. Objective

Evaluate a suitable communication architecture between the UAV-mounted ESP32 and the ground station.

## 3. Project Context Supplied to the AI

The project requires environmental sensor telemetry from an ESP32 mounted on a UAV to be received and monitored by a ground station. The communication link should be suitable for an outdoor UAV environment and should avoid unnecessary power consumption.

## 4. Prompt or Input

**RECONSTRUCTED SUMMARY — not a verbatim prompt:** Ask ChatGPT to suggest a communication approach for sending UAV sensor data to a ground station, considering range, reliability, latency, and power use.

## 5. AI Output

**SUMMARY:** ChatGPT initially suggested using the ESP32 Wi-Fi Access Point mode, with the ground station connecting to the UAV network and receiving sensor data through an MQTT-based workflow.

## 6. Claims and Recommendations Requiring Verification

| ID | Claim or recommendation | Verification method / source | Status | Notes |
|---|---|---|---|---|
| V-01 | ESP32 Wi-Fi can provide the required outdoor link | Outdoor range and stability test | PARTIALLY VERIFIED | Team's audit summary reports unstable Wi-Fi beyond approximately 30 m; retain the measurement only if test notes support it. |
| V-02 | Wi-Fi operation is acceptable for UAV power budget | Compare current draw / battery behavior | NOT VERIFIED | No numerical power measurements are recorded in the source summary. |
| V-03 | LoRa EBYTE E32-433T20D is a suitable alternative | Module datasheet and bench/range test | PENDING VERIFICATION | Confirm configured frequency, legal use, antenna, wiring, and actual range. |

## 7. Human Review

- **What appears useful:** Wi-Fi is straightforward for prototyping, while LoRa may be more suitable for a longer-range telemetry link.
- **Potential errors or unsupported assumptions:** A claimed range or latency advantage cannot be generalized without controlled tests. LoRa is not automatically a replacement for every Wi-Fi/MQTT function.
- **Changes made by human reviewer:** The team audit summary records a change from Wi-Fi to EBYTE E32-433T20D LoRa in Transparent Mode.
- **Independent verification performed:** The source summary reports outdoor testing. Exact test logs, distance measurements, and power measurements were not attached to this reconstructed entry.

## 8. Team Decision

- **Decision:** PROPOSED / REPORTED IN TEAM AUDIT SUMMARY
- **Decision evidence:** AI_Audit_Log.md, Entry 1. Original meeting minutes or approval record not available.
- **Participants:** TRAN PHI LONG; NGUYEN BAO PHUC
- **Date:** 2026-10-01 (proposed; reconstructed)
- **Conditions and limitations:** Confirm the actual radio configuration and test results before describing the LoRa link as validated.

## 9. Implementation and Testing

- **Implementation status:** REPORTED IN TEAM AUDIT SUMMARY; exact implementation evidence not attached here.
- **Test performed:** Outdoor Wi-Fi link check is reported in the source summary.
- **Observed result:** Source summary describes unstable Wi-Fi when the UAV was more than approximately 30 m from the ground. No raw logs or repeated-trial data were supplied.
- **Test artifact:** Add actual range-test photos, serial logs, or repository commit if available.
- **Limitations:** Do not present the approximate 30 m observation as a statistically established maximum range.

## 10. Follow-up Actions

| Action | Owner | Due date | Status |
|---|---|---|---|
| Attach LoRa datasheet and wiring/configuration evidence | TRAN PHI LONG; NGUYEN BAO PHUC | 2026-11-18 | OPEN |
| Add actual range and power test logs, if available | TRAN PHI LONG; NGUYEN BAO PHUC | 2026-11-18 | OPEN |

## 11. Provenance and Revision History

- **Prepared on:** 2026-11-16
- **Source fidelity:** RECONSTRUCTED
- **Reviewer:** TRAN PHI LONG; NGUYEN BAO PHUC
- **Revision notes:** Structured from Entry 1 of AI_Audit_Log.md. Date, time, operator attribution, and verification details are reconstructed and require team confirmation.
