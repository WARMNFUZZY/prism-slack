import requests
import json

from pprint import pprint 
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

        @self.app.action("button_approved")
        def action_button_approved(body, ack, say):
            ack()
            from pprint import pprint
            pprint(body)
            thread_ts = body['message'].get('ts')
            blocks = body['message'].get('blocks', [])
            for block in blocks:
                for field in block.get('fields', []):
                    if field.get('text', '').startswith('*Artist:*'):
                        user_id = field['text'].strip().split(" ")[-1].strip("_<>")
                        break 

            url = "https://slack.com/api/chat.postMessage"
            headers = {
                "Authorization": f"Bearer {self.token}",
            }
            payload = {
                "channel": body["channel"]["id"],
                "text": "Marked as: Approved by " f"<{user_id}>",
                "thread_ts": thread_ts
            }
            response = requests.post(url, headers=headers, json=payload)

        @self.app.action("button_needs_revised")
        def action_button_needs_revised(body, ack, client):
            ack()

            metadata = json.dumps({
                "timestamp": body["message"]["ts"],
                "channel": body["channel"]["id"]
            })
            artist = body["user"]["id"]
            client.views_open(
                trigger_id=body["trigger_id"],
                view= {
                    "type": "modal",
                    "callback_id": "modal-needs-revised",
                    "title": {"type": "plain_text", "text": "Needs Revised"}, 
                    "blocks": [
                        self.blocks.revision_description(artist),
                        self.blocks.text_input(),

                    ],
                    "close": {"type": "plain_text", "text": "Cancel"},
                    "submit": {"type": "plain_text", "text": "Submit"},
                    "private_metadata": metadata
                },
            )

        @self.app.view("modal-needs-revised")
        def view_submission_needs_revised(ack, body, client):
            ack()

            metadata = json.loads(body["view"]["private_metadata"])
            user_id = body["user"]["id"]
            for block in body['view']['blocks']:
                if 'element' in block and 'action_id' in block['element']:
                    element_id = block['element']['action_id']
                    break
            comments = body["view"]["state"]["values"]["input_comments"][element_id]["value"]

            url = "https://slack.com/api/chat.postMessage"
            headers = {
                "Authorization": f"Bearer {self.token}",
            }
            payload = {
                "channel": metadata['channel'],
                "text": f"Marked as: *Needs revised* by <@{user_id}>\n\n{comments}",
                "thread_ts": metadata["timestamp"]
            }
            response = requests.post(url, headers=headers, json=payload)

        @self.app.action("button_cbb")
        def action_button_cbb(body, ack, client):
            ack()

            metadata = json.dumps({
                "timestamp": body["message"]["ts"],
                "channel": body["channel"]["id"]
            })
            artist = body["user"]["id"]
            client.views_open(
                trigger_id=body["trigger_id"],
                view= {
                    "type": "modal",
                    "callback_id": "modal-cbb",
                    "title": {"type": "plain_text", "text": "Could Be Better"}, 
                    "blocks": [
                        self.blocks.cbb_description(artist),
                        self.blocks.text_input(),

                    ],
                    "close": {"type": "plain_text", "text": "Cancel"},
                    "submit": {"type": "plain_text", "text": "Submit"},
                    "private_metadata": metadata
                },
            )

        @self.app.view("modal-cbb")
        def view_submission_cbb(ack, body, client):
            ack()

            metadata = json.loads(body["view"]["private_metadata"])
            user_id = body["user"]["id"]
            for block in body['view']['blocks']:
                if 'element' in block and 'action_id' in block['element']:
                    element_id = block['element']['action_id']
                    break
            comments = body["view"]["state"]["values"]["input_comments"][element_id]["value"]

            url = "https://slack.com/api/chat.postMessage"
            headers = {
                "Authorization": f"Bearer {self.token}",
            }
            payload = {
                "channel": metadata['channel'],
                "text": f"Marked as: *CBB* by <@{user_id}>\n\n{comments}",
                "thread_ts": metadata["timestamp"]
            }
            response = requests.post(url, headers=headers, json=payload)