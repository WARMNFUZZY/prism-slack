import os
import subprocess
import socket
import win32api

from pathlib import Path
from pprint import pprint

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from integration.slack_config import SlackConfig
from util.settings_ui import SettingsUI
from util.dialogs import *

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
        self.settings_ui.createSlackSettingsUI(origin, settings)
        pprint(f"Attributes for origin: {dir(origin)}")
        self.setStudioOptions(origin)
        self.connectEvents(origin)

    # Load the UI for the Slack plugin in the project settings window
    @err_catcher(name=__name__)
    def projectSettings_loadUI(self, origin):
        self.settings_ui.createSlackSettingsUI(origin, settings=None)
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

        if server_status == "":
            server_status = "Not running"

        self.slackMenu = QMenu(f"Slack Server")
        
        plugin_directory = Path(__file__).resolve().parents[1]
        self.slack_icon = QIcon(os.path.join(plugin_directory, "Resources", "slack-icon.png"))
        self.slackMenu.setIcon(self.slack_icon)
        
        self.statusServerAction = QAction(server_status)
        
        if server_status == "Running":
            self.slack_server_running_icon = QIcon(os.path.join(plugin_directory, "Resources", "running.png"))
            self.statusServerAction.setIcon(self.slack_server_running_icon)        
        else:
            self.slack_server_stopped_icon = QIcon(os.path.join(plugin_directory, "Resources", "stopped.png"))
            self.statusServerAction.setIcon(self.slack_server_stopped_icon)
        
        self.stopServerAction = QAction("Stop Server")
        self.stopServerAction.triggered.connect(self.slackTrayToggle)
        self.startServerAction = QAction("Start Server")
        self.startServerAction.triggered.connect(self.slackTrayToggle)

        if server_status == "Running" and server_machine == socket.gethostname():
            self.stopServerAction.setEnabled(True)
            self.startServerAction.setEnabled(False)
        else:
            self.stopServerAction.setEnabled(False)
            self.startServerAction.setEnabled(True)
        
        if server_status == "Running" and server_machine != socket.gethostname():
            self.dialogs = ServerNonWarning()
            self.dialogs.exec_()
        
        self.slackMenu.addAction(self.statusServerAction)
        self.slackMenu.addAction(self.startServerAction)
        self.slackMenu.addAction(self.stopServerAction)
        # menu.addMenu(self.slackMenu)
        tray_actions = menu.actions()[0]
        menu.insertMenu(tray_actions, self.slackMenu)

    @err_catcher(name=__name__)
    def slackTrayToggle(self):
        pipeline_data = self.slack_config.loadConfig(mode="studio")
        server_status = pipeline_data["slack"]["server"].get("status")
        server_machine = pipeline_data["slack"]["server"].get("machine")

        plugin_directory = Path(__file__).resolve().parents[1]

        if server_status == "Running":
            if server_machine == socket.gethostname():
                self.stopServer()
                self.stopServerAction.setEnabled(False)
                self.startServerAction.setEnabled(True)
                self.statusServerAction.setText("Not running")
                self.statusServerAction.setIcon(QIcon(os.path.join(plugin_directory, "Resources", "stopped.png")))
            else:
                self.dialogs = ServerNonWarning()
                self.dialogs.exec_()
        else:
            self.startServer()
            self.stopServerAction.setEnabled(True)
            self.startServerAction.setEnabled(False)
            self.statusServerAction.setText("Running")
            self.statusServerAction.setIcon(QIcon(os.path.join(plugin_directory, "Resources", "running.png")))

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
        self.checkServerStatus(origin)

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

        if self.isStudioLoaded():
            user_pool.append("Studio")
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
    def startServer(self):
        scripts_path = Path(__file__).resolve().parents[0]
        bolt_path = os.path.join(scripts_path, "server", "bolt.py")
        self.config = self.slack_config.loadConfig(mode="studio")
        token = self.config["slack"]["token"]
        app_token = self.config["slack"]["server"]["app_token"]
        executable = os.path.join(self.core.prismLibs, "Python311", "python.exe")

        sub_env = os.environ.copy()
        sub_env["BOLTPATH"] = f"{Path(__file__).resolve().parents[1]}\PythonLibs"
        sub_env["SCRIPTSPATH"] = f"{Path(__file__).resolve().parents[0]}"
        sub_env["PRISMPATH"] = f"{self.core.prismLibs}\PythonLibs\Python3"
        sub_env["PRISM_CORE"] = f"{self.core.prismLibs}\Scripts"

        self.server_status = self.config["slack"]["server"].get("status")
        self.machine = self.config["slack"]["server"].get("machine")

        win32api.SetConsoleCtrlHandler(lambda event: (self.resetServerStatus() if event == 2 else False), True)

        try:
            if self.server_status != "Running" and os.path.exists(bolt_path):
                self.bolt = subprocess.Popen(
                    [executable, bolt_path, token, app_token], 
                    env=sub_env, 
                    text=True
                )

                pipeline_data = self.slack_config.loadConfig(mode="studio")
                pipeline_data["slack"]["server"]["status"] = "Running"
                pipeline_data["slack"]["server"]["machine"] = socket.gethostname()
                pipeline_data["slack"]["server"]["pid"] = self.bolt.pid
                self.slack_config.saveConfigSetting(pipeline_data, mode="studio")

        except Exception as e:
            self.core.popup(f"Error starting the Slack Bolt Server: {e}")
            self.stopServer()

    def resetServerStatus(self, origin):
        pipeline_data = self.slack_config.loadConfig(mode="studio")
        pipeline_data["slack"]["server"]["status"] = ""
        pipeline_data["slack"]["server"]["machine"] = ""
        pipeline_data["slack"]["server"]["pid"] = ""
        self.slack_config.saveConfigSetting(pipeline_data, mode="studio")

        self.checkServerStatus(origin)

    @err_catcher(name=__name__)
    def stopServer(self):
        self.config = self.slack_config.loadConfig(mode="studio")
        status = self.config["slack"]["server"].get("status")
        pid = self.config["slack"]["server"].get("pid")

        if status == "Running":
            try:
                self.resetServerStatus(origin=None)
                os.kill(pid, 9)
                print("Slack Bolt Server stopped")
            except Exception as e:
                self.core.popup(f"Error stopping the Slack Bolt Server: {e}")

    @err_catcher(name=__name__)
    def guiStartServer(self, origin):
        start_check = ServerStartWarning()
        if start_check.exec_() == QDialog.Accepted:
            self.startServer()
            origin.b_server.setText("Stop Server")
            origin.b_reset_server.setEnabled(False)
            self.checkServerStatus(origin)
        else:
            return
    
    @err_catcher(name=__name__)
    def guiStopServer(self, origin):
        stop_check = ServerStopWarning()
        if stop_check.exec_() == QDialog.Accepted:
            self.stopServer()
            origin.b_server.setText("Start Server")
            origin.b_reset_server.setEnabled(True)
            self.checkServerStatus(origin)
        else:
            return

    @err_catcher(name=__name__)
    def checkServerStatus(self, origin):
        pipeline_data = self.slack_config.loadConfig(mode="studio")
        self.slack_config.checkSlackOptions(pipeline_data)

        status = pipeline_data["slack"]["server"].get("status", "Not running")
        machine = pipeline_data["slack"]["server"].get("machine", "---------")

        if origin is not None:
            origin.l_server_status_value.setText(status)
            origin.l_machine_value.setText(machine)

        return pipeline_data["slack"]["server"].get("status")

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
                self.guiStopServer(origin)
        else:
            b_reset_server.setEnabled(True)
            self.guiStartServer(origin)

    # Check if the studio plugin is loaded
    @err_catcher(name=__name__)
    def isStudioLoaded(self):
        return self.core.getPlugin("Studio") 