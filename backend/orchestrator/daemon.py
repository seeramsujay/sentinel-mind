"""
Orchestrator Daemon
Monitors /emergencies for triaged entries (duplicate check) and conflict entries (AI resolution).
"""

import os
import time
from .auth import SentinelAuth
from .spatial_logic import detect_duplicates
from .resolver import ConflictResolver
from .audit import GovernanceAudit

RESOLVED_LOG = "/tmp/sentinelmind_resolved.json"


def _load_resolved() -> set:
    try:
        import json
        with open(RESOLVED_LOG) as f:
            return set(json.load(f))
    except (FileNotFoundError, ImportError):
        return set()


def _save_resolved(resolved: set):
    import json
    try:
        with open(RESOLVED_LOG, "w") as f:
            json.dump(list(resolved), f)
    except OSError as e:
        print(f"[Orchestrator] Failed to persist resolved log: {e}")


class OrchestratorDaemon:
    def run(self):
        db = SentinelAuth.get_firestore()
        resolved = _load_resolved()
        resolver = ConflictResolver()
        print(f"[Orchestrator] Booted. Loaded {len(resolved)} resolved IDs.")
        print("[Orchestrator] Monitoring /emergencies …")

        while True:
            try:
                col_ref = db.collection("emergencies")
                for doc in col_ref.stream():
                    doc_dict = doc.to_dict()
                    if doc_dict is None:
                        continue

                    status = doc_dict.get("status")
                    doc_id = doc.id

                    if status == "triaged":
                        self._handle_triaged(doc, doc_dict, db)
                    elif status == "conflict" and doc_id not in resolved:
                        self._handle_conflict(doc, doc_dict, db, resolver)
                        resolved.add(doc_id)

                _save_resolved(resolved)
                time.sleep(5)

            except Exception as e:
                print(f"[Orchestrator] Error — sleeping 10s: {e}")
                time.sleep(10)

    def _handle_triaged(self, doc, data: dict, db):
        doc_id = doc.id
        existing = db.collection("emergencies").where(
            "status", "in", ["triaged", "awaiting_dispatch", "dispatched"]
        ).get()
        existing = [d for d in existing if d.id != doc_id]
        dup_id = detect_duplicates(data, existing)
        if dup_id:
            print(f"[Orchestrator] MERGED {doc_id} → {dup_id}")
            doc.reference.update({
                "status": "merged",
                "merged_into": dup_id,
                "intelligence.meta_note": f"Merged into {dup_id} via Proxy User Logic."
            })
        else:
            print(f"[Orchestrator] PROMOTED {doc_id} → awaiting_dispatch")
            doc.reference.update({"status": "awaiting_dispatch"})

    def _handle_conflict(self, doc, data: dict, db, resolver):
        doc_id = doc.id
        print(f"[Orchestrator] RESOLVING CONFLICT: {doc_id}")

        resources = [
            r.to_dict() for r in db.collection("resources")
            .where("status", "==", "available").get()
        ]
        conflicts = [data]
        decision = resolver.resolve(conflicts, resources)
        if not decision or "decisions" not in decision:
            print(f"[Orchestrator] No decision from resolver for {doc_id}")
            return

        for d in decision["decisions"]:
            if d.get("emergency_id") != doc_id:
                continue
            
            # HITL Override Logic
            is_hitl = d.get("hitl_mandatory", False)
            final_status = "awaiting_human_approval" if is_hitl else ("dispatched" if d.get("action") == "dispatch" else "awaiting_human_approval")
            
            doc.reference.update({
                "status": final_status,
                "resource_assignment.unit_id": d.get("resource_id"),
                "intelligence.bias_score": d.get("bias_score", 0),
                "intelligence.fairness_audit": d.get("fairness_audit", "")
            })
            
            if is_hitl:
                GovernanceAudit.log_hitl_flag(doc_id, d.get("hitl_reasoning", "Bias risk detected."), db)
            else:
                print(f"[Orchestrator] RESOLVED {doc_id} → {d.get('action')}")


if __name__ == "__main__":
    OrchestratorDaemon().run()