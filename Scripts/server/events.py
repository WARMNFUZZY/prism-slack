import requests
import json
class SlackEvents:
    def __init__(self, app, token):
        self.app = app
        self.token = token
        self.metadata = {}  # Store metadata for thread timestamps
        
        # Register actions
        self.register_actions()

    def register_actions(self):
        # Listens to incoming messages that contain "hello
        @self.app.message("hello")
        def message_hello(message, say):
            # Post the message with a button
            response = say(
                blocks=[
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"}
                    },
                    {    
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {"type": "plain_text", "text": "Approved"},
                                "style": "primary",
                                "action_id": "button_approved"
                            },
                            {
                                "type": "button",
                                "text": {"type": "plain_text", "text": "Needs Revised"},
                                "style": "danger",
                                "action_id": "button_needs_revised"
                            },
                            {
                                "type": "button",
                                "text": {"type": "plain_text", "text": "CBB"},
                                "action_id": "button_cbb"
                            }
                        ]
                    }
                ],
                text=f"Hey there <@{message['user']}>!"
            )
            from pprint import pprint
            pprint(response.data)
            # Save the message timestamp for threading
            self.app.metadata = {"thread_ts": response.get("ts")}
            print(self.app.metadata)

        @self.app.action("button_approved")
        def approved_button_click(body, ack):
            ack()

            thread_ts = self.app.metadata.get("thread_ts", None)
            if thread_ts:
                url = "https://slack.com/api/chat.postMessage"
                headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "channel": body["channel"]["id"],
                    "text": "Your submission has been approved!",
                    "thread_ts": thread_ts
                }

            self.post_threaded_message(body, "Your submission has been approved!")

        # Handles button clicks
        # @self.app.action("button_click")
        # def action_button_click(body, ack):
        #     # Acknowledge the button click
        #     ack()
        #     from pprint import pprint
        #     pprint(self.app.metadata)
        #     # Retrieve the parent message's timestamp
        #     thread_ts = self.app.metadata.get("thread_ts", None)
        #     if thread_ts:
        #         # Post a threaded reply using the Slack Web API
        #         url = "https://slack.com/api/chat.postMessage"
        #         headers = {
        #             "Authorization": f"Bearer {self.token}",
        #             "Content-Type": "application/json"
        #         }
        #         payload = {
        #             "channel": body["channel"]["id"],
        #             "text": "This is a reply in the thread!",
        #             "thread_ts": thread_ts
        #         }
        #         response = requests.post(url, headers=headers, json=payload)
        #         if response.status_code != 200 or not response.json().get("ok"):
        #             print(f"Error posting message: {response.json()}")
        #     else:
        #         print("Thread timestamp not found.")



    def approval_buttons(self, channel):
        # Post a message with interactive buttons
        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "channel": channel,
            "text": "Please review the submission:",
            "blocks": [
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Approved"},
                            "style": "primary",
                            "action_id": "button_approved"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Needs Revised"},
                            "style": "danger",
                            "action_id": "button_needs_revised"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "CBB"},
                            "action_id": "button_cbb"
                        }
                    ]
                }
            ]
        }
        response = requests.post(url, headers=headers, json=payload)

        self.metadata["thread_ts"] = response.json()["ts"]

    def post_threaded_message(self, body, text):
        # Post a reply in the thread
        thread_ts = self.metadata.get("thread_ts")
        if not thread_ts:
            print("Thread timestamp not found.")
            return

        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "channel": body["channel"]["id"],
            "text": text,
            "thread_ts": thread_ts
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200 or not response.json().get("ok"):
            print(f"Error posting threaded message: {response.json()}")