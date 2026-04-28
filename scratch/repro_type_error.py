import sys
import os

# Mocking the environment
os.environ["GEMINI_API_KEY"] = "mock"
os.environ["GOOGLE_CLOUD_PROJECT"] = "mock-project"

sys.path.insert(0, os.getcwd())

from backend.logistics.resource_manager import ResourceManager
from unittest.mock import MagicMock

def test_repro_type_error():
    rm = ResourceManager()
    # Mocking haversine_distance to return None
    import backend.logistics.resource_manager as rm_module
    rm_module.haversine_distance = MagicMock(return_value=None)
    
    mock_units = [MagicMock()]
    mock_units[0].to_dict.return_value = {"location": {"lat": 0, "lng": 0}}
    
    rm.db.collection.return_value.where.return_value.where.return_value.get.return_value = mock_units
    
    print("Testing for TypeError...")
    try:
        rm.find_best_responder({"lat": 1, "lng": 1}, "Ambulance")
        print("No error (unexpected if haversine returns None)")
    except TypeError as e:
        print(f"Caught expected TypeError: {e}")
    except Exception as e:
        print(f"Caught unexpected exception: {e}")

if __name__ == "__main__":
    # We need to mock SentinelAuth before importing ResourceManager if it calls get_firestore on init
    # But ResourceManager calls it in __init__
    from backend.orchestrator.auth import SentinelAuth
    SentinelAuth.get_firestore = MagicMock()
    
    test_repro_type_error()
