# EV-002 — Gemini Initial Architecture Analysis

**Project:** UAV Environmental Monitoring System  
**Course:** IOT102 — Fall 2026  
**Audit Entry:** ENTRY-001  
**Evidence ID:** EV-002  
**AI Tool:** Google Gemini  
**Interaction Type:** Initial Architecture Recommendation  
**Evidence Status:** RESPONSE SUMMARY VERIFIED AGAINST CONTENT SHARED IN CHAT — ORIGINAL TRANSCRIPT NOT YET ARCHIVED

## 1. Response Overview

Gemini provided an initial engineering analysis of the proposed ESP32-based UAV environmental monitoring system.

The response contained:

- System requirements.
- Communication architecture alternatives.
- A proposed block diagram.
- Engineering risks.
- Open technical questions.
- A pre-flight verification plan.
- A student-team decision checklist.

The following sections summarize the response provided by Gemini. They are not a verbatim reproduction of the entire original response.

## 2. Functional Requirements Identified

| ID | Requirement | Gemini Proposal |
|---|---|---|
| FR-01 | Temperature and humidity | Read DHT22 data |
| FR-02 | Gas detection | Use MQ-2 for relative gas/smoke sensing |
| FR-03 | Rain detection | Use YL-83/FC-37 |
| FR-04 | Adaptive operation | Use an event-driven FSM |
| FR-05 | Wireless telemetry | Use Wi-Fi and MQTT |
| FR-06 | Ground monitoring | Use Mosquitto and MQTT Explorer |
| FR-07 | Local data logging | Optional microSD |
| FR-08 | Position information | GPS to be determined |

Gemini also proposed non-functional requirements related to UAV payload weight, power stability, and electromagnetic interference.

The proposed payload limit of 150–200 g was not supported by a specific UAV configuration.

## 3. Communication Alternatives

### Alternative A — Direct Wi-Fi + MQTT

Architecture:

ESP32 → Wi-Fi Access Point → Mosquitto Broker → MQTT Explorer / Dashboard

**Advantages identified by Gemini:**

- Relatively low implementation complexity.
- Integrated Wi-Fi capability on ESP32.
- No additional radio gateway required.
- Convenient for initial bench testing.
- Compatible with existing MQTT tools.

**Limitations:**

- Dependent on Wi-Fi connectivity.
- Susceptible to interference and signal attenuation.
- Wireless reliability during flight was not demonstrated.

### Alternative B — ESP-NOW / LoRa + Gateway

Architecture:

ESP32 → ESP-NOW/LoRa Receiver → Gateway → MQTT Broker → Monitoring Interface

**Potential advantages:**

- Alternative communication approaches for different operating conditions.
- Possible benefits for particular latency, range, or power requirements.

**Limitations:**

- Additional receiver or gateway required.
- Increased hardware and integration complexity.
- Performance advantages depend on configuration and operating conditions.

## 4. Initial AI Recommendation

Gemini recommended **Alternative A: Direct Wi-Fi + MQTT** for the initial prototype.

The main reasoning was reduced complexity, ease of development, and convenient bench testing.

This recommendation was an engineering proposal rather than an experimentally verified conclusion.

## 5. Proposed Data Flow

The initial architecture used the following sequence:

1. DHT22, MQ-2, and rain sensors provide environmental readings.
2. ESP32 processes the latest readings.
3. An FSM evaluates environmental conditions.
4. ESP32 publishes telemetry using MQTT over Wi-Fi.
5. Mosquitto distributes messages to MQTT Explorer or a dashboard.

Gemini gave an example of increasing the sampling frequency during warning conditions.

However, the example did not adequately distinguish the DHT22 physical reading interval from the FSM evaluation interval and MQTT publishing interval.

## 6. Engineering Risks Identified

| Risk | Gemini's Initial Assessment | Review Requirement |
|---|---|---|
| DHT22 timing | Reading interval limitation | Separate sensor polling from reporting |
| ESP32 ADC | Analog input noise and nonlinearity | Check ADC pins and voltage limits |
| MQ-2 heater | Power consumption and warm-up | Verify manufacturer documentation |
| Rain sensor | Corrosion and unreliable wetness readings | Evaluate power switching and placement |
| UAV EMI | Interference from ESC and motors | Evaluate wiring and power filtering |
| Wi-Fi | Potential packet loss and disconnection | Define and perform wireless tests |
| Sampling versus publishing | Excessive reporting may create unnecessary traffic | Define independent scheduling |

## 7. Proposed Verification Activities

Gemini proposed the following future activities:

- Individual sensor bench testing.
- Integrated FSM testing.
- MQTT connectivity and reconnection testing.
- Power and electromagnetic interference evaluation.

These were proposed tests only.

No results, measurements, screenshots, or successful test outcomes were provided.

## 8. Limitations Identified During Review

The initial response contained assumptions requiring further investigation:

1. The DHT22 warning-state sampling example was insufficiently constrained.
2. MQ-2 warm-up duration was presented without adequate source verification.
3. UAV payload limits were estimated without a selected airframe.
4. A separate battery was recommended without a complete power trade-off.
5. Wireless reliability comparisons were generalized.
6. The ADC input protection design was incomplete.
7. Doppler effects were emphasized without demonstrating their importance at low UAV speeds.
8. Optional GPS and microSD features were introduced without confirmed project requirements.

## 9. Evidence Interpretation

Gemini's response was useful for generating architectural alternatives and identifying risks.

It did not establish the feasibility of the final hardware configuration or prove that the recommended architecture would perform reliably during flight.

The response therefore required further technical review before a team decision.

## 10. Original Transcript

The complete initial Gemini response was supplied in the project discussion and should be preserved as an unedited export from the original Gemini session.

**Verbatim transcript archived in this file:** NO — THIS DOCUMENT IS A STRUCTURED SUMMARY.

**Related Evidence:**

- [EV-001 — Gemini Prompt](EV-001-Gemini-Prompt.md)
- [EV-003 — ChatGPT Review](EV-003-ChatGPT-Review.md)
