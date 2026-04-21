"""
Discord Actuator Daemon
Listens to Firestore /emergencies collection. When an emergency flips to
status == "dispatched", sends an alert to Discord via webhook.
"""

import os
import time
import firebase_admin
from firebase_admin import credentials, firestore
import requests
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "sentinelmind")

COLOR_RED = 0xFF0000
COLOR_ORANGE = 0xFF7F00
COLOR_YELLOW = 0xFFFF00

ALERTED_LOG = "/tmp/sentinelmind_dispatched.json"


def init_firestore():
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {"projectId": PROJECT_ID})
    return firestore.client()


def load_alerted() -> set:
    try:
        with open(ALERTED_LOG) as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_alerted(alerted: set):
    import json
    with open(ALERTED_LOG, "w") as f:
        json.dump(list(alerted), f)


def urgency_color(urgency: str) -> int:
    mapping = {"P1": COLOR_RED, "P2": COLOR_ORANGE, "P3": COLOR_YELLOW}
    return mapping.get(urgency.upper(), COLOR_ORANGE)


def build_embed(doc: dict, doc_id: str) -> dict:
    import json
    urgency = doc.get("urgency", "P2").upper()
    color = urgency_color(urgency)

    location = doc.get("location_name", "Unknown location")
    lat = doc.get("latitude", "N/A")
    lon = doc.get("longitude", "N/A")
    hazard = doc.get("hazard_type", "Unknown")
    eta = doc.get("eta_minutes", "N/A")
    assigned = doc.get("assigned_unit", "Unassigned")
    carbon_saved = doc.get("carbon_saved_kg", 0)

    title = f"\u26a0\ufe0f [{urgency}] {hazard} — {location}"

    desc = (
        f"**Location:** {location} ({lat}, {lon})\n"
        f"**Unit:** {assigned}\n"
        f"**ETA:** {eta} min\n"
        f"**CO\u2082 Saved:** {carbon_saved:.2f} kg\n"
        f"**Doc ID:** `{doc_id}`"
    )

    return {
        "embeds": [
            {
                "title": title,
                "description": desc,
                "color": color,
                "footer": {"text": "SentinelMind — Auto-Dispatched"},
            }
        ]
    }


def send_discord_alert(embed_payload: dict, is_p1: bool = False):
    url = os.getenv("DISCORD_ALERT_WEBHOOK_URL") if is_p1 else os.getenv("DISCORD_WEBHOOK_URL")
    if not url:
        print("[DiscordActuator] No webhook URL set — skipping.")
        return

    try:
        resp = requests.post(url, json=embed_payload, headers={"Content-Type": "application/json"}, timeout=10)
        if resp.status_code in (200, 204):
            print(f"[DiscordActuator] Sent to {'P1' if is_p1 else 'general'} channel.")
        else:
            print(f"[DiscordActuator] Failed: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"[DiscordActuator] Error: {e}")


def main():
    db = init_firestore()
    alerted = load_alerted()
    print(f"[DiscordActuator] Loaded {len(alerted)} previously alerted IDs.")

    print("[DiscordActuator] Starting listener on /emergencies …")

    while True:
        try:
            col_ref = db.collection("emergencies")
            for doc in col_ref.stream():
                doc_dict = doc.to_dict()
                if doc_dict.get("status") != "dispatched":
                    continue
                if doc.id in alerted:
                    continue

                payload = build_embed(doc_dict, doc.id)
                urgency = doc_dict.get("urgency", "P2")
                send_discord_alert(payload, urgency.upper() == "P1")
                alerted.add(doc.id)

            save_alerted(alerted)
            time.sleep(5)

        except Exception as e:
            print(f"[DiscordActuator] Error — sleeping 10s: {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()