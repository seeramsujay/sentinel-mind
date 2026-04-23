import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orchestrator.logistics_logic import ResourceAllocator, RoutingService, RiskAssessor

class TestRole3Logic(unittest.TestCase):

    def test_haversine_distance(self):
        # Coordinates for London and Paris
        coord1 = {'lat': 51.5074, 'lng': -0.1278}
        coord2 = {'lat': 48.8566, 'lng': 2.3522}
        
        distance = ResourceAllocator.haversine_distance(coord1, coord2)
        # Approximate distance is ~344km
        self.assertGreater(distance, 340000)
        self.assertLess(distance, 350000)

    def test_find_best_resource(self):
        emergency_loc = {'lat': 0, 'lng': 0}
        resources = [
            {'id': 'far', 'location': {'lat': 1, 'lng': 1}},
            {'id': 'near', 'location': {'lat': 0.1, 'lng': 0.1}},
            {'id': 'mid', 'location': {'lat': 0.5, 'lng': 0.5}}
        ]
        
        best = ResourceAllocator.find_best_resource(emergency_loc, resources)
        self.assertEqual(best['id'], 'near')

    @patch('googlemaps.Client')
    def test_routing_service(self, MockClient):
        mock_gmaps = MockClient.return_value
        mock_gmaps.directions.return_value = [{
            'legs': [{
                'duration': {'text': '15 mins'},
                'distance': {'value': 5000}
            }],
            'overview_polyline': {'points': 'mock_polyline'}
        }]
        
        # Use a realistic-looking fake key to pass initial validation if any
        service = RoutingService(api_key="AIzaSy...fake")
        res = service.get_route_details({'lat': 0, 'lng': 0}, {'lat': 0.1, 'lng': 0.1})
        
        self.assertEqual(res['polyline_route'], 'mock_polyline')
        self.assertEqual(res['eta'], '15 mins')
        self.assertEqual(res['distance_meters'], 5000)

    @patch('googlemaps.Client')
    def test_routing_fallback(self, MockClient):
        # Cause an error in directions
        mock_gmaps = MockClient.return_value
        mock_gmaps.directions.side_effect = Exception("API Error")
        
        service = RoutingService(api_key="AIzaSy...fake")
        res = service.get_route_details({'lat': 0, 'lng': 0}, {'lat': 0.01, 'lng': 0.01})
        self.assertEqual(res['polyline_route'], 'FALLBACK_STRAIGHT_LINE')
        self.assertIn('mins (est)', res['eta'])

    @patch('orchestrator.logistics_logic.GenerativeModel')
    @patch('orchestrator.logistics_logic.SentinelAuth.init_vertex')
    def test_risk_assessor(self, mock_init, MockModel):
        mock_model_instance = MockModel.return_value
        mock_response = MagicMock()
        mock_response.text = '```json {"risk_score": 90, "assessment": "Critical", "trend": "Worsening"} ```'
        mock_model_instance.generate_content.return_value = mock_response
        
        assessor = RiskAssessor()
        res = assessor.get_risk_assessment({'hazard_type': 'Flood', 'urgency': 'P1'})
        
        self.assertEqual(res['risk_score'], 90)
        self.assertEqual(res['trend'], 'Worsening')

    def test_automl_prediction_mock(self):
        assessor = RiskAssessor()
        res = assessor.get_automl_prediction({'hazard_type': 'Flood', 'urgency': 'P1'})
        # base (40) + P1 (30) + Flood (20) = 90
        self.assertEqual(res['spread_probability'], '90%')


if __name__ == '__main__':
    unittest.main()
