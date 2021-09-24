import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtCore import pyqtSignal
from login_form_ui import Ui_login_form
from mysql.connector import MySQLConnection, Error, errorcode


class LoginWindow(QWidget):
    login_success = pyqtSignal(MySQLConnection)
    def __init__(self, parent):
        super().__init__()
        self.parent_window = parent
        self.ui = Ui_login_form()
        self.ui.setupUi(self)
        self.ui.login_btn.clicked.connect(self.login)
        self.login_success.connect(self.parent_window.login_success)
        self.show()

    def login(self):
        login = self.ui.login_edit.text()
        password = self.ui.password_edit.text()
        if login == '' or password == '':
            QMessageBox.warning(self, "Login Failed",
                                "Neither login or password can be empty",
                                QMessageBox.Ok)
            return
        args = {
            'user': login,
            'password': password,
            'database': self.get_chema_name(),
            'autocommit': True
        }
        connection = self.get_connection(args)
        if connection is None:
            return
        self.hide()
        self.login_success.emit(connection)

    def get_connection(self, args):
        try:
            connection = MySQLConnection(**args)
        except Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                QMessageBox.warning(self, "Login Failed",
                                    "Login or password is incorrect",
                                    QMessageBox.Ok)
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                QMessageBox.critical(self, "Login Failed",
                                     "Database does not exist or unavailable",
                                     QMessageBox.Ok)
            else:
                QMessageBox.critical(self, "Unknown error!",
                                     str(err),
                                     QMessageBox.Ok)
            return None
        else:
            return connection

    def get_chema_name(self):
        return 'library'


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginWindow()
    sys.exit(app.exec_())