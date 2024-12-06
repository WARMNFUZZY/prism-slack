class SlackBlocks():
    def __init__(self):
        pass
    
    def approval_buttons(self):
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Approved"
                    },
                    "style": "primary",
                    "action_id": "button_approved"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Needs Revised"
                    },
                    "style": "danger",
                    "action_id": "button_needs_revised"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "CBB"
                    },
                    "action_id": "button_cbb"
                }
            ]
        }

    def divider(self):
        {
            "type": "divider"
        },