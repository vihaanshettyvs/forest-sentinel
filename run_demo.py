from pipeline import process_detections

detections = [
    {
        "sensor_id": "S01",
        "event_type": "chainsaw",
        "confidence": 0.91
    },
    {
        "sensor_id": "S02",
        "event_type": "chainsaw",
        "confidence": 0.87
    },
    {
        "sensor_id": "S03",
        "event_type": "chainsaw",
        "confidence": 0.84
    },
    {
        "sensor_id": "S04",
        "event_type": "chainsaw",
        "confidence": 0.45
    }
]

process_detections(detections)