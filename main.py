import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from main_window_ui import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.handler)
        self.show()

    def handler(self):
        print("i am here")
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM room')
        for row in cursor:
            self.ui.test_label.setText(self.ui.test_label.text() + str(row))
            # print(row)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow(None)
    sys.exit(app.exec_())