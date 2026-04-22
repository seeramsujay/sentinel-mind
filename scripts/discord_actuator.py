"""
Discord Actuator Daemon
Listens to Firestore /emergencies collection. When an emergency flips to
status == "dispatched", sends an alert to Discord via webhook.
"""

import json
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


def _str(val, default: str = "N/A") -> str:
    if val is None:
        return default
    return str(val)


def _float(val, default: float = 0.0) -> float:
    if val is None:
        return default
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _int(val, default: int = 0) -> int:
    if val is None:
        return default
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


def load_alerted() -> set:
    try:
        with open(ALERTED_LOG) as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError, PermissionError):
        return set()


def save_alerted(alerted: set):
    try:
        with open(ALERTED_LOG, "w") as f:
            json.dump(list(alerted), f)
    except OSError as e:
        print(f"[DiscordActuator] Failed to persist alerted log: {e}")


def urgency_color(urgency: str) -> int:
    mapping = {"P1": COLOR_RED, "P2": COLOR_ORANGE, "P3": COLOR_YELLOW}
    return mapping.get(str(urgency).strip().upper(), COLOR_ORANGE)


def is_p1(urgency: str) -> bool:
    return str(urgency).strip().upper() == "P1"


def _extract_location(doc: dict) -> tuple:
    loc = doc.get("location") or {}
    address = loc.get("address") if isinstance(loc, dict) else _str(doc.get("location_name"))
    lat = _float(loc.get("lat") if isinstance(loc, dict) else doc.get("latitude"))
    lon = _float(loc.get("lng") if isinstance(loc, dict) else doc.get("longitude"))
    return address, lat, lon


def _extract_resource(doc: dict) -> tuple:
    ra = doc.get("resource_assignment") or {}
    if isinstance(ra, dict):
        unit_id = ra.get("unit_id") or doc.get("assigned_unit")
        eta_raw = ra.get("eta") or doc.get("eta_minutes")
        carbon = ra.get("carbon_saved") or doc.get("carbon_saved_kg")
    else:
        unit_id = doc.get("assigned_unit")
        eta_raw = doc.get("eta_minutes")
        carbon = doc.get("carbon_saved_kg")
    return unit_id, eta_raw, carbon


def build_embed(doc: dict, doc_id: str) -> dict:
    urgency = _str(doc.get("urgency"), "P2").strip().upper()
    color = urgency_color(urgency)
    hazard = _str(doc.get("hazard_type"), "Unknown")

    location_name, lat, lon = _extract_location(doc)
    unit_id, eta_raw, carbon = _extract_resource(doc)

    eta_display = _str(eta_raw)
    eta_int = _int(eta_raw)
    eta_suffix = " min" if eta_int > 0 else ""
    eta_formatted = f"{eta_int}{eta_suffix}" if eta_int > 0 else "N/A"

    title = f"\u26a0\ufe0f [{urgency}] {hazard} — {location_name}"

    desc = (
        f"**Location:** {location_name} ({lat}, {lon})\n"
        f"**Unit:** {_str(unit_id, 'Unassigned')}\n"
        f"**ETA:** {eta_formatted}\n"
        f"**CO\u2082 Saved:** {_float(carbon):.2f} kg\n"
        f"**Doc ID:** `{_str(doc_id)}`"
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


def send_discord_alert(embed_payload: dict, is_p1_flag: bool = False) -> bool:
    url = os.getenv("DISCORD_ALERT_WEBHOOK_URL") if is_p1_flag else os.getenv("DISCORD_WEBHOOK_URL")
    if not url:
        print("[DiscordActuator] No webhook URL set — skipping.")
        return False

    try:
        resp = requests.post(url, json=embed_payload, headers={"Content-Type": "application/json"}, timeout=10)
        if resp.status_code in (200, 204):
            print(f"[DiscordActuator] Sent to {'P1' if is_p1_flag else 'general'} channel.")
            return True
        print(f"[DiscordActuator] Failed: {resp.status_code} {resp.text}")
        return False
    except requests.exceptions.Timeout:
        print("[DiscordActuator] Request timed out.")
        return False
    except Exception as e:
        print(f"[DiscordActuator] Error: {e}")
        return False


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
                if doc_dict is None:
                    continue
                if doc_dict.get("status") != "dispatched":
                    continue
                if doc.id in alerted:
                    continue

                payload = build_embed(doc_dict, doc.id)
                send_discord_alert(payload, is_p1(doc_dict.get("urgency", "")))
                alerted.add(doc.id)

            save_alerted(alerted)
            time.sleep(5)

        except Exception as e:
            print(f"[DiscordActuator] Error — sleeping 10s: {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()