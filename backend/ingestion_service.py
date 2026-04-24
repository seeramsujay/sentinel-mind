import feedparser
import time
import json
import os
from firebase_admin import firestore
from vertexai.generative_models import GenerativeModel
from orchestrator.auth import SentinelAuth

class IngestionService:
    def __init__(self):
        if not os.getenv("GEMINI_API_KEY"):
            raise EnvironmentError("GEMINI_API_KEY is not set. Ingestion Service requires this for Triage AI.")
            
        self.db = SentinelAuth.get_firestore()
        SentinelAuth.init_vertex()
        self.model = GenerativeModel("gemini-2.5-flash-lite")
        self.feeds = [
            "https://www.ndma.gov.in/rss", # Mock/Placeholder
            "https://gdacs.org/xml/rss.xml" # Global Disaster Alert and Coordination System
        ]

    def poll_feeds(self):
        print("[Ingestion] Service Started. Polling RSS feeds...")
        while True:
            for url in self.feeds:
                try:
                    feed = feedparser.parse(url)
                    for entry in feed.entries:
                        if not self._is_new(entry.link):
                            continue
                        
                        print(f"[Ingestion] New alert found: {entry.title}")
                        self.process_entry(entry)
                except Exception as e:
                    print(f"[Ingestion] Error polling {url}: {e}")
            
            time.sleep(300) # Poll every 5 mins

    def _is_new(self, link):
        # Check Firestore to see if this alert link was already processed
        docs = self.db.collection('emergencies').where('source_link', '==', link).limit(1).get()
        return len(docs) == 0

    def process_entry(self, entry):
        prompt = f"""
        System: SentinelMind Triage AI
        Task: Convert unstructured disaster alert into a structured JSON emergency report.
        
        Alert Title: {entry.title}
        Alert Description: {getattr(entry, 'description', getattr(entry, 'summary', 'No description available'))}
        
        Output Requirements (JSON):
        1. hazard_type (Flood, Earthquake, Fire, Cyclone, etc.)
        2. urgency (P1, P2, P3) - P1 is life-threatening, P3 is low risk.
        3. location (JSON object with 'address', 'lat', 'lng') - Estimate if not explicit.
        4. description (Brief summary)
        
        Return ONLY valid JSON.
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = response.text.strip()
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            
            data = json.loads(result)
            data['status'] = 'triaged' # Direct to triaged for Orchestrator to Pick up
            data['source_link'] = entry.link
            data['timestamp'] = firestore.SERVER_TIMESTAMP
            
            self.db.collection('emergencies').add(data)
            print(f"[Ingestion] Triaged and added: {data['hazard_type']} at {data['location'].get('address')}")
            
        except Exception as e:
            print(f"[Ingestion] Error processing entry: {e}")

if __name__ == "__main__":
    service = IngestionService()
    service.poll_feeds()
