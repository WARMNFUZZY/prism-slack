import os
import win32api
import socket
import subprocess
from pathlib import Path

from integration.slack_config import SlackConfig
from util.dialogs import *

from PrismUtils.Decorators import err_catcher_plugin as err_catcher

class ServerControls:
    def __init__(self, core):
        self.core = core
        self.slack_config = SlackConfig(self.core)
        
    @err_catcher(name=__name__)
    def startServer(self):
        scripts_path = os.path.join(self.core.getPlugin("Slack").pluginDirectory, "Scripts")
        bolt_path = os.path.join(scripts_path, "server", "bolt.py")
        self.config = self.slack_config.loadConfig(mode="studio")
        token = self.config["slack"]["token"]
        app_token = self.config["slack"]["server"]["app_token"]
        executable = os.path.join(self.core.prismLibs, "Python311", "python.exe")

        sub_env = os.environ.copy()
        sub_env["BOLTPATH"] = f"{Path(__file__).resolve().parents[2]}\PythonLibs"
        sub_env["SCRIPTSPATH"] = f"{Path(__file__).resolve().parents[1]}"
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
        print(pid)

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

        status = pipeline_data["slack"]["server"].get("status")
        machine = pipeline_data["slack"]["server"].get("machine")

        print(origin)

        if origin is not None:
            origin.l_server_status_value.setText(status)
            origin.l_machine_value.setText(machine)

        return pipeline_data["slack"]["server"].get("status")