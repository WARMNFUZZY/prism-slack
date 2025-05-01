import os
import socket
from pathlib import Path

from Scripts.client.slack.slack_config import SlackConfig
from Scripts.client.prism.ui import ServerNonWarning
from Scripts.server.controls import ServerControls
from Scripts.client.prism.ui.tray_ui import TrayUI

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


# Load the UI for the Slack plugin in the system tray context menu
def trayContextMenuRequested(core, origin, menu):
    config = SlackConfig(core).load_config(mode="studio")
    # SlackConfig(core).check_slack_options(config)

    server_status = config["slack"]["server"].get("status")
    server_machine = config["slack"]["server"].get("machine")

    # Set the server status in the tray to "Not running" if it is empty
    if server_status == "":
        server_status = "Not running"

    # Create the tray menu items
    tray_ui = TrayUI()
    tray_ui.create_tray_slack_ui(menu, server_status, server_machine)

    # Get the tray menu items
    stop_action = tray_ui.stop_server_action
    start_action = tray_ui.start_server_action

    # Connect the actions to the tray menu items
    stop_action.triggered.connect(
        lambda: _slack_tray_toggle(core, tray_ui, server_status, server_machine)
    )
    start_action.triggered.connect(
        lambda: _slack_tray_toggle(core, tray_ui, server_status, server_machine)
    )


# Toggle the Slack menu status and actions in the system tray
def _slack_tray_toggle(core, tray_ui, server_status, server_machine):
    plugin_directory = Path(__file__).resolve().parents[4]

    stop_server_action = tray_ui.stop_server_action
    start_server_action = tray_ui.start_server_action
    status_server_action = tray_ui.status_server_action

    if server_status == "Running":
        if server_machine == socket.gethostname():
            print("Stopping the server")
            ServerControls(core).stop_server()
            stop_server_action.setEnabled(False)
            start_server_action.setEnabled(True)
            status_server_action.setText("Not running")
            status_server_action.setIcon(
                QIcon(os.path.join(plugin_directory, "Resources", "stopped.png"))
            )
        else:
            dialogs = ServerNonWarning()
            dialogs.exec_()
    else:
        print("Starting the server")
        ServerControls(core).start_server()
        stop_server_action.setEnabled(True)
        start_server_action.setEnabled(False)
        status_server_action.setText("Running")
        status_server_action.setIcon(
            QIcon(os.path.join(plugin_directory, "Resources", "running.png"))
        )
