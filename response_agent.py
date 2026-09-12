class ResponseAgent:

    def process(self, threat_result):

        threat_level = threat_result["threat_level"]
        location = threat_result["location"]
        threat_score = threat_result["threat_score"]

        if threat_level == "CRITICAL":
            action = "IMMEDIATE ALERT"
            priority = "URGENT"

        elif threat_level == "HIGH":
            action = "ALERT AUTHORITIES"
            priority = "HIGH"

        elif threat_level == "MEDIUM":
            action = "MONITOR AREA"
            priority = "MEDIUM"

        else:
            action = "CONTINUE MONITORING"
            priority = "LOW"

        return {
            "location": location,
            "threat_score": threat_score,
            "threat_level": threat_level,
            "action": action,
            "priority": priority
        }


if __name__ == "__main__":

    agent = ResponseAgent()

    threat_result = {
        "threat_score": 94,
        "threat_level": "CRITICAL",
        "location": "B7"
    }

    result = agent.process(threat_result)

    print(result)