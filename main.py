import os
import threading
import uvicorn
from fastapi import FastAPI

# Import the daemon entrypoints
from backend.orchestrator.daemon import OrchestratorDaemon
from backend.logistics.logistics_daemon import LogisticsDaemon
from scripts.discord_actuator import main as discord_main

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "ok", "service": "sentinel-mind-daemons"}

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
