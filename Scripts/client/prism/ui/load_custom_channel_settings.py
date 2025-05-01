import os
from pathlib import Path

from Scripts.client.prism.api import API
from Scripts.client.slack import get_channel_id
from Scripts.client.slack.slack_config import SlackConfig

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


def load_custom_channel_settings(core, origin):
    _check_custom_channel(core, origin)
    _connect_events(core, origin)


def _connect_events(core, origin):
    origin.b_custom_channel_verify.clicked.connect(
        lambda: _verify_custom_channel(core, origin)
    )


def _check_custom_channel(core, origin):
    config = SlackConfig(core).load_config(mode="project")
    if "slack" not in config:
        config["slack"] = {}
        SlackConfig(core).save_config_setting(config, mode="project")

    if "custom" not in config["slack"]:
        config["slack"]["custom"] = {}
        config["slack"]["custom"]["channel"] = ""
        SlackConfig(core).save_config_setting(config, mode="project")
            
        origin.le_custom_channel.setPlaceholderText("Enter a custom channel")

    custom_channel = API(core).get_notify_custom_channel()

    if custom_channel != "":
        origin.le_custom_channel.setText(custom_channel)

        plugin_directory = Path(__file__).resolve().parents[4]
        i_verified = os.path.join(plugin_directory, "Resources", "running.png")

        origin.b_custom_channel_verify.setText("Verified")
        origin.b_custom_channel_verify.setIcon(QIcon(i_verified))

    else:
        origin.le_custom_channel.setPlaceholderText("Enter a custom channel")


# Verify the custom channel exists on Slack
def _verify_custom_channel(core, origin):
    custom_channel = origin.le_custom_channel.text().lower()
    plugin_directory = Path(__file__).resolve().parents[4]

    if custom_channel == "":
        i_not_verified = os.path.join(plugin_directory, "Resources", "not_verified.png")

        origin.b_custom_channel_verify.setText("Not Verified")
        origin.b_custom_channel_verify.setIcon(QIcon(i_not_verified))

    else:
        token = API(core).get_access_token()
        if "token" != "":
            channel_id = get_channel_id(access_token=token, project_name=custom_channel)

            if channel_id is not None:
                i_verified = os.path.join(plugin_directory, "Resources", "running.png")

                origin.b_custom_channel_verify.setText("Verified")
                origin.b_custom_channel_verify.setIcon(QIcon(i_verified))

                # Save the custom channel to the config file
                config = SlackConfig(core).load_config(mode="project")
                if "slack" not in config:
                    config["slack"] = {}
                if "custom" not in config["slack"]:
                    config["slack"]["custom"] = {}
                config["slack"]["custom"]["channel"] = custom_channel
                SlackConfig(core).save_config_setting(config, mode="project")

            else:
                core.popup("Couldn't verify the custom channel")