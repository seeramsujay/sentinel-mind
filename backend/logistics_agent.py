import asyncio
import time
import os
from datetime import datetime, timedelta, timezone
import logging
from firebase_admin import firestore
from dotenv import load_dotenv
from backend.orchestrator.auth import SentinelAuth
from backend.orchestrator.logistics_logic import ResourceAllocator, RoutingService, RiskAssessor, SDGMeter, VectorSearchClient

load_dotenv()

class LogisticsAgent:
    """
    Role 3: Logistics & Prediction Lead
    Monitors Firestore for 'awaiting_dispatch' emergencies and dispatches resources concurrently.
    """
    
    def __init__(self):
        if not os.getenv("GEMINI_API_KEY"):
            raise EnvironmentError("GEMINI_API_KEY is not set. Logistics Agent requires this for Risk Assessment.")
            
        self.db = SentinelAuth.get_firestore()
        self.routing = RoutingService()
        self.assessor = RiskAssessor()
        self.semaphore = asyncio.Semaphore(5) # Throttled for Gemini quota
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - Role 3 - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("SentinelMind Role 3 (Logistics Swarm) Booted.")

    async def run_swarm(self):
        """Async main loop to process awaiting_dispatch emergencies in parallel."""
        while True:
            try:
                # 0. Auto-release busy resources (Mock Simulation Logic)
                self.auto_release_resources()

                # 1. Query for 'awaiting_dispatch' emergencies
                docs = self.db.collection('emergencies')\
                    .where('status', '==', 'awaiting_dispatch')\
                    .limit(50)\
                    .get()

                if not docs:
                    await asyncio.sleep(2)
                    continue

                self.logger.info(f"Swarm detected {len(docs)} pending items. Scaling workers...")
                
                # 2. Process all docs in parallel with semaphore control
                tasks = [self.process_emergency_async(doc) for doc in docs]
                await asyncio.gather(*tasks)

                await asyncio.sleep(1)

            except Exception as e:
                self.logger.error(f"Swarm Loop Error: {e}")
                await asyncio.sleep(5)

    async def process_emergency_async(self, doc):
        """Asynchronous worker for a single incident with Distributed Firestore Transaction."""
        async with self.semaphore:
            try:
                emergency_ref = doc.reference
                data = doc.to_dict()
                emergency_id = doc.id
                if data.get('role1_override') is True: return

                emergency_loc = data.get('location') or data.get('location_coordinates')
                if not emergency_loc: return

                # Transactional Resource Acquisition
                transaction = self.db.transaction()
                
                @firestore.transactional
                def atomic_dispatch(transaction, emergency_ref, data):
                    # 1. Fresh check of status
                    snapshot = emergency_ref.get(transaction=transaction)
                    if snapshot.get('status') != 'awaiting_dispatch':
                        return None, "Already processed"

                    # 2. Get available resources
                    agency_id = data.get('agency_id')
                    res_query = self.db.collection('resources').where('status', '==', 'available')
                    if agency_id:
                        res_query = res_query.where('agency_id', '==', agency_id)
                    
                    available_resources = res_query.get(transaction=transaction)

                    if not available_resources:
                        transaction.update(emergency_ref, {
                            "status": "awaiting_resource",
                            "escalated": True,
                            "escalation_note": "No resources available at this time."
                        })
                        return None, "No resources"

                    # 3. Find best match
                    best_resource = ResourceAllocator.find_best_resource(emergency_loc, available_resources)
                    if not best_resource:
                        transaction.update(emergency_ref, {
                            "status": "awaiting_resource",
                            "escalated": True,
                            "escalation_note": "Available resources do not match deployment criteria."
                        })
                        return None, "No match found"

                    # 4. Atomic Commit
                    res_ref = best_resource.reference
                    transaction.update(res_ref, {
                        "status": "busy",
                        "assigned_to": emergency_id,
                        "last_dispatched": firestore.SERVER_TIMESTAMP
                    })
                    transaction.update(emergency_ref, {"status": "dispatching"})
                    return best_resource.to_dict(), "Success"

                res_data, result_msg = atomic_dispatch(transaction, emergency_ref, data)
                
                if not res_data:
                    if result_msg != "Already processed":
                        self.logger.warning(f"Dispatch aborted for {emergency_id}: {result_msg}")
                    return

                # 2. Parallel Intelligence Tasks (OUTSIDE Transaction/Lock)
                route = self.routing.get_route_details(res_data.get('location'), emergency_loc)
                risk = self.assessor.get_risk_assessment(data)
                automl = self.assessor.get_automl_prediction(data)
                rag_context = VectorSearchClient.get_historical_context(f"{data.get('hazard_type')} response")
                sitrep = self.generate_sitrep(data, risk, route, rag_context)

                # 3. Final Dispatch Commit
                doc.reference.update({
                    "status": "dispatched",
                    "severity": data.get('severity') or max(1, min(5, int(risk.get('risk_score', 50) / 20))),
                    "resource_assignment": {
                        "unit_id": res_data.get('unit_id'),
                        "resource_type": res_data.get('resource_type', 'Default'),
                        "polyline_route": route['polyline_route'],
                        "eta": route['eta']
                    },
                    "intelligence": {
                        "risk_assessment": risk.get('assessment'),
                        "spread_probability": automl['spread_probability'],
                        "situation_report": sitrep,
                        "ndma_protocol": rag_context
                    }
                })
                
                self.logger.info(f"SUCCESS: Dispatched {res_data['unit_id']} to {emergency_id}")

            except Exception as e:
                self.logger.error(f"Worker Error for {doc.id}: {e}")

    def generate_sitrep(self, data, risk_data, route_details, rag_context):
        """Drafts a professional Situation Report (SitRep) using Gemini + RAG."""
        prompt = f"""
        System: SentinelMind Crisis Prediction Engine (Role 3)
        Task: Draft a professional SitRep.
        
        Incident: {data.get('hazard_type')} at {data.get('location', {}).get('address')}
        Risk: {risk_data.get('risk_score')} ({risk_data.get('assessment')})
        ETA: {route_details.get('eta')}
        
        Mandatory Protocol (RAG Context):
        {rag_context}
        
        Requirement: Integrate the mandatory protocol into the tactical advice. Use gemini-2.5-flash-lite.
        """
        try:
            response = self.assessor.model.generate_content(prompt)
            return response.text.strip()
        except:
            return "SitRep generation failed."

    def perform_vision_analysis(self, data):
        """Analyzes field images using Gemini Vision for damage assessment."""
        image_url = data.get('field_image_url')
        prompt = "Analyze this disaster field image and classify damage severity (Low/Medium/High). Identify structural hazards."
        
        # Note: In a real implementation with vertexai, we would use Part.from_uri
        try:
            # Simulation of vision analysis call
            return f"Vision Analysis: High severity detected from image {image_url[-10:]}. Potential flooding around foundation."
        except:
            return "Vision analysis failed."

    def auto_release_resources(self):
        """Simulation logic to free up resources after a 'mission'."""
        busy = self.db.collection('resources').where('status', '==', 'busy').get()
        now = datetime.now(timezone.utc)
        for res in busy:
            data = res.to_dict()
            last_dispatched = data.get('last_dispatched')
            if last_dispatched and (now - last_dispatched).total_seconds() > 300: # 5 min mock mission
                res.reference.update({"status": "available", "assigned_to": None})

if __name__ == "__main__":
    agent = LogisticsAgent()
    asyncio.run(agent.run_swarm())
 
