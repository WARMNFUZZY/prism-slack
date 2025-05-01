from Scripts.client.prism.ui.settings_ui import SettingsUI
from Scripts.client.slack.slack_config import SlackConfig


# Load the UI for the Slack plugin in the user settings window
def userSettings_loadUI(core, origin):
    SettingsUI(core).create_user_settings_ui(origin)
    _check_username(core, origin)
    origin.b_userSave.clicked.connect(lambda: _save_username(core, origin))


# Check the Slack display name in the user settings window and set it if it exists
def _check_username(core, origin):
    le_user = origin.le_user
    user_data = SlackConfig(core).load_config("user")

    if "slack" not in user_data:
        user_data["slack"] = {}
        user_data["slack"]["username"] = ""

    if "username" in user_data["slack"]:
        le_user.setText(user_data["slack"].get("username"))
    else:
        le_user.setPlaceholderText("Enter your Slack Display Name")

    SlackConfig(core).save_config_setting(user_data, "user")


# Save the Slack display name in the user config file
def _save_username(core, origin):
    le_user = origin.le_user
    user_data = SlackConfig(core).load_config("user")

    user_data["slack"]["username"] = le_user.text()
    SlackConfig(core).save_config_setting(user_data, "user")
