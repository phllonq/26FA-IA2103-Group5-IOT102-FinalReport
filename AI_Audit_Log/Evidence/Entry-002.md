# AI Audit Entry 002 — Dual-I2C Sensor Architecture

## 1. Entry Metadata

- **Entry ID:** ENTRY-002
- **Evidence ID:** EV-002
- **Date and time:** Week 5 (as labelled in the original AI Audit Log's hardware-selection entry; exact date/time not recorded)
- **AI tool and model:** NOT VERIFIED
- **Human operator:** NOT VERIFIED (the source identifies Group 5, Class IA2103, not the individual operator)
- **Interaction type:** PROMPT / RESPONSE / REVIEW / DECISION (interaction details reconstructed from the available records)
- **Evidence classification:** PARTIALLY VERIFIED; AI interaction details NOT VERIFIED
- **Source location:** `AI_Audit_Log.md` — Entry 2; `ADR-002-Dual_I2C-v1.0.md`

## 2. Objective

Record the available evidence about hardware selection and sensor-bus design for the two BMP280 sensors mounted on the UAV. The original AI Audit Log's Entry 2 concerns battery power regulation and records an AI recommendation to connect a 3S LiPo directly to ESP32 VIN, followed by the team's reported Mini 360 buck-converter decision. The additional ADR-002 file documents a separate engineering decision: using two independent I2C buses to connect two BMP280 sensors with the same default I2C address.

These are related hardware-design topics but are distinct decisions. ADR-002 does not verify the Mini 360 power-supply decision, and the supplied records do not establish that the AI proposed the Dual-I2C architecture.

## 3. Project Context Supplied to the AI

The project is an IOT102 Fall 2026 UAV environmental-monitoring system. The hardware described in the records includes an ESP32 DevKit V1, a 3S LiPo battery, an EBYTE E32 LoRa module, and two BMP280 sensors on the UAV.

The original AI Audit Log records a power-management concern: a fully charged 3S LiPo is approximately 12.6 V, and the team was concerned about heating of the ESP32 board's AMS1117-3.3 regulator and the LoRa module's maximum input voltage. ADR-002 separately explains that both BMP280 modules use the default I2C address `0x76`, creating an address collision if both are connected to the same bus.

## 4. Prompt or Input

**RECONSTRUCTED SUMMARY — not a verbatim prompt.** The original AI Audit Log indicates that AI assistance was used for hardware selection and power management, specifically whether a 3S LiPo could be connected directly to ESP32 DevKit V1 VIN. The exact prompt is not preserved.

No prompt or AI interaction about Dual-I2C is preserved in the supplied files. ADR-002 is an engineering decision record, not evidence of an AI prompt.

## 5. AI Output

**SUMMARY — original AI response not preserved verbatim.** The original AI Audit Log records that the AI suggested connecting the positive terminal of a 3S LiPo battery (approximately 12.6 V when fully charged) directly to the ESP32 DevKit V1 `VIN`, on the stated basis that the board regulator could tolerate up to 15 V.

The supplied files do not preserve the full AI response, cited datasheet, or any AI-generated recommendation about the Dual-I2C arrangement.

## 6. Claims and Recommendations Requiring Verification

| ID | Claim or recommendation | Verification method / source | Status | Notes |
|---|---|---|---|---|
| V-01 | A 3S LiPo at approximately 12.6 V can be connected directly to the ESP32 DevKit V1 VIN for this load. | Check the exact board schematic, regulator datasheet, thermal dissipation, input conditions and measured load. | NOT ACCEPTED BY TEAM / NOT INDEPENDENTLY VERIFIED HERE | The AI Audit Log reports that the team considered regulator heating and thermal shutdown risk. |
| V-02 | The ESP32 board's AMS1117-3.3 regulator may overheat under the stated input and radio load. | Verify the exact regulator fitted, its datasheet, thermal design and temperature under measured operating conditions. | REPORTED AS TEAM REVIEW; RAW EVIDENCE NOT SUPPLIED | The audit log describes a datasheet check but does not include the datasheet or temperature measurements. |
| V-03 | The Mini 360 buck converter was adjusted to 5.0 V for the ESP32 and E32 module. | Inspect the actual power circuit, measured output under load, and hardware test record. | RECORDED IN AI AUDIT LOG; NOT CORROBORATED BY THE FOUR ADR FILES | ADR-002 concerns I2C, not power regulation. |
| V-04 | Both BMP280 modules have default I2C address `0x76`, so a shared bus would cause an address conflict. | Inspect module configuration / datasheets and verify addresses on the assembled system. | RECORDED IN ADR-002 | ADR-002 describes this as the design constraint. |
| V-05 | ESP32 uses two independent I2C buses: `Wire` on GPIO 21/22 and `Wire1` on GPIO 18/19. | Inspect wiring and firmware initialization; run separate sensor-read tests. | ACCEPTED / IMPLEMENTED AS RECORDED IN ADR-002 | ADR-002 states the design was approved and physically soldered on ESP32 DevKit V1. |
| V-06 | Dual-I2C provides fault isolation if one sensor or bus fails. | Disconnect or fault one sensor/bus and observe whether the other bus continues reading. | RATIONALE RECORDED; TEST RESULT NOT PROVIDED | ADR-002 describes this as a benefit, but no fault-injection test artifact is supplied. |

## 7. Human Review

- **What appears useful:** The original audit log records a human review of the direct-battery-power suggestion. ADR-002 provides a concrete hardware rationale for separating two BMP280 sensors whose default I2C addresses are identical.
- **Potential errors or unsupported assumptions:** The AI's stated 15 V regulator-tolerance claim should not be treated as sufficient proof that direct 3S LiPo input is thermally safe under the actual load. The supplied records do not include the exact board schematic or thermal measurements. Also, ADR-002 must not be interpreted as proof that AI suggested Dual-I2C.
- **Changes made by human reviewer:** The original AI Audit Log records the team's decision to add a Mini 360 buck converter adjusted to 5.0 V and a 100 kΩ / 33 kΩ voltage-divider branch for battery monitoring. ADR-002 separately records the decision to use two I2C buses: `Wire` (GPIO 21 SDA, GPIO 22 SCL) for BMP280 #1 and `Wire1` (GPIO 18 SDA, GPIO 19 SCL) for BMP280 #2.
- **Independent verification performed:** The original audit log says the team consulted the AMS1117-3.3 datasheet. ADR-002 records the address-collision rationale and physical implementation. The actual datasheet copy, circuit measurements, wiring photos, and sensor test logs were not supplied.

## 8. Team Decision

- **Decision:** ACCEPTED for the Dual-I2C architecture as recorded in ADR-002. The Mini 360 power decision is RECORDED in the AI Audit Log but is NOT VERIFIED by the supplied ADRs.
- **Decision evidence:** `ADR-002-Dual_I2C-v1.0.md` records Accepted status and states that the Dual-I2C design was physically soldered on ESP32 DevKit V1. `AI_Audit_Log.md` — Entry 2 records the Mini 360 and voltage-divider decision.
- **Participants:** NOT VERIFIED
- **Date:** ADR-002 version v1.0; approval date NOT VERIFIED. The original power-management entry is labelled Week 5; exact calendar date NOT VERIFIED.
- **Conditions and limitations:** Dual-I2C uses two additional GPIO pins. The ADR describes fault isolation as a benefit, but no fault-injection test evidence was supplied. The power-regulation decision remains separate and requires its own circuit/test evidence.

## 9. Implementation and Testing

- **Implementation status:** Dual-I2C: IMPLEMENTED AS RECORDED IN ADR-002. Mini 360 power branch: NOT VERIFIED by the supplied ADRs.
- **Test performed:** ADR-002 states that the Dual-I2C circuit was physically soldered on ESP32 DevKit V1. Specific sensor-read, bus-isolation, or fault-injection test procedures are NOT PROVIDED. The original audit log reports a datasheet review for the power issue but does not provide the underlying artifact.
- **Observed result:** No measured sensor-read reliability, bus-isolation result, regulator temperature, or power-rail stability data is included in the supplied files.
- **Test artifact:** `ADR-002-Dual_I2C-v1.0.md` and `AI_Audit_Log.md`. No firmware source, wiring photograph, oscilloscope capture, multimeter log, or raw test dataset was supplied.
- **Limitations:** The ADR supports the decision and implementation status as documented by the team; it does not independently establish measured performance. The Dual-I2C decision is not to be conflated with the Mini 360 power decision.

## 10. Follow-up Actions

| Action | Owner | Due date | Status |
|---|---|---|---|
| Preserve the circuit diagram and wiring photographs for the Mini 360, ESP32, E32 and battery-divider branch. | NOT ASSIGNED | NOT SET | OPEN |
| Record the exact buck-converter output under operating load. | NOT ASSIGNED | NOT SET | OPEN |
| Preserve firmware and sensor-read results for both I2C buses. | NOT ASSIGNED | NOT SET | OPEN |
| Perform and record a one-bus / one-sensor fault-isolation test if required for project validation. | NOT ASSIGNED | NOT SET | OPEN |

## 11. Provenance and Revision History

- **Prepared on:** 2026-11-16
- **Source fidelity:** SUMMARY / RECONSTRUCTED
- **Reviewer:** NOT VERIFIED
- **Revision notes:** This entry deliberately distinguishes the original AI Audit Log's power-management topic from ADR-002's Dual-I2C architecture. ADR-002 is used as evidence for the Dual-I2C decision only; it is not used to claim that AI proposed that architecture or to validate the Mini 360 circuit.

---
**Integrity rule:** This entry documents AI assistance and human review; it does not itself prove technical correctness, team approval, implementation, or experimental success.
