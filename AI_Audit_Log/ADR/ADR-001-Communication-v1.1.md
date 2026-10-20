# ADR-001 — UAV Communication Architecture

**Project:** UAV Environmental Monitoring System  
**Course:** IOT102 — Fall 2026  
**Document ID:** ADR-001  
**Version:** 1.1  
**Decision Date:** 2026-09-22  
**Status:** ACCEPTED IN PRINCIPLE — PROTOTYPE ONLY  
**Implementation Status:** NOT IMPLEMENTED  
**Decision Authority:** Project Team  

---

## 1. Context

The project aims to develop a UAV-based environmental monitoring system using an ESP32 microcontroller and environmental sensors.

The planned sensor configuration includes:

- **DHT22:** Temperature and humidity measurement.
- **MQ-2:** Relative gas/smoke indication.
- **YL-83 / FC-37:** Rain or surface wetness detection.

The planned communication and monitoring components include:

- ESP32 Wi-Fi connectivity.
- MQTT messaging protocol.
- Mosquitto MQTT broker.
- MQTT Explorer or a monitoring dashboard.
- PlatformIO for firmware development.

The team is currently in the research, component selection, and system design stage. Hardware integration, communication performance testing, and UAV flight testing have not been confirmed as completed.

The team evaluated direct Wi-Fi + MQTT and an alternative architecture using ESP-NOW or LoRa with an additional receiver or gateway.

The purpose of this ADR is to record the team's communication architecture decision and distinguish it from unresolved engineering questions.

## 2. Decision

On 2026-09-22, the team agreed in principle to use **direct Wi-Fi + MQTT as the communication architecture for the initial prototype**.

The proposed communication flow is:

```text
Environmental Sensors
        |
        v
      ESP32
        |
        v
   Wi-Fi Network
        |
        v
 Mosquitto MQTT Broker
        |
        v
 MQTT Explorer / Dashboard
```

The ESP32 is intended to collect sensor readings, process the relevant data, and publish telemetry through MQTT over Wi-Fi.

The Mosquitto broker is intended to receive and distribute MQTT messages to a monitoring client.

This decision applies to the initial prototype only. It does not establish that the system has achieved reliable wireless communication during UAV flight.

## 3. Decision Rationale

The team accepted this architecture in principle for the following reasons.

### 3.1 Reduced Initial Complexity

Direct Wi-Fi avoids the need to develop an additional ESP-NOW or LoRa receiver gateway for the initial prototype.

### 3.2 Compatibility with ESP32

The ESP32 provides integrated Wi-Fi connectivity, making it suitable for exploring direct wireless telemetry.

### 3.3 MQTT Integration

MQTT supports a publisher-broker-subscriber communication model. The planned Mosquitto broker and MQTT Explorer workflow can be used to inspect messages during development.

### 3.4 Incremental Development

The communication pipeline can be developed and evaluated through bench testing before integration with the UAV platform.

These reasons represent architectural considerations. They are not experimentally verified performance results.

## 4. Alternatives Considered

### Alternative A — Direct Wi-Fi + MQTT

**Status:** ACCEPTED IN PRINCIPLE FOR THE INITIAL PROTOTYPE

Proposed flow:

ESP32 → Wi-Fi Access Point → Mosquitto Broker → MQTT Explorer / Dashboard

**Potential advantages:**

- Relatively simple initial architecture.
- Uses the ESP32's integrated Wi-Fi capability.
- Compatible with the planned MQTT monitoring tools.
- Does not require a dedicated wireless receiver gateway.
- Allows communication testing independently of UAV flight.

**Limitations and risks:**

- Communication depends on Wi-Fi coverage and network availability.
- Interference, obstructions, and signal attenuation may affect connectivity.
- Packet loss, latency, and reconnection behavior have not been measured.
- Reliable communication during flight has not been demonstrated.

### Alternative B — ESP-NOW or LoRa with a Gateway

**Status:** NOT SELECTED FOR THE INITIAL PROTOTYPE

Proposed flow:

ESP32 → ESP-NOW / LoRa Receiver → Gateway → MQTT Broker → Monitoring Interface

**Potential advantages:**

- Provides alternative communication options for different operational requirements.
- LoRa may be appropriate for certain low-data-rate, longer-range applications.
- ESP-NOW can support direct communication between compatible devices without a conventional Wi-Fi access point.

**Limitations and risks:**

- A receiver or gateway may be required.
- Additional hardware and integration work may increase complexity.
- Actual range, reliability, latency, and power consumption depend on the selected implementation and operating environment.

The team may reconsider this alternative if future testing shows that direct Wi-Fi + MQTT does not meet the project's operational requirements.

No experimental comparison between these alternatives has been completed.

## 5. Consequences of the Decision

### 5.1 Expected Benefits

- The initial communication architecture remains relatively simple.
- The team can test sensor data transmission and MQTT message reception in stages.
- A dedicated LoRa or ESP-NOW gateway is not required for the initial design.
- The architecture is compatible with the proposed Mosquitto and MQTT Explorer workflow.

### 5.2 Trade-offs

- The system depends on a reachable Wi-Fi network and MQTT broker.
- Wireless coverage and stability must be evaluated.
- Reconnection behavior and message handling require further design.
- Communication performance during UAV movement remains unknown.
- Power consumption must be considered alongside sensor and UAV power requirements.

## 6. Decisions and Open Issues

The team has accepted the communication architecture in principle. The following engineering issues remain unresolved.

| ID | Issue | Status |
|---|---|---|
| PD-01 | Exact ESP32 board model and GPIO assignments | PENDING |
| PD-02 | UAV frame, payload capacity, and mounting arrangement | PENDING |
| PD-03 | Main battery with regulator versus auxiliary battery | PENDING |
| PD-04 | MQ-2 analog output conditioning and ADC protection | PENDING |
| PD-05 | Sensor polling intervals | PENDING |
| PD-06 | FSM states, transition logic, and thresholds | PENDING |
| PD-07 | MQTT publishing interval, QoS, and message schema | PENDING |
| PD-08 | Wi-Fi reconnection and temporary network-loss handling | PENDING |
| PD-09 | MQTT broker deployment and ground-station network | PENDING |
| PD-10 | GPS and microSD inclusion | PENDING |
| PD-11 | Communication acceptance criteria for UAV operation | PENDING |

The proposed separation of sensor polling, FSM evaluation, and MQTT publishing is a design recommendation that still requires team approval.

Specific sampling rates, warning thresholds, and MQTT settings must not be treated as finalized decisions until reviewed and documented by the team.

## 7. Planned Verification

The following activities are planned for future implementation and testing. They have not been recorded as completed.

### Test 1 — Wi-Fi Connectivity

Connect the selected ESP32 board to the intended Wi-Fi network and record the connection result.

### Test 2 — MQTT Message Transmission

Configure the ESP32 to publish a test message to the Mosquitto broker.

### Test 3 — Message Reception

Use MQTT Explorer or an equivalent client to verify whether the test message is received.

### Test 4 — Reconnection Behavior

Interrupt Wi-Fi connectivity under controlled conditions and evaluate whether the ESP32 can reconnect and resume publishing.

### Test 5 — Communication Performance

Define a test procedure to measure message delivery, latency, and disconnection behavior under specified conditions.

### Test 6 — UAV Environment Evaluation

After bench testing and appropriate safety checks, evaluate whether the communication architecture meets the project's requirements in the intended operating environment.

Numerical acceptance thresholds must be established before the tests are conducted.

No successful test outcomes are claimed in this ADR.

## 8. Reconsideration Criteria

The team should reconsider the architecture if future evidence indicates that direct Wi-Fi + MQTT cannot satisfy the project's requirements for:

- Communication coverage.
- Message delivery reliability.
- Latency.
- Reconnection behavior.
- Power consumption.
- Operational safety.

Any change should be documented in a revised ADR, including the evidence supporting the change and the team's approval.

## 9. Evidence and Traceability

The decision is associated with the following AI Audit Log evidence files:

- [EV-001 — Gemini Architecture Analysis Prompt](../Evidence/Entry-001/EV-001-Gemini-Prompt.md)
- [EV-002 — Gemini Initial Architecture Response](../Evidence/Entry-001/EV-002-Gemini-Response.md)
- [EV-003 — ChatGPT Technical Critique](../Evidence/Entry-001/EV-003-ChatGPT-Review.md)
- [EV-004 — Gemini Technical Self-Review](../Evidence/Entry-001/EV-004-Gemini-Self-Review.md)
- [EV-005 — Team Engineering Decision](../Evidence/Entry-001/EV-005-Team-Decision.md)

These files currently contain structured records and summaries. Original prompts and AI responses should be preserved separately or inserted as verbatim transcripts where required.

## 10. Limitations

This ADR records an architectural decision, not a completed implementation.

The following claims are not established by this document:

- Successful hardware integration.
- Verified sensor accuracy.
- Confirmed communication range.
- Measured packet delivery ratio.
- Measured communication latency.
- Verified UAV flight reliability.
- Completed flight testing.

AI-generated recommendations were used as inputs to the engineering review. The team remains responsible for verifying technical claims and approving subsequent implementation decisions.

## 11. Final Decision Statement

On **2026-09-22**, the team agreed in principle to use **direct Wi-Fi + MQTT for the initial UAV environmental monitoring prototype**.

The choice is intended to support a relatively simple initial development workflow using ESP32, Wi-Fi, Mosquitto, and MQTT monitoring tools.

Operational communication reliability remains unverified. The architecture must be evaluated through future implementation and testing before any claim of reliable UAV communication can be made.

**Final Status:** ACCEPTED IN PRINCIPLE — PROTOTYPE ONLY  
**Implementation Status:** NOT IMPLEMENTED  
**Verification Status:** PENDING
