import os
from pathlib import Path

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from PrismUtils.Decorators import err_catcher_plugin as err_catcher

class SettingsUI():
    def __init__(self, core):
        self.core = core

    # Create the UI for the Slack plugin
    @err_catcher(__name__)
    def createSlackSettingsUI(self, origin, settings):
        if not hasattr(self, "w_slackTab"):
            self.w_slackTab = QWidget()
            self.lo_slack = QVBoxLayout(self.w_slackTab)

            self.createSlackTokenMenuSettingsMenu()

            self.createNotificationsSettingsMenu()

            self.createServerSettingsMenu()

            origin.addTab(self.w_slackTab, "Slack")

    @err_catcher(__name__)
    def createUserSettingsUI(self, origin):
        if not hasattr(self, "w_slackUserTab"):
            self.w_slackUserTab = QWidget()
            self.lo_slackUserTab = QVBoxLayout(self.w_slackUserTab)

            self.i_slackLogo = self.grabSlacklogo()
            self.lo_user = QHBoxLayout()
            self.l_user = QLabel()
            self.l_user.setText("Display Name: ")
            self.le_user = QLineEdit()
            self.le_user.setPlaceholderText("Enter your Slack Display Name")
            self.i_userHelp = self.grabHelpIcon()
            self.i_userHelp.setToolTip("""<p style='line-height:1;'>
                                       Input your Display Name, not your Full Name from your Slack Profile
                                       </p>""")

            self.lo_user.addWidget(self.l_user)
            self.lo_user.addWidget(self.le_user)
            self.lo_user.addWidget(self.i_userHelp)

            self.lo_save = QHBoxLayout()

            self.lo_save.addStretch()
            self.b_userSave = QPushButton("Save")
            self.lo_save.addWidget(self.b_userSave)
            self.lo_save.addStretch()

            self.lo_slackUserTab.addStretch()
            self.lo_slackUserTab.addWidget(self.i_slackLogo)
            self.lo_slackUserTab.addLayout(self.lo_user)
            self.lo_slackUserTab.addLayout(self.lo_save)
            self.lo_slackUserTab.addStretch()

            origin.addTab(self.w_slackUserTab, "Slack")

    @err_catcher(__name__)
    def createSlackTokenMenuSettingsMenu(self):
            self.l_slack_logo = self.grabSlacklogo()

            self.le_slack_token = QLineEdit()
            self.le_slack_token.setPlaceholderText("Enter your Slack API Token")
            self.le_slack_token.setEchoMode(QLineEdit.Password)
            self.le_slack_token.setReadOnly(True)
            self.le_slack_token.setFocusPolicy(Qt.NoFocus)
            self.le_slack_token.setContextMenuPolicy(Qt.NoContextMenu)
            self.l_slack_token_help = self.grabHelpIcon()
            self.l_slack_token_help.setToolTip("""<p style='line-height:1;'>
                                             <span> Can be found in your Slack app settings under OAuth & Permissions -> Bot User OAuth Token</span>
                                             </p>""")

            self.b_slack_token = QPushButton("Input Token")

            self.lo_slack.addStretch()
            self.lo_slack.addWidget(self.l_slack_logo)
            self.lo_slack.setAlignment(self.l_slack_logo, Qt.AlignBottom)

            self.lo_slack.addWidget(self.le_slack_token)
            self.lo_slack.setAlignment(self.le_slack_token, Qt.AlignBottom)

            self.lo_slack.addWidget(self.b_slack_token)
            self.lo_slack.setAlignment(self.b_slack_token, Qt.AlignBottom | Qt.AlignCenter)

    @err_catcher(__name__)
    def createNotificationsSettingsMenu(self):
            self.gb_notifications = QGroupBox()
            self.gb_notifications.setTitle("Notifications")
            self.gb_notifications.setContentsMargins(0, 30, 0, 0)
            self.lo_notifications = QVBoxLayout()
            self.gb_notifications.setLayout(self.lo_notifications)

            self.lo_notify_user_pool = QHBoxLayout()
            self.l_notify_method = QLabel("Notify Method:")
            self.l_notify_user_pool = QLabel("User Pool:")
            self.cb_notify_user_pool = QComboBox()
            self.cb_notify_user_pool.setPlaceholderText("Notify User Pool")
            self.l_notify_user_pool_help = self.grabHelpIcon()
            self.l_notify_user_pool_help.setToolTip("""<p style='line-height:1;'>
                                        <span style='color:DodgerBlue;'><b>Studio</b></span>: Draw from the users in the Studio plugin pool<br>
                                        <br>
                                        <span style='color:Tomato;'><b>Channel</b></span>: Draw from the users in the Slack Project Channel<br>
                                        <br>
                                        <span style='color:MediumSeaGreen;'><b>Team</b></span>: Draw from the users in the Slack Team pool<br>
                                        <i>Note: If not kept up to date, your Team pool could be rather large</i>
                                        </p>""")

            self.lo_notify_user_pool.addWidget(self.l_notify_user_pool)
            self.lo_notify_user_pool.addWidget(self.cb_notify_user_pool)
            self.lo_notify_user_pool.addWidget(self.l_notify_user_pool_help)
            self.lo_notify_user_pool.addStretch()
            self.lo_notifications.addLayout(self.lo_notify_user_pool)

            self.lo_notify_method = QHBoxLayout()
            self.l_notify_method = QLabel("Method: ")
            self.cb_notify_method = QComboBox()
            self.cb_notify_method.setPlaceholderText("Notify Method")
            self.l_notify_method_help = self.grabHelpIcon()
            self.l_notify_method_help.setToolTip("""<p style='line-height:1;'>
                                        <span style='color:DodgerBlue;'><b>Direct</b></span>: Notify the selected user by Direct message<br>
                                        <br>
                                        <span style='color:Tomato;'><b>Channel</b></span>: Notify selected user in the Slack Channel<br>
                                        <br>
                                        <span style='color:MediumSeaGreen;'><b>Ephemeral Direct</b></span>: Notify the selected user in an ephemeral Direct message<br>
                                        <br>
                                        <span style='color:MediumSlateBlue;'><b>Ephemeral Channel</b></span>: Notify selected user in an ephemeral Channel message<br>
                                        </p>""")
            
            self.lo_notify_method.addWidget(self.l_notify_method)
            self.lo_notify_method.addWidget(self.cb_notify_method)
            self.lo_notify_method.addWidget(self.l_notify_method_help)
            self.lo_notify_method.addStretch()
            self.lo_notifications.addLayout(self.lo_notify_method)

            self.lo_slack.addWidget(self.gb_notifications)
            self.lo_slack.setAlignment(self.lo_notifications, Qt.AlignTop | Qt.AlignLeft)

    @err_catcher(__name__)
    def createServerSettingsMenu(self):
            self.gb_server = QGroupBox()
            self.gb_server.setTitle("Server")
            self.gb_server.setContentsMargins(0, 30, 0, 0)
            self.lo_server = QVBoxLayout()
            self.gb_server.setLayout(self.lo_server)

            self.lo_app_token = QHBoxLayout()
            self.le_app_token = QLineEdit()
            self.le_app_token.setPlaceholderText("Enter your Slack App-Level Token")
            self.le_app_token.setEchoMode(QLineEdit.Password)
            self.le_app_token.setReadOnly(True)
            self.le_app_token.setFocusPolicy(Qt.NoFocus)
            self.le_app_token.setContextMenuPolicy(Qt.NoContextMenu)
            self.l_app_token_help = self.grabHelpIcon()
            self.l_app_token_help.setToolTip("""<p style='line-height:1;'>
                                             <span> Can be found in your app settings under Basic Information -> App-Level Tokens</span>
                                             </p>""")

            self.lo_app_token.addWidget(self.le_app_token)
            self.lo_app_token.addWidget(self.l_app_token_help)

            self.lo_button_app_token = QHBoxLayout()
            self.b_app_token = QPushButton("Input App-Level Token")

            self.b_start_server = QPushButton("Start Server")

            self.lo_button_app_token.addStretch()
            self.lo_button_app_token.addWidget(self.b_app_token)
            self.lo_button_app_token.addWidget(self.b_start_server)
            self.lo_button_app_token.addStretch()

            self.lo_server.addLayout(self.lo_app_token)
            self.lo_server.addLayout(self.lo_button_app_token)

            self.lo_slack.addWidget(self.gb_server)
            self.lo_slack.setAlignment(self.lo_server, Qt.AlignTop | Qt.AlignLeft)
            self.lo_slack.addStretch()

    @err_catcher(__name__)
    def grabSlacklogo(self):
        self.l_slack = QLabel()
        
        plugin_directory = Path(__file__).resolve().parents[2]
        self.i_slack = os.path.join(plugin_directory, "Resources", "slack-logo.png")

        pixmap = QPixmap(self.i_slack)

        # Set pixmap to label and scale
        scale = 0.05
        self.l_slack.setPixmap(pixmap)
        self.l_slack.setScaledContents(True)
        self.l_slack.setFixedSize(pixmap.width() * scale, pixmap.height() * scale)
        self.l_slack.setContentsMargins(0, 0, 0, 0)

        return self.l_slack

    @err_catcher(__name__)
    def grabHelpIcon(self):
        self.l_help = QLabel()
        self.help_icon = os.path.join(self.core.prismLibs, "Scripts", "UserInterfacesPrism", "help.png")

        pixmap = QPixmap(self.help_icon)

        self.l_help.setPixmap(pixmap)
        
        return self.l_help