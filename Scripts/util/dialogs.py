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
        self.setWindowTitle('Slack Upload')
        self.setModal(True)
        self.setLayout(QVBoxLayout())
        
        self.label = QLabel('Uploading to Slack...')
        self.layout().addWidget(self.label)


class CommentDialog(QDialog):
    def __init__(self):
        super(CommentDialog, self).__init__()

        plugin_directory = Path(__file__).resolve().parents[2]

        self.setWindowTitle('Slack Additional Comments')
        self.setWindowIcon(QIcon(os.path.join(plugin_directory, "Resources", "slack-icon.png")))
        self.setModal(True)
        self.setLayout(QVBoxLayout())
        self.buttonLayout = QHBoxLayout()
        
        self.label = QLabel('Please leave your additional comments below (optional)')
        self.layout().addWidget(self.label)
        
        self.text_edit = QTextEdit()
        self.layout().addWidget(self.text_edit)
        
        self.button_ok = QPushButton('OK')
        self.button_cancel = QPushButton('Cancel')

        self.buttonLayout.addWidget(self.button_ok)
        self.buttonLayout.addWidget(self.button_cancel)
        self.layout().addLayout(self.buttonLayout)

        self.button_ok.clicked.connect(self.accept)
        self.button_cancel.clicked.connect(self.reject)

    def get_comments(self):
        return self.text_edit.toPlainText()
    

class WarningDialog(QDialog):
    def __init__(self, team_user=None):
        super(WarningDialog, self).__init__(team_user)

        self.setWindowTitle('Warning')
        self.setModal(True)
        self.setLayout(QVBoxLayout())

        self.l_warning = QLabel(f'{team_user} is not in the Channel!\nThis could unintentionally invite them to a channel by tagging them, or let them know what you are working on.\n\nAre you sure you want to proceed?')
        
        self.button_layout = QHBoxLayout()
        self.button_yes = QPushButton('Yes')
        self.button_no = QPushButton('No')
        self.button_layout.addWidget(self.button_yes)
        self.button_layout.addWidget(self.button_no)

        self.layout().addWidget(self.l_warning)
        self.layout().addLayout(self.button_layout)

        self.button_yes.accepted.connect(self.accept)
        self.button_no.rejected.connect(self.reject)