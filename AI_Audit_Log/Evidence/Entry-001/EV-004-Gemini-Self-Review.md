# EV-004 — Gemini Technical Self-Review and Architecture Revision

**Project:** UAV Environmental Monitoring System  
**Course:** IOT102 — Fall 2026  
**Audit Entry:** ENTRY-001  
**Evidence ID:** EV-004  
**AI Tool:** Google Gemini  
**Interaction Type:** Follow-up Technical Self-Review  
**Architecture Version:** Proposed v1.1  
**Evidence Status:** STRUCTURED SUMMARY OF RESPONSE SHARED IN CHAT

## 1. Purpose

After ChatGPT identified limitations in Gemini's initial architecture proposal, Gemini was asked to reconsider the engineering assumptions and propose corrections.

The follow-up focused on eight issues:

1. DHT22 sampling limits.
2. MQ-2 preheating and stabilization.
3. UAV payload assumptions.
4. Main battery versus auxiliary battery.
5. ESP-NOW/LoRa versus direct Wi-Fi.
6. ESP32 ADC input protection.
7. Doppler effect in low-speed UAV communication.
8. Confirmed requirements versus optional features.

## 2. Follow-up Prompt

The Gemini follow-up requested a technical self-review of the initial architecture.

For each issue, Gemini was asked to provide:

- Original Claim.
- Technical Assessment.
- Error or Limitation.
- Corrected Recommendation.
- Supporting Source.
- Confidence Level.
- Required Team Verification.

The request also asked for a revised architecture and a list of decisions requiring team approval.

The exact follow-up prompt must be preserved separately or inserted here from the original Gemini conversation before this document is described as a complete verbatim transcript.

## 3. Summary of Revised Recommendations

### 3.1 DHT22 and Task Scheduling

Gemini recognized that the earlier one-second warning-state sampling example was inconsistent with DHT22 timing constraints.

It proposed separating:

- Sensor polling.
- FSM evaluation.
- MQTT publishing.

The revised example used DHT22 polling no faster than approximately every two seconds, FSM evaluation every 500 ms, and state-dependent MQTT publishing.

**Review assessment:** The separation is technically reasonable. Exact scheduling parameters remain unapproved.

### 3.2 MQ-2 Preheating

Gemini distinguished initial preheating, short-term warm-up, and sensor stabilization.

It suggested extended initial preheating and a short warm-up before operation.

**Review assessment:** The distinction is useful, but specific durations require verification against the exact sensor datasheet and actual stabilization behavior.

### 3.3 UAV Payload

Gemini withdrew the claim that 150–200 g is a universally safe payload limit.

It recognized that allowable payload depends on the actual UAV configuration.

**Review assessment:** Correct direction. No payload limit has been approved.

### 3.4 Power Architecture

Gemini compared a separate battery with a regulated supply derived from the main UAV battery.

It recognized trade-offs involving mass, power availability, noise, and operational complexity.

**Review assessment:** A separate battery cannot be assumed to provide absolutely noise-free measurements. The final choice requires electrical design and testing.

### 3.5 Wireless Communication

Gemini clarified that ESP-NOW and LoRa do not automatically outperform Wi-Fi under all operating conditions.

It maintained its recommendation for direct Wi-Fi + MQTT during initial prototype development.

**Review assessment:** Suitable as a prototype candidate. Any fixed distance threshold for changing communication technology remains unsupported.

### 3.6 ESP32 ADC Protection

Gemini proposed adding voltage division and input protection for analog sensor connections.

**Review assessment:** Protection is necessary where sensor output levels can exceed permitted input limits. Specific component values and clamping designs must be calculated and verified.

### 3.7 Doppler Effect

Gemini reduced the priority of Doppler shift for low-speed UAV operation.

It emphasized path loss, antenna orientation, interference, and obstruction.

**Review assessment:** More appropriate risk prioritization for the proposed prototype.

### 3.8 Project Scope

Gemini distinguished the core environmental sensing and MQTT communication functions from optional GPS and microSD features.

**Review assessment:** Appropriate scope management. The team has not yet formally approved inclusion or exclusion of optional features.

## 4. Architecture v1.1 — Proposed Data Flow

The revised proposal can be summarized as:

Environmental Sensors → ESP32 Sensor Polling → Latest Data Storage → FSM Evaluation → MQTT Publishing → Wi-Fi Access Point → Mosquitto Broker → MQTT Explorer

The design also proposed:

- Analog input voltage conditioning.
- Stable power regulation.
- Consideration of power filtering.
- Independent scheduling for sensor reading and reporting.
- Further testing before UAV integration.

These remain design recommendations, not completed hardware implementations.

## 5. Comparison of Initial and Revised Responses

| Issue | Initial Proposal | Revised Proposal | Final Status |
|---|---|---|---|
| DHT22 timing | Warning sampling example at 1 s | Sensor-specific polling | PENDING IMPLEMENTATION |
| MQ-2 | Short warm-up estimate | Distinguish preheating and stabilization | PENDING DATASHEET CHECK |
| Payload | 150–200 g estimate | UAV-dependent payload analysis | PENDING |
| Power | Prefer auxiliary battery | Compare auxiliary battery and regulated main supply | PENDING |
| Wireless | General reliability advantage for alternatives | Context-dependent comparison | WI-FI + MQTT ACCEPTED IN PRINCIPLE |
| ADC | Incomplete protection | Add voltage conditioning and protection | PENDING DESIGN |
| Doppler | Included as significant risk | Lower priority at low speed | REVIEWED |
| GPS / microSD | Added as possible requirements | Treat as optional candidates | PENDING SCOPE DECISION |

## 6. Remaining Technical Uncertainties

The revised architecture did not resolve:

- Exact ESP32 board model and GPIO assignments.
- MQ-2 manufacturer, preheating conditions, and calibration procedure.
- ADC voltage-divider and protection circuit values.
- Power supply capacity and noise performance.
- UAV payload capability.
- FSM states and transition thresholds.
- MQTT QoS, publishing frequency, and reconnect strategy.
- Wireless coverage and message reliability during flight.

## 7. Review Outcome

The second Gemini response improved the clarity of the architecture and corrected several assumptions.

However, it still contained claims requiring independent verification.

The team subsequently accepted direct Wi-Fi + MQTT in principle for the prototype, without approving all other proposed hardware and firmware details.

## 8. Evidence Integrity

This document is a structured record of the follow-up Gemini response supplied during the project discussion.

It is not the complete verbatim Gemini transcript.

The original response should be archived separately or appended unchanged before final submission if the assessment requires full prompt-response evidence.

**Related Evidence:**

- [EV-002 — Initial Gemini Response](EV-002-Gemini-Response.md)
- [EV-003 — ChatGPT Technical Review](EV-003-ChatGPT-Review.md)
- [EV-005 — Team Decision](EV-005-Team-Decision.md)
