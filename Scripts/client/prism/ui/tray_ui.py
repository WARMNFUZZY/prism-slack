import os
import socket
from pathlib import Path

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


class TrayUI:
    def __init__(self):
        pass

    # Create the Tray UI for the Slack Server
    def create_tray_slack_ui(self, menu, server_status, server_machine):
        self.slack_menu = QMenu(f"Slack Server")

        plugin_directory = Path(__file__).resolve().parents[4]
        self.slack_icon = QIcon(
            os.path.join(plugin_directory, "Resources", "slack-icon.png")
        )
        self.slack_menu.setIcon(self.slack_icon)

        self.status_server_action = QAction(server_status)

        if server_status == "Running":
            self.slack_server_running_icon = QIcon(
                os.path.join(plugin_directory, "Resources", "running.png")
            )
            self.status_server_action.setIcon(self.slack_server_running_icon)
        else:
            self.slack_server_stopped_icon = QIcon(
                os.path.join(plugin_directory, "Resources", "stopped.png")
            )
            self.status_server_action.setIcon(self.slack_server_stopped_icon)

        self.stop_server_action = QAction("Stop Server")
        self.start_server_action = QAction("Start Server")

        if server_status == "Running" and server_machine == socket.gethostname():
            self.stop_server_action.setEnabled(True)
            self.start_server_action.setEnabled(False)
        else:
            self.stop_server_action.setEnabled(False)
            self.start_server_action.setEnabled(True)

        self.slack_menu.addAction(self.status_server_action)
        self.slack_menu.addAction(self.start_server_action)
        self.slack_menu.addAction(self.stop_server_action)

        tray_actions = menu.actions()[0]
        menu.insertMenu(tray_actions, self.slack_menu)
