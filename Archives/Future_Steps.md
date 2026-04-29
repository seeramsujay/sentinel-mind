# Future Steps & Phase 2 Readiness

Following the successful completion of Phase 1, the following upgrades are planned to move Sentinel-Mind toward a production-grade enterprise system.

## Phase 2: Production Hardening
1. **GCP Secret Migration:** Move all hardcoded keys from `.env` and Docker build context into **Google Cloud Secret Manager** to implement a Zero-Trust security architecture.
2. **Distributed Concurrency Control:** Transition from local `asyncio.Lock` to **Firestore Transactions** or a Redis-backed locking mechanism in `logistics_agent.py`. This is critical for multi-instance scaling in Cloud Run.
3. **Data Pipeline Resilience:** Enhance `ingestion_service.py` with pydantic validation and intelligent retry logic to handle malformed or partial RSS feeds from erratic disaster data sources.
4. **Automated SitReps (RAG Expansion):** Move from the manual dashboard view to a fully automated, scheduled Situation Report generation service using Vertex AI Vector Search on the NDMA corpus.

## Long-term Vision
- **Cross-Agency Sync:** Enable interoperability with regional disaster management nodes via standardized JSON-LD schema.
- **Edge Deployment:** Deploy lightweight triage models to edge devices (satellite-linked drones) for offline operation in complete communication blackout zones.
