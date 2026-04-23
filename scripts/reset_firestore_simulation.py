import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

# Path to service account logic
SERVICE_ACCOUNT_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'service-account.json')

def reset_simulation_state():
    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        print(f"ERROR: {SERVICE_ACCOUNT_PATH} not found.")
        return

    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()

    print("Resetting Emergency states...")
    emergencies = db.collection('emergencies').get()
    for doc in emergencies:
        # Reset to 'triaged' and clear Role 3 data
        doc.reference.update({
            "status": "awaiting_dispatch",
            "resource_assignment": firestore.DELETE_FIELD,
            "intelligence": firestore.DELETE_FIELD,
            "severity": firestore.DELETE_FIELD,
            "escalated": firestore.DELETE_FIELD,
            "escalation_note": firestore.DELETE_FIELD
        })
    print(f"  ✓ Reset {len(emergencies)} emergencies.")

    print("Resetting Resource states...")
    resources = db.collection('resources').get()
    for doc in resources:
        doc.reference.update({
            "status": "available",
            "assigned_to": firestore.DELETE_FIELD,
            "last_dispatched": firestore.DELETE_FIELD,
            "estimated_mission_minutes": firestore.DELETE_FIELD
        })
    print(f"  ✓ Reset {len(resources)} resources.")

    print("Simulation state reset complete.")

if __name__ == "__main__":
    reset_simulation_state()
