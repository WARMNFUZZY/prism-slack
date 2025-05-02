from Scripts.client.prism.ui import SlackStudioPathNotFound
from Scripts.client.prism.ui.settings_ui import SettingsUI
from Scripts.client.prism.ui.load_settings import load_settings
from Scripts.client.prism.ui.load_custom_channel_settings import (
    load_custom_channel_settings,
)


def studioSettings_loadSettings(core, origin, settings):
    settings = SettingsUI(core)

    if core.getPlugin("Studio").getStudioConfigPath() is None:
        SlackStudioPathNotFound().exec_()
        return

    if core.getPlugin("Studio").isStudioActive() is False:
        return

    settings.create_slack_studio_settings_ui(origin, settings)
    load_settings(core, origin, settings)
