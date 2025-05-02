import os
import socket
from pathlib import Path
from Scripts.client.slack.slack_config import SlackConfig
from Scripts.client.prism.ui import (
    ServerStartWarning,
    ServerStopWarning,
    ServerNonWarning,
)

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from PrismUtils.Decorators import err_catcher_plugin as err_catcher


class ServerControls:
    def __init__(self, core):
        self.core = core

    # Start the Slack Bolt Server
    @err_catcher(name=__name__)
    def start_server(self):
        import win32api
        import subprocess
        # Create paths for the environment variables to be used in the Slack Bolt Server
        scripts_path = self.core.getPlugin("Slack").pluginDirectory
        bolt_path = os.path.join(scripts_path, "server", "bolt.py")

        config = SlackConfig(self.core).load_config(mode="studio")
        token = config["slack"]["token"]
        app_token = config["slack"]["server"]["app_token"]

        executable = os.path.join(self.core.prismLibs, "Python311", "python.exe")

        # Set the environment variables for the Slack Bolt Server
        sub_env = os.environ.copy()
        sub_env["BOLTPATH"] = f"{Path(__file__).resolve().parents[2]}\PythonLibs"
        sub_env["SCRIPTSPATH"] = f"{Path(__file__).resolve().parents[1]}"
        sub_env["PRISMPATH"] = f"{self.core.prismLibs}\PythonLibs\Python3"
        sub_env["PRISM_CORE"] = f"{self.core.prismLibs}\Scripts"
        sub_env["PRISM_UTILS"] = F"{self.core.prismLibs}\Scripts\PrismUtils"

        server_status = config["slack"]["server"].get("status")
        machine = config["slack"]["server"].get("machine")

        # Set handler for console events to reset the server status if the server is stopped
        win32api.SetConsoleCtrlHandler(
            lambda event: (self.reset_server_status() if event == 2 else False), True
        )

        # Attempt to start the Slack Bolt Server
        try:
            if server_status != "Running" and os.path.exists(bolt_path):
                bolt = subprocess.Popen(
                    [executable, bolt_path, token, app_token], env=sub_env, text=True
                )

                # Update the server status/machine/pid in the config file
                config = SlackConfig(self.core).load_config(mode="studio")
                config["slack"]["server"]["status"] = "Running"
                config["slack"]["server"]["machine"] = socket.gethostname()
                config["slack"]["server"]["pid"] = bolt.pid
                SlackConfig(self.core).save_server_config_setting(config, mode="studio")
            
            else:
                print("Slack Bolt Server is already running")
                return

        except Exception as e:
            self.core.popup(f"Error starting the Slack Bolt Server: {e}")
            self.stop_server()

    # Reset the server status in the conig file
    def reset_server_status(self):
        config = SlackConfig(self.core).load_config(mode="studio")
        config["slack"]["server"]["status"] = ""
        config["slack"]["server"]["machine"] = ""
        config["slack"]["server"]["pid"] = ""
        SlackConfig(self.core).save_server_config_setting(config, mode="studio")


    # Stop the Slack Bolt Server
    @err_catcher(name=__name__)
    def stop_server(self):
        config = SlackConfig(self.core).load_config(mode="studio")
        status = config["slack"]["server"].get("status")
        pid = config["slack"]["server"].get("pid")

        if status == "Running":
            try:
                if os.name == "nt":
                    os.system(f"taskkill /F /PID {pid}")
                    print("Slack Bolt Server stopped")
                    self.reset_server_status()

            except Exception as e:
                print(f"Error stopping the Slack Bolt Server: {e}")

    # Start the Slack Bolt Server from the GUI
    @err_catcher(name=__name__)
    def gui_start_server(self, origin):
        start_check = ServerStartWarning()
        if start_check.exec_() == QDialog.Accepted:
            self.start_server()
            origin.b_server.setText("Stop Server")
            origin.b_reset_server.setEnabled(False)
            self.check_server_status(origin)
        else:
            return

    # Stop the Slack Bolt Server from the GUI
    @err_catcher(name=__name__)
    def gui_stop_server(self, origin):
        stop_check = ServerStopWarning()
        if stop_check.exec_() == QDialog.Accepted:
            self.stop_server()
            origin.b_server.setText("Start Server")
            origin.b_reset_server.setEnabled(True)
            self.check_server_status(origin)
        else:
            return
        
    # Reset the Slack Bolt Server status from the GUI
    @err_catcher(name=__name__)
    def gui_reset_server_status(self, origin):
        self.reset_server_status()
        origin.b_server.setText("Start Server")
        origin.b_reset_server.setEnabled(False)
        self.check_server_status(origin)


    # Check the status of the Slack Bolt Server from the config file
    @err_catcher(name=__name__)
    def check_server_status(self, origin):
        config = SlackConfig(self.core).load_config(mode="studio")

        status = config["slack"]["server"].get("status")
        machine = config["slack"]["server"].get("machine")

        if origin is not None:
            origin.l_server_status_value.setText(status)
            origin.l_machine_value.setText(machine)

        return config["slack"]["server"].get("status")

    # Toggle the Server controls in the studio/project settings window
    @err_catcher(name=__name__)
    def toggle_server(self, origin):
        config = SlackConfig(self.core).load_config(mode="studio")

        server_machine = config["slack"]["server"].get("machine")
        server_status = config["slack"]["server"].get("status")

        if server_status == "Running":
            if socket.gethostname() != server_machine:
                non_server_check = ServerNonWarning()
                non_server_check.exec_()
                return
            else:
                self.gui_stop_server(origin)
        else:
            origin.b_reset_server.setEnabled(True)
            self.gui_start_server(origin)
