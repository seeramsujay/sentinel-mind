# QA Error Report: Sentinel Mind Backend

As requested, exhaustive unit and integration testing was executed against the Sentinel Mind backend architecture. Several critical bugs and integration issues were uncovered. Per testing requirements, **no corrections were applied to the application code**.

## Dependency & Environment Issues
1.  **Missing Requirements:** The `requirements.txt` is incomplete. The following required modules are not listed, causing immediate `ModuleNotFoundError` crashes in production and test environments:
    *   `feedparser` (Required by `ingestion_service.py`)
    *   `googlemaps` (Required by `orchestrator/logistics_logic.py`)
    *   `google-cloud-secret-manager` (Required by `orchestrator/secrets_manager.py`)
2.  **Environment Variable Handling:** Initialization of `LogisticsAgent` and `IngestionService` does not gracefully fail or validate the presence of `GEMINI_API_KEY`. If undefined, the application will throw unhandled exceptions deeper in the Google/Vertex AI SDKs rather than providing clean, immediate validation checks.

## Codebase & Architectural Bugs
### 1. Missing `get_project_id` in `SentinelAuth`
*   **File Location:** `backend/orchestrator/secrets_manager.py:20` & `backend/orchestrator/auth.py`
*   **Description:** `SentinelSecrets.get_secret()` calls `SentinelAuth.get_project_id()`. However, `SentinelAuth` inside `auth.py` does not implement or define `get_project_id`.
*   **Impact:** Fatal `AttributeError`. Every time `LogisticsAgent` initializes, it instantiates `RoutingService`, which in turn attempts to invoke `SentinelSecrets.get_secret("GOOGLE_MAPS_API_KEY")`. This throws an `AttributeError` and crashes the entire swarm service.

### 2. Ingestion Service Error Handling
*   **File Location:** `backend/ingestion_service.py`
*   **Description:** `process_entry` relies heavily on `getattr(entry, 'description', entry.summary)`. If an RSS feed entry lacks both `description` and `summary` (which is common in malformed RSS feeds like NDMA mocked streams), this throws an `AttributeError`, causing the ingestion loop for that item to fail.
*   **Impact:** Missing alerts during high-priority data intake. 

### 3. Asynchronous Lock Race Condition 
*   **File Location:** `backend/logistics_agent.py`
*   **Description:** The `run_swarm()` function uses an `asyncio.Semaphore(5)` to limit API quota. While `process_emergency_async` uses an `asyncio.Lock()`, Python's standard `asyncio.Lock` does not scale across multiple process workers (if the daemon scales horizontally, this lock only protects the current Python thread/proccess). Real distributed locking via Firestore transactions or Redis is missing, making it susceptible to double dispatch.
*   **Impact:** In a production 100-signal burst scenario as outlined in the roadmap constraints, multiple workers could still theoretically dispatch the same resource if the Firestore delay is >0ms.

### 4. Firestore Query Edge Cases
*   **File Location:** `backend/logistics_agent.py:82`
*   **Description:** The query `self.db.collection('resources').where('status', '==', 'available')` relies on the fact that an emergency can safely match the best resource. If `best_resource` returns `None`, the application silently returns without marking the emergency as escalated. It only marks it escalated if the initial query returns *zero* available resources, but ignores the state where resources exist but do not match the criteria inside `find_best_resource`.
*   **Impact:** Silent failure. Emergencies remain in `awaiting_dispatch` essentially forever, creating zombie SOS signals.

## Conclusion
The backend is fundamentally unstable due to the `SentinelAuth.get_project_id()` omission. Even with that patched, missing dependencies prevent standard initialization and containerization in Cloud Run.
