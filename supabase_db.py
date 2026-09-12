import os
import json
from uuid import uuid4

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def clean_json(data):
    return json.loads(json.dumps(data, default=str))

def new_incident_id():
    return f"INC-{uuid4().hex[:8].upper()}"

def save_detection(incident_id, detection, sensor_locations):
    event_id = f"EVT-{uuid4().hex[:8].upper()}"
    sensor_id = detection["sensor_id"]

    supabase.table("events").insert({
        "event_id": event_id,
        "incident_id": incident_id,
        "sensor_id": sensor_id,
        "event_type": detection["event_type"],
        "confidence": detection["confidence"],
        "sector": sensor_locations[sensor_id],
        "source": "simulator"
    }).execute()

    return event_id

def save_agent_decision(incident_id, agent_name, result, event_id=None):
    result = clean_json(result)

    supabase.table("agent_decisions").insert({
        "incident_id": incident_id,
        "event_id": event_id,
        "agent_name": agent_name,
        "result": result,
        "reasoning": result.get("reasoning") or result.get("reason"),
        "score": result.get("risk_score") or result.get("confidence")
    }).execute()

def save_threat(incident_id, anchor_event_id, threat_result, response_result):
    threat_result = clean_json(threat_result)
    response_result = clean_json(response_result)

    supabase.table("threats").upsert({
        "incident_id": incident_id,
        "anchor_event_id": anchor_event_id,
        "threat_level": threat_result.get("threat_level", "LOW"),
        "risk_score": threat_result.get("risk_score", 0),
        "action": response_result.get(
            "action",
            threat_result.get("action", "monitor")
        ),
        "notify_ranger": response_result.get(
            "notify_ranger",
            threat_result.get("notify_ranger", False)
        ),
        "reason": response_result.get(
            "reason",
            threat_result.get("reason", "No explanation returned")
        ),
        "status": "pending_approval"
    }).execute()

def save_ranger_feedback(incident_id, outcome, ranger_name, notes=""):
    supabase.table("ranger_feedback").insert({
        "incident_id": incident_id,
        "outcome": outcome,
        "ranger_name": ranger_name,
        "notes": notes
    }).execute()
