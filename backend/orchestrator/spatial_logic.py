import math


def haversine_distance(coord1: dict, coord2: dict) -> float | None:
    try:
        lat1 = coord1.get("lat") if coord1.get("lat") is not None else coord1.get("latitude")
        lon1 = coord1.get("lng") if coord1.get("lng") is not None else coord1.get("longitude")
        lat2 = coord2.get("lat") if coord2.get("lat") is not None else coord2.get("latitude")
        lon2 = coord2.get("lng") if coord2.get("lng") is not None else coord2.get("longitude")
        lat1 = float(lat1); lon1 = float(lon1); lat2 = float(lat2); lon2 = float(lon2)
    except (TypeError, ValueError):
        return None

    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def detect_duplicates(new_event: dict, existing_events, threshold_meters: float = 500) -> str | None:
    new_loc = new_event.get("location") or {}
    if not isinstance(new_loc, dict):
        new_loc = {}
    new_lat = new_loc.get("lat") or new_event.get("latitude")
    new_lng = new_loc.get("lng") or new_event.get("longitude")
    if new_lat is None or new_lng is None:
        return None

    new_type = new_event.get("hazard_type")
    if not new_type:
        return None

    new_coord = {"lat": new_lat, "lng": new_lng}

    for existing in existing_events:
        if not hasattr(existing, "id"):
            existing_dict = existing
        else:
            existing_dict = existing if isinstance(existing, dict) else existing.to_dict()

        if isinstance(existing, dict):
            existing_data = existing
        elif hasattr(existing, "to_dict"):
            existing_data = existing.to_dict()
        else:
            continue

        existing_type = existing_data.get("hazard_type")
        if not existing_type or existing_type != new_type:
            continue

        existing_loc = existing_data.get("location") or {}
        ex_lat = existing_loc.get("lat") if isinstance(existing_loc, dict) else existing_data.get("latitude")
        ex_lng = existing_loc.get("lng") if isinstance(existing_loc, dict) else existing_data.get("longitude")
        if ex_lat is None or ex_lng is None:
            continue

        distance = haversine_distance(new_coord, {"lat": ex_lat, "lng": ex_lng})
        if distance is None:
            continue

        doc_id = existing.id if hasattr(existing, "id") else existing_data.get("id")
        if distance <= threshold_meters and doc_id:
            return doc_id

    return None