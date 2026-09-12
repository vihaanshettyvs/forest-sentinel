from datetime import datetime


class AcousticAgent:

    def __init__(self, confidence_threshold=0.70):
        self.confidence_threshold = confidence_threshold

    def process(self, detection):

        event_type = detection["event_type"]
        confidence = detection["confidence"]

        if confidence >= self.confidence_threshold:
            status = "DETECTED"
        else:
            status = "UNCERTAIN"

        timestamp = datetime.now().isoformat()

        return {
            "sensor_id": detection["sensor_id"],
            "event_type": event_type,
            "timestamp": timestamp,
            "confidence": confidence,
            "status": status
        }


if __name__ == "__main__":

    agent = AcousticAgent()

    detection = {
        "sensor_id": "S03",
        "event_type": "chainsaw",
        "confidence": 0.91
    }

    result = agent.process(detection)

    print(result)