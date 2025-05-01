import requests
import json


class SlackEvents:
    def __init__(self, app, token, core):
        self.core = core
        self.app = app
        self.token = token
        self.metadata = {}

        # ------------------------------
        # REMEMBER, YOU CAN USE PCORE IN HERE TO ACCESS THE CORE FUNCTIONALITY TO FURTHER ENHANCE YOUR SLACK APP
        # ------------------------------

        # Register actions
        self.register_actions()

    def register_actions(self):
        @self.app.event("channel_created")
        def event_channel_created(ack, event, say):
            ack()

            channel_id = event["channel"]["id"]
            channel_name = event["channel"]["name"].upper()
            
            url = "https://slack.com/api/conversations.join"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
            payload = {"channel": channel_id}

            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                if response.json().get("ok"):
                    print(f"Joined channel: {channel_id}")
                else:
                    print(
                        f"Failed to join channel: {channel_id}\n\n {response.json().get('error')}"
                    )
            else:
                print(f"Failed to join channel: {channel_id}\n\n {response.text}")