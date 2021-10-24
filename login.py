import sys
import mysql
# from main import MainWindow
from mysql.connector import connect
from PyQt5.QtWidgets import (QWidget)
from PyQt5.QtCore import pyqtSignal, QObject
from login_form import Ui_LoginForm


class SuccessLogin(QObject):
    signal = pyqtSignal(mysql.connector.connection.MySQLConnection)


class LoginWindow(QWidget):
    def __init__(self):
        super(LoginWindow, self).__init__()
        self.ui = Ui_LoginForm()
        self.ui.setupUi(self)
        self.initializeUI()

    def initializeUI(self):
        self.ui.login_btn.clicked.connect(self.connect_to_database)
        self.connect = SuccessLogin()
        self.show()

    def connect_to_database(self):
        user = self.ui.login_le.text()
        password = self.ui.password_le.text()
        config = {
            'user': user,
            'password': password,
            'host': '127.0.0.1',
            'port': 3306,
            'database': 'library'
        }
        connection = connect(**config)
        self.connect.signal.emit(connection)
        self.close()