import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

class SDGAggregator:
    def __init__(self):
        # Path to service account logic
        service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'service-account.json')
        if not firebase_admin._apps:
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
        
        self.db = firestore.client()

    def aggregate_daily_impact(self):
        """
        Scans all dispatched emergencies and sums the carbon_saved metric.
        """
        print("Starting SDG Impact Aggregation...")
        emergencies = self.db.collection('emergencies').get()
        
        total_carbon_saved = 0.0
        dispatched_count = 0
        total_risk_score = 0
        
        for doc in emergencies:
            data = doc.to_dict()
            if data.get('status') == 'dispatched':
                res_assignment = data.get('resource_assignment', {})
                carbon = res_assignment.get('carbon_saved', 0.0)
                total_carbon_saved += carbon
                dispatched_count += 1
                
                intelligence = data.get('intelligence', {})
                total_risk_score += intelligence.get('risk_score', 0)

        avg_risk_mitigated = total_risk_score / dispatched_count if dispatched_count > 0 else 0
        
        report_id = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        report_data = {
            "date": report_id,
            "total_incidents_mitigated": dispatched_count,
            "total_carbon_saved_kg": round(total_carbon_saved, 3),
            "avg_risk_mitigated": round(avg_risk_mitigated, 1),
            "last_updated": firestore.SERVER_TIMESTAMP,
            "sdg_targets": ["SDG 13: Climate Action", "SDG 11: Sustainable Cities"]
        }
        
        self.db.collection('sdg_reports').document(report_id).set(report_data)
        print(f"  ✓ Daily Report Generated: {report_id}")
        print(f"  ✓ Total Carbon Saved: {report_data['total_carbon_saved_kg']} kg")

if __name__ == "__main__":
    aggregator = SDGAggregator()
    aggregator.aggregate_daily_impact()
