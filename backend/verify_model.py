import os
from vertexai.generative_models import GenerativeModel
from backend.orchestrator.auth import SentinelAuth

def verify_model():
    SentinelAuth.init_vertex()
    model_id = os.getenv("VERTEX_MODEL_ID", "gemini-2.5-flash-lite")
    print(f"Testing model: {model_id}")
    model = GenerativeModel(model_id)
    try:
        response = model.generate_content("Hello, respond in 1 word.")
        print(f"Response: {response.text}")
        print("Model verification SUCCESS.")
    except Exception as e:
        print(f"Model verification FAILED: {e}")

if __name__ == "__main__":
    verify_model()
