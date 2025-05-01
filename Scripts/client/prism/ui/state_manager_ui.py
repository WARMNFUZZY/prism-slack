from Scripts.client.slack.slack_config import SlackConfig

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from PrismUtils.Decorators import err_catcher_plugin as err_catcher


class StateManagerUI:
    def __init__(self, core):
        self.core = core

    # Create the Slack section of the State Manager UI
    @err_catcher(__name__)
    def createStateManagerSlackUI(self, state):
        state.cb_slackUserPool = QComboBox()
        state.cb_slackUserPool.setPlaceholderText("Select Artist")

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
        lo_slack_notify.addWidget(state.cb_slackUserPool)

        state.lo_slack_publish = lo_slack_publish
        state.lo_slack_notify = lo_slack_notify
        
        if state.className != "Export":
            state.gb_slack.layout().addLayout(lo_slack_publish)
        state.gb_slack.layout().addLayout(lo_slack_notify)

        lo_comments = QHBoxLayout()
        lo_comments.setContentsMargins(10, 5, 0, 0)

        if state.className != "Export":
            state.te_slackComments = QTextEdit()
            state.te_slackComments.setPlaceholderText("(Optional) Leave your Slack comments here")
            lo_comments.addWidget(state.te_slackComments)

        state.gb_slack.layout().addLayout(lo_comments)

    # Remove the Slack section of the State Manager UI
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
                    elif item.layout():
                        sub_layout.removeItem(item)
                        item.deleteLater()

                layout.removeItem(sub_layout)
                sub_layout.deleteLater()

                delattr(state, attribute_name)

            for attr in [
                "chb_slackPublish",
                "l_slackPublish",
                "cb_slackUserPool",
                "l_slackNotify",
                "chb_slackNotify",
                "te_slackComments",
            ]:
                if hasattr(state, attr):
                    widget = getattr(state, attr)
                    if isinstance(widget, QWidget):
                        widget.deleteLater()
                    delattr(state, attr)
