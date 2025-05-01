from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


# Create a dialog to make sure the user wants to stop the server
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
