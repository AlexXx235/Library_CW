import sys
from PyQt5.QtWidgets import QApplication, QWidget
from login_form_ui import Ui_login_form
from mysql.connector import MySQLConnection, Error, errorcode
from main import MainWindow


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_login_form()
        self.ui.setupUi(self)
        self.ui.login_btn.clicked.connect(self.login)
        self.show()

    def login(self):
        login = self.ui.login_edit.text()
        password = self.ui.password_edit.text()
        # if login == '' or password == '':
        args = {
            'user': login,
            'password': password,
            'database': 'library',
            'autocommit': True
        }
        print(args)
        try:
            connection = MySQLConnection(**args)
        except Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        else:
            print("Success!")
            self.main_window = MainWindow(connection)
            self.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginWindow()
    sys.exit(app.exec_())