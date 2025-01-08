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
    def createSlackStudioSettingsUI(self, origin, settings):
        if not hasattr(origin, "w_slackStudioTab"):
            origin.w_slackStudioTab = QWidget()
            lo_slack = QVBoxLayout(origin.w_slackStudioTab)

            self.createSlackTokenSettingsMenu(lo_slack, origin)
            self.createNotificationsSettingsMenu(lo_slack, origin)
            self.createServerSettingsMenu(lo_slack, origin)

            origin.addTab(origin.w_slackStudioTab, "Slack")

    @err_catcher(__name__)
    def createSlackProjectSettingsUI(self, origin, settings):
        if not hasattr(origin, "w_slackProjectTab"):
            origin.w_slackProjectTab = QWidget()
            lo_slack = QVBoxLayout(origin.w_slackProjectTab)

            self.createSlackTokenSettingsMenu(lo_slack, origin)
            self.createNotificationsSettingsMenu(lo_slack, origin)
            self.createCustomChannelUI(lo_slack, origin, settings)
            self.createServerSettingsMenu(lo_slack, origin)

            origin.addTab(origin.w_slackProjectTab, "Slack")

    @err_catcher(__name__)
    def createCustomChannelUI(self, lo_slack, origin, settings):
        gb_custom_channel = QGroupBox()
        lo_custom_channel = QHBoxLayout()
        gb_custom_channel.setLayout(lo_custom_channel)

        origin.l_custom_channel = QLabel("Custom Notification Channel: ")
        origin.le_custom_channel = QLineEdit()

        lo_custom_channel.addWidget(origin.l_custom_channel)
        lo_custom_channel.addWidget(origin.le_custom_channel)

        lo_slack.addWidget(gb_custom_channel)

    @err_catcher(__name__)
    def createUserSettingsUI(self, origin):
        if not hasattr(origin, "w_slackUserTab"):
            origin.w_slackUserTab = QWidget()  # Store it as an attribute
            lo_slackUserTab = QVBoxLayout(origin.w_slackUserTab)

            i_slackLogo = self.grabSlacklogo()
            lo_user = QHBoxLayout()
            l_user = QLabel("Display Name: ")
            le_user = QLineEdit()
            le_user.setPlaceholderText("Enter your Slack Display Name")
            origin.le_user = le_user

            i_userHelp = self.grabHelpIcon()
            i_userHelp.setToolTip("""<p style='line-height:1;'>
                                    Input your Display Name, not your Full Name from your Slack Profile
                                    </p>""")

            lo_user.addWidget(l_user)
            lo_user.addWidget(origin.le_user)
            print("Added origin.le_user")
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

    @err_catcher(__name__)
    def createSlackTokenSettingsMenu(self, lo_slack, origin):
        l_slack_logo = self.grabSlacklogo()

        le_slack_token = QLineEdit()
        le_slack_token.setPlaceholderText("Enter your Slack API Token")
        le_slack_token.setEchoMode(QLineEdit.Password)
        le_slack_token.setReadOnly(True)
        le_slack_token.setFocusPolicy(Qt.NoFocus)
        le_slack_token.setContextMenuPolicy(Qt.NoContextMenu)
        origin.le_slack_token = le_slack_token

        l_slack_token_help = self.grabHelpIcon()
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

    @err_catcher(__name__)
    def createNotificationsSettingsMenu(self, lo_slack, origin):
        gb_notifications = QGroupBox()
        gb_notifications.setTitle("Notifications")
        gb_notifications.setContentsMargins(0, 30, 0, 0)
        lo_notifications = QVBoxLayout()
        gb_notifications.setLayout(lo_notifications)

        lo_notify_user_pool = QHBoxLayout()
        l_notify_method = QLabel("Notify Method:")
        l_notify_user_pool = QLabel("User Pool:")
        cb_notify_user_pool = QComboBox()
        cb_notify_user_pool.setPlaceholderText("Notify User Pool")
        origin.cb_notify_user_pool = cb_notify_user_pool

        l_notify_user_pool_help = self.grabHelpIcon()
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

        l_notify_method_help = self.grabHelpIcon()
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

    @err_catcher(__name__)
    def createServerSettingsMenu(self, lo_slack, origin):
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

        l_app_token_help = self.grabHelpIcon()
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

    @err_catcher(__name__)
    def grabSlacklogo(self):
        l_slack = QLabel()

        plugin_directory = Path(__file__).resolve().parents[2]
        i_slack = os.path.join(plugin_directory, "Resources", "slack-logo.png")

        pixmap = QPixmap(i_slack)

        # Set pixmap to label and scale
        scale = 0.05
        l_slack.setPixmap(pixmap)
        l_slack.setScaledContents(True)
        l_slack.setFixedSize(pixmap.width() * scale, pixmap.height() * scale)
        l_slack.setContentsMargins(0, 0, 0, 0)

        return l_slack

    @err_catcher(__name__)
    def grabHelpIcon(self):
        l_help = QLabel()
        help_icon = os.path.join(
            self.core.prismLibs, "Scripts", "UserInterfacesPrism", "help.png"
        )

        pixmap = QPixmap(help_icon)

        l_help.setPixmap(pixmap)

        return l_help
