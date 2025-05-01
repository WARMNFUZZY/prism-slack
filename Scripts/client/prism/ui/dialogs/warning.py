from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


# Create a dialog to warn the user that the user is not in the channel
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
