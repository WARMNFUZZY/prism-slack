import os
from pathlib import Path

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from PrismUtils.Decorators import err_catcher_plugin as err_catcher


class SettingsUI:
    def __init__(self, core):
        super().__init__()
        self.core = core

    # Create the UI for the Slack plugin
    @err_catcher(__name__)
    def create_slack_studio_settings_ui(self, origin, settings):
        if not hasattr(origin, "w_slackStudioTab"):
            origin.w_slackStudioTab = QWidget()
            lo_slack = QVBoxLayout(origin.w_slackStudioTab)

            self._create_slack_token_settings_menu(lo_slack, origin)
            self._create_notifications_publish_settings_menu(lo_slack, origin)
            self._create_server_settings_menu(lo_slack, origin)

            origin.addTab(origin.w_slackStudioTab, "Slack")

    # Create the Slack UI for the Project Settings
    @err_catcher(__name__)
    def create_slack_project_settings_ui(self, origin, settings):
        if not hasattr(origin, "w_slackProjectTab"):
            origin.w_slackProjectTab = QWidget()
            lo_slack = QVBoxLayout(origin.w_slackProjectTab)

            self._create_slack_token_settings_menu(lo_slack, origin)
            self._create_notifications_publish_settings_menu(lo_slack, origin)
            self._create_custom_channel_settings(lo_slack, origin)
            self._create_server_settings_menu(lo_slack, origin)

            origin.addTab(origin.w_slackProjectTab, "Slack")

    # Create the Custom Channel UI for Project tab
    @err_catcher(__name__)
    def create_slack_custom_channel_ui(self, origin, settings):
        if not hasattr(origin, "w_slackCustomChannelTab"):
            origin.w_slackCustomChannelTab = QWidget()
            lo_slack = QVBoxLayout(origin.w_slackCustomChannelTab)

            self._create_custom_channel_settings(lo_slack, origin)

            origin.addTab(origin.w_slackCustomChannelTab, "Slack")

    # Create the User Settings UI
    @err_catcher(__name__)
    def create_user_settings_ui(self, origin):
        if not hasattr(origin, "w_slackUserTab"):
            origin.w_slackUserTab = QWidget()
            lo_slackUserTab = QVBoxLayout(origin.w_slackUserTab)

            i_slackLogo = self._grab_slack_logo()
            lo_user = QHBoxLayout()
            l_user = QLabel("Display Name: ")
            le_user = QLineEdit()
            le_user.setPlaceholderText("Enter your Slack Display Name")
            origin.le_user = le_user

            i_userHelp = self._grab_help_icon()
            i_userHelp.setToolTip("""<p style='line-height:1;'>
                                    Input your Display Name, not your Full Name from your Slack Profile
                                    </p>""")

            lo_user.addWidget(l_user)
            lo_user.addWidget(origin.le_user)
            lo_user.addWidget(i_userHelp)

            lo_save = QHBoxLayout()

            lo_save.addStretch()
            b_userSave = QPushButton("Save")
            origin.b_userSave = b_userSave

            lo_save.addWidget(origin.b_userSave)
            lo_save.addStretch()

            lo_slackUserTab.addStretch()
            lo_slackUserTab.addWidget(i_slackLogo)
            lo_slackUserTab.addLayout(lo_user)
            lo_slackUserTab.addLayout(lo_save)
            lo_slackUserTab.addStretch()

            origin.addTab(origin.w_slackUserTab, "Slack")

    # Create the Slack OAuth Token Settings Menu
    @err_catcher(__name__)
    def _create_slack_token_settings_menu(self, lo_slack, origin):
        l_slack_logo = self._grab_slack_logo()

        le_slack_token = QLineEdit()
        le_slack_token.setPlaceholderText("Enter your Slack API Token")
        le_slack_token.setEchoMode(QLineEdit.Password)
        le_slack_token.setReadOnly(True)
        le_slack_token.setFocusPolicy(Qt.NoFocus)
        le_slack_token.setContextMenuPolicy(Qt.NoContextMenu)
        origin.le_slack_token = le_slack_token

        l_slack_token_help = self._grab_help_icon()
        l_slack_token_help.setToolTip("""<p style='line-height:1;'>
                                                <span> Can be found in your Slack app settings under OAuth & Permissions -> Bot User OAuth Token</span>
                                                </p>""")

        b_slack_token = QPushButton("Input Token")
        origin.b_slack_token = b_slack_token

        lo_slack.addStretch()
        lo_slack.addWidget(l_slack_logo)
        lo_slack.setAlignment(l_slack_logo, Qt.AlignBottom)

        lo_slack.addWidget(origin.le_slack_token)
        lo_slack.setAlignment(origin.le_slack_token, Qt.AlignBottom)

        lo_slack.addWidget(origin.b_slack_token)
        lo_slack.setAlignment(origin.b_slack_token, Qt.AlignBottom | Qt.AlignCenter)

    # Create the Notifications Settings Menu
    @err_catcher(__name__)
    def _create_notifications_publish_settings_menu(self, lo_slack, origin):
        gb_notifications = QGroupBox()
        gb_notifications.setTitle("Notifications/Publish")
        gb_notifications.setContentsMargins(0, 30, 0, 0)
        lo_notifications = QVBoxLayout()
        gb_notifications.setLayout(lo_notifications)

        lo_notify_user_pool = QHBoxLayout()
        l_notify_method = QLabel("Notify Method:")
        l_notify_user_pool = QLabel("User Pool:")
        cb_notify_user_pool = QComboBox()
        cb_notify_user_pool.setPlaceholderText("Notify User Pool")
        origin.cb_notify_user_pool = cb_notify_user_pool

        l_notify_user_pool_help = self._grab_help_icon()
        l_notify_user_pool_help.setToolTip("""<p style='line-height:1;'>
                                        <span style='color:DodgerBlue;'><b>Studio</b></span>: Draw from the users in the Studio plugin pool<br>
                                        <br>
                                        <span style='color:Tomato;'><b>Channel</b></span>: Draw from the users in the Slack Project Channel<br>
                                        <br>
                                        <span style='color:MediumSeaGreen;'><b>Team</b></span>: Draw from the users in the Slack Team pool<br>
                                        <i>Note: If not kept up to date, your Team pool could be rather large</i>
                                        </p>""")

        lo_notify_user_pool.addWidget(l_notify_user_pool)
        lo_notify_user_pool.addWidget(origin.cb_notify_user_pool)
        lo_notify_user_pool.addWidget(l_notify_user_pool_help)
        lo_notify_user_pool.addStretch()
        lo_notifications.addLayout(lo_notify_user_pool)

        lo_notify_method = QHBoxLayout()
        l_notify_method = QLabel("Method: ")
        cb_notify_method = QComboBox()
        cb_notify_method.setPlaceholderText("Notify Method")
        origin.cb_notify_method = cb_notify_method

        l_notify_method_help = self._grab_help_icon()
        l_notify_method_help.setToolTip("""<p style='line-height:1;'>
                                        <span style='color:DodgerBlue;'><b>Direct</b></span>: Notify the selected user by Direct message<br>
                                        <br>
                                        <span style='color:Tomato;'><b>Channel</b></span>: Notify selected user in the Slack Channel<br>
                                        <br>
                                        <span style='color:MediumSeaGreen;'><b>Ephemeral Direct</b></span>: Notify the selected user in an ephemeral Direct message<br>
                                        <br>
                                        <span style='color:MediumSlateBlue;'><b>Ephemeral Channel</b></span>: Notify selected user in an ephemeral Channel message<br>
                                        </p>""")

        lo_notify_method.addWidget(l_notify_method)
        lo_notify_method.addWidget(origin.cb_notify_method)
        lo_notify_method.addWidget(l_notify_method_help)
        lo_notify_method.addStretch()
        lo_notifications.addLayout(lo_notify_method)

        lo_slack.addWidget(gb_notifications)
        lo_slack.setAlignment(lo_notifications, Qt.AlignTop | Qt.AlignLeft)

    # Create Custom Channel Settings
    @err_catcher(__name__)
    def _create_custom_channel_settings(self, lo_slack, origin):
        gb_custom_channel = QGroupBox()
        gb_custom_channel.setTitle("Custom Channel")
        gb_custom_channel.setContentsMargins(0, 30, 0, 0)
        lo_custom_channel = QHBoxLayout()
        gb_custom_channel.setLayout(lo_custom_channel)

        origin.l_custom_channel = QLabel("Channel Name: ")
        origin.le_custom_channel = QLineEdit()
        origin.le_custom_channel.setPlaceholderText("Enter the custom channel name")

        origin.b_custom_channel_verify = QPushButton("Verify")
        plugin_directory = Path(__file__).resolve().parents[4]
        i_verify = os.path.join(plugin_directory, "Resources", "not_verified.png")
        origin.b_custom_channel_verify.setIcon(QIcon(i_verify))

        origin.l_custom_channel_help = self._grab_help_icon()
        origin.l_custom_channel_help.setToolTip("""<p style='line-height:1;'>
                                        <span>Enter the name of the custom channel you want to send notifications/publishes. <br><br> </span>
                                        <span><i>NOTE: If you want to remove the custom channel, delete the text and press the verify button again</i></span>
                                        </p>""")

        lo_custom_channel.addWidget(origin.l_custom_channel)
        lo_custom_channel.addWidget(origin.le_custom_channel)
        lo_custom_channel.addWidget(origin.b_custom_channel_verify)
        lo_custom_channel.addWidget(origin.l_custom_channel_help)
        lo_custom_channel.addStretch()

        lo_slack.addWidget(gb_custom_channel)
        lo_slack.setAlignment(lo_custom_channel, Qt.AlignTop | Qt.AlignLeft)


    # Create the Server Settings Menu
    @err_catcher(__name__)
    def _create_server_settings_menu(self, lo_slack, origin):
        gb_server = QGroupBox()
        gb_server.setTitle("Server")
        gb_server.setContentsMargins(0, 30, 0, 0)
        lo_server = QVBoxLayout()
        gb_server.setLayout(lo_server)

        lo_status = QHBoxLayout()
        l_server_status = QLabel("Status: ")
        l_server_status_value = QLabel("Offline")
        fo_server_status_value = l_server_status_value.font()
        fo_server_status_value.setItalic(True)
        l_server_status_value.setFont(fo_server_status_value)
        origin.l_server_status_value = l_server_status_value

        lo_status.addWidget(l_server_status)
        lo_status.addWidget(origin.l_server_status_value)
        lo_status.addStretch()

        b_server = QPushButton("Start Server")
        origin.b_server = b_server
        lo_status.addWidget(origin.b_server)

        b_reset_server = QPushButton("Reset Server")
        origin.b_reset_server = b_reset_server
        lo_status.addWidget(origin.b_reset_server)

        lo_machine = QHBoxLayout()
        l_machine = QLabel("Machine: ")
        l_machine_value = QLabel("---------")
        fo_machine_value = l_machine_value.font()
        fo_machine_value.setItalic(True)
        l_machine_value.setFont(fo_machine_value)
        origin.l_machine_value = l_machine_value

        lo_machine.addWidget(l_machine)
        lo_machine.addWidget(origin.l_machine_value)
        lo_machine.addStretch()

        lo_app_token = QHBoxLayout()
        le_app_token = QLineEdit()
        le_app_token.setPlaceholderText("Enter your Slack App-Level Token")
        le_app_token.setEchoMode(QLineEdit.Password)
        le_app_token.setReadOnly(True)
        le_app_token.setFocusPolicy(Qt.NoFocus)
        le_app_token.setContextMenuPolicy(Qt.NoContextMenu)
        origin.le_app_token = le_app_token

        l_app_token_help = self._grab_help_icon()
        l_app_token_help.setToolTip("""<p style='line-height:1;'>
                                                <span> Can be found in your app settings under Basic Information -> App-Level Tokens</span>
                                                </p>""")

        lo_app_token.addWidget(origin.le_app_token)
        lo_app_token.addWidget(l_app_token_help)

        lo_button_app_token = QHBoxLayout()
        b_app_token = QPushButton("Input App-Level Token")
        origin.b_app_token = b_app_token

        lo_button_app_token.addStretch()
        lo_button_app_token.addWidget(origin.b_app_token)
        lo_button_app_token.addStretch()

        lo_server.addLayout(lo_status)
        lo_server.addLayout(lo_machine)
        lo_server.addLayout(lo_app_token)
        lo_server.addLayout(lo_button_app_token)

        lo_slack.addWidget(gb_server)
        lo_slack.setAlignment(lo_server, Qt.AlignTop | Qt.AlignLeft)
        lo_slack.addStretch()

    # Grab the Slack logo
    @err_catcher(__name__)
    def _grab_slack_logo(self):
        l_slack = QLabel()

        plugin_directory = Path(__file__).resolve().parents[4]
        i_slack = os.path.join(plugin_directory, "Resources", "slack-logo.png")

        pixmap = QPixmap(i_slack)

        # Set pixmap to label and scale
        scale = 0.05
        l_slack.setPixmap(pixmap)
        l_slack.setScaledContents(True)
        l_slack.setFixedSize(pixmap.width() * scale, pixmap.height() * scale)
        l_slack.setContentsMargins(0, 0, 0, 0)

        return l_slack

    # Grab the Help Icon
    @err_catcher(__name__)
    def _grab_help_icon(self):
        l_help = QLabel()
        help_icon = os.path.join(
            self.core.prismLibs, "Scripts", "UserInterfacesPrism", "help.png"
        )

        pixmap = QPixmap(help_icon)

        l_help.setPixmap(pixmap)

        return l_help

    # Grab verify icon
    def _grab_verify_icon(self):
        l_verify = QLabel()
        plugin_directory = Path(__file__).resolve().parents[4]
        i_verify = os.path.join(plugin_directory, "Resources", "not_verified.png")

        pixmap = QPixmap(l_verify)

        l_verify.setPixmap(pixmap)

        return l_verify
