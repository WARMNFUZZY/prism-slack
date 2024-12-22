import os
import socket
from pathlib import Path

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

class TrayUI():
    def __init__(self, origin):
        pass

    # Create the Tray UI for the Slack Server
    def createTraySlackUI(self, menu, server_status, server_machine):
        self.slackMenu = QMenu(f"Slack Server")
        
        plugin_directory = Path(__file__).resolve().parents[2]
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
        self.startServerAction = QAction("Start Server")

        if server_status == "Running" and server_machine == socket.gethostname():
            self.stopServerAction.setEnabled(True)
            self.startServerAction.setEnabled(False)
        else:
            self.stopServerAction.setEnabled(False)
            self.startServerAction.setEnabled(True)
        
        self.slackMenu.addAction(self.statusServerAction)
        self.slackMenu.addAction(self.startServerAction)
        self.slackMenu.addAction(self.stopServerAction)
        
        tray_actions = menu.actions()[0]
        menu.insertMenu(tray_actions, self.slackMenu)