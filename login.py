import mysql
from mysql.connector import connect, Error, errorcode
from PyQt5.QtWidgets import (QWidget, QMessageBox)
from PyQt5.QtCore import pyqtSignal, QObject, QSettings
from login_form import Ui_LoginForm
from settings import SettingsForm


class SuccessLogin(QObject):
    signal = pyqtSignal(mysql.connector.connection.MySQLConnection)


class LoginWindow(QWidget):
    def __init__(self):
        super(LoginWindow, self).__init__()
        self.ui = Ui_LoginForm()
        self.ui.setupUi(self)
        self.initializeUI()

    def initializeUI(self):
        self.settings = QSettings('MySoft', 'Library')
        self.ui.login_btn.clicked.connect(self.connect_to_database)
        self.ui.settings_btn.clicked.connect(self.open_settings)
        self.connect = SuccessLogin()
        self.show()

    def connect_to_database(self):
        user = self.ui.login_le.text()
        password = self.ui.password_le.text()
        config = {
            'user': user,
            'password': password,
            'host': self.settings.value('host', 'localhost'),
            'port': int(self.settings.value('port', 3306)),
            'database': 'library',
            'autocommit': True,
            'charset': 'utf8'
        }
        try:
            connection = connect(**config)
        except Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                QMessageBox.information(self, 'Access denied',
                                        'Probably your login or password is incorrect.\nTry again.',
                                        QMessageBox.Ok)
            elif err.errno == errorcode.CR_CONN_HOST_ERROR:
                self.connection_blocked_msg()
            else:
                QMessageBox.critical(self, 'Something went wrong', str(err), QMessageBox.Ok)
        else:
            self.connect.signal.emit(connection)
            self.close()

    def connection_blocked_msg(self):
        mb = QMessageBox(self)
        mb.setIcon(QMessageBox.Critical)
        mb.setWindowTitle('Connection blocked')
        mb.setText('Probably the server is not running or you are '
                   'trying to connect incorrect host/port.')
        settings_btn = mb.addButton('Settings', QMessageBox.ActionRole)
        mb.addButton('Ok', QMessageBox.YesRole)
        mb.exec_()
        if mb.clickedButton() == settings_btn:
            self.open_settings()

    def open_settings(self):
        self.settings_form = SettingsForm()
