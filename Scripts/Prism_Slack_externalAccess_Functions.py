import os
import json
import sys
import subprocess

from pathlib import Path

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from server.bolt import SlackBoltServer
from slack_integration.slack_config import SlackConfig
from util.settings_ui import SettingsUI
from util.dialogs import InputDialog

from PrismUtils.Decorators import err_catcher_plugin as err_catcher

class Prism_Slack_externalAccess_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin
        self.slack_config = SlackConfig(self.core)
        self.settings_ui = SettingsUI(self.core)
        

        if self.isStudioLoaded() is not None:
            self.core.registerCallback("studioSettings_loadSettings", self.studioSettings_loadSettings, plugin=self)
        else:
            self.core.registerCallback("onPluginsLoaded", self.onPluginsLoaded, plugin=self)
        
        self.core.registerCallback("userSettings_loadUI", self.userSettings_loadUI, plugin=self)

    @err_catcher(name=__name__)
    def onPluginsLoaded(self):
        if self.isStudioLoaded() is not None:
            self.core.registerCallback("studioSettings_loadSettings", self.studioSettings_loadSettings, plugin=self)
        else:
            self.core.registerCallback("projectSettings_loadUI", self.projectSettings_loadUI, plugin=self)

    # Load the UI for the Slack plugin in the studio settings window
    @err_catcher(name=__name__)
    def studioSettings_loadSettings(self, origin, settings):
        self.settings_ui.createSlackSettingsUI(origin, settings)
        self.setOptions()
        self.connectEvents()

    # Load the UI for the Slack plugin in the project settings window
    @err_catcher(name=__name__)
    def projectSettings_loadUI(self, origin):
        self.settings_ui.createSlackSettingsUI(origin, settings=None)
        self.setOptions()
        self.connectEvents()

    @err_catcher(name=__name__)
    def userSettings_loadUI(self, origin):
        self.settings_ui.createUserSettingsUI(origin)
        self.checkUsername()
        self.saveUsername()

    @err_catcher(name=__name__)
    def checkUsername(self):
        self.le_user = self.settings_ui.le_user
        user_data = self.slack_config.loadConfig('user')

        if "slack" not in user_data:
            user_data["slack"] = {}
            user_data["slack"]["username"] = ""
        
        if "username" in user_data["slack"]:
            self.le_user.setText(user_data["slack"].get("username"))
        else:
            self.le_user.setPlaceholderText("Enter your Slack Display Name")

        self.slack_config.saveConfigSetting(user_data, "user")

    @err_catcher(name=__name__)
    def saveUsername(self):
        self.le_user = self.settings_ui.le_user
        user_data = self.slack_config.loadConfig('user')

        user_data["slack"]["username"] = self.le_user.text()
        self.slack_config.saveConfigSetting(user_data, "user")

    @err_catcher(name=__name__)
    def setOptions(self):
        # Check for the slack oauth token and assign it in the ui
        self.checkToken()

        # Add current methods for notifications and set the current method in the ui
        self.addNotifyMethods()
        self.checkNotifyMethod()

        # Add the current user pools for notifications and set the current user pool in the ui
        self.addNotifyUserPools()
        self.checkNotifyUserPool()

        # Check for the app-level token and assign it in the ui
        self.checkAppLevelToken()

    @err_catcher(name=__name__)
    def connectEvents(self):
        self.b_slack_token = self.settings_ui.b_slack_token
        self.b_slack_token.clicked.connect(self.inputToken)
        
        self.cb_notify_user_pool.currentIndexChanged.connect(self.UpdateNotifyUserPool)
        self.cb_notify_method.currentIndexChanged.connect(self.updateNotifyMethod)

        self.b_userSave = self.settings_ui.b_userSave
        self.b_userSave.clicked.connect(self.saveUsername)

        self.b_app_token = self.settings_ui.b_app_token
        self.b_app_token.clicked.connect(self.inputAppLevelToken)

        self.b_start_server = self.settings_ui.b_start_server
        self.b_start_server.clicked.connect(self.guiStartServer)

    @err_catcher(name=__name__)
    def addNotifyMethods(self):
        methods = ["Direct", "Channel", "Ephemeral Direct", "Ephemeral Channel"]
        
        self.cb_notify_method = self.settings_ui.cb_notify_method
        self.cb_notify_method.addItems(methods)
    
    @err_catcher(name=__name__)
    def updateNotifyMethod(self, index):
        notify_method = self.cb_notify_method.currentText()
        pipeline_data = self.slack_config.loadConfig("studio")
        self.slack_config.checkSlackOptions(pipeline_data)

        if "method" in pipeline_data["slack"]["notifications"]:
            pipeline_data["slack"]["notifications"]["method"] = notify_method
        
        self.slack_config.saveConfigSetting(pipeline_data, "studio")

    @err_catcher(name=__name__)
    def checkNotifyMethod(self):
        pipeline_data = self.slack_config.loadConfig("studio")
        self.slack_config.checkSlackOptions(pipeline_data)

        if "method" in pipeline_data["slack"]["notifications"]:
            notify_method = pipeline_data["slack"]["notifications"].get("method")
            self.cb_notify_method.setCurrentText(notify_method)
        else:
            notify_method = None

    @err_catcher(name=__name__)
    def addNotifyUserPools(self):
        self.cb_notify_user_pool = self.settings_ui.cb_notify_user_pool
        
        user_pool = []

        if self.isStudioLoaded():
            user_pool.append("Studio")
        user_pool.append("Channel")

        self.cb_notify_user_pool.addItems(user_pool)

    @err_catcher(name=__name__)
    def UpdateNotifyUserPool(self, index):
        notify_user_pool = self.cb_notify_user_pool.currentText()
        pipeline_data = self.slack_config.loadConfig("studio")
        self.slack_config.checkSlackOptions(pipeline_data)

        if "user_pool" in pipeline_data["slack"]["notifications"]:
            pipeline_data["slack"]["notifications"]["user_pool"] = notify_user_pool

        self.slack_config.saveConfigSetting(pipeline_data, "studio")
    
    # Check the method of notification to Slack users
    @err_catcher(name=__name__)
    def checkNotifyUserPool(self):
        pipeline_data = self.slack_config.loadConfig(mode="studio")
        self.slack_config.checkSlackOptions(pipeline_data)

        if "user_pool" in pipeline_data["slack"]["notifications"]:
            notify_user_pool = pipeline_data["slack"]["notifications"].get("user_pool")
            self.cb_notify_user_pool.setCurrentText(notify_user_pool)
        else:
            notify_user_pool = None

    # Pop up a dialog to input the Slack API token
    @err_catcher(name=__name__)
    def inputToken(self):
        input_dialog = InputDialog(title="Enter your Slack API Token")
        if input_dialog.exec_() == QDialog.Accepted:
            text = input_dialog.get_input()
            slack_token = text
            self.le_slack_token.setText(slack_token)
            self.saveToken(slack_token)
    
    # Check if the Slack API token is present in the pipeline configuration file
    @err_catcher(name=__name__)
    def checkToken(self):
        self.le_slack_token = self.settings_ui.le_slack_token
        pipeline_data = self.slack_config.loadConfig(mode="studio")
        self.slack_config.checkSlackOptions(pipeline_data)
        
        if "token" not in pipeline_data["slack"]:
            self.le_slack_token.setPlaceholderText("Enter your Slack API Token")

        token = pipeline_data["slack"]["token"]
        self.le_slack_token.setText(token)

    # Save the token in the pipeline configuration file
    @err_catcher(name=__name__)
    def saveToken(self, token):
        pipeline_data = self.slack_config.loadConfig(mode="studio")
        self.slack_config.checkSlackOptions(pipeline_data)

        if "token" in pipeline_data["slack"]:
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
    def inputAppLevelToken(self):
        input_dialog = InputDialog(title="Enter your Slack App-Level Token")
        if input_dialog.exec_() == QDialog.Accepted:
            text = input_dialog.get_input()
            app_token = text
            self.le_app_token.setText(app_token)
            self.saveAppLevelToken(app_token)

    @err_catcher(name=__name__)
    def checkAppLevelToken(self):
        self.le_app_token = self.settings_ui.le_app_token
        pipeline_data = self.slack_config.loadConfig(mode="studio")
        self.slack_config.checkSlackOptions(pipeline_data)

        if "app_token" not in pipeline_data["slack"]["server"]:
            self.le_app_token.setPlaceholderText("Enter your Slack App-Level Token")
        
        app_token = pipeline_data["slack"]["server"]["app_token"]
        self.le_app_token.setText(app_token)

    @err_catcher(name=__name__)
    def startServer(self):
        scripts_path = Path(__file__).resolve().parents[0]
        bolt_path = os.path.join(scripts_path, "server", "bolt.py")
        
        self.config = self.slack_config.loadConfig(mode="studio")
        token = self.config["slack"]["token"]
        app_token = self.config["slack"]["server"]["app_token"]
        executable = sys.executable

        self.bolt = SlackBoltServer(self.core, token, app_token)

        if os.path.exists(bolt_path):
            self.bolt = subprocess.Popen(
                [executable, bolt_path], 
                 shell=True, 
                 text=True
                 )
        else:
            QMessageBox.critical(self, "Error", "bolt.py not found. Please make sure you have installed the required dependencies.")
    
    @err_catcher(name=__name__)
    def guiStartServer(self):
        self.core.popup("This feature is not currently available in the GUI. Please use the command line to start the server. You can do so by following the documentation")

    # Check if the studio plugin is loaded
    @err_catcher(name=__name__)
    def isStudioLoaded(self):
        studio = self.core.getPlugin("Studio")
        return studio