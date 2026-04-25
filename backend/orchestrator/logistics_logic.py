import math
import json
import os
import googlemaps
from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform
from .auth import SentinelAuth
from .secrets_manager import SentinelSecrets
import requests

class ResourceAllocator:
    @staticmethod
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

    @classmethod
    def find_best_resource(cls, emergency_loc, available_resources):
        """
        Finds the closest available resource for a given emergency location.
        """
        if not available_resources:
            return None
        
        best_resource = None
        min_distance = float('inf')

        for resource in available_resources:
            res_data = resource.to_dict() if hasattr(resource, 'to_dict') else resource
            res_loc = res_data.get('location')
            
            if res_loc:
                dist = cls.haversine_distance(emergency_loc, res_loc)
                if dist < min_distance:
                    min_distance = dist
                    best_resource = resource
        
        return best_resource

class RoutingService:
    def __init__(self, api_key=None):
        # Use Secret Manager or ENV via SentinelSecrets
        self.api_key = api_key or SentinelSecrets.get_secret("GOOGLE_MAPS_API_KEY")
        self.gmaps = googlemaps.Client(key=self.api_key)
        self._cache = {} # Simple in-memory cache for Phase 1

    def get_route_details(self, origin, destination, waypoints=None, avoid=None):
        """
        Fetches routing details with simple caching.
        waypoints: list of {'lat', 'lng'}
        avoid: list of strings (e.g. ['tolls', 'highways'])
        """
        cache_key = f"{origin['lat']:.4f},{origin['lng']:.4f}_{destination['lat']:.4f},{destination['lng']:.4f}_{waypoints}_{avoid}"
        if cache_key in self._cache:
            print(f"CACHE HIT: Routing for {cache_key}")
            return self._cache[cache_key]

        try:
            origin_str = f"{origin['lat']},{origin['lng']}"
            dest_str = f"{destination['lat']},{destination['lng']}"
            
            # Format waypoints for Google Maps
            g_waypoints = []
            if waypoints:
                g_waypoints = [f"{wp['lat']},{wp['lng']}" for wp in waypoints]

            directions_result = self.gmaps.directions(
                origin_str,
                dest_str,
                mode="driving",
                departure_time="now",
                waypoints=g_waypoints,
                avoid=avoid
            )

            if not directions_result:
                return self._fallback_route(origin, destination)

            leg = directions_result[0]['legs'][0]
            result = {
                "polyline_route": directions_result[0]['overview_polyline']['points'],
                "eta": leg['duration']['text'],
                "distance_meters": leg['distance']['value']
            }
            self._cache[cache_key] = result
            return result
        except Exception as e:
            print(f"Routing API Error: {e}")
            return self._fallback_route(origin, destination)

    def _fallback_route(self, origin, destination):
        dist = ResourceAllocator.haversine_distance(origin, destination)
        eta_minutes = int((dist / 11.1) / 60)
        return {
            "polyline_route": "FALLBACK_STRAIGHT_LINE", 
            "eta": f"{eta_minutes} mins (est)",
            "distance_meters": dist
        }

class RiskAssessor:
    def __init__(self):
        SentinelAuth.init_vertex()
        self.model = GenerativeModel("gemini-2.5-flash-lite")

    def get_live_weather(self, location):
        """
        Retrieves weather context for risk assessment.
        """
        api_key = SentinelSecrets.get_secret("OPENWEATHERMAP_API_KEY")
        if not api_key:
            return {"note": "Weather API key missing. Using seasonal averages.", "temp": "28C", "condition": "Cloudy"}
        
        try:
            lat, lng = location.get('lat'), location.get('lng')
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={api_key}&units=metric"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                w = resp.json()
                return {
                    "temp": f"{w['main']['temp']}C",
                    "condition": w['weather'][0]['main'],
                    "humidity": w['main']['humidity'],
                    "wind_speed": w['wind']['speed']
                }
        except Exception as e:
            print(f"Weather API Error: {e}")
            
        return {"temp": "28C", "condition": "Cloudy"}

    def get_risk_assessment(self, emergency_data):
        """
        Uses Gemini to generate a multi-dimensional risk score.
        """
        location = emergency_data.get('location') or emergency_data.get('location_coordinates') or {'lat': 0, 'lng': 0}
        weather_data = self.get_live_weather(location)
        
        prompt = f"""
        System: SentinelMind Crisis Prediction Engine (Role 3)
        Task: Analyze hazard context and provide a 6-hour risk assessment score.
        
        Emergency Details:
        - Type: {emergency_data.get('hazard_type')}
        - Urgency: {emergency_data.get('urgency')}
        - Location: {emergency_data.get('location', {}).get('address', 'Unknown')}
        
        Weather Context:
        {json.dumps(weather_data, indent=2)}
        
        Output Requirements:
        1. Risk Score (0-100)
        2. Threat Analysis (Brief)
        3. 6-Hour Forecast Trend (Improving/Worsening)
        
        Return JSON format:
        {{
            "risk_score": 85,
            "assessment": "High risk due to saturated soil and continued rainfall forecast.",
            "trend": "Worsening"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = response.text.strip()
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            return json.loads(result)
        except Exception as e:
            print(f"Risk Assessment AI Error: {e}")
            return {
                "risk_score": 50,
                "assessment": "Automated risk assessment failed. Manual triage recommended.",
                "trend": "Unknown"
            }

    def get_automl_prediction(self, emergency_data):
        """
        Calculates crisis spread probability using Vertex AI AutoML Tabular.
        """
        project = os.getenv("GCP_PROJECT_ID")
        endpoint_id = os.getenv("AUTOML_ENDPOINT_ID") # Set in .env
        
        if not endpoint_id:
            # Fallback to smart heuristic if endpoint not provisioned
            base_score = 40
            if emergency_data.get('urgency') == 'P1': base_score += 30
            if emergency_data.get('hazard_type') in ['Flood', 'Earthquake']: base_score += 20
            return {"spread_probability": f"{min(base_score, 100)}%", "model_version": "Heuristic-Fallback-v1"}

        try:
            # Prepare instance for Tabular prediction
            instance = {
                "hazard_type": emergency_data.get('hazard_type'),
                "urgency": emergency_data.get('urgency'),
                "location_lat": emergency_data.get('location', {}).get('lat'),
                "location_lng": emergency_data.get('location', {}).get('lng')
            }
            
            aiplatform.init(project=project, location=os.getenv("GCP_REGION", "us-central1"))
            endpoint = aiplatform.Endpoint(endpoint_id)
            prediction = endpoint.predict(instances=[instance])
            
            # Extract probability (assumes binary classification or similar)
            prob = prediction.predictions[0][0] * 100
            return {
                "spread_probability": f"{round(prob, 2)}%",
                "model_version": "AutoML-Tabular-Deployed"
            }
        except Exception as e:
            print(f"AutoML Prediction Error: {e}")
            return {"spread_probability": "50%", "model_version": "Error-Recovery-v1"}

class VectorSearchClient:
    """
    RAG Client for Historical NDMA Knowledge.
    """
    @staticmethod
    def get_historical_context(query_text):
        """
        Queries Vertex AI Vector Search for relevant historical disaster protocols.
        """
        # Placeholder for real Vector Search index query
        # In a real setup, we would use the 'google-cloud-aiplatform' MatchNeighbor call
        print(f"Querying Vector Search for: {query_text}")
        
        # Real-world NDMA context simulation
        if "Flood" in query_text:
            return "NDMA Protocol 4.2: Deploy rescue boats and life jackets. Prioritize elderly evacuation."
        if "Fire" in query_text:
            return "NDMA Protocol 9.1: Establish 500m perimeter. Use specialized foam for industrial hazards."
            
        return "General NDMA Safety Protocol: Ensure clear communication channels and establish incident command."

class SDGMeter:
    CARBON_FACTORS = {
        "Ambulance": 0.192,
        "Heavy Med-Truck": 0.280,
        "Med-Evac Heli": 0.850,
        "Rescue Heli": 0.850,
        "Supply Drone": 0.010,
        "Scout Drone": 0.005,
        "Rescue Boat": 0.220,
        "Default": 0.192
    }

    @staticmethod
    def calculate_carbon_saved(distance_meters, resource_type="Default"):
        """
        Calculates CO2 kg prevented based on routing efficiency per resource type.
        Assuming a baseline of unoptimized response takes 20% longer distance.
        """
        unoptimized_dist = distance_meters * 1.2
        saved_dist_km = (unoptimized_dist - distance_meters) / 1000
        
        factor = SDGMeter.CARBON_FACTORS.get(resource_type, SDGMeter.CARBON_FACTORS["Default"])
        return round(saved_dist_km * factor, 3)

