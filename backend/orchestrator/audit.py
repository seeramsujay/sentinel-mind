from .auth import SentinelAuth

class GovernanceAudit:
    """Logs AI reasoning and fairness metrics to Firestore for transparency."""
    
    @staticmethod
    def log_audit(emergency_id, audit_text):
        db = SentinelAuth.get_firestore()
        doc_ref = db.collection('emergencies').document(emergency_id)
        
        try:
            doc_ref.update({
                "intelligence.fairness_audit": audit_text,
                "intelligence.audited_at": firestore.SERVER_TIMESTAMP
            })
            print(f"Audit logged for {emergency_id}")
        except Exception as e:
            print(f"Governance Log Error: {e}")

from firebase_admin import firestore # Needed for SERVER_TIMESTAMP
