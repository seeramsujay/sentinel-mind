# Role 1 Walkthru — Meta-Orchestrator & Cloud Ops

## What This Role Does

The Meta-Orchestrator is the brain of SentinelMind. It owns three concerns:

1. **Duplicate Detection** — merges panic-call duplicates before they waste resources
2. **Conflict Resolution** — uses Gemini 1.5 Pro to resolve resource overlaps
3. **Fairness & HITL** — logs AI reasoning and flags biased dispatches for human approval

---

## File Map

| File | What It Does |
|------|-------------|
| `backend/orchestrator/daemon.py` | Main polling loop. Orchestrates everything. |
| `backend/orchestrator/spatial_logic.py` | Haversine distance + duplicate detection. |
| `backend/orchestrator/resolver.py` | Gemini 1.5 Pro → conflict resolution JSON. |
| `backend/orchestrator/audit.py` | Fairness audit logging + HITL flag/approve. |
| `backend/orchestrator/secrets_manager.py` | GCP Secret Manager access. |
| `backend/orchestrator/auth.py` | GCP/Firestore initialization singleton. |

---

## State Machine (What This Role Owns)

```
triaged  →  awaiting_dispatch          (via spatial duplicate check)
         →  merged                   (duplicate found, absorbed)

conflict  →  dispatched               (AI resolved, unit assigned)
          →  awaiting_human_approval  (AI flagged bias → HITL)
```

All other transitions belong to other roles.

---

## Running the Daemon

```bash
cd backend/orchestrator
python daemon.py
```

Or from project root:
```bash
PYTHONPATH=. python scripts/discord_actuator.py
```

---

## Environment Variables (from `.env`)

| Var | Required | Purpose |
|-----|----------|---------|
| `GCP_PROJECT_ID` | Yes | GCP project + Vertex AI init |
| `GCP_REGION` | Yes | Vertex AI location |
| `GOOGLE_APPLICATION_CREDENTIALS` | Yes* | Firebase service account |
| `GEMINI_API_KEY` | Yes | Gemini API (via auth fallback) |

*If `service-account.json` doesn't exist, falls back to Application Default Credentials.

---

## How the Duplicate Detection Works

`spatial_logic.detect_duplicates(new_doc, existing_docs)`:
- Calculates Haversine distance between new event and all existing `triaged`/`awaiting_dispatch`/`dispatched` events
- Threshold: 500 meters by default
- Must match same `hazard_type` (flood ≠ earthquake even if same location)
- Returns the doc_id of the duplicate, or `None`
- Daemon flips status to `merged` and writes `merged_into` + `meta_note`

---

## How the Conflict Resolution Works

`resolver.ConflictResolver.resolve()`:
- Called when `status == "conflict"` is detected
- Sends conflict docs + available resources to Gemini 1.5 Pro
- Pro returns structured JSON with decisions:
  - `action: "dispatch"` → writes `status: "dispatched"` + `unit_id`
  - `action: "wait"` → does nothing (waits for resource)
  - `action: "reroute"` → flips to `awaiting_human_approval`
- Writes `fairness_audit` to `intelligence.fairness_audit` in every case

---

## How HITL Override Works

`audit.py` exposes two methods:

```python
from backend.orchestrator.audit import GovernanceAudit

# Flag a dispatch for human review
GovernanceAudit.log_hitl_flag(emergency_id, reason)

# Approve (flip back to dispatched)
GovernanceAudit.approve_dispatch(emergency_id)
```

Also ships a standalone HITL daemon:
```bash
python -c "from backend.orchestrator.audit import hitl_daemon; hitl_daemon()"
```

---

## Running Tests

```bash
PYTHONPATH=. pytest scripts/test_role1.py -v
```

Tests cover:
- Haversine distance calculations (known coords, null, invalid)
- Duplicate detection (exact match, threshold, wrong hazard, no location)
- Resolver JSON parsing (valid, fenced, empty, missing key)
- Audit null-safety (empty IDs return False)
- Schema null handling (all fields can be None)
- Both flat + nested coordinate formats
- Both P1 + general Discord routing

---

## Common Issues

| Symptom | Fix |
|---------|-----|
| `No module named 'vertexai'` | `pip install google-cloud-aiplatform vertexai` |
| `FIREBASE_DATABASE_URL not set` | Set in `.env` — falls back to ApplicationDefault |
| Duplicate alerts in Discord | `alerted_log` in `/tmp/` cleared on restart |
| Conflicting duplicate detections | Run Role 1 daemon BEFORE Role 3 daemon |
| No `conflict` status ever triggered | Role 3 sets this — check `/resources` collection first |

---

## Key Design Decisions

1. **Polling over on_snapshot** — simpler, easier to debug, survives restarts
2. **Alerted IDs in `/tmp/`** — survives in-process restart, clears on OS reboot
3. **Strict JSON from Gemini** — resolver enforces `decisions` key or drops response
4. **Dual-channel Discord** — P1 goes to `DISCORD_ALERT_WEBHOOK_URL`, others to `DISCORD_WEBHOOK_URL`
5. **ApplicationDefault fallback** — works in Cloud Run without local credentials