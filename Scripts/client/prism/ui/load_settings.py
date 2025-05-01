from Scripts.client.slack.slack_config import SlackConfig
from Scripts.server.controls import ServerControls
from Scripts.client.prism.ui import InputDialog
from Scripts.client.prism.api import API

from Scripts.client.prism.ui.load_custom_channel_settings import (
    load_custom_channel_settings,
)

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


pcore = None


def load_settings(core, origin, settings):
    global pcore
    pcore = core

    _set_options(origin)
    _connect_events(origin)
    

# Set the Slack options in the studio/project settings window
def _set_options(origin):
    # Check for the slack oauth token and assign it in the ui
    _check_token(origin)

    # Add current methods for notifications and set the current method in the ui
    _add_notify_methods(origin)
    _check_notify_method(origin)

    # Add the current user pools for notifications and set the current user pool in the ui
    _add_notify_user_pools(origin)
    _check_notify_user_pool(origin)

    # Check for the app-level token and assign it in the ui
    _check_app_level_token(origin)
    ServerControls(pcore).check_server_status(origin)


# Connect the events in the studio/project settings window
def _connect_events(origin):
    origin.b_slack_token.clicked.connect(lambda: _input_token(origin))
    origin.cb_notify_user_pool.currentIndexChanged.connect(
        lambda index: _update_notify_user_pool(origin, index)
    )
    origin.cb_notify_method.currentIndexChanged.connect(
        lambda index: _update_notify_method(origin, index)
    )

    origin.b_app_token.clicked.connect(lambda: _input_app_level_token(origin))
    origin.b_server.clicked.connect(lambda: ServerControls(pcore).toggle_server(origin))
    origin.b_reset_server.clicked.connect(
        lambda: ServerControls(pcore).gui_reset_server_status(origin)
    )


# Pop up a dialog to input the Slack API token
def _input_token(origin):
    input_dialog = InputDialog(title="Enter your Slack Bot API Token")
    if input_dialog.exec_() == QDialog.Accepted:
        slack_token = input_dialog.get_input()
        origin.le_slack_token.setText(slack_token)

        # Save the token to the config file
        config = SlackConfig(pcore).load_config(mode="studio")
        config["slack"]["token"] = slack_token
        SlackConfig(pcore).save_config_setting(config, mode="studio")


# Check if the Slack API token is present in the pipeline configuration file
def _check_token(origin):
    token = API(pcore).get_access_token()
    
    if token == "":
        origin.le_slack_token.setPlaceholderText("Enter your Slack API Token")
    else:
        origin.le_slack_token.setText(token)


# Add notification methods to the dropdown in the studio/project settings Slack window
def _add_notify_methods(origin):
    methods = ["Direct", "Channel", "Ephemeral Direct", "Ephemeral Channel"]

    origin.cb_notify_method.addItems(methods)


# Change the notification method in the studio/project settings Slack window
def _update_notify_method(origin, index):
    config = SlackConfig(pcore).load_config("studio")

    config["slack"]["notifications"]["method"] = origin.cb_notify_method.currentText()

    SlackConfig(pcore).save_config_setting(config, "studio")


# Check the notification method in the studio/project settings Slack window
def _check_notify_method(origin):
    notify_method = API(pcore).get_notify_user_method()

    if notify_method != "":
        origin.cb_notify_method.setCurrentText(notify_method)

    else:
        return


# Add the user pools used for notifications to the dropdown in the studio/project settings Slack window
def _add_notify_user_pools(origin):
    user_pool = []
    # Disabling the Studio user pool for now until I set a better method for acquiring all studio Display Names
    # if pcore.getPlugin("Studio"):
    #     user_pool.append("Studio")
    user_pool.append("Channel")

    origin.cb_notify_user_pool.addItems(user_pool)


# Update the user pools used for notifications in the studio/project settings Slack window
def _update_notify_user_pool(origin, index):
    config = SlackConfig(pcore).load_config("studio")

    config["slack"]["notifications"]["user_pool"] = (
        origin.cb_notify_user_pool.currentText()
    )

    SlackConfig(pcore).save_config_setting(config, "studio")


# Check the method of notification to Slack users
def _check_notify_user_pool(origin):
    notify_user_pool = API(pcore).get_notify_user_pool()

    if notify_user_pool != "":
        origin.cb_notify_user_pool.setCurrentText(notify_user_pool)

    else:
        return


# Input the App-Level Token in the project/studio settings Window
def _input_app_level_token(origin):
    input_dialog = InputDialog(title="Enter your Slack App-Level Token")
    if input_dialog.exec_() == QDialog.Accepted:
        app_token = input_dialog.get_input()
        origin.le_app_token.setText(app_token)

        config = SlackConfig(pcore).load_config(mode="studio")
        config["slack"]["server"]["app_token"] = app_token
        SlackConfig(pcore).save_config_setting(config, mode="studio")


# Check the App-Level token in the project/studio config file
def _check_app_level_token(origin):
    app_token = API(pcore).get_app_level_token()

    if "app_token" != "":
        origin.le_app_token.setText(app_token)

    else:
        origin.le_app_token.setPlaceholderText("Enter your Slack App-Level Token")
        return
