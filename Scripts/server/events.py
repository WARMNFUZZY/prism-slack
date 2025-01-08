import requests
import json

from pprint import pprint
from server.blocks import SlackBlocks


class SlackEvents:
    def __init__(self, app, token, core):
        self.core = core
        self.app = app
        self.token = token
        self.metadata = {}
        self.blocks = SlackBlocks()

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

        @self.app.action("button_approved")
        def action_button_approved(body, ack, say):
            ack()

            thread_ts = body["message"].get("ts")

            url = "https://slack.com/api/chat.postMessage"
            headers = {
                "Authorization": f"Bearer {self.token}",
            }
            payload = {
                "channel": body["channel"]["id"],
                "text": "Marked as: Approved by " f"<@{body['user']['id']}>",
                "thread_ts": thread_ts,
            }
            response = requests.post(url, headers=headers, json=payload)

        # When the Needs Revised Button is clicked, gather information and open the Modal window
        @self.app.action("button_needs_revised")
        def action_button_needs_revised(body, ack, client):
            ack()

            metadata = json.dumps(
                {
                    "timestamp": body["message"]["ts"],
                    "channel": body["channel"]["id"],
                    "reviewer": body["user"]["id"],
                }
            )

            blocks = body["message"].get("blocks", [])
            for block in blocks:
                for field in block.get("fields", []):
                    if field.get("text", "").startswith("*Artist:*"):
                        artist = field["text"].strip().split(" ")[-1].strip("_<@>")
                        break

            client.views_open(
                trigger_id=body["trigger_id"],
                view={
                    "type": "modal",
                    "callback_id": "modal-needs-revised",
                    "title": {"type": "plain_text", "text": "Needs Revised"},
                    "blocks": [
                        self.blocks.revision_description(artist),
                        self.blocks.text_input(),
                    ],
                    "close": {"type": "plain_text", "text": "Cancel"},
                    "submit": {"type": "plain_text", "text": "Submit"},
                    "private_metadata": metadata,
                },
            )

        # When the Needs Revised Submit Button is clicked, close the Modal window and make a Threaded response
        @self.app.view("modal-needs-revised")
        def view_submission_needs_revised(ack, body, client):
            ack()

            metadata = json.loads(body["view"]["private_metadata"])
            reviewer = body["user"]["id"]
            for block in body["view"]["blocks"]:
                if "element" in block and "action_id" in block["element"]:
                    element_id = block["element"]["action_id"]
                    break
            comments = body["view"]["state"]["values"]["input_comments"][element_id][
                "value"
            ]

            url = "https://slack.com/api/chat.postMessage"
            headers = {
                "Authorization": f"Bearer {self.token}",
            }
            payload = {
                "channel": metadata["channel"],
                "text": f"Marked as: *Needs revised* by <@{reviewer}>\n\n{comments}",
                "thread_ts": metadata["timestamp"],
            }
            response = requests.post(url, headers=headers, json=payload)

        # When the CBB Button is clicked, gather information and open the Modal window
        @self.app.action("button_cbb")
        def action_button_cbb(body, ack, client):
            ack()

            metadata = json.dumps(
                {
                    "timestamp": body["message"]["ts"],
                    "channel": body["channel"]["id"],
                    "reviewer": body["user"]["id"],
                }
            )

            blocks = body["message"].get("blocks", [])
            for block in blocks:
                for field in block.get("fields", []):
                    if field.get("text", "").startswith("*Artist:*"):
                        artist = field["text"].strip().split(" ")[-1].strip("_<@>")
                        break

            client.views_open(
                trigger_id=body["trigger_id"],
                view={
                    "type": "modal",
                    "callback_id": "modal-cbb",
                    "title": {"type": "plain_text", "text": "Could Be Better"},
                    "blocks": [
                        self.blocks.cbb_description(artist),
                        self.blocks.text_input(),
                    ],
                    "close": {"type": "plain_text", "text": "Cancel"},
                    "submit": {"type": "plain_text", "text": "Submit"},
                    "private_metadata": metadata,
                },
            )

        # When the CBB Submit Button is clicked, close the Modal window and make a Threaded response
        @self.app.view("modal-cbb")
        def view_submission_cbb(ack, body, client):
            ack()

            metadata = json.loads(body["view"]["private_metadata"])
            reviewer = body["user"]["id"]

            for block in body["view"]["blocks"]:
                if "element" in block and "action_id" in block["element"]:
                    element_id = block["element"]["action_id"]
                    break
            comments = body["view"]["state"]["values"]["input_comments"][element_id][
                "value"
            ]

            url = "https://slack.com/api/chat.postMessage"
            headers = {
                "Authorization": f"Bearer {self.token}",
            }
            payload = {
                "channel": metadata["channel"],
                "text": f"Marked as: *CBB* by <@{reviewer}>\n\n{comments}",
                "thread_ts": metadata["timestamp"],
            }
            response = requests.post(url, headers=headers, json=payload)
