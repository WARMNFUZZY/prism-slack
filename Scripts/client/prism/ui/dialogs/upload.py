from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

import os
from pathlib import Path

# Create an "Uploading" dialog for the user to see while the file is being uploaded
class UploadDialog(QDialog):
    def __init__(self):
        super(UploadDialog, self).__init__()
        
        plugin_directory = Path(__file__).resolve().parents[5]
        
        self.setWindowTitle("Slack Upload")
        self.setWindowIcon(
            QIcon(os.path.join(plugin_directory, "Resources", "slack-icon.png"))
        )
        self.setModal(True)
        self.setLayout(QVBoxLayout())

        self.label = QLabel("Uploading to Slack...")
        self.layout().addWidget(self.label)
