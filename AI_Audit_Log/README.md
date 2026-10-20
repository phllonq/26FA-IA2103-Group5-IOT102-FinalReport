# AI Audit Log — UAV Environmental Monitoring System

## 1. Project Information

- **Project:** UAV Environmental Monitoring System
- **Course:** IOT102 — Fall 2026, FPT University
- **Team:** Group 5 (IA2103)
- **Repository:** [26FA-IA2103-Group5-IOT102-FinalReport](https://github.com/phllonq/26FA-IA2103-Group5-IOT102-FinalReport)
- **Audit status:** DRAFT — some dates, team approval details, and project status claims require verification.

## 2. Purpose

This directory records AI assistance used during research, component selection, architecture discussion, and planning. It distinguishes AI-generated recommendations from human review, documented team decisions, and implementation or test evidence.

AI output is advisory. It is not a substitute for datasheet checks, engineering tests, or team approval.

## 3. Project Scope

The current proposed system includes:

- ESP32 as the IoT controller.
- DHT22 for temperature and humidity.
- MQ-2 for relative gas/smoke indication.
- YL-83 / FC-37 for rain or surface-wetness detection.
- Wi-Fi and MQTT for telemetry.
- Mosquitto as the planned MQTT broker.
- MQTT Explorer or a dashboard for monitoring.
- PlatformIO as the planned firmware development environment.

The exact hardware configuration, implementation progress, and testing status must be confirmed against current team records. Do not infer completed assembly, calibration, communication benchmarks, or UAV flight tests from planning documents.

## 4. Current Decision Snapshot

- **Communication architecture:** Direct Wi-Fi + MQTT is documented as a proposal for the initial prototype; team acceptance remains NOT VERIFIED.
- **Decision evidence:** See [ADR-001](ADR/ADR-001-Communication-v1.1.md) and [EV-005](Evidence/Entry-001/EV-005-Team-Decision.md).
- **Decision date and formal approval:** NOT VERIFIED against primary team records.
- **Implementation status:** NOT VERIFIED from this audit log alone; consult the team's current source code and hardware records.
- **Testing and calibration:** NOT VERIFIED from this audit log alone.

Treat the architecture decision as provisional until the team approval record and date have been checked.

## 5. Directory and File Inventory

```text
AI_Audit_Log/
├── README.md
├── AI_Audit_Log.docx (content/usability NOT VERIFIED)
├── AI_Audit_Log.pdf (content/usability NOT VERIFIED)
├── ADR/
│   └── ADR-001-Communication-v1.1.md
└── Evidence/
    ├── Entry-001/
    │   ├── Cross-File-Consistency-Report.md
        ├── EV-001-Gemini-Prompt.md
        ├── EV-002-Gemini-Response.md
        ├── EV-003-ChatGPT-Review.md
        ├── EV-004-Gemini-Self-Review.md
        └── EV-005-Team-Decision.md
```

The inventory reflects the paths visible in the repository at the time of inspection. The `.docx` and `.pdf` files are present but appear to be placeholder-sized files; their contents and usability have not been validated. The reusable entry template and cross-file consistency report are listed below.

## 6. Evidence Classification

- **ORIGINAL:** Verbatim record preserved from the original AI interaction.
- **SUMMARY:** Condensed account of an AI response or review.
- **RECONSTRUCTED:** Recreated prompt or dialogue based on available context; not a verbatim primary source.
- **PARTIALLY VERIFIED:** Some claims checked against identified technical documentation, but not fully validated.
- **NOT VERIFIED:** Requires confirmation from primary records, datasheets, implementation, or testing.

Each evidence file should clearly identify which classification applies. Do not label a reconstruction or summary as a verbatim transcript.

## 7. Decision Status Definitions

- **ACCEPTED IN PRINCIPLE — PROTOTYPE ONLY:** A provisional direction for prototype planning, subject to verification and further testing. Use only when a supporting team record exists.
- **ACCEPTED:** Formally adopted by the team with traceable approval evidence.
- **REJECTED:** Explicitly rejected in a documented decision.
- **PENDING / NOT VERIFIED:** Decision or supporting evidence has not been confirmed.
- **NOT IMPLEMENTED:** Evidence indicates the decision has not yet been implemented. If implementation status has not been checked, use NOT VERIFIED instead.

## 8. Pending Engineering Decisions

Refer to [ADR-001](ADR/ADR-001-Communication-v1.1.md) for the list of open issues, including ESP32 board and GPIO selection, power regulation, MQ-2 analog input protection, sensor polling intervals, MQTT settings, reconnection behavior, broker deployment, optional GPS/microSD, and acceptance criteria.

Do not treat proposed sampling rates, FSM thresholds, payload limits, or communication performance as finalized without team approval and supporting evidence.

## 9. Audit Maintenance Rules

1. Preserve original AI prompts and responses when available.
2. If the original interaction is unavailable, label the entry RECONSTRUCTED or SUMMARY.
3. Record human review separately from AI-generated claims.
4. Record team decisions only when supported by actual team notes, messages, or meeting records.
5. Mark unconfirmed dates, participants, implementation status, and test results as NOT VERIFIED.
6. Keep relative links consistent with the repository's actual file paths.
7. Update this README when files are added, removed, or renamed.
8. Do not claim that repository files, hardware, or tests were updated or verified unless the corresponding action or evidence exists.

## 10. Manual Verification Required

- Confirm the official project title and team/course metadata.
- Verify the date and approval evidence for the Wi-Fi + MQTT decision.
- Confirm hardware assembly, firmware deployment, and test status with the team.
- Inspect the contents of `AI_Audit_Log.docx` and `AI_Audit_Log.pdf`; replace them with valid exported documents if required.
- Create and maintain a template directory only if the team intends to use a standard entry template.
