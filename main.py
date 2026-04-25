import os
import threading
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the daemon entrypoints
from backend.orchestrator.daemon import OrchestratorDaemon
from backend.logistics.logistics_daemon import LogisticsDaemon
from scripts.discord_actuator import main as discord_main

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "sentinel-mind-daemons"}

@app.get("/emergencies")
def get_emergencies():
    from firebase_admin import firestore
    try:
        db = firestore.client()
        docs = db.collection('emergencies').get()
        return [doc.to_dict() | {"id": doc.id} for doc in docs]
    except Exception as e:
        return {"error": str(e)}

@app.on_event("startup")
def startup_event():
    print("[main] Starting Daemons in threads...")

    # Start Orchestrator Daemon
    orch_thread = threading.Thread(target=OrchestratorDaemon().run, daemon=True)
    orch_thread.start()
    
    # Start Logistics Daemon
    logistics_thread = threading.Thread(target=LogisticsDaemon().run, daemon=True)
    logistics_thread.start()
    
    # Start Discord Actuator
    discord_thread = threading.Thread(target=discord_main, daemon=True)
    discord_thread.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
