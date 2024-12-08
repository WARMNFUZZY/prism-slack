import requests

from server.blocks import SlackBlocks

class SlackEvents:
    def __init__(self, app, token, blocks):
        self.app = app
        self.token = token
        self.metadata = {}  # Store metadata for thread timestamps
        self.blocks = SlackBlocks()

        
        # Register actions
        self.register_actions()

    def register_actions(self):
        from pprint import pprint
        blocks = self.blocks.approval_buttons()
        pprint(blocks)

        # Listens to incoming messages that contain "hello
        @self.app.message("hello")
        def message_hello(message, say):
            # Post the message with a button
            from pprint import pprint
            pprint(message)
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
            self.app.metadata = {"thread_ts": response["ts"]}

        @self.app.action("button_approved")
        def action_button_approved(body, ack, say):
            ack()
            from pprint import pprint
            pprint(body)
            user_id = body["user"]["id"]
            pprint(user_id)
            thread_ts = self.app.metadata.get("thread_ts", None)
            if thread_ts:
                url = "https://slack.com/api/chat.postMessage"
                headers = {
                    "Authorization": f"Bearer {self.token}",
                }
                payload = {
                    "channel": body["channel"]["id"],
                    "text": "Approved by " f"<@{user_id}>",
                    "thread_ts": thread_ts
                }
                response = requests.post(url, headers=headers, json=payload)
                if response.status_code != 200 or not response.json().get("ok"):
                    print(f"Error posting message: {response.json()}")
            else:
                print("Thread timestamp not found.")

        @self.app.action("button_needs_revised")
        def action_button_needs_revised(body, ack):
            ack()


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