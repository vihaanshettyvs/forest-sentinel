class LocalizationAgent:

    def __init__(self, sensor_locations):
        self.sensor_locations = sensor_locations

    def process(self, detections):

        detected_events = []

        for detection in detections:

            if detection["status"] == "DETECTED":

                sensor_id = detection["sensor_id"]
                event_type = detection["event_type"]

                location = self.sensor_locations[sensor_id]

                detected_events.append({
                    "event_type": event_type,
                    "location": location,
                    "sensor_id": sensor_id
                })

        location_counts = {}

        for event in detected_events:

            location = event["location"]

            if location not in location_counts:
                location_counts[location] = 0

            location_counts[location] += 1

        most_likely_location = max(
            location_counts,
            key=location_counts.get
        )

        return {
            "detections": detected_events,
            "location_counts": location_counts,
            "most_likely_location": most_likely_location
        }


sensor_locations = {
    "S01": "B6",
    "S02": "B7",
    "S03": "B7",
    "S04": "C7"
}


if __name__ == "__main__":

    agent = LocalizationAgent(sensor_locations)

    detections = [
        {
            "sensor_id": "S01",
            "event_type": "chainsaw",
            "confidence": 0.91,
            "status": "DETECTED"
        },
        {
            "sensor_id": "S02",
            "event_type": "chainsaw",
            "confidence": 0.87,
            "status": "DETECTED"
        },
        {
            "sensor_id": "S03",
            "event_type": "chainsaw",
            "confidence": 0.84,
            "status": "DETECTED"
        },
        {
            "sensor_id": "S04",
            "event_type": "chainsaw",
            "confidence": 0.45,
            "status": "UNCERTAIN"
        }
    ]

    result = agent.process(detections)

    print(result)