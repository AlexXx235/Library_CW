from settings_form import Ui_Form
from PyQt5.QtWidgets import (QWidget)
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QIntValidator


class SettingsForm(QWidget):
    def __init__(self):
        super(SettingsForm, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.initializeUI()

    def initializeUI(self):
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)
        self.fill_edits()
        self.ui.save_btn.clicked.connect(self.save_settings)
        self.ui.cancel_btn.clicked.connect(self.close)
        self.show()

    def fill_edits(self):
        self.ui.port_le.setValidator(QIntValidator(0, 65535))
        self.settings = QSettings('MySoft', 'Library')
        self.ui.host_le.setText(self.settings.value('host', 'localhost'))
        self.ui.port_le.setText(self.settings.value('port', '3306'))

    def save_settings(self):
        host = self.ui.host_le.text()
        port = self.ui.port_le.text()
        self.settings.setValue('host', host)
        self.settings.setValue('port', port)
        self.close()
