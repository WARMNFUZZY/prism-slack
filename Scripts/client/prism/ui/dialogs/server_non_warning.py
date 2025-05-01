from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


# Create a dialog to let the user know that the server is not running on their machine and it cannot be stopped from here
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
