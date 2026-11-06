# Plan: Claims status self-service
Intent: intent.md
Spec: spec.md
Author: S. Engineer (portal team)
Date: 2026-06-04
Status: draft

## Files that change
- claims-api/routes/status.py (new): `GET /claims/status` endpoint behind the gateway JWT.
- claims-api/app.py (modified): register the new route.
- claims-api/tests/test_status.py (new): four claim states, ownership check, schema has no pii fields.
- portal/src/claims/StatusPanel.tsx (new): panel component.
- portal/src/claims/ClaimsPage.tsx (modified): render the panel.
- portal/src/claims/StatusPanel.test.tsx (new): renders each state.

## Order of work
1. Add the status endpoint behind existing auth with a 60 s per-customer cache; tests for the four states and the 403 case.
2. Build the panel against the endpoint; component tests for each state.
3. Wire the panel into the claims page and the portal nav.
4. Run the load test against staging.

## Risks
- claims-core rate-limits at 50 rps; without the cache the panel could trip it at peak.
- Mapping internal states to the four public states could hide a state we have not seen; unknown states fall back to "assessing" and are logged.
- Riskiest step: step 1, because the ownership check is the only thing stopping cross-customer data exposure.

## Alternatives considered
- Polling claims-core directly from the portal: rejected, it would expose the internal API and bypass the cache.
- Nightly export of statuses to the portal database: rejected, statuses would be up to a day stale.

## Proof
- AC1: `make test` runs claims-api/tests/test_status.py (four states) and StatusPanel.test.tsx.
- AC2: test_status.py::test_other_customer_forbidden returns 403.
- AC3: `make loadtest USERS=200` against staging shows under 50 rps to claims-core.
- AC4: test_status.py::test_schema_has_no_pii checks the response schema.

## Deviations from plan
None yet.
