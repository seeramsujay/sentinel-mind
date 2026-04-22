import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

class MapsRoutesClient:
    """Wrapper for Google Maps Routes API (v2)."""
    
    BASE_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            from ..orchestrator.secrets_manager import SentinelSecrets
            self.api_key = SentinelSecrets.get_secret("GOOGLE_MAPS_API_KEY")

    def get_route(self, origin, destination):
        """
        Calculates a route between origin and destination.
        Args:
            origin: dict {'lat': float, 'lng': float}
            destination: dict {'lat': float, 'lng': float}
        Returns:
            dict with polyline, duration_seconds, and distance_meters or None
        """
        if not self.api_key:
            print("ERROR: Maps API Key missing.")
            return None

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline"
        }

        payload = {
            "origin": {
                "location": {"latLng": {"latitude": origin['lat'], "longitude": origin['lng']}}
            },
            "destination": {
                "location": {"latLng": {"latitude": destination['lat'], "longitude": destination['lng']}}
            },
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE",
            "computeAlternativeRoutes": False,
            "routeModifiers": {
                "avoidTolls": False,
                "avoidHighways": False,
                "avoidFerries": False
            }
        }

        try:
            response = requests.post(self.BASE_URL, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if 'routes' in data and len(data['routes']) > 0:
                    route = data['routes'][0]
                    # Format "duration": "123s" -> 123
                    duration_str = route.get('duration', '0s')
                    duration_secs = int(duration_str.replace('s', ''))
                    
                    return {
                        "polyline": route.get('polyline', {}).get('encodedPolyline'),
                        "duration": duration_secs,
                        "distance": route.get('distanceMeters', 0)
                    }
            else:
                print(f"Maps API Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Maps Client Exception: {e}")
            return None
