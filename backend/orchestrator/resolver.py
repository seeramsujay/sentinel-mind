from vertexai.generative_models import GenerativeModel, Part
from .auth import SentinelAuth
import json

class ConflictResolver:
    """Uses Gemini 1.5 Pro to autonomously resolve resource overlaps and ethical dilemmas."""
    
    def __init__(self):
        SentinelAuth.init_vertex()
        self.model = GenerativeModel("gemini-1.5-pro")

    def resolve(self, conflicts, resources):
        """
        Processes conflicting emergency reports and available resources 
        to produce an optimal, fair dispatch plan.
        """
        prompt = f"""
        System: SentinelMind Meta-Orchestrator
        Task: Resolve resource allocation conflict for emergency dispatch.
        
        Conflicting Emergencies:
        {json.dumps(conflicts, indent=2)}
        
        Available Resources:
        {json.dumps(resources, indent=2)}
        
        Goal: 
        1. Prioritize based on life-threat potential and urgency (P1/P2/P3).
        2. Optimize distance/ETA.
        3. Maintain ethical fairness (documented in fairness_audit).
        
        Return JSON format:
        {{
            "decisions": [
                {{
                    "emergency_id": "string",
                    "action": "dispatch" | "wait" | "reroute",
                    "resource_id": "string",
                    "fairness_audit": "string explaining reasoning"
                }}
            ]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Basic parsing - assuming model follows JSON constraint
            result = response.text.strip()
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            return json.loads(result)
        except Exception as e:
            print(f"AI Resolution Error: {e}")
            return None
