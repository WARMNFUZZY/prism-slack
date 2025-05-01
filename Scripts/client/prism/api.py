from Scripts.client.slack.slack_config import SlackConfig
from Scripts.client.prism.ui import WarningDialog, InputDialog

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

studio_config = None
project_config = None
user_config = None

class API:
    def __init__(self, core):

        global studio_config, project_config, user_config

        self.core = core
        if self.is_studio_loaded() is not None:
            studio_config = SlackConfig(self.core).load_config("studio")
            project_config = SlackConfig(self.core).load_config("project")
        else:
            try:
                studio_config = SlackConfig(self.core).load_config("studio")
            except:
                studio_config = None

            project_config = SlackConfig(self.core).load_config("project")
        
        user_config = SlackConfig(self.core).load_config("user")

    # Get Slack Access Token from config file
    def get_access_token(self):
        return studio_config["slack"]["token"]

    # Get Slack App Level Token from config file
    def get_app_level_token(self):
        return studio_config["slack"]["server"]["app_token"]

    # Get the current project name
    def get_current_project(self):
        custom_channel = self.get_notify_custom_channel()

        if custom_channel == "" or custom_channel is None:
            project = self.core.getConfig(
                "globals", "project_name", configPath=self.core.prismIni
            ).lower()

        else:
            project = custom_channel

        return project

    # Get Slack Notification Method from config file
    def get_notify_user_method(self):
        return studio_config["slack"]["notifications"]["method"]

    # Get Slack Notification User Pool from config file
    def get_notify_user_pool(self):
        return studio_config["slack"]["notifications"]["user_pool"]

    # Get Custom Slack Notification Channel from config file
    def get_notify_custom_channel(self):
        return project_config["slack"]["custom"]["channel"]

    def get_server_approvals(self):
        return studio_config["slack"]["approvals"]["enabled"]

    def get_approvals_usergroup(self):
        return studio_config["slack"]["approvals"]["usergroup"]

    def get_server_status(self):
        return studio_config["slack"]["server"]["status"]

    def get_server_machine(self):
        return studio_config["slack"]["server"]["machine"]

    def get_server_pid(self):
        return studio_config["slack"]["server"]["pid"]

    # Get Slack Display Name from prism user configuration
    def get_prism_slack_username(self):
        user_data = SlackConfig(self.core).load_config("user")

        if user_data["slack"]["username"] == "":
            input_dialog = InputDialog(title="Enter your Slack Display Name")
            if input_dialog.exec_() == QDialog.Accepted:
                username = input_dialog.get_input()
                user_data["slack"]["username"] = username
                SlackConfig(self.core).save_config_setting(user_data, "user")
                return username

        else:
            return user_data["slack"].get("username")

    # Get Slack User ID from user list
    def get_slack_user_id(self, username, user_pool):
        for user in user_pool:
            if username == user["display_name"]:
                return user.get("id")

        return None

    # Check if the studio plugin is loaded
    def is_studio_loaded(self):
        return self.core.getPlugin("Studio")

    # Open dialog warning user that they are part of the team but not part of the project
    def teams_user_warning(self, user):
        dialog = WarningDialog(team_user=user)
        if dialog.exec_() == QDialog.Accepted:
            return True
        else:
            return False

    # Get the message to send to the user
    def get_render_message(self, slack_user, seq, shot, product, sender):
        import random

        if random.randint(0, 100) == 90:
            message = f"Dearest <@{slack_user}>,\nI bring you tidings of the utmost importance! The {product} render for Shot `{shot}` in the enchanting Sequence `{seq}` has begun. Courtesy of the illustrious <@{sender}>, of course. May the pixels align in harmonious perfection!\nYours in cinematic anticipation,\nMoira Rose"

        elif random.randint(0, 100) == 100:
            message = f"<@{slack_user}>\n`{product}`/`{seq}`/`{shot}`\n<https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExeW4xNGl1dGxtMWY5d2tsMTBuYXc3enYza3FkNnpoZDNoYWlremh5NSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/SSiwN19NtD1xUAikqf/giphy.gif>"

        else:
            message = f"Heads up <@{slack_user}>!\n A new version of `{product}` for `{seq}`/`{shot}` is on the way!"

        return message