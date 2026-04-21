import math

def haversine_distance(coord1, coord2):
    """
    Calculate the great-circle distance between two points on the Earth 
    (specified in decimal degrees) in meters.
    """
    lat1, lon1 = coord1['lat'], coord1['lng']
    lat2, lon2 = coord2['lat'], coord2['lng']

    R = 6371000  # Radius of earth in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def detect_duplicates(new_event, existing_events, threshold_meters=500):
    """
    Detects if a new event is a duplicate of an existing one based on 
    spatial proximity and hazard type.
    """
    new_loc = new_event.get('location')
    new_type = new_event.get('hazard_type')

    if not new_loc or not new_type:
        return None

    for existing in existing_events:
        existing_data = existing.to_dict()
        existing_loc = existing_data.get('location')
        existing_type = existing_data.get('hazard_type')

        if existing_loc and existing_type == new_type:
            distance = haversine_distance(new_loc, existing_loc)
            if distance <= threshold_meters:
                return existing.id
                
    return None
