import sys
import library_queries as lq
from login import LoginWindow
from main_form import Ui_MainWindow
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableWidgetItem, QHeaderView, QInputDialog,
                             QMessageBox)
from mysql.connector import Error, errorcode


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
        self.ui.readers_book_search_btn.clicked.connect(self.readers_book_search)
        self.init_room_combo_box()
        self.configure_books_table()
        self.showMaximized()

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
        cipher = self.ui.cipher_le.text()
        if cipher != '':
            self.ui.query_label.setText(f'Книга с шифром: {cipher}')
            books = lq.get_book_by_cipher(self.cursor, cipher)
        else:

            title = self.ui.title_le.text()
            author = self.ui.author_le.text()
            room = self.ui.room_combo_box.currentText()
            if room == any_room_text:
                room = ''
            self.set_query_label(title, author, room)
            books = lq.filtered_book_search(self.cursor, title=title,
                                            author=author, room=room)
        self.fill_table(books)

    def set_query_label(self, title, author, room):
        if title == '' and author == '' and room == '':
            self.ui.query_label.setText('Все книги')
        else:
            label_text = "Книги по запросу:"
            if title != '':
                label_text += f" Название = '{title}',"
            if author != '':
                label_text += f" Автор = '{author}',"
            if room != '':
                label_text += f" Читальный зал = '{room}'"
            if label_text[-1] == ',':
                label_text = label_text[:-1]
            self.ui.query_label.setText(label_text)

    def fill_table(self, books):
        self.ui.books_table.clearContents()
        self.ui.books_table.setRowCount(len(books))
        if books:
            for row in range(len(books)):
                for column in range(self.ui.books_table.columnCount()):
                    item = QTableWidgetItem(str(books[row][column]))
                    self.ui.books_table.setItem(row, column, item)

    def change_cipher(self, row, column):
        if column == 0:
            old_cipher = self.ui.books_table.item(row, column).text()
            new_cipher, ok = QInputDialog.getInt(self, 'Введите новый шифр', 'Новый шифр: ')
            if ok and new_cipher != '':
                try:
                    lq.change_book_cipher(self.cursor, int(old_cipher), new_cipher)
                except Error as err:
                    if err.errno == errorcode.ER_DUP_ENTRY:
                        QMessageBox.critical(self, 'Попытка дублирования.',
                                             'Шифры книг должны быть уникальными.', QMessageBox.Ok)
                    else:
                        QMessageBox.critical(self, 'Упс! Что-то пошло не так', str(err), QMessageBox.Ok)
                else:
                    self.ui.books_table.item(row, column).setText(str(new_cipher))

    def readers_book_search(self):
        text = self.ui.card_number_le.text()
        if text != '':
            if text.isdigit():
                self.ui.query_label.setText(f'Книги читателя с номером билета: {text}')
                card_number = int(text)
                books = lq.get_books_by_reader(self.cursor, card_number)
                self.fill_table(books)

    def control_filters(self):
        if self.ui.cipher_le.text() == '':
            self.ui.author_le.setEnabled(True)
            self.ui.title_le.setEnabled(True)
        else:
            self.ui.author_le.setEnabled(False)
            self.ui.title_le.setEnabled(False)

    def configure_books_table(self):
        labels = [
            'Шифр',
            'Название',
            'Автор',
            'Год издания',
            'Читальный зал'
        ]
        self.ui.books_table.setColumnCount(len(labels))
        self.ui.books_table.setHorizontalHeaderLabels(labels)
        self.ui.books_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.books_table.cellDoubleClicked.connect(self.change_cipher)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())