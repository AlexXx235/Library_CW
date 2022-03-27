import sys

import mysql
import library_queries as lq
from mysql.connector import connect, Error, errorcode
from PyQt5.QtWidgets import (QWidget, QMessageBox)
from PyQt5.QtCore import pyqtSignal, QObject, QSettings, Qt
from forms.login_form import Ui_LoginForm
from settings import SettingsForm


class SuccessLogin(QObject):
    signal = pyqtSignal(mysql.connector.connection.MySQLConnection, str)


class LoginWindow(QWidget):
    def __init__(self):
        super(LoginWindow, self).__init__()
        self.ui = Ui_LoginForm()
        self.ui.setupUi(self)
        self.initializeUI()

    def initializeUI(self):
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)
        self.settings = QSettings('MySoft', 'Library')
        self.ui.login_btn.clicked.connect(self.connect_to_database)
        self.ui.settings_btn.clicked.connect(self.open_settings)
        self.connect = SuccessLogin()
        self.ui.login_le.setFocus()
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
                QMessageBox.information(self, 'Доступ запрещен',
                                        'Неверный логин или пароль.',
                                        QMessageBox.Ok)
            elif err.errno == errorcode.CR_CONN_HOST_ERROR:
                self.connection_blocked_msg()
            else:
                QMessageBox.critical(self, 'Упс! Что-то пошло не так', str(err), QMessageBox.Ok)
        else:
            role = lq.get_role(connection.cursor())
            if role == '`admin_role`@`%`' or role == '`librarian`@`%`':
                self.connect.signal.emit(connection, role)
                self.close()
            else:
                QMessageBox.critical(self, 'Уходите',
                                     'Вы не работник библиотеки, до свидания!',
                                     QMessageBox.Ok)
                sys.exit()

    def connection_blocked_msg(self):
        mb = QMessageBox(self)
        mb.setIcon(QMessageBox.Critical)
        mb.setWindowTitle('Соединение не установлено')
        mb.setText('Возможно, сервер не запущен или у вас'
                   'установлен направильный адрес или порт. '
                   'Вы можете исправить это в настройках')
        settings_btn = mb.addButton('Настройки', QMessageBox.ActionRole)
        mb.addButton('Ок', QMessageBox.YesRole)
        mb.exec_()
        if mb.clickedButton() == settings_btn:
            self.open_settings()

    def open_settings(self):
        self.settings_form = SettingsForm()

    def keyPressEvent(self, key_event):
        if key_event.key() == Qt.Key_Return:
            self.ui.login_btn.clicked.emit()
