# QA Checklist: Sentinel Mind

| Issue ID | Component | Test Case | Expected Result | Priority | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SM-QA-01** | **Backend/Auth** | Verify `SentinelAuth.get_project_id()` | System retrieves GCP Project ID without `AttributeError`. | **BLOCKER** | [ ] |
| **SM-QA-02** | **Backend/Deps** | Run `pip install -r requirements.txt` | All dependencies (`feedparser`, `googlemaps`, etc.) install successfully. | **BLOCKER** | [ ] |
| **SM-QA-03** | **Role 2 (Triage)** | Inject malformed RSS entry (no desc/summary) | `ingestion_service.py` skips or handles gracefully instead of crashing. | **HIGH** | [ ] |
| **SM-QA-04** | **Role 3 (Logistics)** | Dispatch when 0 matching resources found | Emergency state updates to `escalated` or `awaiting_resource` (no zombie SOS). | **HIGH** | [ ] |
| **SM-QA-05** | **Role 1 (Orchestrator)** | Burst test: 100 signals / 5 seconds | `asyncio.Lock` or Firestore transactions prevent double-dispatch. | **CRITICAL** | [ ] |
| **SM-QA-06** | **Frontend/UI** | Dashboard data polling | UI updates dynamically when Firestore docs change without full page refresh. | **MEDIUM** | [ ] |
| **SM-QA-07** | **Frontend/UX** | Mobile Responsiveness (Viewport < 768px) | Layout collapses to single column; map remains usable. | **MEDIUM** | [ ] |
| **SM-QA-08** | **Frontend/Auth** | Login with invalid credentials | User receives clear error message (not 403 raw dump). | **HIGH** | [ ] |
| **SM-QA-09** | **Role 4 (UI)** | Multi-Lingual Toggle (Hindi/Telugu) | UI text and SitReps translate instantly via Gemini. | **MEDIUM** | [ ] |
| **SM-QA-10** | **Role 1 (HITL)** | "Approve Dispatch" Button Workflow | Clicking button flips status from `awaiting_human_approval` to `dispatched`. | **CRITICAL** | [ ] |
| **SM-QA-11** | **Role 3 (Logistics)** | Carbon Savings Math | `carbon_saved` field is populated with non-zero value after routing. | **MEDIUM** | [ ] |
| **SM-QA-12** | **System** | GEMINI_API_KEY Missing | Application provides clean error log at startup, not SDK stack trace. | **HIGH** | [ ] |

## Failure Point Analysis (Pre-Submission)

### 1. The "SentinelAuth" Trap
*   **Vector**: `secrets_manager.py` calls a non-existent method.
*   **Symptom**: Instant crash on any logic requiring API keys.
*   **Test**: `python3 backend/orchestrator/secrets_manager.py` (unit test).

### 2. Double-Dispatch Race
*   **Vector**: Multiple workers picking up the same `triaged` emergency.
*   **Symptom**: Two trucks sent to same fire; wasted resources.
*   **Test**: Run `backend/logistics_agent.py` with multiple instances against same Firestore collection.

### 3. Zombie Emergencies
*   **Vector**: No resource matches `find_best_resource`.
*   **Symptom**: SOS signal stays "triaged" forever.
*   **Test**: Create emergency far away from all available resources.

### 4. Front-end "White Screen"
*   **Vector**: malformed Firestore data (e.g. missing `polyline`).
*   **Symptom**: React crashes on render.
*   **Test**: Manually delete `polyline` field in a `dispatched` emergency doc.
