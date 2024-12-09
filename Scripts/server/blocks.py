class SlackBlocks():
    def __init__(self):
        pass

    # def profile_accessory(self, user_avatar):
    #     return {
    #         "type": "image",
    #         "image_url": user_avatar,
    #         "alt_text": "User profile picture"
    #     }
    
    def identifier_information(self, sequence, shot, identifier, version, artist, user_avatar, status):
        return {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Sequence:* _{sequence}_"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Identifier:* _{identifier}_"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Shot:* _{shot}_"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Version:* _{version}_"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Artist:* _<@{artist}>_"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Status:* _{status}_"

                }
            ],
            "accessory": {
                "type": "image",
                "image_url": user_avatar,
                "alt_text": "User profile picture"
            }
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
        }
    
    def comments(self, comments):
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Comments: *\n{comments}"
            }
        }
    
    def revision_description(self, artist):
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Leave some revision comments/notes for <@{artist}>. We will notify them that there are some adjustments needed."
            }
        }

    def text_input(self):
        return {
            "type": "input",
            "block_id": "input_comments",
            "label": {
                "type": "plain_text",
                "text": "Comments"
            },
            "element": {
                "type": "plain_text_input",
                "multiline": True
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