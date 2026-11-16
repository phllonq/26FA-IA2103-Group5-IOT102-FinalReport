# AI Audit Entry — IOT102 Fall 2026

> **Record status:** RECONSTRUCTED / APPROXIMATE. The original exact timestamps and meeting records were not available. The date/time below is a proposed timeline aligned with the course week, not a verified historical timestamp. Confirm or replace it before submission.
>
> **Project:** Adaptive IoT-UAV Environmental Monitoring System with Downwash-Aware Sensing and Adaptive Communication  
> **Course / Group:** IOT102 — Group 5, IA2103  
> **AI tool:** ChatGPT  
> **Human operators:** TRAN PHI LONG; NGUYEN BAO PHUC  
> **Source location:** Reconstructed from the team's AI_Audit_Log.md; no original conversation permalink available.

## 1. Entry Metadata

- **Entry ID:** ENTRY-003
- **Evidence ID:** EV-003
- **Date and time:** 2026-10-15, 19:45 (proposed; reconstructed)
- **AI tool and model:** ChatGPT
- **Human operator:** TRAN PHI LONG; NGUYEN BAO PHUC
- **Interaction type:** PROMPT / RESPONSE / REVIEW / DECISION
- **Evidence classification:** RECONSTRUCTED / APPROXIMATE
- **Source location:** Team AI audit summary; original prompt and conversation link not preserved.

## 2. Objective

Review the sensor-reading firmware structure so sensor failures do not block LoRa communication or corrupt recorded environmental data.

## 3. Project Context Supplied to the AI

The UAV firmware reads two BMP280 sensors and communicates with the ground station through the LoRa module connected to Serial2. The ground station processes received data for later analysis. Sensor-read failures must be distinguishable from valid measurements.

## 4. Prompt or Input

**RECONSTRUCTED SUMMARY — not a verbatim prompt:** Ask ChatGPT to help structure ESP32 firmware for reading two BMP280 sensors while maintaining LoRa serial communication and handling failed sensor readings safely.

## 5. AI Output

**SUMMARY:** The team audit summary describes an AI-generated example that used blocking `delay()` calls and substituted `0.0` when a sensor read failed. Those choices were reviewed because they could interfere with communication and make invalid measurements look valid.

## 6. Claims and Recommendations Requiring Verification

| ID | Claim or recommendation | Verification method / source | Status | Notes |
|---|---|---|---|---|
| V-01 | Blocking delays can postpone servicing the LoRa serial receive path | Inspect firmware control flow and test serial responsiveness | REPORTED ISSUE | Attach code revision or serial test if available. |
| V-02 | Replacing sensor errors with 0.0 can distort statistical analysis | Inject/disconnect sensor and inspect logged output and analysis pipeline | TECHNICALLY PLAUSIBLE; TEST EVIDENCE NOT ATTACHED | Zero is a possible real reading and should not represent a failed read. |
| V-03 | A 50 ms I2C timeout is appropriate | Check library support and test under actual bus conditions | PENDING VERIFICATION | Confirm the API and timeout behavior for the installed library. |
| V-04 | JSON `null` can represent invalid sensor data | Validate the ground-station JSON parser and downstream handling | PENDING VERIFICATION | Ensure parser distinguishes null from numeric values. |

## 7. Human Review

- **What appears useful:** Non-blocking scheduling helps keep sensor acquisition from unnecessarily delaying communication handling. Explicit invalid-value representation improves data quality.
- **Potential errors or unsupported assumptions:** A 50 ms timeout is not universally optimal; it must be tested with the actual sensor, wiring, and library. The receiver must correctly parse JSON null.
- **Changes made by human reviewer:** The team audit summary records moving to a non-blocking structure, setting an I2C timeout of 50 ms, and emitting JSON `null` for failed sensor readings rather than `0`.
- **Independent verification performed:** The source summary reports a runtime issue involving Serial2 and sensor disconnection. Original logs and code diff were not attached here.

## 8. Team Decision

- **Decision:** REPORTED IN TEAM AUDIT SUMMARY
- **Decision evidence:** AI_Audit_Log.md, Entry 3. Original meeting minutes or approval record not available.
- **Participants:** TRAN PHI LONG; NGUYEN BAO PHUC
- **Date:** 2026-10-15 (proposed; reconstructed)
- **Conditions and limitations:** Confirm that the current firmware actually implements the non-blocking logic, timeout, and null handling.

## 9. Implementation and Testing

- **Implementation status:** REPORTED IN TEAM AUDIT SUMMARY; current code revision not checked in this reconstructed record.
- **Test performed:** The source summary describes UAV runtime testing and a sensor-disconnection scenario.
- **Observed result:** The source summary reports that blocking delays affected Serial2 handling and that a failed sensor could otherwise be represented as 0.0. No timing measurements or captured payloads were supplied.
- **Test artifact:** Add the relevant ESP32 firmware commit, serial log, and sample JSON payload for both valid and failed sensor reads.
- **Limitations:** Do not claim that all communication blocking was eliminated without a repeatable test.

## 10. Follow-up Actions

| Action | Owner | Due date | Status |
|---|---|---|---|
| Link the firmware revision implementing non-blocking reads | TRAN PHI LONG; NGUYEN BAO PHUC | 2026-11-19 | OPEN |
| Attach serial log and JSON invalid-reading example | TRAN PHI LONG; NGUYEN BAO PHUC | 2026-11-19 | OPEN |

## 11. Provenance and Revision History

- **Prepared on:** 2026-11-16
- **Source fidelity:** RECONSTRUCTED
- **Reviewer:** TRAN PHI LONG; NGUYEN BAO PHUC
- **Revision notes:** Structured from Entry 3 of AI_Audit_Log.md. Date, time, operator attribution, and verification details are reconstructed and require team confirmation.
