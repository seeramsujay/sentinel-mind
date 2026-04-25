import firebase_admin
from firebase_admin import credentials, firestore
import os
import random
import uuid
from datetime import datetime, timedelta

def seed_dynamic_data():
    SERVICE_ACCOUNT_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'service-account.json')
    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        print(f"ERROR: {SERVICE_ACCOUNT_PATH} not found.")
        return

    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    col = db.collection('emergencies')

    # Hazard types and locations in India
    hazards = ["flood", "earthquake", "fire", "landslide", "cyclone", "medical", "structural_collapse", "chemical_spill"]
    locations = [
        {"name": "Mumbai", "lat": 19.0760, "lng": 72.8777},
        {"name": "Delhi", "lat": 28.6139, "lng": 77.2090},
        {"name": "Bangalore", "lat": 12.9716, "lng": 77.5946},
        {"name": "Hyderabad", "lat": 17.3850, "lng": 78.4867},
        {"name": "Chennai", "lat": 13.0827, "lng": 80.2707},
        {"name": "Kolkata", "lat": 22.5726, "lng": 88.3639},
        {"name": "Ahmedabad", "lat": 23.0225, "lng": 72.5714},
        {"name": "Pune", "lat": 18.5204, "lng": 73.8567},
        {"name": "Jaipur", "lat": 26.9124, "lng": 75.7873},
        {"name": "Lucknow", "lat": 26.8467, "lng": 80.9462}
    ]

    print(f"Seeding 50 dynamic incidents...")
    batch = db.batch()
    
    for i in range(50):
        loc = random.choice(locations)
        hazard = random.choice(hazards)
        severity = random.randint(1, 5)
        
        # Add random jitter to coordinates
        lat = float(loc["lat"]) + (random.random() - 0.5) * 2
        lng = float(loc["lng"]) + (random.random() - 0.5) * 5
        
        doc_id = str(uuid.uuid4())
        data = {
            "emergency_id": doc_id,
            "hazard_type": hazard,
            "location_coordinates": {"lat": lat, "lng": lng},
            "location": {"lat": lat, "lng": lng, "address": f"Sector {random.randint(1,99)}, {loc['name']}"},
            "severity": severity,
            "urgency": "P1" if severity >= 4 else "P2",
            "status": random.choice(["triaged", "awaiting_dispatch", "dispatched"]),
            "timestamp": datetime.now() - timedelta(minutes=random.randint(1, 1440)),
            "description": f"Simulation: {hazard.capitalize()} event detected near {loc['name']}. Immediate response required.",
            "intelligence": {
                "risk_score": random.randint(70, 99),
                "situation_report": f"Automated sensor network indicates increasing threshold for {hazard}.",
                "ndma_protocol": f"Protocol {random.choice(['Alpha', 'Beta', 'Gamma'])} engaged at {datetime.now().strftime('%H:%M:%S')}."
            }
        }
        
        doc_ref = col.document(doc_id)
        batch.set(doc_ref, data)
        
        if (i + 1) % 10 == 0:
            batch.commit()
            batch = db.batch()
            print(f"  {i + 1} incidents synced...")

    print("Dynamic seeding complete.")

if __name__ == "__main__":
    seed_dynamic_data()
