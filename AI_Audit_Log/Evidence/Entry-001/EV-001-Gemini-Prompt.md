# EV-001 — Gemini Architecture Analysis Prompt

**Project:** UAV Environmental Monitoring System  
**Course:** IOT102 — Fall 2026  
**Audit Entry:** ENTRY-001  
**Evidence ID:** EV-001  
**AI Tool:** Google Gemini  
**Interaction Type:** Initial Architecture Analysis  
**Project Stage:** Research and System Design  
**Evidence Status:** PROMPT RECONSTRUCTION — ORIGINAL TRANSCRIPT REQUIRES VERIFICATION
**Interaction Date:** [RECONSTRUCTED / APPROXIMATE: 2026-09-22 — verify against original Gemini history]

## 1. Purpose

The purpose of this AI interaction was to obtain an initial engineering assessment of the proposed UAV environmental monitoring system before hardware implementation.

The team needed support in evaluating system architecture, wireless communication options, hardware limitations, technical risks, and verification requirements.

AI was used as an engineering analysis assistant, not as the final decision-maker.

## 2. Project Context

The proposed system consists of:

| Component | Intended Function |
|---|---|
| ESP32 | Main IoT processing and communication unit |
| DHT22 | Temperature and humidity measurement |
| MQ-2 | Relative gas/smoke sensing |
| YL-83 / FC-37 | Rain or surface wetness detection |
| Wi-Fi | Wireless communication |
| MQTT | Telemetry messaging |
| Mosquitto | MQTT broker |
| MQTT Explorer | Ground-station monitoring |
| PlatformIO | Firmware development environment |
| Multirotor UAV | Mobile sensor-carrying platform |

The project also proposes an event-based Finite State Machine (FSM) for adaptive sampling or reporting.

At the time of the analysis, the team was still researching and designing the system. Hardware assembly, integrated testing, and UAV flight testing were not established as completed.

## 3. Prompt Content

The following is a reconstructed description of the engineering request used in this workflow. It is **not certified as the exact original Gemini prompt**.

The engineering request asked Gemini to act as a Senior Embedded Systems Engineer, IoT System Architect, and Academic Research Supervisor and analyze the proposed UAV environmental monitoring architecture.

The requested outputs included:

1. A functional and non-functional requirements table.
2. A comparison of at least two possible system or communication architectures.
3. A recommended system block diagram.
4. An engineering risk register covering sensor limitations, electrical interfaces, power, electromagnetic interference, and wireless communication.
5. Open technical questions requiring team decisions.
6. A verification plan suitable for the pre-implementation stage.
7. A decision checklist for the student team.

The analysis was to consider ESP32, DHT22, MQ-2, YL-83/FC-37, Wi-Fi, MQTT, Mosquitto, and a multirotor UAV.

The response was not to assume that the hardware had already been assembled or tested.

## 4. Original Prompt Verification

**Original Gemini prompt:** NOT YET ARCHIVED VERBATIM.

Before treating this file as a complete primary-source record, the team must compare this reconstruction with the original Gemini conversation and replace Section 3 with the exact submitted prompt.

The original conversation URL, if available, should also be preserved.

## 5. Expected Output

The requested output was an architecture analysis containing technical alternatives, risks, recommendations, and unresolved decisions.

The AI was not authorized to claim that the system had passed hardware or flight testing.

## 6. Evidence Integrity

This file documents the purpose and known scope of the interaction.

A reconstructed prompt is not equivalent to an original prompt transcript. The team must not present this reconstruction as a verbatim historical record.

**Related Evidence:** [EV-002 — Gemini Response](EV-002-Gemini-Response.md)
