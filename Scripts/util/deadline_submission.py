import os


class DeadlineScript(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin

    def deadline_submission_script(self, output, state, comment, type, ui):
        root = self.core.prismRoot + "/Scripts"
        root = root.replace("\\", "/")

        code = f"""
import os
import sys
sys.path.append("{root}")
import PrismCore
pcore = PrismCore.create(prismArgs=["noUI", "loadProject"])
slack = pcore.getPlugin('Slack')

slack.publishToSlack(r"{output}", "{state}", "{comment}", "{type}", "{ui}")

"""

        return code
