# Intent: Claims status self-service
Author: J. Ortiz (claims operations)
Date: 2026-06-02
Status: draft
Source: idea

## Problem
Customers phone the contact center to ask where their claim is. Handlers spend roughly a
third of call time on status-only queries, and customers wait on hold for an answer that
is already in our systems.

## Proposed outcome
Customers see their claim status, the next step and the expected date in the customer
portal without calling.

## Affected users and systems
Policyholders using the portal, claims handlers, the portal team, the claims-core API.

## Constraints
No new PII in the portal session. Existing portal authentication only. Must work on mobile.

## Out of scope
Changing claim decisions or uploading documents from the portal.

## What success looks like
Status-only calls fall by at least half within three months of launch, measured from the
contact-center call reasons report.

## Open questions
Do third-party loss adjusters need access too?
