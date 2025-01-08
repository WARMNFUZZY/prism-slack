import os
from pathlib import Path

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from PrismUtils.Decorators import err_catcher_plugin as err_catcher


class StateManagerUI:
    def __init__(self, core):
        self.core = core

    @err_catcher(__name__)
    def createStateManagerSlackUI(self, state):
        state.cb_userPool = QComboBox()
        state.cb_userPool.setPlaceholderText("Select Artist")

        lo_slack_publish = QHBoxLayout()
        lo_slack_publish.setContentsMargins(10, 5, 0, 0)

        state.l_slackPublish = QLabel("Publish to Slack:")
        state.chb_slackPublish = QCheckBox()
        state.chb_slackPublish.setLayoutDirection(Qt.RightToLeft)

        lo_slack_notify = QHBoxLayout()
        lo_slack_notify.setContentsMargins(10, 5, 0, 0)

        state.l_slackNotify = QLabel("Notify Artist:")
        state.chb_slackNotify = QCheckBox()
        state.chb_slackNotify.setLayoutDirection(Qt.RightToLeft)

        lo_slack_publish.addWidget(state.l_slackPublish)
        lo_slack_publish.addWidget(state.chb_slackPublish)
        lo_slack_notify.addWidget(state.l_slackNotify)
        lo_slack_notify.addWidget(state.chb_slackNotify)
        lo_slack_notify.addWidget(state.cb_userPool)

        state.lo_slack_publish = lo_slack_publish
        state.lo_slack_notify = lo_slack_notify
        state.gb_slack.layout().addLayout(lo_slack_publish)
        state.gb_slack.layout().addLayout(lo_slack_notify)

    @err_catcher(__name__)
    def removeCleanupLayout(self, layout, attribute_name, state):
        if hasattr(state, attribute_name):
            sub_layout = getattr(state, attribute_name)
            if sub_layout:
                for i in reversed(range(sub_layout.count())):
                    item = sub_layout.itemAt(i)
                    if item.widget():
                        widget = item.widget()
                        sub_layout.removeWidget(widget)
                        widget.deleteLater()

                layout.removeItem(sub_layout)
                sub_layout.deleteLater()

                delattr(state, attribute_name)

            for attr in [
                "chb_slackPublish",
                "l_slackPublish",
                "cb_userPool",
                "l_slackNotify",
                "chb_slackNotify",
            ]:
                if hasattr(state, attr):
                    delattr(state, attr)
