import time
import json
from .auth import SentinelAuth
from vertexai.generative_models import GenerativeModel

class ConflictDaemon:
    """Worker 3: The Conflict Resolution Brain"""
    def __init__(self):
        self.db = SentinelAuth.get_firestore()
        SentinelAuth.init_vertex()
        self.model = GenerativeModel("gemini-2.5-flash-lite")

    def resolve_conflict(self, unit_id, conflicting_docs):
        print(f"CONFLICT DETECTED: Unit {unit_id} double-booked for {len(conflicting_docs)} emergencies.")
        
        payload = []
        for doc in conflicting_docs:
            data = doc.to_dict()
            payload.append({
                "id": doc.id,
                "hazard_type": data.get("hazard_type"),
                "urgency": data.get("urgency"),
                "location": data.get("location")
            })

        prompt = f"""
        You are an AI Conflict Resolution Commander.
        Multiple disasters have been assigned the same response unit: {unit_id}.
        
        Disasters competing for this unit:
        {json.dumps(payload, indent=2)}
        
        Analyze the urgency, hazard_type, and assess prioritizing the most critical one.
        Return ONLY the string ID of the emergency that should KEEP the resource. No other text.
        """
        
        try:
            response = self.model.generate_content(prompt)
            winner_id = response.text.strip()
            print(f"GEMINI RESOLUTION: Priority awarded to {winner_id}")
            
            # Apply resolution
            for doc in conflicting_docs:
                if doc.id == winner_id:
                    print(f"WORKER_3: {doc.id} keeps resource {unit_id}.")
                else:
                    print(f"WORKER_3: REJECTING {doc.id} - returning to AWAITING_DISPATCH.")
                    doc.reference.update({
                        "status": "awaiting_dispatch",
                        "resource_assignment": None
                    })
        except Exception as e:
            print(f"Conflict resolution failed: {e}")

    def run(self):
        print("[main] Worker 3 (Conflict AI) Active. Scanning for double-bookings...")
        
        while True:
            try:
                dispatched = self.db.collection('emergencies').where('status', '==', 'dispatched').get()
                
                # Group by unit
                unit_map = {}
                for doc in dispatched:
                    data = doc.to_dict()
                    assignment = data.get('resource_assignment')
                    if assignment and 'unit_id' in assignment:
                        unit_id = assignment['unit_id']
                        if unit_id not in unit_map:
                            unit_map[unit_id] = []
                        unit_map[unit_id].append(doc)
                        
                for unit_id, docs in unit_map.items():
                    if len(docs) > 1:
                        self.resolve_conflict(unit_id, docs)
                        
                time.sleep(5)
            except Exception as e:
                print(f"Conflict Daemon Error: {e}")
                time.sleep(5)

if __name__ == "__main__":
    daemon = ConflictDaemon()
    daemon.run()
