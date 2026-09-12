import os
import asyncio

from dotenv import load_dotenv
from supabase import acreate_client, AsyncClient
from pipeline import process_detections

load_dotenv()


async def main():
    supabase: AsyncClient = await acreate_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )

    def handle_event(payload):
        print("\nNEW EVENT RECEIVED:")

        event = payload["data"]["record"]

        detection = {
            "sensor_id": event["sensor_id"],
            "event_type": event["event_type"],
            "confidence": float(event["confidence"])
        }

        print("Processing detection:")
        print(detection)

        process_detections([detection], save_events=False, incident_id=event["incident_id"], anchor_event_id=event["event_id"])

    channel = supabase.channel("forest-events")

    channel.on_postgres_changes(
        event="INSERT",
        schema="public",
        table="events",
        callback=handle_event
    )

    await channel.subscribe()

    print("Realtime worker listening for new events...")
    print("Press Ctrl+C to stop.")

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())