from Scripts.client.prism.ui import SlackStudioPathNotFound
from Scripts.client.prism.ui.settings_ui import SettingsUI
from Scripts.client.prism.ui.load_settings import load_settings


def studioSettings_loadSettings(core, origin, settings):
    settings_ui = SettingsUI(core)

    if core.getPlugin("Studio").getStudioConfigPath() is None:
        SlackStudioPathNotFound().exec_()
        return

    settings_ui.create_slack_studio_settings_ui(origin, settings)
    load_settings(core, origin, settings)
