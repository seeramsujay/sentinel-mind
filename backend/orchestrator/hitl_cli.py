import sys
from .auth import SentinelAuth
from .audit import GovernanceAudit

def list_pending():
    db = SentinelAuth.get_firestore()
    pending = db.collection('emergencies').where('status', '==', 'awaiting_human_approval').get()
    
    if not pending:
        print("No emergencies awaiting human approval.")
        return
    
    print("\n--- PENDING HUMAN APPROVAL ---")
    for doc in pending:
        data = doc.to_dict()
        intel = data.get('intelligence', {})
        print(f"ID: {doc.id}")
        print(f"Type: {data.get('hazard_type')}")
        print(f"Reason: {intel.get('hitl_reason', 'No reason provided')}")
        print(f"Bias Score: {intel.get('bias_score', 'N/A')}")
        print("-" * 30)

def approve(doc_id):
    GovernanceAudit.approve_dispatch(doc_id)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 -m backend.orchestrator.hitl_cli [list|approve <id>]")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "list":
        list_pending()
    elif cmd == "approve" and len(sys.argv) == 3:
        approve(sys.argv[2])
    else:
        print("Invalid command.")
