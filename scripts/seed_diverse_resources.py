import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

# Path to service account logic
SERVICE_ACCOUNT_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'service-account.json')

def seed_diverse_resources():
    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        print(f"ERROR: {SERVICE_ACCOUNT_PATH} not found.")
        return

    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    resources_col = db.collection('resources')

    # Diverse fleet spanning diverse regions of India
    diverse_resources = [
        {"unit_id": "AMB-HYD-01", "resource_type": "Ambulance", "location": {"lat": 17.3850, "lng": 78.4867}, "status": "available"},
        {"unit_id": "HELI-UK-01", "resource_type": "Med-Evac Heli", "location": {"lat": 30.3165, "lng": 78.0322}, "status": "available"},
        {"unit_id": "DRONE-KL-01", "resource_type": "Supply Drone", "location": {"lat": 9.9312, "lng": 76.2673}, "status": "available"},
        {"unit_id": "BOAT-OD-01", "resource_type": "Rescue Boat", "location": {"lat": 20.2961, "lng": 85.8245}, "status": "available"},
        {"unit_id": "TRUCK-MAH-01", "resource_type": "Heavy Med-Truck", "location": {"lat": 19.0760, "lng": 72.8777}, "status": "available"},
        {"unit_id": "AMB-TN-01", "resource_type": "Ambulance", "location": {"lat": 13.0827, "lng": 80.2707}, "status": "available"},
        {"unit_id": "HELI-AS-01", "resource_type": "Rescue Heli", "location": {"lat": 26.1158, "lng": 91.7086}, "status": "available"},
        {"unit_id": "DRONE-GJ-01", "resource_type": "Scout Drone", "location": {"lat": 23.0225, "lng": 72.5714}, "status": "available"},
        {"unit_id": "TRUCK-RJ-01", "resource_type": "Water Tanker", "location": {"lat": 26.9124, "lng": 75.7873}, "status": "available"},
        {"unit_id": "BOAT-AP-01", "resource_type": "Rescue Boat", "location": {"lat": 16.5062, "lng": 80.6480}, "status": "available"}
    ]

    print(f"Seeding {len(diverse_resources)} diverse resources...")
    for res in diverse_resources:
        resources_col.document(res['unit_id']).set(res)
        print(f"  ✓ Seeded {res['unit_id']} ({res['resource_type']})")

    print("Diverse resource seeding complete.")

if __name__ == "__main__":
    seed_diverse_resources()
