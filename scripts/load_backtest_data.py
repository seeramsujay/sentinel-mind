import firebase_admin
from firebase_admin import firestore, credentials
import os
import random
import time

# Use the same auth logic or direct firestore client
project_id = os.getenv("GCP_PROJECT_ID", "slingshot-amd")
db = firestore.Client(project=project_id)

def load_backtest_data():
    print(f"Propagating 100 backtesting signals to Firestore (Project: {project_id})...")
    
    hazards = ["Flood", "Flash Flood", "River Overflow", "Cyclone Surge"]
    # Coordinates centered around Andhra Pradesh (Vijayawada/Guntur region)
    base_lat = 16.5062
    base_lng = 80.6480
    
    batch = db.batch()
    for i in range(100):
        doc_id = f"backtest_signal_{i:03d}"
        doc_ref = db.collection('emergencies').document(doc_id)
        
        # Jitter coordinates slightly
        lat = base_lat + (random.random() - 0.5) * 0.5
        lng = base_lng + (random.random() - 0.5) * 0.5
        
        data = {
            "hazard_type": random.choice(hazards),
            "urgency": random.choice(["P1", "P1", "P2"]), # Higher P1 frequency for stress
            "location": {
                "address": f"Andhra Pradesh Cluster {i}",
                "lat": lat,
                "lng": lng
            },
            "status": "awaiting_dispatch",
            "timestamp": firestore.SERVER_TIMESTAMP,
            "is_backtest": True,
            "description": f"Historical NDMA Signal {i}: Urgent flood response required."
        }
        batch.set(doc_ref, data)
        
        if (i + 1) % 50 == 0:
            batch.commit()
            print(f"Committed {i+1} signals...")
            batch = db.batch()

    print("Backtesting data LOADED successfully.")

if __name__ == "__main__":
    load_backtest_data()
