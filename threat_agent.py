class ThreatAssessmentAgent:

    def process(self, acoustic_results, location_result, context_result):

        threat_score = 0

        # Find the strongest acoustic confidence
        highest_confidence = max(
            result["confidence"]
            for result in acoustic_results
            if result["status"] == "DETECTED"
        )

        # Acoustic confidence contributes up to 40 points
        threat_score += highest_confidence * 40

        # Multiple sensors provide stronger evidence
        location_counts = location_result["location_counts"]

        most_likely_location = location_result["most_likely_location"]

        sensor_count = location_counts[most_likely_location]

        # Corroboration contributes up to 30 points
        threat_score += min(sensor_count * 10, 30)

        # Unauthorized activity contributes 30 points
        if context_result["context_status"] == "UNAUTHORIZED":
            threat_score += 30

        threat_score = round(threat_score)

        # Convert score into threat level
        if threat_score >= 81:
            threat_level = "CRITICAL"
        elif threat_score >= 61:
            threat_level = "HIGH"
        elif threat_score >= 31:
            threat_level = "MEDIUM"
        else:
            threat_level = "LOW"

        return {
            "threat_score": threat_score,
            "threat_level": threat_level,
            "location": most_likely_location
        }