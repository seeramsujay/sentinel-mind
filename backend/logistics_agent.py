import asyncio
import time
import os
from datetime import datetime, timedelta, timezone
import logging
from firebase_admin import firestore
from dotenv import load_dotenv
from orchestrator.auth import SentinelAuth
from orchestrator.logistics_logic import ResourceAllocator, RoutingService, RiskAssessor, SDGMeter, VectorSearchClient

load_dotenv()

class LogisticsAgent:
    """
    Role 3: Logistics & Prediction Lead
    Monitors Firestore for 'awaiting_dispatch' emergencies and dispatches resources concurrently.
    """
    
    def __init__(self):
        self.db = SentinelAuth.get_firestore()
        self.routing = RoutingService()
        self.assessor = RiskAssessor()
        
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
                # Fetching snapshot to process current batch
                docs = self.db.collection('emergencies')\
                    .where('status', '==', 'awaiting_dispatch')\
                    .get()

                if not docs:
                    await asyncio.sleep(2)
                    continue

                self.logger.info(f"Swarm detected {len(docs)} pending items. Scaling workers...")
                
                # 2. Process all docs in parallel using asyncio.gather
                tasks = [self.process_emergency_async(doc) for doc in docs]
                await asyncio.gather(*tasks)

                await asyncio.sleep(1)

            except Exception as e:
                self.logger.error(f"Swarm Loop Error: {e}")
                await asyncio.sleep(5)

    async def process_emergency_async(self, doc):
        """Asynchronous worker for a single incident with Transactional Safety."""
        try:
            data = doc.to_dict()
            emergency_id = doc.id
            if data.get('role1_override') is True: return

            emergency_loc = data.get('location') or data.get('location_coordinates')
            if not emergency_loc: return

            # Transactional Dispatch Logic
            transaction = self.db.transaction()
            result = await self._dispatch_transactional(transaction, doc.reference, data, emergency_loc)
            
            if result:
                self.logger.info(f"TRANSACTION SUCCESS: {result} dispatched to {emergency_id}")
            else:
                self.logger.warning(f"TRANSACTION CONFLICT/FAILURE for {emergency_id}")

        except Exception as e:
            self.logger.error(f"Worker Error for {doc.id}: {e}")

    @firestore.transactional
    def _dispatch_transactional(self, transaction, doc_ref, data, emergency_loc):
        """Atomic block for resource selection and status updates."""
        # 1. Get available resources with Agency Affinity
        agency_id = data.get('agency_id')
        res_query = self.db.collection('resources').where('status', '==', 'available')
        if agency_id:
            res_query = res_query.where('agency_id', '==', agency_id)
        
        available_resources = list(res_query.get(transaction=transaction))

        if not available_resources:
            doc_ref.update({
                "status": "awaiting_resource",
                "escalated": True,
                "escalation_note": "Resource depletion (atomic check)."
            }, transaction=transaction)
            return None

        # 2. Find best resource
        best_resource = ResourceAllocator.find_best_resource(emergency_loc, available_resources)
        if not best_resource: return None

        res_data = best_resource.to_dict()
        res_ref = best_resource.reference
        unit_id = res_data.get('unit_id') or best_resource.id

        # 3. Intelligence (Heavy tasks outside transaction if possible, but for simplicity here)
        route = self.routing.get_route_details(res_data.get('location'), emergency_loc)
        risk = self.assessor.get_risk_assessment(data)
        automl = self.assessor.get_automl_prediction(data)
        rag_context = VectorSearchClient.get_historical_context(f"{data.get('hazard_type')} response")
        sitrep = self.generate_sitrep(data, risk, route, rag_context)

        # 4. Atomic Updates
        transaction.update(res_ref, {
            "status": "busy",
            "assigned_to": doc_ref.id,
            "last_dispatched": firestore.SERVER_TIMESTAMP
        })

        transaction.update(doc_ref, {
            "status": "dispatched",
            "severity": data.get('severity') or max(1, min(5, int(risk.get('risk_score', 50) / 20))),
            "resource_assignment": {
                "unit_id": unit_id,
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
        return unit_id

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
