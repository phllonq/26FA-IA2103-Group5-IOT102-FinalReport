# EV-005 — Team Engineering Decision Record

**Project:** UAV Environmental Monitoring System  
**Course:** IOT102 — Fall 2026  
**Audit Entry:** ENTRY-001  
**Evidence ID:** EV-005  
**Decision Topic:** Communication Architecture Selection  
**Decision Status:** ACCEPTED IN PRINCIPLE  
**Implementation Status:** NOT IMPLEMENTED  
**Decision Date:** 2026-09-22 
**Related ADR:** [ADR-001 v1.1](../../ADR/ADR-001-Communication-v1.1.md)

## 1. Decision Context

The team is currently conducting research, selecting components, and designing an IoT-based UAV environmental monitoring system.

The proposed system includes ESP32, DHT22, MQ-2, a rain sensor, and an MQTT-based ground monitoring workflow.

During architecture analysis, Gemini proposed direct Wi-Fi + MQTT and an alternative communication architecture using ESP-NOW or LoRa with an additional gateway.

ChatGPT was subsequently used to critically review Gemini's initial technical assumptions. Gemini then produced a revised architecture after receiving a follow-up request.

The team considered the architecture alternatives and communicated its agreement in principle with direct Wi-Fi + MQTT for the initial prototype.

## 2. Confirmed Decision

**Decision ID:** DEC-001

**Decision:** Use direct Wi-Fi + MQTT as the intended communication architecture for the initial prototype.

**Decision Status:** ACCEPTED IN PRINCIPLE.

**Proposed Communication Flow:**

ESP32 → Wi-Fi Access Point → Mosquitto MQTT Broker → MQTT Explorer / Monitoring Interface

This decision is limited to the initial prototype.

It does not imply that the system has already achieved reliable telemetry transmission during UAV operation.

## 3. Decision Rationale

The direct Wi-Fi + MQTT approach was accepted in principle because it offers a relatively simple starting architecture for prototype development.

The approach uses ESP32's integrated Wi-Fi capability and supports the planned Mosquitto and MQTT Explorer workflow.

It avoids the need for an additional wireless gateway during the initial development stage.

The architecture also allows the communication pipeline to be evaluated through bench testing before UAV integration.

These are design considerations. They are not claims of measured communication performance.

## 4. Alternatives Considered

### Alternative A — Direct Wi-Fi + MQTT

**Disposition:** ACCEPTED IN PRINCIPLE FOR PROTOTYPE.

Advantages considered:

- Reduced initial hardware complexity.
- Compatibility with ESP32 and MQTT tools.
- Suitable for staged bench testing.
- No dedicated receiver gateway required.

Remaining risks:

- Limited or variable Wi-Fi coverage.
- Possible packet loss and disconnection.
- Unknown communication reliability during flight.
- Unverified power consumption.

### Alternative B — ESP-NOW / LoRa + Gateway

**Disposition:** NOT SELECTED FOR THE INITIAL PROTOTYPE.

This alternative remains available for future evaluation if direct Wi-Fi + MQTT does not satisfy operational requirements.

No experimental comparison between the alternatives has been performed.

## 5. Human Delta

### 5.1 Critical Thinking

The team did not accept the AI recommendation as proof of system reliability.

The final acceptance was restricted to the suitability of direct Wi-Fi + MQTT as an initial prototype architecture.

The team did not approve unverified claims regarding maximum wireless range, packet delivery reliability, sensor accuracy, or flight performance.

Technical limitations identified during AI-assisted review remain subject to datasheet verification and future testing.

### 5.2 Contextualization

The decision reflects the project's current research and design stage.

The proposed system uses ESP32 and a ground-station workflow based on MQTT.

At this stage, selecting a relatively simple communication architecture allows the team to focus on establishing a working prototype before evaluating more complex wireless alternatives.

The actual operating environment, UAV configuration, and performance requirements remain to be finalized.

### 5.3 Creative Synthesis

The engineering workflow combines the initial Gemini architecture proposal with the technical objections raised during ChatGPT review and Gemini's subsequent revisions.

The resulting approach is to begin with direct Wi-Fi + MQTT, verify its performance during later development, and reconsider alternative communication technologies if necessary.

The team has not yet approved the proposed sensor polling, FSM scheduling, or MQTT publishing parameters.

### 5.4 Decision Ownership

The team explicitly confirmed its agreement in principle with direct Wi-Fi + MQTT for the initial prototype.

The final decision belongs to the team, not to Gemini or ChatGPT.

Other recommendations remain open for team review.

The date, participant list, and formal approval record should be added from actual team records.

## 6. Decision Status Matrix

| Decision ID | Engineering Decision | Status |
|---|---|---|
| DEC-001 | Direct Wi-Fi + MQTT for initial prototype | ACCEPTED IN PRINCIPLE |
| DEC-002 | Independent sensor polling, FSM, and publishing schedules | PENDING |
| DEC-003 | MQ-2 measurement and calibration strategy | PENDING |
| DEC-004 | ESP32 ADC conditioning and protection | PENDING |
| DEC-005 | Main battery with regulator versus auxiliary battery | PENDING |
| DEC-006 | UAV frame and payload capacity | PENDING |
| DEC-007 | FSM states and environmental thresholds | PENDING |
| DEC-008 | MQTT QoS, payload schema, and reconnect handling | PENDING |
| DEC-009 | GPS and microSD scope | PENDING |
| DEC-010 | Flight communication reliability requirements | PENDING |

## 7. Planned Verification

The following activities have not been reported as completed:

1. Connect ESP32 to the intended Wi-Fi network.
2. Publish a test message to Mosquitto.
3. Verify reception using MQTT Explorer.
4. Evaluate MQTT reconnect behavior after Wi-Fi interruption.
5. Measure message delivery and latency.
6. Evaluate communication under representative operating conditions.
7. Review whether the selected architecture meets the project's final requirements.

Acceptance criteria and measurement methods must be established before testing.

## 8. Evidence Traceability

| Evidence ID | Description |
|---|---|
| EV-001 | Initial Gemini architecture prompt |
| EV-002 | Gemini initial architecture analysis |
| EV-003 | ChatGPT technical critique |
| EV-004 | Gemini technical self-review |
| EV-005 | Team decision record |

## 9. Limitations

The project remains in the research and design stage.

No completed hardware integration, communication benchmark, or UAV flight test is claimed.

The team has not finalized the electrical design, firmware architecture, or environmental thresholds.

AI-generated recommendations are treated as supporting information requiring independent engineering verification.

## 10. Final Decision Statement

The team has **accepted direct Wi-Fi + MQTT in principle as the communication architecture for the initial UAV environmental monitoring prototype**.

The decision is provisional with respect to operational performance and may be revisited after implementation and testing.

All other unresolved engineering decisions remain PENDING.

**Record Status:** DECISION DOCUMENTED — SUPPORTING TEAM APPROVAL DETAILS PENDING.
