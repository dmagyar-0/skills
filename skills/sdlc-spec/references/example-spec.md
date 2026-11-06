# Spec: Claims status self-service
Intent: intent.md
Author: agent, prompted by A. Product (portal product owner)
Date: 2026-06-03
Status: draft

## Summary
Add a claim status panel to the customer portal that shows each open claim's status, next
step and expected date. Data comes from claims-core through a new read-only endpoint in
claims-api, so customers stop phoning for status-only questions.

## Requirements
### Functional
- R1: A signed-in customer sees all of their open claims with status, next step and expected date.
- R2: Only claims belonging to the signed-in customer are returned.
- R3: The four claim states (received, assessing, approved, paid) each show a plain-language next step.

### Non-functional
- NFR1: Panel loads in under 2 seconds at p95.
- NFR2: claims-core is called at most 50 requests per second in total (its rate limit).
- NFR3: No PII beyond claim reference and status is sent to the portal session.

## Design
- claims-api: new `GET /claims/status` behind the existing gateway JWT. Reads from
  claims-core, maps internal states to the four public states, caches per customer for 60 s.
- portal: new StatusPanel component on the claims page, calling the endpoint above.
- No schema changes. No new data stored.

## Acceptance criteria
- AC1 (R1, R3): Integration tests cover all four states and the panel renders each.
- AC2 (R2): A test proves a customer cannot see another customer's claim (403).
- AC3 (NFR2): Load test at 200 portal users stays under 50 rps to claims-core.
- AC4 (NFR3): Response schema contains no field tagged pii.

## Policies applied
| Policy (skill or steering file) | Version | How it shaped the spec |
|---|---|---|
| secure-api-review | 1.2.0 | Gateway JWT required; audit event not needed (read-only); no PII in logs |
| ux-standards | a1b2c3d | Plain-language status labels; mobile layout first |

## Areas of concern
| # | Concern | Policy or source | Severity (high/medium/low) | Decision owner | Resolution |
|---|---|---|---|---|---|
| C1 | Expected date is an estimate; showing it may create a commitment | Customer communications policy | medium | Claims operations lead | open |
| C2 | Loss adjusters' access is undecided and would need a different auth path | Intent open question | low | Portal product owner | open |

## Open questions
- From intent: do third-party loss adjusters need access too? Still open (see C2).

## Out of scope
Changing claim decisions, uploading documents, notifications.
