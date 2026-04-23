"""
mock_spammer.py — SentinelMind Mock Data Spammer
=================================================
Generates 50 realistic, LLM-authored emergency scenarios using Gemini 1.5 Flash
with strict JSON schema enforcement (response_schema), then writes them to the
Firestore /emergencies collection using rate-limited, batched writes.

Usage:
    python scripts/mock_spammer.py

Prerequisites:
    pip install firebase-admin google-genai python-dotenv
    .env file with GEMINI_API_KEY and GOOGLE_APPLICATION_CREDENTIALS set.
    service-account.json in the project root (or path set in .env).
"""

import os
import sys
import uuid
import time
import json
import logging
import datetime

from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import google.genai as genai
from google.genai import types

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

load_dotenv()  # Pull GEMINI_API_KEY + GOOGLE_APPLICATION_CREDENTIALS from .env

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service-account.json")

TOTAL_EMERGENCIES = 50          # Total documents to generate and push
FIRESTORE_BATCH_SIZE = 10       # Firestore recommends ≤500 writes/batch; 10 keeps us safe
INTER_BATCH_SLEEP_SEC = 1.5     # Pause between Firestore batch commits (rate-limit guard)
GEMINI_MODEL = "gemini-3.1-flash-lite-preview"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("mock_spammer")

# ---------------------------------------------------------------------------
# Gemini Structured Output Schema
# ---------------------------------------------------------------------------
# We define the JSON schema directly via google.genai's types.Schema objects.
# This is passed to `response_schema` in the GenerateContent call, which forces
# the model to return ONLY valid JSON matching this schema — no markdown fences,
# no prose, no hallucinated keys. It's enforced at the decoder level by Gemini.

# Inner schema: a single Emergency object
EMERGENCY_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    required=["hazard_type", "location_coordinates", "severity", "description"],
    properties={
        # The model generates these four fields; emergency_id and status are
        # injected by *us* after generation so they are never LLM-guessed.
        "hazard_type": types.Schema(
            type=types.Type.STRING,
            description=(
                "Mock Incident: Simulation of a disaster event for Role 3 testing using gemini-2.5-flash-lite. "
                "Category of disaster. One of: flood, earthquake, fire, "
                "landslide, cyclone, medical, structural_collapse, chemical_spill, "
                "drought, tsunami."
            ),
        ),
        "location_coordinates": types.Schema(
            type=types.Type.OBJECT,
            required=["lat", "lng"],
            properties={
                "lat": types.Schema(type=types.Type.NUMBER, description="Latitude (India-region)"),
                "lng": types.Schema(type=types.Type.NUMBER, description="Longitude (India-region)"),
            },
        ),
        "severity": types.Schema(
            type=types.Type.INTEGER,
            description="Severity score from 1 (minor) to 5 (catastrophic).",
        ),
        "description": types.Schema(
            type=types.Type.STRING,
            description=(
                "2-3 sentence realistic situation report written from a first-responder "
                "perspective. Include affected population estimate and immediate needs."
            ),
        ),
    },
)

# Outer schema: an array of 50 Emergency objects
RESPONSE_SCHEMA = types.Schema(
    type=types.Type.ARRAY,
    items=EMERGENCY_SCHEMA,
)

# ---------------------------------------------------------------------------
# Step 1 — Generate emergencies via Gemini 1.5 Flash
# ---------------------------------------------------------------------------

def generate_emergencies() -> list[dict]:
    """
    Calls Gemini 1.5 Flash with response_schema set to RESPONSE_SCHEMA.
    The SDK serialises the schema into the API request and the model is
    constrained to emit ONLY valid JSON that matches it — no extra keys,
    no omitted required fields.
    Returns a Python list of dicts (one per emergency).
    """
    if not GEMINI_API_KEY:
        log.error("GEMINI_API_KEY is not set. Add it to your .env file.")
        sys.exit(1)

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""
You are a disaster-response data generator for India.

Generate exactly {TOTAL_EMERGENCIES} unique, highly realistic emergency incidents
spread across diverse Indian states (Andhra Pradesh, Telangana, Odisha, Kerala,
Maharashtra, Assam, Uttarakhand, Tamil Nadu, Gujarat, Rajasthan).

Rules:
- Cover a realistic mix of hazard_type values.
- Use actual Indian city / district coordinates (lat/lng).
- severity must vary between 1 and 5 across the dataset.
- Each description must read like a real field report, not a template.
- Do NOT include emergency_id or status fields — those are managed externally.
"""

    log.info("Calling Gemini %s for %d structured emergencies …", GEMINI_MODEL, TOTAL_EMERGENCIES)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            # response_schema + response_mime_type together enable "Controlled
            # Generation" — Gemini's token sampler is constrained to only emit
            # tokens that keep the running JSON valid against the schema.
            response_mime_type="application/json",
            response_schema=RESPONSE_SCHEMA,
            temperature=1.0,   # High temperature → more diverse scenarios
            max_output_tokens=8192,
        ),
    )

    raw_json = response.text
    log.info("Received %d characters from Gemini.", len(raw_json))

    try:
        emergencies = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        log.error("Failed to parse Gemini response as JSON: %s", exc)
        log.debug("Raw response: %s", raw_json[:500])
        sys.exit(1)

    if not isinstance(emergencies, list):
        log.error("Expected a JSON array from Gemini, got: %s", type(emergencies))
        sys.exit(1)

    log.info("Parsed %d emergency objects from Gemini.", len(emergencies))
    return emergencies

# ---------------------------------------------------------------------------
# Step 2 — Enrich and sanitise each document
# ---------------------------------------------------------------------------

def enrich(raw: dict) -> dict:
    """
    Adds the fields that must NEVER be delegated to the LLM:
      - emergency_id : a fresh UUID (deterministic identity for each doc)
      - status       : hardcoded "triaged" — critical for the swarm state machine
      - timestamp    : server-side Firestore sentinel for accurate ordering

    Also clamps severity to [1, 5] in case the model drifts slightly.
    """
    return {
        # LLM-generated fields
        "hazard_type":            str(raw.get("hazard_type", "unknown")).lower().strip(),
        "location_coordinates":   {
            "lat": float(raw["location_coordinates"]["lat"]),
            "lng": float(raw["location_coordinates"]["lng"]),
        },
        "severity":               max(1, min(5, int(raw.get("severity", 3)))),
        "description":            str(raw.get("description", "")).strip(),

        # Injected fields — LLM never touches these
        "emergency_id":           str(uuid.uuid4()),
        "status":                 "triaged",   # HARDCODED — swarm state machine entry point
        "timestamp":              firestore.SERVER_TIMESTAMP,
    }

# ---------------------------------------------------------------------------
# Step 3 — Write to Firestore with batched, rate-limited writes
# ---------------------------------------------------------------------------

def write_to_firestore(docs: list[dict]) -> None:
    """
    Writes `docs` to /emergencies using Firestore atomic batch writes.

    Rate-limiting strategy:
      - Documents are grouped into batches of FIRESTORE_BATCH_SIZE (10).
      - Each batch is committed atomically in a single RPC — far more efficient
        than 50 individual .set() calls and far less likely to hit quota limits.
      - A time.sleep(INTER_BATCH_SLEEP_SEC) pause is inserted between batch
        commits to stay well under Firestore's 1 write/sec per-document and
        1 MB/s write rate limits. At 10 docs/batch + 1.5 s sleep, we land at
        ~6-7 docs/sec — comfortably within free-tier quota.
    """
    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        log.error(
            "Service account file not found at '%s'. "
            "Set GOOGLE_APPLICATION_CREDENTIALS in your .env.",
            SERVICE_ACCOUNT_PATH,
        )
        sys.exit(1)

    if not firebase_admin._apps:  # Guard against double-initialisation
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    collection = db.collection("emergencies")

    total = len(docs)
    written = 0

    # Chunk `docs` into slices of FIRESTORE_BATCH_SIZE
    for batch_start in range(0, total, FIRESTORE_BATCH_SIZE):
        chunk = docs[batch_start : batch_start + FIRESTORE_BATCH_SIZE]

        # A Firestore WriteBatch groups multiple writes into one atomic commit.
        # If any write in the batch fails, none of them are applied.
        batch = db.batch()
        for doc in chunk:
            # Use emergency_id as the Firestore document ID for easy lookups
            doc_ref = collection.document(doc["emergency_id"])
            batch.set(doc_ref, doc)

        batch_num = (batch_start // FIRESTORE_BATCH_SIZE) + 1
        total_batches = -(-total // FIRESTORE_BATCH_SIZE)  # ceiling division

        log.info(
            "Committing batch %d/%d (%d docs) …",
            batch_num, total_batches, len(chunk),
        )
        batch.commit()
        written += len(chunk)
        log.info("  ✓ %d / %d documents written.", written, total)

        # Rate-limit guard: sleep between batches (skip after the last one)
        if batch_start + FIRESTORE_BATCH_SIZE < total:
            log.debug("  Sleeping %.1f s before next batch …", INTER_BATCH_SLEEP_SEC)
            time.sleep(INTER_BATCH_SLEEP_SEC)

    log.info("All %d documents successfully written to Firestore /emergencies.", written)

# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main():
    start = time.perf_counter()
    log.info("=== SentinelMind Mock Spammer ===")

    # 1. Generate raw emergencies from Gemini (structured output)
    raw_emergencies = generate_emergencies()

    # Guard: Gemini may occasionally return slightly fewer items if the response
    # is truncated by max_output_tokens. Log a warning but continue.
    if len(raw_emergencies) < TOTAL_EMERGENCIES:
        log.warning(
            "Gemini returned %d items (expected %d). "
            "Consider increasing max_output_tokens or reducing TOTAL_EMERGENCIES.",
            len(raw_emergencies), TOTAL_EMERGENCIES,
        )

    # 2. Enrich / sanitise each document (inject UUID, status, timestamp)
    enriched = [enrich(r) for r in raw_emergencies]

    # 3. Write to Firestore with batching + rate limiting
    write_to_firestore(enriched)

    elapsed = time.perf_counter() - start
    log.info("Done. Total time: %.1f seconds.", elapsed)


if __name__ == "__main__":
    main()
