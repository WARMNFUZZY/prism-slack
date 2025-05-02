import os
import json

from PrismUtils.Decorators import err_catcher_plugin as err_catcher
from pprint import pprint


class SlackConfig:
    def __init__(self, core):
        self.core = core

    # Get the slack configuration file
    @err_catcher(name=__name__)
    def get_slack_config(self):
        # Get the path to the pipeline configuration file from the environment variable PRISM_STUDIO_PATH
        studio_path = os.getenv("PRISM_STUDIO_PATH")
        if studio_path:
            return os.path.join(studio_path, "configs", "slack.json")

        # If the Studio plugin is not available, check the project configuration file
        elif self.core.getPlugin("Studio") is None:
            project_config_path = self.get_project_config()

            return project_config_path

        # Get the config from the studio path
        else:
            studio_plugin = self.core.getPlugin("Studio")
            studio_path = studio_plugin.getStudioPath()
            
            if studio_path is None:
                project_config_path = self.get_project_config()
                return project_config_path
            else:    
                return os.path.join(studio_path, "configs", "slack.json")
            

    # Get the Prism user configuration file
    @err_catcher(name=__name__)
    def get_user_config(self):
        config = self.core.configs.getConfigPath("user")

        return config

    # Get Prism Project configuration file
    @err_catcher(name=__name__)
    def get_project_config(self):
        user_config = self.get_user_config()
        with open(user_config, "r") as f:
            config = json.load(f)["globals"]["current project"]

        return config
    
    # Load the slack configuration file
    @err_catcher(name=__name__)
    def load_config(self, mode):
        if mode == "user":
            config = self.get_user_config()
            with open(config, "r") as f:
                return json.load(f)

        elif mode == "studio":
            config = self.get_slack_config()

        elif mode == "project":
            config = self.get_project_config()

        else:
            self.core.popup("Cannot retrieve configuration file")
            return

        try:
            # If the pipeline file doesn't exist, create it and initialize the slack token field
            if not os.path.exists(config):
                os.makedirs(os.path.dirname(config), exist_ok=True)
                with open(config, "w") as f:
                    json.dump({"slack": {"token": ""}}, f, indent=4)

            # Load and read the file
            with open(config, "r") as f:
                return json.load(f)
            
        except Exception as e:
            print(f"Error loading config file: {e}")
            return

    # Save the settings to the slack configuration file
    @err_catcher(__name__)
    def save_config_setting(self, setting, mode):
        if mode == "user":
            config = self.get_user_config()

        elif mode == "studio":
            config = self.get_slack_config()
        
        elif mode == "project":
            config = self.get_project_config()
        
        else:
            self.core.popup("Cannot retrieve the Slack configuration file")
            return
        
        try:
            if mode == "studio":
                studio = self.core.getPlugin("Studio")
                if studio is not None:
                    user = self.core.username
                    role = studio.getUserRole(user)
                    if "admin" in role:
                        with open(config, "w") as f:
                            json.dump(setting, f, indent=4)
                    else:
                        return 
                else:
                    with open(config, "w") as f:
                        json.dump(setting, f, indent=4)                 
            else:
                with open(config, "w") as f:
                    json.dump(setting, f, indent=4)

        except Exception as e:
            print(f"Error saving config file: {e}")
            return
        
    @err_catcher(name=__name__)
    def save_server_config_setting(self, setting, mode):
        if mode == "studio":
            config = self.get_slack_config()
        else:
            print("Cannot retrieve the Slack configuration file")
            return

        try:
            # Save the updated config
            with open(config, "w") as f:
                json.dump(setting, f, indent=4)

        except Exception as e:
            print(f"Error saving server config file: {e}")
            return

    # Check if Slack options are present in the pipeline/slack configuration file. If it's not, add them
    @err_catcher(name=__name__)
    def check_slack_studio_options(self, config):
        slack_defaults = {
            "token": "",
            "notifications": {
                "method": "",
                "user_pool": "",
            },
            "custom": {"channel": ""},
            "server": {
                "status": "",
                "machine": "",
                "pid": "",
                "app_token": "",
            },
        }

        try:
            if "slack" not in config:
                config["slack"] = slack_defaults
            else:
                for key, value in slack_defaults.items():
                    if key not in config["slack"]:
                        config["slack"][key] = value
                    elif isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if sub_key not in config["slack"][key]:
                                config["slack"][key][sub_key] = sub_value

            # Save updated config
            self.save_config_setting(config, "studio")
        except Exception as e:
            self.save_config_setting(config, "studio")
            return
