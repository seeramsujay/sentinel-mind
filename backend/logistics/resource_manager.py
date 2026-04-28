from ..orchestrator.auth import SentinelAuth
from ..orchestrator.spatial_logic import haversine_distance

class ResourceManager:
    """Matches emergencies with the closest suitable and available responder unit."""
    
    def __init__(self):
        self.db = SentinelAuth.get_firestore()

    def find_best_responder(self, emergency_loc, resource_type):
        """
        Finds the closest available resource of a specific type.
        Args:
            emergency_loc: dict {'lat', 'lng'}
            resource_type: string (e.g., 'Ambulance', 'Rescue Boat')
        Returns:
            dict with resource data or None
        """
        resources_ref = self.db.collection('resources')
        # Simple query for availability and type
        query = resources_ref.where('status', '==', 'available')\
                            .where('resource_type', '==', resource_type)
        
        available_units = query.get()
        
        best_unit = None
        min_distance = float('inf')

        for doc in available_units:
            res_data = doc.to_dict()
            res_loc = res_data.get('location')
            
            if res_loc:
                distance = haversine_distance(emergency_loc, res_loc)
                if distance is not None and distance < min_distance:
                    min_distance = distance
                    best_unit = res_data
                    best_unit['id'] = doc.id # Ensure we have the firestore ID
                    
        return best_unit
