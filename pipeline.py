from acoustic_agent import AcousticAgent
from localization_agent import LocalizationAgent
from context_agent import ContextAgent
from threat_agent import ThreatAssessmentAgent
from response_agent import ResponseAgent
from coordinator_agent import CoordinatorAgent
from supabase_db import (
    new_incident_id,
    save_detection,
    save_agent_decision,
    save_threat
)

# Create our agents
acoustic_agent = AcousticAgent()

sensor_locations = {
    "S01": "B6",
    "S02": "B7",
    "S03": "B7",
    "S04": "C7" 
}

localization_agent = LocalizationAgent(sensor_locations)

zone_data = {
    "B6": {
        "authorized_logging": True
    },
    "B7": {
        "authorized_logging": False
    },
    "C7": {
        "authorized_logging": False
    }
}

context_agent = ContextAgent(zone_data)
threat_agent = ThreatAssessmentAgent()
response_agent = ResponseAgent()
coordinator_agent = CoordinatorAgent()

def process_detections(detections, save_events=True, incident_id=None, anchor_event_id=None):
    if incident_id is None:
        incident_id = new_incident_id()
    print("INCIDENT ID:", incident_id)

    # Acoustic Agent processes each detection
    acoustic_results = []

    for detection in detections:
        result = acoustic_agent.process(detection)
        acoustic_results.append(result)

    # Save detected events to Supabase when processing new sensor data
    event_ids = []

    if save_events:
        for result in acoustic_results:
            if result["status"] == "DETECTED":
                event_id = save_detection(
                    incident_id,
                    result,
                    sensor_locations
                )

                event_ids.append(event_id)

    # Save Acoustic Agent decisions
    detected_results = [
        r for r in acoustic_results
        if r["status"] == "DETECTED"
    ]

    if save_events:
        for result, event_id in zip(detected_results, event_ids):
            save_agent_decision(
                incident_id,
                "AcousticAgent",
                result,
                event_id
            )
    else:
        for result in detected_results:
            save_agent_decision(
                incident_id,
                "AcousticAgent",
                result
            )

    print("ACOUSTIC RESULTS:")

    for result in acoustic_results:
        print(result)

    # Localization Agent
    location_result = localization_agent.process(acoustic_results)

    print("\nLOCALIZATION RESULT:")
    print(location_result)

    save_agent_decision(
        incident_id,
        "LocalizationAgent",
        location_result
    )

    # Context Agent
    context_result = context_agent.process(location_result)

    print("\nCONTEXT RESULT:")
    print(context_result)

    save_agent_decision(
        incident_id,
        "ContextAgent",
        context_result
    )

    # Threat Assessment Agent
    threat_result = threat_agent.process(
        acoustic_results,
        location_result,
        context_result
    )

    print("\nTHREAT RESULT:")
    print(threat_result)

    save_agent_decision(
        incident_id,
        "ThreatAssessmentAgent",
        threat_result
    )

    # Response Agent
    response_result = response_agent.process(threat_result)

    print("\nRESPONSE RESULT:")
    print(response_result)

    save_agent_decision(
        incident_id,
        "ResponseAgent",
        response_result
    )

    # Coordinator Agent
    coordinator_result = coordinator_agent.process(
        acoustic_results,
        location_result,
        context_result,
        threat_result,
        response_result
    )

    print("\nCOORDINATOR RESULT:")
    print(coordinator_result)

    # Adapt agent output to database schema
    db_threat_result = {
        "threat_level": threat_result["threat_level"],
        "risk_score": threat_result["threat_score"],
        "location": threat_result["location"]
    }

    db_response_result = {
        "action": response_result["action"],
        "notify_ranger": response_result["priority"] in ["URGENT", "HIGH"],
        "reason": (
            f"Threat assessed as {threat_result['threat_level']} "
            f"with score {threat_result['threat_score']}/100 "
            f"at {threat_result['location']}."
        )
    }

    # Save final threat
    threat_event_id = event_ids[0] if event_ids else anchor_event_id
    print("THREAT EVENT ID:", threat_event_id)

    if threat_event_id:
        save_threat(
            incident_id,
            threat_event_id,
            db_threat_result,
            db_response_result
        )

    # Save Coordinator decision
    save_agent_decision(
        incident_id,
        "CoordinatorAgent",
        coordinator_result
    )

    return coordinator_result