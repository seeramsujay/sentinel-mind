import time
from ..orchestrator.auth import SentinelAuth
from .resource_manager import ResourceManager
from .maps_client import MapsRoutesClient

class LogisticsDaemon:
    """Listens for dispatch requests and calculates optimal routing."""
    
    def __init__(self):
        self.db = SentinelAuth.get_firestore()
        self.resource_mgr = ResourceManager()
        self.maps_client = MapsRoutesClient()

    def on_snapshot(self, col_snapshot, changes, read_time):
        """Watcher for emergencies awaiting dispatch."""
        for change in changes:
            doc = change.document
            data = doc.to_dict()
            
            if (change.type.name == 'ADDED' or change.type.name == 'MODIFIED') and data.get('status') == 'awaiting_dispatch':
                self.process_dispatch(doc, data)

    def process_dispatch(self, doc, data):
        """Matches a resource and calculates the route."""
        print(f"LOGISTICS: Processing dispatch for {doc.id}")
        
        emergency_loc = data.get('location')
        # Map hazard type to resource requirement (simplified logic)
        resource_req = "Rescue Boat" if data.get('hazard_type') == "Flood" else "Ambulance"
        
        # 1. Match resource
        best_unit = self.resource_mgr.find_best_responder(emergency_loc, resource_req)
        
        if not best_unit:
            print(f"LOGISTICS: No available {resource_req} units. Setting to CONFLICT.")
            doc.reference.update({"status": "conflict"})
            return

        # 2. Get route
        route = self.maps_client.get_route(best_unit['location'], emergency_loc)
        
        if not route:
            print(f"LOGISTICS: Maps routing failed for {doc.id}")
            return

        # 3. Update Firestore
        # Mock carbon saved calculation: distance in km * 0.15 kg CO2
        distance_km = route['distance'] / 1000.0
        carbon_saved = round(distance_km * 0.15, 2)
        
        doc.reference.update({
            "status": "dispatched",
            "resource_assignment": {
                "unit_id": best_unit['id'],
                "resource_type": best_unit['resource_type'],
                "polyline_route": route['polyline'],
                "eta": f"{route['duration'] // 60} mins",
                "carbon_saved": carbon_saved
            }
        })
        
        # Mark resource as busy
        self.db.collection('resources').document(best_unit['id']).update({"status": "busy"})
        print(f"LOGISTICS: Dispatched {best_unit['id']} to {doc.id} (ETA: {route['duration'] // 60}m)")

    def run(self):
        print("SentinelMind Logistics Engine Active. Monitoring /emergencies...")
        query = self.db.collection('emergencies').where('status', '==', 'awaiting_dispatch')
        watch = query.on_snapshot(self.on_snapshot)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping Logistics Engine...")
            watch.unsubscribe()

if __name__ == "__main__":
    daemon = LogisticsDaemon()
    daemon.run()
