# EV-003 — ChatGPT Technical Critique

**Project:** UAV Environmental Monitoring System  
**Course:** IOT102 — Fall 2026  
**Audit Entry:** ENTRY-001  
**Evidence ID:** EV-003  
**AI Tool:** ChatGPT  
**Interaction Type:** Independent AI-Assisted Technical Review  
**Review Target:** Gemini Initial Architecture Analysis  
**Evidence Status:** REVIEW SUMMARY BASED ON ACTUAL CHAT INTERACTION

## 1. Review Objective

The purpose of this interaction was to critically examine Gemini's initial architecture proposal rather than accept it without verification.

ChatGPT was used to identify inconsistencies, unsupported assumptions, and technical risks that required additional investigation.

This was a second AI-assisted review, not independent laboratory validation.

## 2. Review Input

The user submitted Gemini's initial architecture report to ChatGPT and requested an assessment.

The report included requirements, communication alternatives, an architecture diagram, engineering risks, verification plans, and a decision checklist.

The original Gemini response is documented in EV-002.

## 3. ChatGPT Review Summary

ChatGPT assessed the initial response as a useful starting point but identified several engineering limitations.

### R-01 — DHT22 Sampling Interval

**Observation:** Gemini proposed increasing the sampling frequency to once per second during warning conditions.

**Issue:** DHT22 has a minimum reading interval around two seconds, making an unrestricted one-second sensor polling recommendation unsuitable.

**Recommendation:** Separate sensor polling, FSM evaluation, and MQTT publishing.

**Status:** TECHNICAL CORRECTION PROPOSED.

### R-02 — MQ-2 Preheating and Stabilization

**Observation:** Gemini described a short warm-up interval.

**Issue:** The stated duration was not adequately supported by the specific sensor manufacturer's documentation.

**Recommendation:** Distinguish initial preheating, short-term warm-up, and stabilization; verify the exact sensor documentation.

**Status:** DATASHEET VERIFICATION REQUIRED.

### R-03 — UAV Payload Assumptions

**Observation:** Gemini proposed a payload target of approximately 150–200 g.

**Issue:** The team had not established the actual UAV frame, motor configuration, maximum takeoff weight, or payload capacity.

**Recommendation:** Avoid a fixed payload limit until the selected UAV configuration has been evaluated.

**Status:** PENDING UAV CONFIGURATION.

### R-04 — Power Supply Architecture

**Observation:** Gemini initially favored a separate battery.

**Issue:** A separate battery adds weight and operational complexity; a regulated supply from the main UAV battery may also be feasible.

**Recommendation:** Compare regulated main-battery power and an independent battery using current requirements, mass, electrical noise, and safety.

**Status:** PENDING POWER DESIGN.

### R-05 — Wireless Reliability

**Observation:** Gemini suggested that ESP-NOW or LoRa would provide better reliability.

**Issue:** Reliability depends on range, interference, antenna configuration, protocol, and environmental conditions.

**Recommendation:** Avoid universal claims. Evaluate direct Wi-Fi + MQTT for the prototype and reconsider alternatives based on future test results.

**Status:** ARCHITECTURAL COMPARISON REQUIRED.

### R-06 — ESP32 ADC Protection

**Observation:** The initial architecture did not sufficiently describe the electrical interface between analog sensors and ESP32.

**Issue:** Some sensor modules may produce signals above the ESP32 GPIO voltage limits.

**Recommendation:** Verify analog output levels, voltage division, suitable ADC1 pin selection when Wi-Fi is enabled, and appropriate protection circuitry.

**Status:** ELECTRICAL DESIGN REQUIRED.

### R-07 — Doppler Effect

**Observation:** Gemini included Doppler shift among major wireless communication risks.

**Issue:** At low UAV speeds, Doppler shift at 2.4 GHz is generally much less significant than path loss, interference, antenna orientation, and obstruction.

**Recommendation:** Prioritize more relevant wireless risks.

**Status:** RISK PRIORITY CORRECTION PROPOSED.

### R-08 — Project Scope

**Observation:** Gemini introduced GPS, microSD, and a fixed payload limit.

**Issue:** These features or limits had not been established as approved project requirements.

**Recommendation:** Distinguish confirmed project scope from optional AI-generated suggestions.

**Status:** SCOPE CONFIRMATION REQUIRED.

## 4. Review Conclusion

ChatGPT recommended retaining direct Wi-Fi + MQTT as a candidate prototype architecture while requesting a technical self-review from Gemini.

The initial architecture was not considered ready for final hardware approval.

The review did not verify the system through physical testing.

## 5. Follow-up Action

A follow-up request was prepared for Gemini to reconsider the eight identified issues and produce a revised architecture.

The resulting Gemini response is documented in EV-004.

## 6. Limitations of This Review

ChatGPT is also an AI system and may generate inaccurate technical claims.

Its critique must therefore be treated as an additional source of analysis, not as proof that the proposed corrections are technically correct.

Final responsibility for engineering decisions remains with the student team.

## 7. Evidence References

- [EV-001 — Initial Prompt](EV-001-Gemini-Prompt.md)
- [EV-002 — Gemini Initial Response](EV-002-Gemini-Response.md)
- [EV-004 — Gemini Self-Review](EV-004-Gemini-Self-Review.md)

**Original ChatGPT transcript:** Available in the conversation history; complete transcript export not yet attached.
