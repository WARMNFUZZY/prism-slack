from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

import os
from pathlib import Path


# Create Dialog for the user to input comments for the Slack Post
class AdditionalInfoDialog(QDialog):
    def __init__(self, core):
        super(AdditionalInfoDialog, self).__init__()

        plugin_directory = Path(__file__).resolve().parents[5]

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

        self.buttonLayout.addWidget(self.button_ok)
        self.buttonLayout.addWidget(self.button_cancel)
        self.layout().addLayout(self.buttonLayout)

        self.button_ok.clicked.connect(self.accept)
        self.button_cancel.clicked.connect(self.reject)

    # Get the comments from the text edit box
    def get_comments(self):
        return self.text_edit.toPlainText()
