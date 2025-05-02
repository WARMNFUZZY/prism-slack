from Scripts.client.slack.slack_config import SlackConfig
from Scripts.client.prism.ui.settings_ui import SettingsUI
from Scripts.client.prism.api import API
from Scripts.client.prism.ui.load_custom_channel_settings import (
    load_custom_channel_settings,
)
from Scripts.client.prism.ui.load_settings import load_settings

pcore = None


# Load the UI for the Slack plugin in the project settings window
def projectSettings_loadUI(core, origin):
    settings = SettingsUI(core)
    
    config = SlackConfig(core).load_config(mode="studio")
    SlackConfig(core).check_slack_studio_options(config)

    if API(core).is_studio_loaded():
        if core.getPlugin("Studio").getStudioConfigPath() is None or core.getPlugin("Studio").isStudioActive() is False:
            settings.create_slack_project_settings_ui(origin, settings=None)
            load_settings(core, origin, settings=None)
            load_custom_channel_settings(core, origin)
            return
        
        settings.create_slack_custom_channel_ui(origin, settings=None)
        load_custom_channel_settings(core, origin)

    else:
        settings.create_slack_project_settings_ui(origin, settings=None)
        load_settings(core, origin, settings=None)
        load_custom_channel_settings(core, origin)
