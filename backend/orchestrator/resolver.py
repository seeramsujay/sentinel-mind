import json
import os
from vertexai.generative_models import GenerativeModel
from .auth import SentinelAuth, SentinelEncoder


class ConflictResolver:
    def __init__(self):
        SentinelAuth.init_vertex()
        self.model = GenerativeModel(os.getenv("VERTEX_MODEL_ID", "gemini-2.5-flash-lite"))
        self._system_prompt = """You are the SentinelMind Meta-Orchestrator.
You must respond ONLY with valid JSON — no markdown, no explanation.
Goal: 
1. Prioritize based on life-threat potential and urgency (P1/P2/P3).
2. Optimize distance/ETA.
3. Maintain ethical fairness (documented in fairness_audit).

Ethical Redlines:
- If resources are scarce, flagging any potential socio-economic bias.
- If decision certainty is low, set hitl_mandatory to true.

Return JSON format:
{
    "decisions": [
        {
            "emergency_id": "string",
            "action": "dispatch" | "wait" | "reroute",
            "resource_id": "string",
            "fairness_audit": "string explaining reasoning",
            "bias_score": float (0.0 to 1.0),
            "hitl_mandatory": boolean,
            "hitl_reasoning": "string explain why human review is needed"
        }
    ]
}
Rules: Prioritize P1 over P2 over P3. Assign nearest available unit.
If no unit is available for a P1, set action to "wait"."""


    def resolve(self, conflicts, resources) -> dict | None:
        if not conflicts or not resources:
            print(f"[ConflictResolver] Skipped — no conflicts or no resources.")
            return None

        payload = {
            "conflicts": conflicts,
            "resources": [
                {k: v for k, v in r.items() if v is not None}
                for r in resources if isinstance(r, dict)
            ]
        }

        user_prompt = f"Conflicting emergencies:\n{json.dumps(payload['conflicts'], indent=2, cls=SentinelEncoder)}\n\nAvailable resources:\n{json.dumps(payload['resources'], indent=2, cls=SentinelEncoder)}"

        try:
            response = self.model.generate_content([self._system_prompt, user_prompt])
            text = response.text.strip() if response and response.text else ""
            return self._parse(text)
        except Exception as e:
            print(f"[ConflictResolver] Generation error: {e}")
            return None

    def _parse(self, text: str) -> dict | None:
        if not text:
            return None
        text = text.strip()
        fences = ["```json", "```", "json"]
        for fence in fences:
            if fence in text:
                parts = text.split(fence)
                if len(parts) >= 2:
                    text = fence.join(parts[1:]).strip()
                    for end in ("```", "`"):
                        text = text.strip(end)
        try:
            parsed = json.loads(text)
            if not isinstance(parsed, dict) or "decisions" not in parsed:
                return None
            return parsed
        except json.JSONDecodeError:
            print(f"[ConflictResolver] JSON parse failed. Raw text:\n{text[:300]}")
            return None