# -----------
# Created by John Kesig while at Warm'n Fuzzy
# Contact: john.d.kesig@gmail.com

import os


class Prism_Slack_Variables(object):
    def __init__(self, core, plugin):
        self.version = "v2.0.16"
        self.pluginName = "Slack"
        self.pluginType = "Custom"
        self.platforms = ["Windows"]
        self.pluginDirectory = os.path.abspath(
            os.path.dirname(os.path.dirname(__file__))
        )
