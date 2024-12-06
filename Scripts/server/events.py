import requests

class SlackEvents:
    def __init__(self, app, token):
        self.app = app
        self.token = token
        self.metadata = {}  # Store metadata for thread timestamps
        
        # Register actions
        self.register_actions()

    def register_actions(self):
        @self.app.action("button_approved")
        def handle_approved_button_click(ack, body):
            ack()
            self.post_threaded_message(body, "Your submission has been approved!")

        @self.app.action("button_needs_revised")
        def handle_needs_revised_button_click(ack, body):
            ack()
            self.post_threaded_message(body, "Your submission needs revisions.")

        @self.app.action("button_cbb")
        def handle_cbb_button_click(ack, body):
            ack()
            self.post_threaded_message(body, "CBB: Could Be Better. Keep trying!")

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
        if response.status_code == 200 and response.json().get("ok"):
            self.metadata["thread_ts"] = response.json()["ts"]
        else:
            print(f"Error posting message: {response.json()}")

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
