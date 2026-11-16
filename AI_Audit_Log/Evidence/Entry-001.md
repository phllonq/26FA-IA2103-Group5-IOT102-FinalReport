# AI Audit Entry 001 — Communication Architecture

## 1. Entry Metadata

- **Entry ID:** ENTRY-001
- **Evidence ID:** EV-001
- **Date and time:** Week 4 (exact date/time not recorded in the supplied AI Audit Log)
- **AI tool and model:** NOT VERIFIED
- **Human operator:** NOT VERIFIED (the source identifies Group 5, Class IA2103, not the individual operator)
- **Interaction type:** PROMPT / RESPONSE / REVIEW / DECISION (interaction details reconstructed from the audit summary)
- **Evidence classification:** RECONSTRUCTED / PARTIALLY VERIFIED
- **Source location:** `AI_Audit_Log.md` — Entry 1; `ADR-001-Communication-v1.1.md`

## 2. Objective

Record the AI-assisted discussion and subsequent team decision concerning the UAV-to-ground-station telemetry link. The original objective was to select a communication approach for sending sensor data from the UAV to the ground station. The supplied audit log records an initial AI suggestion to use ESP32 Wi-Fi Access Point with MQTT, followed by the team's decision to replace Wi-Fi with LoRa.

## 3. Project Context Supplied to the AI

The project is the IOT102 Fall 2026 project of Group 5, Class IA2103: **Adaptive IoT-UAV Environmental Monitoring System with Downwash-Aware Sensing and Adaptive Communication**. The system uses an ESP32 on the UAV and a ground station to receive sensor data. The supplied audit log states that outdoor Wi-Fi became unstable when the UAV was more than 30 metres from the ground and that continuous Wi-Fi operation increased LiPo battery consumption.

ADR-001 further records concerns about Wi-Fi range, power consumption, and reconnection delay. It documents the selected EBYTE E32-433T20D LoRa module at 433 MHz, UART at 9600 bps (8N1), and Transparent Mode 0. These ADR details are supporting project-decision context; they are not a preserved verbatim prompt to the AI.

## 4. Prompt or Input

**RECONSTRUCTED SUMMARY — not a verbatim prompt.** The team sought help choosing a communication architecture for telemetry between the UAV and the ground station. The exact wording of the prompt and the full context supplied to the AI were not preserved in the supplied records.

## 5. AI Output

**SUMMARY — original AI response not preserved verbatim.** The supplied AI Audit Log records that the AI proposed using the ESP32 in Wi-Fi Access Point mode on the UAV, with the ground station connecting to it and retrieving sensor data through MQTT.

The audit log does not preserve the full AI response, code, configuration, or supporting references.

## 6. Claims and Recommendations Requiring Verification

| ID | Claim or recommendation | Verification method / source | Status | Notes |
|---|---|---|---|---|
| V-01 | ESP32 Wi-Fi AP with MQTT is suitable for the intended UAV telemetry link. | Compare with measured outdoor link behaviour and project requirements. | REJECTED BY TEAM | The audit log reports unstable Wi-Fi beyond 30 m and increased LiPo consumption. |
| V-02 | Wi-Fi reconnection delay can interrupt real-time telemetry. | Record reconnection behaviour during controlled link-loss tests. | RECORDED IN ADR; TEST DETAILS NOT PROVIDED | ADR-001 lists reconnection latency as a reason for moving away from Wi-Fi. |
| V-03 | EBYTE E32-433T20D at 433 MHz is the selected replacement. | ADR-001 decision record and implementation record. | ACCEPTED / IMPLEMENTED AS RECORDED IN ADR | ADR-001 states it was approved and implemented on the UAV and ground station. |
| V-04 | LoRa link provides the required operational range and reliability. | Measure packet delivery and link stability at defined distances and conditions. | NOT VERIFIED BY TEST DATA IN SUPPLIED FILES | The ADR records the decision and claimed benefits but supplies no measurement dataset. |
| V-05 | UART 9600 bps, 8N1 and Transparent Mode 0 are the configured settings. | Inspect firmware configuration and module settings. | RECORDED IN ADR; CONFIGURATION ARTIFACT NOT SUPPLIED | ADR-001 specifies these settings. |

## 7. Human Review

- **What appears useful:** The Wi-Fi proposal gave the team an initial architecture to evaluate. The audit log records that the team considered actual outdoor range and battery behaviour rather than accepting the suggestion without review.
- **Potential errors or unsupported assumptions:** The initial Wi-Fi recommendation did not adequately account for the reported UAV operating distance, battery constraints, or recovery from link loss. The supplied files do not include raw test logs establishing the exact range or power measurements.
- **Changes made by human reviewer:** The team rejected Wi-Fi for the remote telemetry link and selected EBYTE E32-433T20D LoRa at 433 MHz. ADR-001 records UART 9600 bps (8N1) and Transparent Mode 0.
- **Independent verification performed:** The AI Audit Log reports an outdoor test in which Wi-Fi was unstable beyond 30 m and reports faster LiPo depletion during continuous Wi-Fi operation. The detailed test procedure, instrumentation, and raw results were not supplied.

## 8. Team Decision

- **Decision:** ACCEPTED
- **Decision evidence:** `AI_Audit_Log.md` — Entry 1 records the team's decision to replace Wi-Fi with LoRa. `ADR-001-Communication-v1.1.md` records the decision as Accepted and states that it was implemented on both the UAV (ESP32) and ground station (ESP8266).
- **Participants:** NOT VERIFIED
- **Date:** Week 4 in the AI Audit Log; exact calendar date NOT VERIFIED. ADR version is v1.1; approval date is not stated.
- **Conditions and limitations:** ADR-001 notes the narrower bandwidth of the LoRa link and the need to keep payloads compact. It records a one-line JSON payload of approximately 110 bytes. The supplied files do not provide a raw throughput or range test report.

## 9. Implementation and Testing

- **Implementation status:** IMPLEMENTED (as recorded in ADR-001)
- **Test performed:** The AI Audit Log reports outdoor Wi-Fi testing and the observed instability beyond 30 m. ADR-001 states that LoRa was deployed on the UAV and ground station. A detailed LoRa test procedure is NOT PROVIDED.
- **Observed result:** Wi-Fi was reported as unstable beyond 30 m and as consuming battery during continuous operation. No numerical LoRa range, packet delivery, or latency result is recorded in the supplied files.
- **Test artifact:** No raw test log, source-code revision, telemetry capture, or measurement dataset was supplied. The available records are `AI_Audit_Log.md` and `ADR-001-Communication-v1.1.md`.
- **Limitations:** The decision and deployment status are recorded, but quantitative evidence of LoRa performance is absent from the supplied materials.

## 10. Follow-up Actions

| Action | Owner | Due date | Status |
|---|---|---|---|
| Preserve raw Wi-Fi and LoRa range / packet-delivery test results. | NOT ASSIGNED | NOT SET | OPEN |
| Preserve the firmware and E32 configuration showing UART 9600 bps, 8N1 and Transparent Mode 0. | NOT ASSIGNED | NOT SET | OPEN |
| Record measured telemetry performance under representative UAV operating conditions. | NOT ASSIGNED | NOT SET | OPEN |

## 11. Provenance and Revision History

- **Prepared on:** 2026-11-16
- **Source fidelity:** SUMMARY / RECONSTRUCTED
- **Reviewer:** NOT VERIFIED
- **Revision notes:** Prepared from the original AI Audit Log and cross-checked against ADR-001. The prompt and AI response are summaries because verbatim interaction records were not supplied. No quantitative LoRa performance results have been invented.

---
**Integrity rule:** This entry documents AI assistance and human review; it does not itself prove technical correctness, team approval, implementation, or experimental success.
