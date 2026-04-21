import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Path to your service account key
SERVICE_ACCOUNT_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'service-account.json')

def seed_data():
    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        print(f"ERROR: {SERVICE_ACCOUNT_PATH} not found. Please place your Firebase Service Account JSON file in the root.")
        return

    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    print("Seeding 'emergencies' collection...")
    emergencies = [
        {
            "hazard_type": "Flood",
            "urgency": "P1",
            "status": "triaged",
            "timestamp": firestore.SERVER_TIMESTAMP,
            "location": {"lat": 16.5062, "lng": 80.6480, "address": "Vijayawada, Andhra Pradesh"},
            "intelligence": {"language_preference": "en"}
        },
        {
            "hazard_type": "Landslide",
            "urgency": "P2",
            "status": "triaged",
            "timestamp": firestore.SERVER_TIMESTAMP,
            "location": {"lat": 17.6868, "lng": 83.2185, "address": "Visakhapatnam, Andhra Pradesh"},
            "intelligence": {"language_preference": "te"}
        }
    ]

    for item in emergencies:
        doc_ref = db.collection('emergencies').add(item)
        print(f"Added emergency: {doc_ref[1].id}")

    print("Seeding 'resources' collection...")
    resources = [
        {
            "unit_id": "AMB-01",
            "resource_type": "Ambulance",
            "status": "available",
            "location": {"lat": 16.5150, "lng": 80.6400}
        },
        {
            "unit_id": "BOAT-01",
            "resource_type": "Rescue Boat",
            "status": "available",
            "location": {"lat": 16.4800, "lng": 80.6800}
        }
    ]

    for item in resources:
        db.collection('resources').document(item['unit_id']).set(item)
        print(f"Added/Updated resource: {item['unit_id']}")

    print("Seeding complete.")

if __name__ == "__main__":
    seed_data()
