import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from main_window_ui import Ui_MainWindow
from login import LoginWindow


class MainWindow(QMainWindow):
    def __init__(self, connection):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.login_window = LoginWindow(self)

    def login_success(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow(None)
    sys.exit(app.exec_())