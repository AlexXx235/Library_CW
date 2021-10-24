import sys
import library_queries as lq
from login import LoginWindow
from main_form import Ui_MainWindow
from PyQt5.QtWidgets import (QApplication, QMainWindow)


any_room_text = 'Любой читальный зал'


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.login()

    def login(self):
        self.login_form = LoginWindow()
        self.login_form.connect.signal.connect(self.get_connection)

    def initializeUI(self):
        self.ui.book_search_btn.clicked.connect(self.book_search)
        self.ui.cipher_le.textEdited.connect(self.control_filters)
        self.init_room_combo_box()
        self.show()

    def get_connection(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.initializeUI()

    def init_room_combo_box(self):
        rooms = lq.get_rooms(self.cursor)
        self.ui.room_combo_box.addItem(any_room_text)
        for room in rooms:
            self.ui.room_combo_box.addItem(room)

    def book_search(self):
        # ----------
        self.ui.test_label.clear()
        # ----------
        cipher = self.ui.cipher_le.text()
        if cipher != '':
            books = lq.get_book_by_cipher(self.cursor, cipher)
        else:
            title = self.ui.title_le.text()
            author = self.ui.author_le.text()
            room = self.ui.room_combo_box.currentText()
            if room == any_room_text:
                room = ''
            books = lq.filtered_book_search(self.cursor, title=title,
                                            author=author, room=room)
        # ----------
        if not books:
            self.ui.test_label.setText('Empty list')
        else:
            for book in books:
                self.ui.test_label.setText(self.ui.test_label.text() + '\n' + str(book))
        # ----------

    def control_filters(self):
        if self.ui.cipher_le.text() == '':
            self.ui.author_le.setEnabled(True)
            self.ui.title_le.setEnabled(True)
        else:
            self.ui.author_le.setEnabled(False)
            self.ui.title_le.setEnabled(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())