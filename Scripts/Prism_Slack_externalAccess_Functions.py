import os
import subprocess
import socket
import win32api

from pathlib import Path
from pprint import pprint

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from server.control import ServerControls
from integration.slack_config import SlackConfig
from util.settings_ui import SettingsUI
from util.tray_ui import TrayUI
from util.dialogs import *

from PrismUtils.Decorators import err_catcher_plugin as err_catcher

class Prism_Slack_externalAccess_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin
        self.slack_config = SlackConfig(self.core)
        self.settings_ui = SettingsUI(self.core)
        self.tray_ui = TrayUI(self.core)
        self.server_controls = ServerControls(self.core)
        
        if self.isStudioLoaded() is not None:
            self.core.registerCallback("studioSettings_loadSettings", self.studioSettings_loadSettings, plugin=self)
        else:
            self.core.registerCallback("onPluginsLoaded", self.onPluginsLoaded, plugin=self)

        self.core.registerCallback("userSettings_loadUI", self.userSettings_loadUI, plugin=self)
        self.core.registerCallback("trayContextMenuRequested", self.systemTrayContextMenuRequested, plugin=self)

    @err_catcher(name=__name__)
    def onPluginsLoaded(self):
        if self.isStudioLoaded() is not None:
            self.core.registerCallback("studioSettings_loadSettings", self.studioSettings_loadSettings, plugin=self)
        else:
            self.core.registerCallback("projectSettings_loadUI", self.projectSettings_loadUI, plugin=self)
            
        self.core.registerCallback("userSettings_loadUI", self.userSettings_loadUI, plugin=self)

    # Load the UI for the Slack plugin in the studio settings window
    @err_catcher(name=__name__)
    def studioSettings_loadSettings(self, origin, settings):
        if self.core.getPlugin('Studio').getStudioConfigPath() is None:
            SlackStudioPathNotFound().exec_()
            return
        self.settings_ui.createSlackStudioSettingsUI(origin, settings)
        self.setStudioOptions(origin)
        self.connectEvents(origin)

    # Load the UI for the Slack plugin in the project settings window
    @err_catcher(name=__name__)
    def projectSettings_loadUI(self, origin):
        self.settings_ui.createSlackProjectSettingsUI(origin, settings=None)
        self.setStudioOptions(origin)
        self.connectEvents(origin)

    @err_catcher(name=__name__)
    def userSettings_loadUI(self, origin):
        self.settings_ui.createUserSettingsUI(origin)
        print("User Settings Added")
        self.checkUsername(origin)
        origin.b_userSave.clicked.connect(lambda: self.saveUsername(origin))

    @err_catcher(name=__name__)
    def systemTrayContextMenuRequested(self, origin, menu):
        pipeline_data = self.slack_config.loadConfig(mode="studio")
        server_status = pipeline_data["slack"]["server"].get("status")
        server_machine = pipeline_data["slack"]["server"].get("machine")
        print(f'Server Status: {server_status}')
        print(f'Server Machine: {server_machine}')

        if server_status == "":
            server_status = "Not running"
        
        self.tray_ui.createTraySlackUI(menu, server_status, server_machine)
        
        self.stop_action = self.tray_ui.stopServerAction
        self.start_action = self.tray_ui.startServerAction

        self.stop_action.triggered.connect(lambda: self.slackTrayToggle(server_status, server_machine))
        self.start_action.triggered.connect(lambda: self.slackTrayToggle(server_status, server_machine))

    @err_catcher(name=__name__)
    def slackTrayToggle(self, server_status, server_machine):

        plugin_directory = Path(__file__).resolve().parents[1]

        self.stop_action = self.tray_ui.stopServerAction
        self.start_action = self.tray_ui.startServerAction
        self.status_action = self.tray_ui.statusServerAction

        if server_status == "Running":
            if server_machine == socket.gethostname():
                print("Stopping the server")
                self.server_controls.stopServer()
                self.stop_action.setEnabled(False)
                self.start_action.setEnabled(True)
                self.status_action.setText("Not running")
                self.status_action.setIcon(QIcon(os.path.join(plugin_directory, "Resources", "stopped.png")))
            else:
                self.dialogs = ServerNonWarning()
                self.dialogs.exec_()
        else:
            print("Starting the server")
            self.server_controls.startServer()
            self.stop_action.setEnabled(True)
            self.start_action.setEnabled(False)
            self.status_action.setText("Running")
            self.status_action.setIcon(QIcon(os.path.join(plugin_directory, "Resources", "running.png")))

    @err_catcher(name=__name__)
    def checkUsername(self, origin):
        le_user = origin.le_user
        user_data = self.slack_config.loadConfig('user')

        if "slack" not in user_data:
            user_data["slack"] = {}
            user_data["slack"]["username"] = ""
        
        if "username" in user_data["slack"]:
            le_user.setText(user_data["slack"].get("username"))
        else:
            le_user.setPlaceholderText("Enter your Slack Display Name")

        self.slack_config.saveConfigSetting(user_data, "user")

    @err_catcher(name=__name__)
    def saveUsername(self, origin):
        le_user = origin.le_user
        user_data = self.slack_config.loadConfig('user')

        user_data["slack"]["username"] = le_user.text()
        self.slack_config.saveConfigSetting(user_data, "user")

    @err_catcher(name=__name__)
    def setStudioOptions(self, origin):
        try:
            # Check for the slack oauth token and assign it in the ui
            self.checkToken(origin)

            # Add current methods for notifications and set the current method in the ui
            self.addNotifyMethods(origin)
            self.checkNotifyMethod(origin)

            # Add the current user pools for notifications and set the current user pool in the ui
            self.addNotifyUserPools(origin)
            self.checkNotifyUserPool(origin)

            # Check for the app-level token and assign it in the ui
            self.checkAppLevelToken(origin)
            self.server_controls.checkServerStatus(origin)
        except Exception as e:
            print(f"Error setting studio options: {e}")

    @err_catcher(name=__name__)
    def connectEvents(self, origin):
        origin.b_slack_token.clicked.connect(lambda: self.inputToken(origin))
        origin.cb_notify_user_pool.currentIndexChanged.connect(lambda index: self.UpdateNotifyUserPool(origin, index))
        origin.cb_notify_method.currentIndexChanged.connect(lambda index: self.updateNotifyMethod(origin, index))
        
        origin.b_app_token.clicked.connect(lambda: self.inputAppLevelToken(origin))
        origin.b_server.clicked.connect(lambda: self.toggleServer(origin))
        origin.b_reset_server.clicked.connect(lambda: self.resetServerStatus(origin))
        
    @err_catcher(name=__name__)
    def addNotifyMethods(self, origin):
        methods = ["Direct", "Channel", "Ephemeral Direct", "Ephemeral Channel"]
        
        cb_notify_method = origin.cb_notify_method
        cb_notify_method.addItems(methods)
    
    @err_catcher(name=__name__)
    def updateNotifyMethod(self, origin, index):
        notify_method = origin.cb_notify_method.currentText()
        pipeline_data = self.slack_config.loadConfig("studio")
        self.slack_config.checkSlackOptions(pipeline_data)

        if "method" in pipeline_data["slack"]["notifications"]:
            pipeline_data["slack"]["notifications"]["method"] = notify_method
        
        self.slack_config.saveConfigSetting(pipeline_data, "studio")

    @err_catcher(name=__name__)
    def checkNotifyMethod(self, origin):
        pipeline_data = self.slack_config.loadConfig("studio")
        self.slack_config.checkSlackOptions(pipeline_data)

        if "method" in pipeline_data["slack"]["notifications"]:
            notify_method = pipeline_data["slack"]["notifications"].get("method")
            origin.cb_notify_method.setCurrentText(notify_method)
        else:
            notify_method = None

    @err_catcher(name=__name__)
    def addNotifyUserPools(self, origin):
        cb_notify_user_pool = origin.cb_notify_user_pool
        
        user_pool = []

        # if self.isStudioLoaded():
        #     user_pool.append("Studio")
        user_pool.append("Channel")

        cb_notify_user_pool.addItems(user_pool)

    @err_catcher(name=__name__)
    def UpdateNotifyUserPool(self, origin, index):
        cb_notify_user_pool = origin.cb_notify_user_pool
        notify_user_pool = cb_notify_user_pool.currentText()
        pipeline_data = self.slack_config.loadConfig("studio")
        self.slack_config.checkSlackOptions(pipeline_data)

        if "user_pool" in pipeline_data["slack"]["notifications"]:
            pipeline_data["slack"]["notifications"]["user_pool"] = notify_user_pool

        self.slack_config.saveConfigSetting(pipeline_data, "studio")
    
    # Check the method of notification to Slack users
    @err_catcher(name=__name__)
    def checkNotifyUserPool(self, origin):
        cb_notify_user_pool = origin.cb_notify_user_pool
        pipeline_data = self.slack_config.loadConfig(mode="studio")
        self.slack_config.checkSlackOptions(pipeline_data)

        if "user_pool" in pipeline_data["slack"]["notifications"]:
            notify_user_pool = pipeline_data["slack"]["notifications"].get("user_pool")
            cb_notify_user_pool.setCurrentText(notify_user_pool)
        else:
            notify_user_pool = None

    # Pop up a dialog to input the Slack API token
    @err_catcher(name=__name__)
    def inputToken(self, origin):
        le_slack_token = origin.le_slack_token
        input_dialog = InputDialog(title="Enter your Slack API Token")
        if input_dialog.exec_() == QDialog.Accepted:
            text = input_dialog.get_input()
            slack_token = text
            le_slack_token.setText(slack_token)
            self.saveToken(slack_token)
    
    # Check if the Slack API token is present in the pipeline configuration file
    @err_catcher(name=__name__)
    def checkToken(self, origin):
        le_slack_token = origin.le_slack_token
        pipeline_data = self.slack_config.loadConfig(mode="studio")
        self.slack_config.checkSlackOptions(pipeline_data)
        
        if "token" not in pipeline_data["slack"]:
            le_slack_token.setPlaceholderText("Enter your Slack API Token")

        token = pipeline_data["slack"]["token"]
        le_slack_token.setText(token)

    # Save the token in the pipeline configuration file
    @err_catcher(name=__name__)
    def saveToken(self, token):
        pipeline_data = self.slack_config.loadConfig(mode="studio")
        self.slack_config.checkSlackOptions(pipeline_data)
        pipeline_data["slack"]["token"] = token
        self.slack_config.saveConfigSetting(pipeline_data, mode="studio")

    @err_catcher(name=__name__)
    def saveAppLevelToken(self, app_token):
        pipeline_data = self.slack_config.loadConfig(mode="studio")
        self.slack_config.checkSlackOptions(pipeline_data)

        if "app_token" in pipeline_data["slack"]["server"]:
            pipeline_data["slack"]["server"]["app_token"] = app_token
        
        self.slack_config.saveConfigSetting(pipeline_data, mode="studio")

    @err_catcher(name=__name__)
    def inputAppLevelToken(self, origin):
        input_dialog = InputDialog(title="Enter your Slack App-Level Token")
        if input_dialog.exec_() == QDialog.Accepted:
            text = input_dialog.get_input()
            app_token = text
            origin.le_app_token.setText(app_token)
            self.saveAppLevelToken(app_token)

    @err_catcher(name=__name__)
    def checkAppLevelToken(self, origin):
        pipeline_data = self.slack_config.loadConfig(mode="studio")
        self.slack_config.checkSlackOptions(pipeline_data)

        if "app_token" not in pipeline_data["slack"]["server"]:
            origin.le_app_token.setPlaceholderText("Enter your Slack App-Level Token")

        app_token = pipeline_data["slack"]["server"].get("app_token", "")
        origin.le_app_token.setText(app_token)

    @err_catcher(name=__name__)
    def toggleServer(self, origin):
        self.config = self.slack_config.loadConfig(mode="studio")
        b_server = origin.b_server
        b_reset_server = origin.b_reset_server

        self.server_machine = self.config["slack"]["server"].get("machine")
        self.server_status = self.config["slack"]["server"].get("status")
        
        if self.server_status == "Running":
            if socket.gethostname() != self.server_machine:
                self.non_server_check = ServerNonWarning()
                self.non_server_check.exec_()
                return
            else:
                self.server_controls.guiStopServer(origin)
        else:
            b_reset_server.setEnabled(True)
            self.server_controls.guiStartServer(origin)

    # Check if the studio plugin is loaded
    @err_catcher(name=__name__)
    def isStudioLoaded(self):
        return self.core.getPlugin("Studio") 