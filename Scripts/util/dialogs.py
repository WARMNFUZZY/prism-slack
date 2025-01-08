import os
from pathlib import Path

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


class InputDialog(QDialog):
    def __init__(self, title):
        super(InputDialog, self).__init__()

        self.setWindowTitle("Slack")
        self.setModal(True)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel(title)
        self.layout.addWidget(self.label)

        self.input_field = QLineEdit()
        self.layout.addWidget(self.input_field)

        self.button_layout = QHBoxLayout()
        self.button_ok = QPushButton("OK")
        self.button_cancel = QPushButton("Cancel")
        self.button_layout.addWidget(self.button_ok)
        self.button_layout.addWidget(self.button_cancel)

        self.button_ok.clicked.connect(self.accept)
        self.button_cancel.clicked.connect(self.reject)

        self.layout.addLayout(self.button_layout)

    def get_input(self):
        return self.input_field.text()


class UploadDialog(QDialog):
    def __init__(self):
        super(UploadDialog, self).__init__()
        self.setWindowTitle("Slack Upload")
        self.setModal(True)
        self.setLayout(QVBoxLayout())

        self.label = QLabel("Uploading to Slack...")
        self.layout().addWidget(self.label)


class AdditionalInfoDialog(QDialog):
    def __init__(self):
        super(AdditionalInfoDialog, self).__init__()

        plugin_directory = Path(__file__).resolve().parents[2]

        self.setWindowTitle("Slack Publish Information")
        self.setWindowIcon(
            QIcon(os.path.join(plugin_directory, "Resources", "slack-icon.png"))
        )
        self.setModal(True)
        self.setLayout(QVBoxLayout())
        self.buttonLayout = QHBoxLayout()

        self.label = QLabel("Please leave your additional comments below (optional)")
        self.layout().addWidget(self.label)

        self.text_edit = QTextEdit()
        self.layout().addWidget(self.text_edit)

        self.button_ok = QPushButton("OK")
        self.button_cancel = QPushButton("Cancel")

        self.div = QFrame()
        self.div.setFrameShape(QFrame.HLine)
        self.div.setFrameShadow(QFrame.Sunken)
        self.layout().addWidget(self.div)

        self.gb_status = QGroupBox("Status")
        self.bg_status = QButtonGroup()
        self.lo_review = QHBoxLayout()
        self.gb_status.setLayout(self.lo_review)

        self.rb_status_wip = QRadioButton("Work In Progress")
        self.rb_status_wip.setStyleSheet(
            """QRadioButton::indicator { width: 15px; height: 15px; }"""
        )
        self.rb_status_wip.setChecked(True)
        self.lo_review.addWidget(self.rb_status_wip)

        self.rb_status_reivew = QRadioButton("Request Review")
        self.rb_status_reivew.setStyleSheet(
            """QRadioButton::indicator { width: 15px; height: 15px; }"""
        )
        self.lo_review.addWidget(self.rb_status_reivew)

        self.bg_status.addButton(self.rb_status_wip)
        self.bg_status.addButton(self.rb_status_reivew)
        self.layout().addWidget(self.gb_status)

        self.buttonLayout.addWidget(self.button_ok)
        self.buttonLayout.addWidget(self.button_cancel)
        self.layout().addLayout(self.buttonLayout)

        self.button_ok.clicked.connect(self.accept)
        self.button_cancel.clicked.connect(self.reject)

    def get_comments(self):
        return self.text_edit.toPlainText()

    def get_status(self):
        return self.bg_status.checkedButton().text()


class WarningDialog(QDialog):
    def __init__(self, team_user=None):
        super(WarningDialog, self).__init__(team_user)

        self.setWindowTitle("Warning")
        self.setModal(True)
        self.setLayout(QVBoxLayout())

        self.l_warning = QLabel(
            f"{team_user} is not in the Channel!\nThis could unintentionally invite them to a channel by tagging them, or let them know what you are working on.\n\nAre you sure you want to proceed?"
        )

        self.button_layout = QHBoxLayout()
        self.button_yes = QPushButton("Yes")
        self.button_no = QPushButton("No")
        self.button_layout.addWidget(self.button_yes)
        self.button_layout.addWidget(self.button_no)

        self.layout().addWidget(self.l_warning)
        self.layout().addLayout(self.button_layout)

        self.button_yes.accepted.connect(self.accept)
        self.button_no.rejected.connect(self.reject)


class SuccessfulPOST:
    def __init__(self, uploaded, method, upload_message):
        upload_message.close()

        if uploaded == True and method == "Media":
            QMessageBox.information(
                None, "Slack Upload", "Asset has been uploaded successfully"
            )
        elif uploaded == False:
            QMessageBox.warning(None, "Slack Upload", "Failed to upload asset to Slack")
        else:
            None


class ServerStartWarning(QDialog):
    def __init__(self):
        super(ServerStartWarning, self).__init__()

        self.setWindowTitle("Warning")
        self.setModal(True)
        self.setLayout(QVBoxLayout())

        self.l_warning = QLabel("Are you sure you want to start the server?")

        self.button_layout = QHBoxLayout()
        self.button_yes = QPushButton("Yes")
        self.button_no = QPushButton("No")
        self.button_layout.addWidget(self.button_yes)
        self.button_layout.addWidget(self.button_no)

        self.layout().addWidget(self.l_warning)
        self.layout().addLayout(self.button_layout)

        self.button_yes.clicked.connect(self.accept)
        self.button_no.clicked.connect(self.reject)


class ServerStopWarning(QDialog):
    def __init__(self):
        super(ServerStopWarning, self).__init__()

        self.setWindowTitle("Warning")
        self.setModal(True)
        self.setLayout(QVBoxLayout())

        self.l_warning = QLabel("Are you sure you want to stop the server?")

        self.button_layout = QHBoxLayout()
        self.button_yes = QPushButton("Yes")
        self.button_no = QPushButton("No")
        self.button_layout.addWidget(self.button_yes)
        self.button_layout.addWidget(self.button_no)

        self.layout().addWidget(self.l_warning)
        self.layout().addLayout(self.button_layout)

        self.button_yes.clicked.connect(self.accept)
        self.button_no.clicked.connect(self.reject)


class ServerNonWarning(QDialog):
    def __init__(self):
        super(ServerNonWarning, self).__init__()

        self.setWindowTitle("Warning")
        self.setModal(True)
        self.setLayout(QVBoxLayout())

        self.l_warning = QLabel(
            "You are trying to stop the Slack Bolt Server,\n"
            "however it is not running on this machine.\n\n"
            "If you want to stop the server, please go to the machine and stop it."
        )

        self.button_layout = QHBoxLayout()
        self.button_yes = QPushButton("Yes")
        self.button_layout.addWidget(self.button_yes)

        self.layout().addWidget(self.l_warning)
        self.layout().addLayout(self.button_layout)

        self.button_yes.clicked.connect(self.accept)


class SlackStudioPathNotFound(QDialog):
    def __init__(self):
        super(SlackStudioPathNotFound, self).__init__()
        plugin_directory = Path(__file__).resolve().parents[2]

        self.setWindowTitle("Slack Config Warning")
        self.setWindowIcon(
            QIcon(os.path.join(plugin_directory, "Resources", "slack-icon.png"))
        )
        self.setModal(True)
        self.setLayout(QVBoxLayout())

        self.l_warning = QLabel(
            "Studio Plugin is enabled but the Studio Path was not found"
        )
        self.l_warning.setAlignment(Qt.AlignCenter)
        self.l_warning_long = QLabel(
            "In order for Slack to operate as intended, please set the Slack Studio Path in the configuration file."
        )
        self.l_warning_long.setAlignment(Qt.AlignCenter)
        self.l_warning_long.setContentsMargins(10, 10, 10, 10)
        self.l_warning_long.setWordWrap(True)

        self.button_layout = QHBoxLayout()
        self.button_ok = QPushButton("OK")
        self.button_layout.addWidget(self.button_ok)

        self.layout().addWidget(self.l_warning)
        self.layout().addWidget(self.l_warning_long)
        self.layout().addLayout(self.button_layout)

        self.button_ok.clicked.connect(self.accept)
