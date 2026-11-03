# cognition remediation plan

[Source review and findings](REVIEW.md) · All tasks below are **planned**, not performed. Observed paths exist in the pinned sample; new test/store paths and the frontend callback caller are proposed or must be located. Do not run target code or contact providers as part of this documentation review.

## Phases and gates

| Phase | Entry | Exit / gate |
|---|---|---|
| 0 Baseline | Pinned review available | T-00 records architecture, data inventory and decisions; reproduction plan is isolated. |
| 1 Identity, consent and OAuth | T-00 decisions; T-01 first | T-01–T-03 implemented; principal, consent and state contracts defined; no claim of complete erasure without inventory. |
| 2 Risk-based security | Policy from T-00 | T-04 validates non-dev configuration, dependencies and storage risks; unresolved issues have owners. |
| 3 Automation | T-01–T-04 ready | T-05 passes behavioral tests and mutation controls, including config checks. |
| 4 Deployment/recovery | T-05 signoff and target decision | T-06 observes deployment, recovery and restore in an authorized isolated environment, or release is blocked. |
| 5 UX/accessibility | Frontend caller located; T-01/T-02 contracts defined | T-07 verifies consent, deletion and callback flows or documents why UI release is blocked. |
| 6 Independent acceptance | T-05–T-07 complete | T-08 independent evidence review and release decision; open blockers prevent release. |

## Tasks

### T-00 — Baseline and boundary decisions
**Link:** COG-001–005; prerequisite for T-01–T-04. **Observed:** `backend/app/routers/auth.py`, `backend/app/routers/consent.py`, `backend/app/routers/user_data.py`, `backend/app/models.py`, `backend/app/config.py`, `docker-compose.yml`. Other routers, schema and frontend caller must be located and inspected later.

1. Trace actual authentication, callback caller, consent collection gates, data writes, deletion targets, provider access and logs; inventory stores, backups and external copies.
2. Define canonical stable principal, session binding, token audience/scope, consent semantics and deletion/retention boundaries; identify unresolved legacy placeholder and orphan-token mapping without guessing ownership.
3. Choose state store/TTL and deployment/recovery objectives; document isolated reproduction, dependencies and safe test data before execution.

**Output:** decision record, ownership/data-flow inventory and reproducible test plan. **Verify:** another reviewer traces every proposed principal and data location to source or marks it unknown. **DoD:** [ ] decisions and unknowns recorded; [ ] legacy data disposition avoids unsafe reassignment; [ ] reproduction environment isolated.

### T-01 — Principal, consent and deletion
**Link:** COG-001, COG-005. **Prerequisite:** T-00. **Observed:** `backend/app/routers/auth.py`, `backend/app/routers/consent.py`, `backend/app/routers/user_data.py`, `backend/app/models.py`.

1. Implement authenticated stable principal resolution and consistent ownership checks for callback and relevant routes; reject missing/invalid sessions.
2. Bind consent reads/updates and collection gates to that principal; replace the unconditional consent response with the agreed truthful semantics.
3. Scope deletion to the same principal, address each inventoried store and external copy under the agreed retention policy, and implement safe legacy-row handling and migration/rollback.

**Output:** ownership, consent and erasure implementation plus migration/disposition record. **Verify:** in isolated tests use two users and unauthenticated requests; check repeated login, consent changes, deletion of one user's token and other inventoried records, and preservation of the other user's data. Check absent/withdrawn consent blocks applicable collection. **DoD:** [ ] no shared identity on protected routes; [ ] consent reflects recorded choice; [ ] erasure coverage and exceptions documented and verified; [ ] legacy records not silently misassigned.

### T-02 — Decide and implement token boundary
**Link:** COG-002. **Prerequisites:** T-00 token decision and T-01 principal. **Observed:** `backend/app/routers/auth.py`, `backend/app/models.py`; frontend caller **to be located**.

1. Inspect the real callback consumer and provider scopes; decide if a trusted client genuinely requires the access token, or choose server-only handling.
2. Implement the chosen response contract and minimum scopes; protect server-side access/refresh tokens with appropriate access, encryption, retention and log-redaction controls.
3. Update the located client and document compatibility and cutover; never treat returning an access token as proof of a leak or assume refresh is returned.

**Output:** agreed token/data-flow contract and implementation. **Verify:** mock provider credentials, inspect response and logs against the chosen contract, and verify permitted client completion and refresh behavior without exposing real credentials. **DoD:** [ ] client need and scope documented; [ ] response matches decision; [ ] token storage and logging controls tested; [ ] frontend compatibility verified.

### T-03 — Atomic OAuth state lifecycle
**Link:** COG-003. **Prerequisites:** T-00 shared-store/TTL decision and T-01 session model. **Observed:** `backend/app/routers/auth.py`; shared store adapter and tests are **proposed**.

1. Persist unpredictable state with initiating-session binding, creation/expiry and an atomic consume operation in the chosen shared store.
2. Atomically validate session and TTL and consume state **before** token exchange; reject missing, expired, cross-session or already-consumed state.
3. Define exchange-failure policy: consumed state stays consumed, and retry starts a new authorization flow; document store outage behavior as fail closed.

**Output:** expiring shared-state adapter and callback contract. **Verify:** test concurrent replay with exactly one successful consume, session mismatch, expiry, store failure, exchange failure/new-flow retry, and cross-worker/restart behavior while the store survives. **DoD:** [ ] atomic single use; [ ] TTL and session binding enforced; [ ] retry and failure policy verified; [ ] cross-process behavior observed in test.

### T-04 — Environment and supply-chain hardening
**Link:** COG-004; preventive injection/dependency and data-protection review. **Prerequisite:** T-00 environment/security policy. **Observed:** `backend/app/config.py`, `docker-compose.yml`, `backend/requirements.txt`, `Dockerfile`, `frontend/package.json`, `frontend/Dockerfile`.

1. Trace `app_secret_key` consumption and document which secrets and OAuth values are required for each supported environment; keep local demo distinct from shared environments.
2. Reject missing, empty or placeholder required credentials in non-dev mode; protect secrets, token storage and logging according to T-02, without claiming the existing defaults were deployed.
3. Review injection boundaries, resolved dependency versions, lock/provenance and vulnerability reports; remediate or explicitly track identified risks without weakening checks.

**Output:** environment validation, dependency/security inventory and configuration guide. **Verify:** isolated startup tests reject bad non-dev configuration and accept explicit valid test configuration; inspect resulting dependency resolution and injection tests. **DoD:** [ ] production policy enforced; [ ] demo defaults clearly scoped; [ ] security unknowns resolved or tracked. T-05 tests T-04 before signoff.

### T-05 — Behavioral automation and negative controls
**Link:** COG-001–005 and preventive testing. **Prerequisites:** T-01–T-04. **Observed:** `backend/demo_test.py`; focused auth, consent, deletion, state and config test files are **proposed**.

1. Add isolated tests with independently specified expected outcomes, fake provider responses, two principals and separate persistent test data; retain existing demo assertions.
2. Cover unauthorized/cross-user access, consent absence/withdrawal, erasure scope, the chosen token response contract, concurrent/restarted/expired state and non-dev config.
3. Introduce controlled mutations such as bypassed ownership, unconditional consent, replay acceptance and disabled config validation; restore each mutation after recording results.

**Output:** repeatable test suite and mutation evidence. **Verify:** correct implementation passes positive and negative tests; each deliberately broken behavior causes its corresponding well-designed test to fail. Negative tests themselves are expected to pass when defenses work. **DoD:** [ ] behavior assertions cover each boundary; [ ] mutations caught individually; [ ] no tests or thresholds weakened; [ ] T-04 included in signoff.

### T-06 — Deploy, rollback and recover
**Link:** preventive operational readiness. **Prerequisites:** T-00 target/restore objectives and T-05 signoff. **Observed:** `docker-compose.yml`, `Dockerfile`, `frontend/Dockerfile`; deployment and backup runbooks are **proposed**.

1. Document target topology, secret provisioning, schema/migration order, state-store availability, monitoring and release/rollback ownership; assess deletion implications for backups.
2. In an authorized isolated environment deploy the candidate, observe health and the mocked auth/consent/deletion path, and record version and configuration evidence.
3. Back up representative test data and restore it into an isolated target; measure recovery against agreed objectives, test rollback and prevent restored deleted records from silently resurfacing.

**Output:** deployment/restore evidence and runbook. **Verify:** independently inspect deployment version, health, restore data and measured recovery; documentation alone is insufficient. **DoD:** [ ] deploy observed; [ ] restore and deletion reconciliation observed; [ ] rollback tested; [ ] unmet objectives block release.

### T-07 — Consent and deletion UX/accessibility
**Link:** COG-001, COG-005; preventive accessibility. **Prerequisites:** T-00 locates frontend caller; T-01/T-02 define contracts. **Observed:** `frontend/package.json`; pages/components and tests are **to be located or proposed**.

1. Inspect actual sign-in, consent choice/withdrawal and deletion confirmation screens; map errors and loading states to the API contract.
2. Implement clear scope and irreversible-action messaging, accessible labels, focus and keyboard behavior, and safe failure/retry feedback as needed.
3. Test the flow with keyboard and screen reader plus automated accessibility checks, using test accounts and mocked provider interactions.

**Output:** UI changes or documented applicability decision and accessibility evidence. **Verify:** a reviewer completes consent, withdrawal and deletion without relying on color or a mouse; errors and focus are announced. **DoD:** [ ] frontend path located; [ ] interaction and accessible feedback verified; [ ] unresolved failures block UI release.

### T-08 — Independent acceptance
**Link:** all findings and release gates. **Prerequisites:** T-05, T-06 and T-07. **Paths:** reviewed implementation and test evidence from T-01–T-07; acceptance record **proposed**.

1. An independent reviewer traces the deployed revision to the reviewed code, decisions, data inventory and test results.
2. Re-run representative ownership, consent, state replay and configuration checks; inspect mutation failures, deployment and restore evidence rather than accepting test counts.
3. Record remaining risks, recovery results and explicit release/block decision; return failed gates to their owning task and reverify after changes.

**Output:** signed acceptance record bound to candidate revision. **Verify:** independent reviewer can reproduce checks and inspect observed operational evidence. **DoD:** [ ] revision and evidence match; [ ] no critical gate bypassed; [ ] release decision and residual risks recorded.

## Dependencies and release policy

T-00 → T-01 → T-02 and T-03; T-00 → T-04; T-01–T-04 → T-05 → T-06; T-00/T-01/T-02 → T-07; T-05/T-06/T-07 → T-08. Store choice is part of T-00, not a separate hidden prerequisite. T-04 is included in T-05 signoff.

**Production acceptance:** [ ] stable authorized identity and consent; [ ] inventoried deletion/retention validated; [ ] approved token boundary and scopes; [ ] state TTL, session binding and atomic replay protection; [ ] config and dependency risks addressed; [ ] mutation controls and UX checks pass; [ ] deployment and restore observed; [ ] independent acceptance recorded.

Existing owner authorization covers defensive documentation; there is no fresh per-finding permission gate. The owner must resolve architecture, deployment, data disposition and risk decisions, and authorize any future external environment access or release as appropriate. Use a staged release with compatible client cutover and a tested rollback. Do not restore the shared development identity or unsafe secret defaults in a shared environment; if safe rollback is impossible, stop release and remediate. No future command or test is claimed to have been executed here.
