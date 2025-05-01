from Scripts.client.slack.slack_config import SlackConfig
from Scripts.client.prism.api import API
from Scripts.client.slack import (
    get_channel_users,
    get_channel_id,
    post_channel_message,
    post_direct_message,
    post_channel_ephemeral_message,
    post_direct_ephemeral_message,
)
from Scripts.client.prism.ui import InputDialog
import os


def prePlayblast(core, **kwargs):
    state = kwargs.get("state", None)

    try:
        access_token = API(core).get_access_token()
    except:
        raise "Failed to retrieve Slack access token. Please check your configuration."

    if state.gb_slack.isChecked():
        if state.chb_slackNotify.isChecked():
            if API(core).get_prism_slack_username() == "":
                local_user = _input_local_slack_user()

            else:
                local_user = API(core).get_prism_slack_username()

            project = API(core).get_current_project()
            notify_user = state.cb_slackUserPool.currentText()
            channel = get_channel_id(access_token, project)
            channel_users = get_channel_users(access_token, channel)
            slack_recipient = API(core).get_slack_user_id(notify_user, channel_users)
            product = state.l_taskName.text()
            slack_sender = API(core).get_slack_user_id(local_user, channel_users)

            notify_slack_user(
                core, access_token, slack_recipient, channel, product, slack_sender
            )


# Notify user about new version of product is on the way!
def notify_slack_user(
    core, access_token, slack_recipient, channel, product, slack_sender
):
    if os.getenv("PRISM_SEQUENCE") is not None:
        seq = os.getenv("PRISM_SEQUENCE")
        shot = os.getenv("PRISM_SHOT")

    message = API(core).get_render_message(slack_recipient, seq, shot, product, slack_sender)

    config = SlackConfig(core).load_config("studio")
    method = config["slack"]["notifications"].get("method")

    if method.lower() == "channel":
        post_channel_message(access_token, channel, message)

    elif method.lower() == "direct":
        post_direct_message(access_token, slack_recipient, message)

    elif method.lower() == "ephemeral direct":
        post_direct_ephemeral_message(access_token, slack_recipient, message)

    else:
        post_channel_ephemeral_message(access_token, slack_recipient, channel, message)


def _input_local_slack_user():
    dialog = InputDialog(title="Enter your Slack Display Name")
    dialog.exec_()

    return dialog.get_input()
