class ContextAgent:

    def __init__(self, zone_data):
        self.zone_data = zone_data

    def process(self, event):

        location = event["most_likely_location"]

        zone = self.zone_data[location]

        if zone["authorized_logging"]:
            context_status = "AUTHORIZED"
        else:
            context_status = "UNAUTHORIZED"

        return {
            "location": location,
            "context_status": context_status
        }


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


if __name__ == "__main__":

    agent = ContextAgent(zone_data)

    event = {
        "most_likely_location": "B7"
    }

    result = agent.process(event)

    print(result)