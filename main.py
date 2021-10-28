import sys
import library_queries as lq
from login import LoginWindow
from main_form import Ui_MainWindow
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableWidgetItem, QHeaderView, QInputDialog,
                             QMessageBox, QMenu, QAction, QLineEdit)
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator, QIntValidator
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
        self.ui.phone_search_btn.clicked.connect(self.reader_phone_search)
        self.ui.add_reader_btn.clicked.connect(self.add_reader)
        self.init_room_combo_box()
        self.init_reader_room_combo_box()
        self.configure_readers_table()
        self.configure_books_table()
        self.configure_rooms_table()
        self.fill_rooms_table()
        self.set_validators()
        self.ui.tabWidget.setCurrentIndex(0)
        self.showMaximized()

    def get_connection(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.initializeUI()

    def set_validators(self):
        phone_validator = QRegExpValidator(QRegExp('89[0-9]{9}'))
        self.ui.phone_search_le.setValidator(phone_validator)
        self.ui.phone_le.setValidator(phone_validator)

        number_validator = QIntValidator(0, 2000000000)
        self.ui.card_number_le.setValidator(number_validator)
        self.ui.room_card_number_le.setValidator(number_validator)
        self.ui.cipher_le.setValidator(number_validator)

        surname_validator = QRegExpValidator(QRegExp('[А-ЯA-Z][А-Яа-яA-Za-z]{1,100}'))
        self.ui.surname_le.setValidator(surname_validator)

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

            title = self.ui.title_le.text().strip().capitalize()
            author = self.ui.author_le.text().strip().capitalize()
            room = self.ui.room_combo_box.currentText()
            if room == any_room_text:
                room = ''
            self.set_query_label(title, author, room)
            books = lq.filtered_book_search(self.cursor, title=title,
                                            author=author, room=room)
        self.fill_table_by_books(books)

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

    def fill_table_by_books(self, books):
        self.ui.books_table.clearContents()
        print(books[0][3])
        if type(books[0][3]) is not int:
            self.ui.books_table.setHorizontalHeaderItem(3,
                                                        QTableWidgetItem('Взята'))
        else:
            self.ui.books_table.setHorizontalHeaderItem(3,
                                                        QTableWidgetItem('Год издания'))
        self.ui.books_table.setRowCount(len(books))
        if books:
            for row in range(len(books)):
                for column in range(self.ui.books_table.columnCount()):
                        item = QTableWidgetItem(str(books[row][column]))
                        self.ui.books_table.setItem(row, column, item)

    def delete_book(self, row):
        cipher = self.ui.books_table.item(row, 0).text()
        readers = lq.get_reader_by_book(self.cursor, cipher)
        if readers:
            text = f'Книга находится у читателя. Фамилия: {readers[0][1]}. ' \
                   f'Телефон: {readers[0][2]}. ' \
                   f'Номер читательского билета: {readers[0][0]} ' \
                   f'Вы уверены, что хотите удалить книгу?'
            btn = QMessageBox.critical(self, 'Книга на руках!', text, QMessageBox.Cancel | QMessageBox.Yes)
            if btn == QMessageBox.Yes:
                lq.delete_book(self.cursor, cipher)
                self.ui.books_table.removeRow(row)
        else:
            btn = QMessageBox.question(self, 'Вы уверены?',
                                       'Вся информация о книг будет безвозвратно удалена.',
                                       QMessageBox.Yes | QMessageBox.No,
                                       defaultButton=QMessageBox.No)
            if btn == QMessageBox.Yes:
                lq.delete_book(self.cursor, cipher)
                self.ui.books_table.removeRow(row)

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
                self.fill_table_by_books(books)

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
            'Читальный зал',
        ]
        self.ui.books_table.setColumnCount(len(labels))
        self.ui.books_table.setHorizontalHeaderLabels(labels)
        self.ui.books_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.books_table.cellDoubleClicked.connect(self.change_cipher)

        self.ui.books_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.books_table.customContextMenuRequested.connect(self.table_context_menu)

    def table_context_menu(self, pos):
        row = self.ui.books_table.currentRow()
        if 0 <= row < self.ui.books_table.rowCount():
            context_menu = QMenu()
            change_cipher_act = QAction('Изменить шифр')
            change_cipher_act.triggered.connect(lambda: self.change_cipher(row, 0))
            delete_book_act = QAction('Удалить книгу')
            delete_book_act.triggered.connect(lambda: self.delete_book(row))

            context_menu.addAction(change_cipher_act)
            context_menu.addSeparator()
            context_menu.addAction(delete_book_act)

            context_menu.exec_(self.ui.books_table.viewport().mapToGlobal(pos))

    def init_reader_room_combo_box(self):
        rooms = lq.get_rooms(self.cursor)
        self.ui.reader_room_combo_box.addItem(any_room_text)
        for room in rooms:
            self.ui.reader_room_combo_box.addItem(room)

    def configure_readers_table(self):
        labels = [
            'Номер билета',
            'Фамилия',
            'Номер телефона',
            'Читальный зал'
        ]

        self.ui.readers_table.setColumnCount(len(labels))
        self.ui.readers_table.setRowCount(1)
        self.ui.readers_table.setHorizontalHeaderLabels(labels)
        self.ui.readers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def configure_rooms_table(self):
        labels = [
            'Читальный зал',
            'Свободных мест',
            'Вместительность'
        ]
        self.ui.rooms_table.setColumnCount(len(labels))
        self.ui.rooms_table.setHorizontalHeaderLabels(labels)
        self.ui.rooms_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def reader_phone_search(self):
        phone_number = self.ui.phone_search_le.text()
        if len(phone_number) == 11:
            reader = lq.get_reader_by_phone_number(self.cursor, phone_number)
            self.fill_readers_table(reader)
        else:
            QMessageBox.warning(self, 'Неправильно набран номер',
                                'Номер должен состоять из 11 цифр',
                                QMessageBox.Ok)

    def fill_readers_table(self, reader):
        self.ui.readers_table.clearContents()
        if reader:
            reader = reader[0]
            for column in range(len(reader)):
                item = QTableWidgetItem(str(reader[column]))
                self.ui.readers_table.setItem(0, column, item)

    def add_reader(self):
        surname = self.ui.surname_le.text()
        phone_number = self.ui.phone_le.text()
        card_number = self.ui.room_card_number_le.text()
        room_name = self.ui.reader_room_combo_box.currentText()
        if not surname:
            QMessageBox.warning(self, 'Заполните поле!',
                                'Поле "Фамилия" не может быть пустым!',
                                QMessageBox.Ok)
        elif not phone_number:
            QMessageBox.warning(self, 'Заполните поле!',
                                'Поле "Номер телефона" не может быть пустым!',
                                QMessageBox.Ok)
        elif not card_number:
            QMessageBox.warning(self, 'Заполните поле!',
                                'Поле "Номер читательского билета" не может быть пустым!',
                                QMessageBox.Ok)
        else:
            try:
                lq.add_reader(self.cursor, (surname, phone_number, card_number, room_name))
            except Error as err:
                if err.errno == errorcode.ER_DUP_ENTRY:
                    QMessageBox.critical(self, 'Попытка дублирования!',
                                         'Читатель с таким номером читательского билета'
                                         ' или телефона уже зарегистрирован!',
                                         QMessageBox.Ok)
                else:
                    QMessageBox.critical(self, 'Упс! Что-то пошло не так!',
                                         f'{str(err)}',
                                         QMessageBox.Ok)
            else:
                self.fill_rooms_table()

    def fill_rooms_table(self):
        readers_count = lq.readers_count(self.cursor)
        self.ui.info_text.setText(f'Количество читателей: {readers_count}')

        self.ui.rooms_table.clearContents()
        rows = lq.get_rooms_table(self.cursor)
        if rows:
            self.ui.rooms_table.setRowCount(len(rows))
            for row in range(len(rows)):
                for column in range(len(rows[0])):
                    self.ui.rooms_table.setItem(row, column,
                                                QTableWidgetItem(str(rows[row][column])))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())