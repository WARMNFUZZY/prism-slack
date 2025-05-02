import os
from pathlib import Path

from Scripts.client.prism.utils.publish_to_slack import PublishToSlack
from Scripts.client.prism.ui import AdditionalInfoDialog
from Scripts.client.prism.api import API

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


def mediaPlayerContextMenuRequested(core, origin, menu):
    if not type(origin.origin).__name__ == "MediaBrowser":
        return

    pluginDirectory = Path(__file__).resolve().parents[4]

    file = origin.seq

    state_data = {
        "project": API(core).get_current_project(),
        "state_type": "Media",
        "ui": "Media",
        "app": "Standalone",
    }

    action = QAction("Publish to Slack", origin)
    iconPath = os.path.join(pluginDirectory, "Resources", "slack-icon.png")
    icon = core.media.getColoredIcon(iconPath)

    action.triggered.connect(
        lambda: _get_comments(
            core=core,
            file=file,
            state_data=state_data,
            prism_user=API(core).get_prism_slack_username(),
        )
    )

    menu.insertAction(menu.actions()[-1], action)
    action.setIcon(icon)


def _get_comments(core, file, state_data, prism_user):
    info_dialog = AdditionalInfoDialog(core)
    if info_dialog.exec_() == QDialog.Accepted:
        comment = info_dialog.get_comments()
        state_data["comments"] = comment

        info_dialog.close()
    
    else:
        info_dialog.close()
        return

    PublishToSlack(core).publish_to_slack(file, state_data, prism_user)
