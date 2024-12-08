class SlackBlocks():
    def __init__(self):
        pass

    def identifier_information(self, sequence, shot, task, identifier, version, artist):
        return {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Sequence: *\n{sequence}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Shot: *\n{shot}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Task: *\n{task}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Identifier: *\n{identifier}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Version: *\n{version}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Artist: *\n{artist}"
                }
            ]
        }
    
    def product_information(self, asset, task, product, version, artist):
        return {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Asset: *\n{asset}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Task: *\n{task}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Product: *\n{product}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Version: *\n{version}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Artist: *\n{artist}"
                }
            ]
        },
    
    def comments(self, comments):
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Comments: *\n{comments}"
            }
        }

    def approval_buttons(self):
        return {
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
        return {
            "type": "divider"
        }