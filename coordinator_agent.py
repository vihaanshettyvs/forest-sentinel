class CoordinatorAgent:

    def process(
        self,
        acoustic_results,
        location_result,
        context_result,
        threat_result,
        response_result
    ):

        threat_level = threat_result["threat_level"]
        location = threat_result["location"]
        action = response_result["action"]

        detected_events = len(
            [
                result
                for result in acoustic_results
                if result["status"] == "DETECTED"
            ]
        )

        if threat_level == "CRITICAL":
            system_status = "EMERGENCY"
        elif threat_level == "HIGH":
            system_status = "ALERT"
        elif threat_level == "MEDIUM":
            system_status = "CAUTION"
        else:
            system_status = "NORMAL"

        return {
            "system_status": system_status,
            "location": location,
            "threat_level": threat_level,
            "threat_score": threat_result["threat_score"],
            "detected_events": detected_events,
            "recommended_action": action
        }


if __name__ == "__main__":

    agent = CoordinatorAgent()

    acoustic_results = [
        {
            "status": "DETECTED",
            "event_type": "chainsaw"
        }
    ]

    location_result = {
        "most_likely_location": "B7"
    }

    context_result = {
        "context_status": "UNAUTHORIZED"
    }

    threat_result = {
        "threat_score": 94,
        "threat_level": "CRITICAL",
        "location": "B7"
    }

    response_result = {
        "action": "IMMEDIATE ALERT"
    }

    result = agent.process(
        acoustic_results,
        location_result,
        context_result,
        threat_result,
        response_result
    )

    print(result)