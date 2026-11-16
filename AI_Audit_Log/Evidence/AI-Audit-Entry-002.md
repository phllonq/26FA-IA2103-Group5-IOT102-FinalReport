# AI Audit Entry — IOT102 Fall 2026

> **Record status:** RECONSTRUCTED / APPROXIMATE. The original exact timestamps and meeting records were not available. The date/time below is a proposed timeline aligned with the course week, not a verified historical timestamp. Confirm or replace it before submission.
>
> **Project:** Adaptive IoT-UAV Environmental Monitoring System with Downwash-Aware Sensing and Adaptive Communication  
> **Course / Group:** IOT102 — Group 5, IA2103  
> **AI tool:** ChatGPT  
> **Human operators:** TRAN PHI LONG; NGUYEN BAO PHUC  
> **Source location:** Reconstructed from the team's AI_Audit_Log.md; no original conversation permalink available.

## 1. Entry Metadata

- **Entry ID:** ENTRY-002
- **Evidence ID:** EV-002
- **Date and time:** 2026-10-08, 20:00 (proposed; reconstructed)
- **AI tool and model:** ChatGPT
- **Human operator:** TRAN PHI LONG; NGUYEN BAO PHUC
- **Interaction type:** PROMPT / RESPONSE / REVIEW / DECISION
- **Evidence classification:** RECONSTRUCTED / APPROXIMATE
- **Source location:** Team AI audit summary; original prompt and conversation link not preserved.

## 2. Objective

Review the UAV electronics power arrangement for the ESP32 and LoRa E32 module.

## 3. Project Context Supplied to the AI

The UAV uses a 3-cell LiPo battery. The electronics include an ESP32 DevKit V1 and an EBYTE E32 LoRa module. The team needs a stable supply and must avoid damaging components or causing resets during radio transmission.

## 4. Prompt or Input

**RECONSTRUCTED SUMMARY — not a verbatim prompt:** Ask ChatGPT whether the ESP32 and LoRa module can be powered directly from a 3S LiPo battery, and request a safe power arrangement.

## 5. AI Output

**SUMMARY:** ChatGPT suggested a direct battery-to-VIN connection based on a presumed regulator input limit. This recommendation required checking against the exact development-board regulator and the LoRa module's supply specification.

## 6. Claims and Recommendations Requiring Verification

| ID | Claim or recommendation | Verification method / source | Status | Notes |
|---|---|---|---|---|
| V-01 | ESP32 board VIN can safely accept the fully charged 3S LiPo voltage under the intended load | Identify the exact board regulator and check its datasheet/thermal limits | NOT VERIFIED | Board variants differ; do not rely on a generic VIN rating. |
| V-02 | E32 module can accept the battery voltage directly | EBYTE E32-433T20D datasheet | REJECTED | Team summary records a module supply limit of approximately 5.2 V; verify against the exact module revision. |
| V-03 | A buck converter can provide a regulated 5.0 V rail | Measure output under load and during radio transmission | PENDING VERIFICATION | Record measured voltage, current, and temperature if tested. |

## 7. Human Review

- **What appears useful:** The AI raised the need to consider the board's input voltage and regulator.
- **Potential errors or unsupported assumptions:** A regulator's nominal maximum input voltage alone does not establish safe operation at high current; thermal dissipation and the exact board design matter. The LoRa module must not be connected directly to a 3S battery.
- **Changes made by human reviewer:** The team audit summary records adding a Mini-360 DC-DC buck converter adjusted to 5.0 V and a 100 kΩ / 33 kΩ voltage-divider branch for battery monitoring.
- **Independent verification performed:** The source summary says the team consulted the AMS1117-3.3 and LoRa module specifications. Datasheet copies and bench measurements were not attached to this entry.

## 8. Team Decision

- **Decision:** REPORTED IN TEAM AUDIT SUMMARY
- **Decision evidence:** AI_Audit_Log.md, Entry 2. Original meeting minutes or approval record not available.
- **Participants:** TRAN PHI LONG; NGUYEN BAO PHUC
- **Date:** 2026-10-08 (proposed; reconstructed)
- **Conditions and limitations:** Confirm the exact ESP32 board revision, buck-converter rating, wiring, and voltage measurements before final submission.

## 9. Implementation and Testing

- **Implementation status:** REPORTED IN TEAM AUDIT SUMMARY; not independently verified in this file.
- **Test performed:** Power-rail adjustment is described in the source summary; detailed test procedure is not preserved.
- **Observed result:** No measured voltage-under-load, current, ripple, or temperature result is recorded in the supplied source.
- **Test artifact:** Add a wiring photograph, multimeter readings, and the exact datasheets if available.
- **Limitations:** Do not claim stable operation or successful battery monitoring without corresponding test evidence.

## 10. Follow-up Actions

| Action | Owner | Due date | Status |
|---|---|---|---|
| Confirm exact ESP32 and E32 module datasheets | TRAN PHI LONG; NGUYEN BAO PHUC | 2026-11-18 | OPEN |
| Attach power wiring photo and measured 5.0 V rail evidence | TRAN PHI LONG; NGUYEN BAO PHUC | 2026-11-19 | OPEN |

## 11. Provenance and Revision History

- **Prepared on:** 2026-11-16
- **Source fidelity:** RECONSTRUCTED
- **Reviewer:** TRAN PHI LONG; NGUYEN BAO PHUC
- **Revision notes:** Structured from Entry 2 of AI_Audit_Log.md. Date, time, operator attribution, and test details are reconstructed and require team confirmation.
