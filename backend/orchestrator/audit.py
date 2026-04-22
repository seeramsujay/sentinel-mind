import os
import time
from datetime import datetime
from firebase_admin import firestore
from .auth import SentinelAuth


class GovernanceAudit:
    @staticmethod
    def log_audit(emergency_id: str, audit_text: str, db=None):
        if not emergency_id or not audit_text:
            print(f"[GovernanceAudit] Skipped — missing emergency_id or audit_text.")
            return
        if db is None:
            db = SentinelAuth.get_firestore()
        doc_ref = db.collection("emergencies").document(emergency_id)
        try:
            doc_ref.update({
                "intelligence.fairness_audit": audit_text,
                "intelligence.audited_at": time.time()
            })
            print(f"[GovernanceAudit] Audit logged for {emergency_id}")
        except Exception as e:
            print(f"[GovernanceAudit] Failed to log audit: {e}")

    @staticmethod
    def log_hitl_flag(emergency_id, reasoning):
        """Logs a mandatory human-in-the-loop safety override."""
        db = SentinelAuth.get_firestore()
        doc_ref = db.collection('emergencies').document(emergency_id)
        try:
            doc_ref.update({
                "intelligence.hitl_flag": True,
                "intelligence.hitl_reason": reasoning,
                "intelligence.flagged_at": firestore.SERVER_TIMESTAMP
            })
            print(f"HITL Flagged for {emergency_id}")
        except Exception as e:
            print(f"HITL Log Error: {e}")

    @staticmethod
    def approve_dispatch(emergency_id):
        """Manually approves an emergency that was flagged for HITL."""
        db = SentinelAuth.get_firestore()
        doc_ref = db.collection('emergencies').document(emergency_id)
        try:
            doc_ref.update({
                "status": "dispatched",
                "intelligence.hitl_approved_at": time.time()
            })
            print(f"[GovernanceAudit] HITL override approved for {emergency_id}")
            return True
        except Exception as e:
            print(f"[GovernanceAudit] Failed to approve dispatch: {e}")
            return False


def hitl_daemon(poll_interval: int = 10):
    """Polls for emergencies flagged awaiting_human_approval — blocks until human approves."""
    db = SentinelAuth.get_firestore()
    flagged_log = "/tmp/sentinelmind_hitl.json"

    def load_flagged():
        try:
            import json
            with open(flagged_log) as f:
                return set(json.load(f))
        except (FileNotFoundError, ImportError):
            return set()

    def save_flagged(ids):
        import json
        try:
            with open(flagged_log, "w") as f:
                json.dump(list(ids), f)
        except OSError as e:
            print(f"[HITL Daemon] Failed to persist flag log: {e}")

    print(f"[HITL Daemon] Starting — poll interval {poll_interval}s …")

    while True:
        try:
            col_ref = db.collection("emergencies")
            flagged = load_flagged()
            for doc in col_ref.stream():
                doc_dict = doc.to_dict()
                if doc_dict is None:
                    continue
                if doc_dict.get("status") != "awaiting_human_approval":
                    continue
                if doc.id in flagged:
                    continue

                reason = doc_dict.get("intelligence", {}).get("hitl_reason", "No reason provided") if isinstance(doc_dict.get("intelligence"), dict) else "No reason provided"
                print(f"[HITL Daemon] FLAGGED {doc.id}: {reason}")
                flagged.add(doc.id)
            save_flagged(flagged)
            time.sleep(poll_interval)
        except Exception as e:
            print(f"[HITL Daemon] Error — sleeping {poll_interval}s: {e}")
            time.sleep(poll_interval)