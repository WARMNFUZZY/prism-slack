from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

import os
from pathlib import Path


# Create a dialog letting the user know that the Slack Studio Path was not found
class SlackStudioPathNotFound(QDialog):
    def __init__(self):
        super(SlackStudioPathNotFound, self).__init__()
        plugin_directory = Path(__file__).resolve().parents[5]

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
            """In order for Slack to operate as intended, please set the Slack Studio Path in the Prism Settings.
            
            Slack configuration will continue to use the current Project to establish Slack settings."""
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
