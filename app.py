import os
import tempfile

from flask import Flask, request, jsonify
from flask_cors import CORS

from classifier import YAMNetClassifier
from agents.supabase_db import (
    supabase,
    new_incident_id,
    save_detection,
    save_agent_decision,
    save_threat
)

app = Flask(__name__)
CORS(app)

classifier = YAMNetClassifier()

SENSOR_LOCATIONS = {
    "S01": "A1",
    "S02": "A2",
    "S03": "B3",
    "S04": "C7",
    "S05": "C3",
    "S06": "C4"
}


def approved_forest_truck(sector):
    response = (
        supabase.table("authorizations")
        .select("*")
        .eq("sector", sector)
        .eq("activity_type", "forest_department_truck")
        .eq("status", "active")
        .execute()
    )
    return bool(response.data)


@app.get("/health")
def health():
    return jsonify({"status": "Forest Sentinel backend online"})


@app.post("/analyze-audio")
def analyze_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file received."}), 400

    audio_file = request.files["audio"]
    sensor_id = request.form.get("sensor_id", "S02")
    sector = SENSOR_LOCATIONS.get(sensor_id, "B7")

    suffix = os.path.splitext(audio_file.filename)[1] or ".wav"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
        audio_file.save(temp.name)
        temp_path = temp.name

    try:
        classification = classifier.classify(temp_path)
    finally:
        os.remove(temp_path)

    label = classification["label"]
    confidence = classification["confidence"]
    incident_id = new_incident_id()

    event_id = save_detection(
        incident_id,
        {
            "sensor_id": sensor_id,
            "event_type": label,
            "confidence": confidence
        },
        SENSOR_LOCATIONS
    )

    truck_approved = (
        label == "vehicle" and approved_forest_truck(sector)
    )

    if label == "bird":
        level, score, action = "LOW", 10, "monitor"
        reason = "Bird sound recognized. Normal forest activity."

    elif truck_approved:
        level, score, action = "LOW", 8, "continue_patrol"
        reason = (
            f"Vehicle sound matches an approved Forest Department "
            f"truck in Sector {sector}."
        )

    elif label in ["chainsaw", "gunshot"]:
        level = "CRITICAL"
        score = 90 if label == "gunshot" else 84
        action = "ranger_alert"
        reason = (
            f"High-confidence {label} evidence in Sector {sector}. "
            "Human ranger approval required."
        )

    else:
        level, score, action = "MEDIUM", 45, "request_second_recording"
        reason = "Unknown sound. Request a second recording."

    acoustic = {
        "event_type": label,
        "confidence": confidence,
        "top_3": classification["top_3"],
        "reasoning": "YAMNet analyzed the uploaded waveform."
    }

    localization = {
        "most_likely_location": sector,
        "reasoning": f"Sensor {sensor_id} maps to Sector {sector}."
    }

    context = {
        "location": sector,
        "context_status": "PERMITTED" if truck_approved else "SUSPICIOUS",
        "reasoning": reason
    }

    threat = {
        "threat_level": level,
        "risk_score": score,
        "threat_score": score,
        "reasoning": reason
    }

    coordinator = {
        "system_status": "EMERGENCY" if level == "CRITICAL" else "MONITORING",
        "detected_events": 1,
        "recommended_action": action,
        "reasoning": reason
    }

    response = {
        "priority": "URGENT" if level == "CRITICAL" else "NORMAL",
        "action": action,
        "location": sector,
        "notify_ranger": level == "CRITICAL",
        "reason": reason
    }

    save_agent_decision(incident_id, "AcousticAgent", acoustic, event_id)
    save_agent_decision(incident_id, "LocalizationAgent", localization, event_id)
    save_agent_decision(incident_id, "ContextAgent", context, event_id)
    save_agent_decision(incident_id, "ThreatAssessmentAgent", threat, event_id)
    save_agent_decision(incident_id, "CoordinatorAgent", coordinator, event_id)
    save_agent_decision(incident_id, "ResponseAgent", response, event_id)

    save_threat(incident_id, event_id, threat, response)

    return jsonify({
        "incident_id": incident_id,
        "classification": classification,
        "threat_level": level,
        "risk_score": score,
        "action": action,
        "reason": reason
    })


if __name__ == "__main__":
    app.run(port=8000, debug=True)