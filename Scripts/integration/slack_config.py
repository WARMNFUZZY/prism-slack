import os
import json

from PrismUtils.Decorators import err_catcher_plugin as err_catcher


class SlackConfig:
    def __init__(self, core):
        self.core = core

    # Get the slack configuration file
    @err_catcher(name=__name__)
    def getSlackConfig(self):
        # Get the path to the pipeline configuration file from the environment variable PRISM_STUDIO_PATH
        studio_path = os.getenv("PRISM_STUDIO_PATH")
        if studio_path:
            return os.path.join(studio_path, "configs", "slack.json")

        # If the Studio plugin is not available, check the project configuration file
        elif self.core.getPlugin("Studio") is None:
            prjConfig_path = os.path.dirname(self.core.prismIni)

            return os.path.join(prjConfig_path, "pipeline.json")

        # Get the config from the studio path
        else:
            studio_plugin = self.core.getPlugin("Studio")
            studio_path = studio_plugin.getStudioPath()

            return os.path.join(studio_path, "configs", "slack.json")

    # Get the user configuration file
    @err_catcher(name=__name__)
    def getUserConfig(self):
        config = self.core.configs.getConfigPath("user")

        return config

    # Load the slack configuration file
    @err_catcher(name=__name__)
    def loadConfig(self, mode):
        if mode == "user":
            user_file = self.getUserConfig()

            with open(user_file, "r") as f:
                return json.load(f)

        elif mode == "studio":
            pipeline_file = self.getSlackConfig()

        else:
            self.core.popup("Cannot retrieve configuration file")
            return
        try:
            # If the pipeline file doesn't exist, create it and initialize the slack token field
            if not os.path.exists(pipeline_file):
                os.makedirs(os.path.dirname(pipeline_file), exist_ok=True)
                with open(pipeline_file, "w") as f:
                    json.dump({"slack": {"token": ""}}, f, indent=4)

            # Load and read the file
            with open(pipeline_file, "r") as f:
                return json.load(f)
        except:
            return

    # Save the settings to the slack configuration file
    @err_catcher(__name__)
    def saveConfigSetting(self, setting, mode):
        if mode == "user":
            config = self.getUserConfig()
        elif mode == "studio":
            config = self.getSlackConfig()
        else:
            self.core.popup("Cannot retrieve configuration file")
            return

        with open(config, "w") as f:
            json.dump(setting, f, indent=4)

    # Check if Slack options are present in the pipeline configuration file. If it's not, add them
    @err_catcher(name=__name__)
    def checkSlackOptions(self, pipeline_data):
        if "slack" not in pipeline_data:
            pipeline_data["slack"] = {}

        if "token" not in pipeline_data["slack"]:
            pipeline_data["slack"]["token"] = ""

        if "notifications" not in pipeline_data["slack"]:
            pipeline_data["slack"]["notifications"] = {}
        if "method" not in pipeline_data["slack"]["notifications"]:
            pipeline_data["slack"]["notifications"]["method"] = ""
        if "user_pool" not in pipeline_data["slack"]["notifications"]:
            pipeline_data["slack"]["notifications"]["user_pool"] = ""

        if "server" not in pipeline_data["slack"]:
            pipeline_data["slack"]["server"] = {}
        if "app_token" not in pipeline_data["slack"]["server"]:
            pipeline_data["slack"]["server"]["app_token"] = ""
        if "status" not in pipeline_data["slack"]["server"]:
            pipeline_data["slack"]["server"]["status"] = ""
        if "machine" not in pipeline_data["slack"]["server"]:
            pipeline_data["slack"]["server"]["machine"] = ""
