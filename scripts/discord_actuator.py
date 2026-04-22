"""
discord_actuator.py — SentinelMind Discord Actuator Daemon
===========================================================
Runs as a long-lived process. Monitors Firestore /emergencies in real-time
using on_snapshot (push-based). When a document satisfies:

    status == "dispatched"  AND  (discord_sent is missing OR discord_sent == False)

...it fires a Discord webhook alert, then immediately writes discord_sent=True
back to that document to prevent duplicate alerts.

Routing (severity-based):
    severity 4 or 5  →  DISCORD_ALERT_WEBHOOK_URL   (High-Priority channel)
    severity 1, 2, 3 →  DISCORD_WEBHOOK_URL          (General channel)

Usage:
    python scripts/discord_actuator.py

Prerequisites:
    pip install firebase-admin python-dotenv requests
    .env with DISCORD_WEBHOOK_URL, DISCORD_ALERT_WEBHOOK_URL, GEMINI_API_KEY,
    GOOGLE_APPLICATION_CREDENTIALS set.
    service-account.json present in project root.
"""

import os
import sys
import time
import logging
import threading

import requests
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("discord_actuator")

# ---------------------------------------------------------------------------
# Config — read from .env
# ---------------------------------------------------------------------------

SERVICE_ACCOUNT_PATH    = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service-account.json")
WEBHOOK_GENERAL         = os.getenv("DISCORD_WEBHOOK_URL", "")           # severity 1-3
WEBHOOK_HIGH_PRIORITY   = os.getenv("DISCORD_ALERT_WEBHOOK_URL", "")     # severity 4-5
POLL_INTERVAL_SEC       = 10   # Fallback polling interval if on_snapshot fails
REQUEST_TIMEOUT_SEC     = 10   # Max wait for Discord HTTP response

# ---------------------------------------------------------------------------
# Firebase initialisation
# ---------------------------------------------------------------------------

def init_firestore() -> firestore.Client:
    """
    Authenticates with Firebase using the service-account.json file whose path
    is read from GOOGLE_APPLICATION_CREDENTIALS in .env.
    Guards against double-initialisation (safe for hot-reload scenarios).
    """
    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        log.error(
            "Service account file not found at '%s'. "
            "Set GOOGLE_APPLICATION_CREDENTIALS in your .env.",
            SERVICE_ACCOUNT_PATH,
        )
        sys.exit(1)

    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred)
        log.info("Firebase initialised from '%s'.", SERVICE_ACCOUNT_PATH)
    else:
        log.debug("Firebase already initialised — reusing existing app.")

    return firestore.client()

# ---------------------------------------------------------------------------
# Severity routing
# ---------------------------------------------------------------------------

def resolve_webhook(severity: int) -> str:
    """
    Routes the alert to the correct Discord channel based on severity integer.

    Routing logic:
      severity 4 or 5  → High-Priority channel (DISCORD_ALERT_WEBHOOK_URL)
                          These are near-catastrophic events requiring immediate
                          attention from senior coordinators.
      severity 1, 2, 3 → General channel (DISCORD_WEBHOOK_URL)
                          Moderate incidents handled by standard response teams.

    Falls back to the general webhook if the high-priority URL is not configured.
    """
    if severity >= 4:
        url = WEBHOOK_HIGH_PRIORITY
        if not url:
            log.warning("severity=%d but DISCORD_ALERT_WEBHOOK_URL is not set — falling back to general.", severity)
            url = WEBHOOK_GENERAL
    else:
        url = WEBHOOK_GENERAL

    return url

# ---------------------------------------------------------------------------
# Discord message builder
# ---------------------------------------------------------------------------

def build_discord_payload(doc: dict) -> dict:
    """
    Constructs the Discord webhook JSON payload.
    The message body is hardcoded per spec; only severity and hazard_type
    are interpolated from the Firestore document.
    """
    severity    = int(doc.get("severity", 0))
    hazard_type = str(doc.get("hazard_type", "unknown")).strip()

    # Exact message format mandated by the spec
    content = (
        "🚨 **SENTINEL-MIND DISPATCH** 🚨\n"
        f"A level **{severity}** **{hazard_type}** has been confirmed. "
        "Emergency units have been routed to the location."
    )

    return {"content": content}

# ---------------------------------------------------------------------------
# Discord sender
# ---------------------------------------------------------------------------

def send_discord_alert(payload: dict, webhook_url: str, doc_id: str) -> bool:
    """
    POSTs `payload` to `webhook_url`.
    Returns True on any 2xx response, False otherwise.
    All network errors are caught so the daemon never crashes on a flaky network.
    """
    if not webhook_url:
        log.error("[%s] No webhook URL resolved — cannot send Discord alert.", doc_id)
        return False

    try:
        resp = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=REQUEST_TIMEOUT_SEC,
        )
        if 200 <= resp.status_code < 300:
            log.info("[%s] ✓ Discord alert sent (HTTP %d).", doc_id, resp.status_code)
            return True
        else:
            log.warning("[%s] Discord returned HTTP %d: %s", doc_id, resp.status_code, resp.text[:200])
            return False

    except requests.exceptions.Timeout:
        log.error("[%s] Discord request timed out after %ds.", doc_id, REQUEST_TIMEOUT_SEC)
        return False
    except requests.exceptions.ConnectionError as exc:
        log.error("[%s] Discord connection error: %s", doc_id, exc)
        return False
    except Exception as exc:
        log.error("[%s] Unexpected error sending Discord alert: %s", doc_id, exc)
        return False

# ---------------------------------------------------------------------------
# State write-back (the idempotency lock)
# ---------------------------------------------------------------------------

def mark_discord_sent(db: firestore.Client, doc_id: str) -> None:
    """
    CRITICAL: Writes discord_sent=True back to the Firestore document
    immediately after a successful Discord POST.

    Why this matters: The daemon continuously watches /emergencies. Without
    this write-back, every polling cycle (or every on_snapshot event) would
    re-trigger the same alert, flooding Discord with duplicates.
    By setting discord_sent=True, we create a persistent, Firestore-level
    idempotency lock that survives daemon restarts — unlike an in-memory set.

    Uses update() (not set()) so we only touch this one field and don't
    accidentally clobber other fields written by other agents in the swarm.
    """
    try:
        db.collection("emergencies").document(doc_id).update({
            "discord_sent": True,
        })
        log.info("[%s] ✓ Firestore: discord_sent=True written.", doc_id)
    except Exception as exc:
        log.error(
            "[%s] FAILED to write discord_sent=True — alert may duplicate on next cycle: %s",
            doc_id, exc,
        )

# ---------------------------------------------------------------------------
# Core processing logic (shared by both on_snapshot and polling paths)
# ---------------------------------------------------------------------------

def process_doc(db: firestore.Client, doc_id: str, doc: dict) -> None:
    """
    Evaluates a single Firestore document against the trigger conditions,
    sends the Discord alert, and writes the idempotency flag on success.

    Trigger conditions (both must be true):
      1. status == "dispatched"
      2. discord_sent is missing (KeyError) OR discord_sent is falsy
    """
    # Condition 1: status gate
    if doc.get("status") != "dispatched":
        return  # Not ready for dispatch alert yet

    # Condition 2: deduplication gate — skip if already notified
    # dict.get() returns None (falsy) when the key is absent, so a missing
    # discord_sent key is treated identically to discord_sent=False.
    if doc.get("discord_sent"):
        return  # Already sent; skip silently

    severity = int(doc.get("severity", 0))
    hazard   = doc.get("hazard_type", "unknown")
    log.info(
        "[%s] Triggered → status=dispatched, severity=%d, hazard=%s",
        doc_id, severity, hazard,
    )

    # Build message and resolve routing
    payload     = build_discord_payload(doc)
    webhook_url = resolve_webhook(severity)
    channel     = "HIGH-PRIORITY" if severity >= 4 else "general"
    log.info("[%s] Routing to %s channel.", doc_id, channel)

    # Send alert
    success = send_discord_alert(payload, webhook_url, doc_id)

    # CRITICAL: Write discord_sent=True ONLY on confirmed 2xx success.
    # If Discord returns an error, we leave discord_sent unset so the
    # next polling cycle will retry. This gives us at-least-once delivery.
    if success:
        mark_discord_sent(db, doc_id)

# ---------------------------------------------------------------------------
# Path A — Real-time on_snapshot listener (preferred)
# ---------------------------------------------------------------------------

def start_snapshot_listener(db: firestore.Client) -> threading.Event:
    """
    Registers an on_snapshot callback on the /emergencies collection.
    Firestore pushes change events in real-time over a persistent gRPC stream,
    making this far more responsive than polling (sub-second latency).

    Returns a threading.Event that is set when the listener is confirmed alive.
    on_snapshot runs the callback in a background thread managed by the SDK.
    """
    ready = threading.Event()

    def on_snapshot(col_snapshot, changes, read_time):
        """
        Called by Firestore SDK on initial load and on every subsequent change.
        `changes` is a list of DocumentChange objects; type is ADDED, MODIFIED, or REMOVED.
        We only care about ADDED and MODIFIED (a doc moving to dispatched status is a MODIFIED event).
        """
        if not ready.is_set():
            ready.set()  # Signal that the first snapshot has arrived

        for change in changes:
            # REMOVED documents are irrelevant; skip them
            if change.type.name == "REMOVED":
                continue
            doc_id  = change.document.id
            doc     = change.document.to_dict() or {}
            process_doc(db, doc_id, doc)

    col_ref = db.collection("emergencies")

    # on_snapshot returns an unsubscribe callable; we keep a reference
    # so we can gracefully shut down if needed (not used here, but good practice).
    _unsubscribe = col_ref.on_snapshot(on_snapshot)

    log.info("on_snapshot listener registered on /emergencies.")
    return ready

# ---------------------------------------------------------------------------
# Path B — Robust polling loop (fallback)
# ---------------------------------------------------------------------------

def polling_loop(db: firestore.Client) -> None:
    """
    Fallback strategy: poll Firestore every POLL_INTERVAL_SEC seconds.
    Scoped query fetches ONLY documents that are dispatched AND not yet notified,
    minimising Firestore read costs (billed per document read).
    """
    log.info("Starting polling loop (interval: %ds).", POLL_INTERVAL_SEC)

    # Compound query: fetch only docs that need processing
    # This is a targeted server-side filter — much cheaper than streaming all docs
    # and filtering client-side.
    query = (
        db.collection("emergencies")
        .where("status", "==", "dispatched")
        .where("discord_sent", "==", False)
    )

    while True:
        try:
            docs = query.stream()
            for snap in docs:
                process_doc(db, snap.id, snap.to_dict() or {})
        except Exception as exc:
            log.error("Polling error — will retry in %ds: %s", POLL_INTERVAL_SEC, exc)

        time.sleep(POLL_INTERVAL_SEC)

# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main():
    log.info("=== SentinelMind Discord Actuator Daemon ===")

    # Validate webhooks before connecting to Firebase
    if not WEBHOOK_GENERAL and not WEBHOOK_HIGH_PRIORITY:
        log.error(
            "Neither DISCORD_WEBHOOK_URL nor DISCORD_ALERT_WEBHOOK_URL is set in .env. "
            "Alerts cannot be sent. Exiting."
        )
        sys.exit(1)
    if not WEBHOOK_GENERAL:
        log.warning("DISCORD_WEBHOOK_URL not set — severity 1-3 alerts will be suppressed.")
    if not WEBHOOK_HIGH_PRIORITY:
        log.warning("DISCORD_ALERT_WEBHOOK_URL not set — severity 4-5 alerts will fall back to general channel.")

    db = init_firestore()

    # Attempt to start the real-time on_snapshot listener.
    # It runs in a background thread managed by the Firestore SDK.
    # We then block the main thread with a keep-alive loop so the process
    # doesn't exit (the daemon pattern).
    try:
        ready_event = start_snapshot_listener(db)

        # Wait up to 15 s for the first snapshot to confirm the stream is live.
        if not ready_event.wait(timeout=15):
            log.warning("on_snapshot did not receive initial snapshot within 15s — falling back to polling.")
            polling_loop(db)   # Blocking fallback
        else:
            log.info("Real-time listener is live. Daemon running — press Ctrl+C to stop.")
            # Keep main thread alive; on_snapshot callbacks fire in background threads.
            while True:
                time.sleep(60)

    except KeyboardInterrupt:
        log.info("Shutdown signal received. Exiting.")
        sys.exit(0)
    except Exception as exc:
        log.error("Fatal error in listener setup: %s — falling back to polling.", exc)
        polling_loop(db)


if __name__ == "__main__":
    main()