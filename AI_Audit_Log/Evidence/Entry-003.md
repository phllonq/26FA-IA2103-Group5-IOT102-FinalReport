# AI Audit Entry 003 — Firmware, Sensor Error Handling and Fault Tolerance

## 1. Entry Metadata

- **Entry ID:** ENTRY-003
- **Evidence ID:** EV-003
- **Date and time:** Week 6 (as labelled in the original AI Audit Log; exact date/time not recorded)
- **AI tool and model:** NOT VERIFIED
- **Human operator:** NOT VERIFIED (the source identifies Group 5, Class IA2103, not the individual operator)
- **Interaction type:** PROMPT / RESPONSE / REVIEW / DECISION (interaction details reconstructed from the audit summary)
- **Evidence classification:** RECONSTRUCTED / PARTIALLY VERIFIED
- **Source location:** `AI_Audit_Log.md` — Entry 3; `ADR-004-Fault-Tolerance-FSM-v1.3.md`

## 2. Objective

Record the AI-assisted firmware issue described in the original AI Audit Log and the team's subsequent approach to non-blocking operation and sensor-error handling. The original entry focuses on code for two BMP280 sensors, blocking `delay()` calls, and the use of `0.0` as a fallback for failed readings. ADR-004 provides additional project-level evidence for the adopted fault-tolerance approach, including a finite state machine (FSM), watchdog timer, I2C timeout, heartbeat monitoring, and JSON `null` for sensor errors.

## 3. Project Context Supplied to the AI

The project is an IOT102 Fall 2026 UAV environmental-monitoring system. The UAV firmware uses an ESP32, two BMP280 sensors, and an EBYTE E32 LoRa module communicating over a serial interface. The ground station receives telemetry and uses the sensor data for research-related calculations, including MAE and RMSE.

The original AI Audit Log states that blocking delays interfered with reading commands from `Serial2` (LoRa), and that substituting `0.0` for failed sensor readings could distort MAE/RMSE calculations. ADR-004 describes the UAV's vibration, motor interference and battery-voltage variation as operational risks, and records the team's adoption of non-blocking FSM-based firmware and fault-handling mechanisms.

## 4. Prompt or Input

**RECONSTRUCTED SUMMARY — not a verbatim prompt.** The supplied audit log indicates that AI assistance was used to generate firmware code for initializing and reading two BMP280 sensors. The exact prompt, source code submitted to the AI, and full interaction are not preserved.

## 5. AI Output

**SUMMARY — original AI response not preserved verbatim.** According to the original AI Audit Log, the AI generated code that initialized two BMP280 sensors, used blocking `delay()` calls, and assigned a default value of `0.0` when a sensor reading failed.

The original generated code and complete response were not supplied. No exact code or verbatim AI wording is reproduced in this entry.

## 6. Claims and Recommendations Requiring Verification

| ID | Claim or recommendation | Verification method / source | Status | Notes |
|---|---|---|---|---|
| V-01 | Blocking `delay()` in the sensor-reading flow interfered with reading LoRa commands on `Serial2`. | Inspect firmware scheduling and test command reception while sensor reads execute. | REPORTED IN AI AUDIT LOG; RAW TEST DATA NOT SUPPLIED | The audit log reports this observed problem. |
| V-02 | A failed sensor read should not be represented as a valid `0.0` measurement. | Inject or simulate sensor failure and inspect serialized data and downstream calculations. | TEAM DECISION RECORDED; SUPPORTING ADR-004 | ADR-004 records JSON `null` as the error representation and explains the data-integrity rationale. |
| V-03 | The firmware should use non-blocking execution / FSM rather than blocking code. | Inspect firmware architecture and test concurrent sensor, serial and fault-handling tasks. | ACCEPTED / IMPLEMENTED AS RECORDED IN ADR-004 | ADR-004 states the non-blocking FSM approach was implemented on ESP32 and ESP8266. |
| V-04 | I2C timeout is configured to 50 ms. | Inspect firmware initialization and test a disconnected or unresponsive sensor. | RECORDED IN ADR-004 | ADR-004 specifies `Wire.setTimeOut(50)`. |
| V-05 | UAV hardware watchdog is configured for 15 seconds. | Inspect firmware WDT setup and perform a controlled hang / recovery test. | RECORDED IN ADR-004; TEST ARTIFACT NOT SUPPLIED | ADR-004 specifies `esp_task_wdt` with a 15-second timeout. |
| V-06 | Ground-station heartbeat FSM marks the UI OFFLINE after more than 12 seconds without a received packet. | Inspect ESP8266 firmware and test packet-loss / timeout scenarios. | RECORDED IN ADR-004; TEST ARTIFACT NOT SUPPLIED | The 12-second threshold is documented in ADR-004. |
| V-07 | JSON `null` is handled correctly by the Python / Pandas processing path. | Send sensor-error payloads and verify parsing, missing-value handling and metric calculations. | NOT VERIFIED BY A SUPPLIED TEST ARTIFACT | ADR-004 describes the intended handling; no Python test output or dataset is included. |

## 7. Human Review

- **What appears useful:** The audit log identifies a practical conflict between blocking sensor code and receiving LoRa commands. ADR-004 records a coherent fault-tolerance direction: non-blocking FSM, watchdog, I2C timeout, heartbeat monitoring, and explicit missing-value representation.
- **Potential errors or unsupported assumptions:** The original AI's `0.0` fallback can make a failed measurement indistinguishable from a real numeric value. However, the supplied files do not include the generated code or the complete test evidence. The claim that downstream processing drops or handles all `null` values correctly still requires a test artifact.
- **Changes made by human reviewer:** The AI Audit Log records a move to non-blocking code, an I2C timeout of 50 ms, and JSON `null` rather than `0.0` for sensor errors (and for invalid humidity field `h`). ADR-004 additionally records FSM-based firmware, a 15-second UAV watchdog, and a 12-second ground-station heartbeat threshold for OFFLINE status.
- **Independent verification performed:** The AI Audit Log reports that blocking delays interfered with `Serial2` command reading. ADR-004 records the selected firmware safeguards and implementation status. The supplied materials do not include source-code diffs, serial logs, watchdog recovery logs, or sensor-failure test results.

## 8. Team Decision

- **Decision:** ACCEPTED (for the fault-tolerance design as recorded in ADR-004)
- **Decision evidence:** `AI_Audit_Log.md` — Entry 3 records the non-blocking, I2C-timeout and JSON `null` changes. `ADR-004-Fault-Tolerance-FSM-v1.3.md` records Accepted status and states that the design was implemented on ESP32 (UAV) and ESP8266 (ground station).
- **Participants:** NOT VERIFIED
- **Date:** Week 6 in the AI Audit Log; exact calendar date NOT VERIFIED. ADR-004 version v1.3; approval date is not stated.
- **Conditions and limitations:** The heartbeat threshold is documented as 12 seconds. ADR-004 also notes that adaptive reporting intervals, including a 60-second sleep/report interval, require heartbeat handling that does not falsely classify the UAV as offline. No complete state-transition table or test report was supplied.

## 9. Implementation and Testing

- **Implementation status:** IMPLEMENTED AS RECORDED IN ADR-004
- **Test performed:** The AI Audit Log reports an observed issue with blocking delay and `Serial2` reception during UAV operation. ADR-004 states that FSM and fault-tolerance mechanisms were implemented. Detailed test procedures for WDT reset, I2C timeout, heartbeat transitions and JSON-null processing are NOT PROVIDED.
- **Observed result:** The supplied files record the design decisions and implementation status but provide no measured recovery time, fault-injection outcome, serial trace, or before/after MAE/RMSE comparison.
- **Test artifact:** `AI_Audit_Log.md` and `ADR-004-Fault-Tolerance-FSM-v1.3.md`. Firmware source, serial logs, fault-injection records and analytical output were not supplied.
- **Limitations:** Implementation is reported in the ADR, but independent test artifacts are absent. The audit entry does not claim that all failure modes or data-processing paths have been experimentally validated.

## 10. Follow-up Actions

| Action | Owner | Due date | Status |
|---|---|---|---|
| Preserve firmware revision showing non-blocking FSM and I2C timeout configuration. | NOT ASSIGNED | NOT SET | OPEN |
| Preserve a controlled watchdog recovery test log. | NOT ASSIGNED | NOT SET | OPEN |
| Test and record ground-station heartbeat transitions during packet loss and adaptive reporting intervals. | NOT ASSIGNED | NOT SET | OPEN |
| Test JSON `null` handling through Python parsing and MAE/RMSE calculations. | NOT ASSIGNED | NOT SET | OPEN |

## 11. Provenance and Revision History

- **Prepared on:** 2026-11-16
- **Source fidelity:** SUMMARY / RECONSTRUCTED
- **Reviewer:** NOT VERIFIED
- **Revision notes:** Prepared from the original AI Audit Log and cross-checked against ADR-004. The AI prompt and generated code were not preserved. ADR-004 supports the team's recorded fault-tolerance decisions and implementation status; no unprovided test results are asserted.

---
**Integrity rule:** This entry documents AI assistance and human review; it does not itself prove technical correctness, team approval, implementation, or experimental success.
