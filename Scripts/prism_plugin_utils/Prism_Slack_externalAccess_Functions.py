# -----------
# Created by John Kesig while at Warm'n Fuzzy
# Contact: john.d.kesig@gmail.com

from functools import partial
from Scripts.client.prism.api import API

from Scripts.client.prism.callbacks.studio_settings_load_settings import (
    studioSettings_loadSettings,
)
from Scripts.client.prism.callbacks.user_settings_load_ui import userSettings_loadUI
from Scripts.client.prism.callbacks.project_settings_load_ui import (
    projectSettings_loadUI,
)
from Scripts.client.prism.callbacks.tray_context_menu_requested import (
    trayContextMenuRequested,
)
from PrismUtils.Decorators import err_catcher_plugin as err_catcher


class Prism_Slack_externalAccess_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin

        self.core.registerCallback(
            "onPluginsLoaded", self.onPluginsLoaded, plugin=self
        )

        self.core.registerCallback(
            "userSettings_loadUI",
            partial(userSettings_loadUI, self.core),
            plugin=self,
        )
        self.core.registerCallback(
            "trayContextMenuRequested",
            partial(trayContextMenuRequested, self.core),
            plugin=plugin,
        )

    @err_catcher(name=__name__)
    def onPluginsLoaded(self):
        if API(self.core).is_studio_loaded() is not None:
            self.core.registerCallback(
                "studioSettings_loadSettings",
                partial(studioSettings_loadSettings, self.core),
                plugin=self,
            )
            self.core.registerCallback(
                "projectSettings_loadUI",
                partial(projectSettings_loadUI, self.core),
                plugin=self,
            )
        else:
            self.core.registerCallback(
                "projectSettings_loadUI",
                partial(projectSettings_loadUI, self.core),
                plugin=self,
            )

        self.core.registerCallback(
            "userSettings_loadUI",
            partial(userSettings_loadUI, self.core),
            plugin=self,
        )
