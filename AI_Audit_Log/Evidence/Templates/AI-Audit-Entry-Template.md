# AI Audit Entry Template

> **Purpose:** Use this template to document one AI-assisted interaction. Replace every bracketed placeholder with verified information or retain `NOT VERIFIED`. Do not invent timestamps, participant names, approval records, quotations, sources, or test results.

## 1. Entry Metadata

- **Entry ID:** [ENTRY-00X]
- **Evidence ID:** [EV-00X]
- **Date and time:** [EXACT DATE/TIME FROM ORIGINAL RECORD, OR RECONSTRUCTED / APPROXIMATE]
- **AI tool and model:** [TO BE RECORDED]
- **Human operator:** [TO BE RECORDED FROM ACTUAL RECORDS, OR NOT VERIFIED]
- **Interaction type:** [PROMPT / RESPONSE / REVIEW / DECISION / OTHER]
- **Evidence classification:** [ORIGINAL / SUMMARY / RECONSTRUCTED / PARTIALLY VERIFIED / NOT VERIFIED]
- **Source location:** [LINK TO ORIGINAL CONVERSATION OR FILE, IF AVAILABLE]

## 2. Objective

[Describe the specific question or task. Distinguish the original objective from later interpretation.]

## 3. Project Context Supplied to the AI

[Summarize the context supplied. Do not include credentials, private keys, passwords, or unnecessary personal information.]

## 4. Prompt or Input

[Paste the exact prompt if preserved. Otherwise write: "RECONSTRUCTED SUMMARY — not a verbatim prompt" and summarize faithfully.]

## 5. AI Output

[Preserve the original response where permitted. If summarizing, label it SUMMARY and do not use quotation marks for paraphrased text.]

## 6. Claims and Recommendations Requiring Verification

| ID | Claim or recommendation | Verification method / source | Status | Notes |
|---|---|---|---|---|
| V-01 | [Claim] | [Datasheet, official documentation, test, or team record] | NOT VERIFIED | [Notes] |

## 7. Human Review

- **What appears useful:** [Evidence-based assessment]
- **Potential errors or unsupported assumptions:** [List]
- **Changes made by human reviewer:** [List, or NONE]
- **Independent verification performed:** [Describe exactly what was checked; otherwise NONE]

## 8. Team Decision

- **Decision:** [PROPOSED / PENDING / ACCEPTED IN PRINCIPLE / ACCEPTED / REJECTED / NOT VERIFIED]
- **Decision evidence:** [Link to actual meeting minutes, message, or decision record]
- **Participants:** [From actual record, otherwise NOT VERIFIED]
- **Date:** [From actual record, otherwise NOT VERIFIED]
- **Conditions and limitations:** [List]

Do not use ACCEPTED or ACCEPTED IN PRINCIPLE as a factual status unless a primary team record supports it.

## 9. Implementation and Testing

- **Implementation status:** [IMPLEMENTED / NOT IMPLEMENTED / NOT VERIFIED]
- **Test performed:** [Exact procedure, or NOT PERFORMED / NOT VERIFIED]
- **Observed result:** [Measured result with units and context, or NO RESULT RECORDED]
- **Test artifact:** [Link to log, code, photo, dataset, or report]
- **Limitations:** [List]

Never describe a proposed test plan as a completed test.

## 10. Follow-up Actions

| Action | Owner | Due date | Status |
|---|---|---|---|
| [Action] | [Name or NOT ASSIGNED] | [Date or NOT SET] | OPEN |

## 11. Provenance and Revision History

- **Prepared on:** [Date this document was actually created or updated]
- **Source fidelity:** [VERBATIM / SUMMARY / RECONSTRUCTED]
- **Reviewer:** [Name from actual review record, or NOT VERIFIED]
- **Revision notes:** [Describe changes]

---
**Integrity rule:** This entry documents AI assistance and human review; it does not itself prove technical correctness, team approval, implementation, or experimental success.
