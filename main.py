import sys
import os
import library_queries as lq
from get_date import GetDateForm
from login import LoginWindow
from add_book_copies import AddBookCopiesForm
from main_form import Ui_MainWindow
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableWidgetItem, QHeaderView, QInputDialog,
                             QMessageBox, QMenu, QAction, QFileDialog)
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator, QIntValidator
from report import Report
from mysql.connector import Error, errorcode


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.login()

    def login(self):
        self.login_form = LoginWindow()
        self.login_form.connect.signal.connect(self.get_connection)

    def initializeUI(self, role):
        if role == '`librarian`@`%`':
            self.ui.add_book_widget.hide()
            self.ui.verticalLayout.removeItem(self.ui.verticalLayout.itemAt(3))
        self.set_validators()
        self.initialize_book_page()

        self.showMaximized()

    def get_connection(self, connection, role):
        print(role)
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.initializeUI(role)

    def create_menu(self):
        menu_bar = self.menuBar()
        reports_menu = menu_bar.addMenu('Отчеты')

        month_report_act = QAction('Отчет за месяц', self)
        month_report_act.setStatusTip('Отчет о работе библиотеки за текущий месяц')
        month_report_act.triggered.connect(self.get_report_date)

        reports_menu.addAction(month_report_act)

    # Pages initialing
    def initialize_book_page(self):
        self.ui.availability_report_btn.clicked.connect(self.availability_note)
        self.ui.search_book_cipher_le.textChanged.connect(self.control_filters)
        self.ui.book_search_btn.clicked.connect(self.book_search)
        self.ui.add_book_btn.clicked.connect(self.add_book)

        self.init_room_combo_box(self.ui.search_book_room_combo_box)
        self.configure_books_table()

    # Common functions
    def set_validators(self):
        # Validators
        phone_validator = QRegExpValidator(QRegExp('89[0-9]{9}'))
        number_validator = QIntValidator(0, 999999999)
        surname_validator = QRegExpValidator(QRegExp('[А-ЯA-Z][А-Яа-яA-Za-z]{1,100}'))

        # Book page
        self.ui.search_book_cipher_le.setValidator(number_validator)
        self.ui.add_book_cipher_le.setValidator(number_validator)

        # Book copy page

        # Reader page

    def control_filters(self):
        if self.ui.search_book_cipher_le.text() == '':
            self.ui.search_book_author_le.setEnabled(True)
            self.ui.search_book_title_le.setEnabled(True)
        else:
            self.ui.search_book_author_le.setEnabled(False)
            self.ui.search_book_title_le.setEnabled(False)

    def init_room_combo_box(self, combo_box):
        rooms = lq.get_rooms(self.cursor)
        combo_box.addItem(lq.any_room_text)
        for room in rooms:
            combo_box.addItem(room)

    # Book actions
    def book_search(self):
        books = self.available_book_search_query()
        self.fill_books_table(books)

    def add_book(self):
        cipher, title, author = self.get_book_add_input()
        if cipher == '' or title == '' or author == '':
            QMessageBox.warning(self, 'Неправильный ввод',
                                'Поля шифр, название и автор не должны быть пустыми!',
                                QMessageBox.Ok)
        elif lq.cipher_exists(self.cursor, cipher):
            QMessageBox.critical(self, 'Попытка дублирования',
                                 'Книга с таким шифром уже существует!',
                                 QMessageBox.Ok)
        else:
            lq.start_transaction(self.cursor)
            try:
                lq.add_book(self.cursor, cipher, title, author)
            except Error as err:
                lq.rollback(self.cursor)
                QMessageBox.critical(self, 'Упс! Что-то пошло не так',
                                     err.msg,
                                     QMessageBox.Ok)
            else:
                self.add_copies_form = AddBookCopiesForm(self.cursor)
                self.add_copies_form.ui.cipher_le.setText(cipher)
                self.add_copies_form.ui.cipher_le.setEnabled(False)

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

    def get_book_search_query(self):
        cipher = self.ui.search_book_cipher_le.text().strip()
        title = self.ui.search_book_title_le.text().strip()
        author = self.ui.search_book_author_le.text().strip()
        room = self.ui.search_book_room_combo_box.currentText()
        return cipher, title, author, room

    def get_book_add_input(self):
        cipher = self.ui.add_book_cipher_le.text().strip()
        title = self.ui.add_book_title_le.text().strip()
        author = self.ui.add_book_author_le.text().strip()
        return cipher, title, author

    def available_book_search_query(self):
        cipher, title, author, room = self.get_book_search_query()
        label_text = self.make_query_label(cipher, title, author, room)
        self.set_query_label(label_text)
        return lq.filtered_available_book_search(self.cursor, cipher=cipher, title=title,
                                       author=author, room=room)

    def set_query_label(self, label_text):
        self.ui.query_label.setText(label_text)

    def make_query_label(self, cipher, title, author, room):
        if cipher != '':
            return f'Шифр: {cipher}, Читальный зал: {room}'
        elif title == '' and author == '' and room == lq.any_room_text:
            return 'Все книги'
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
            return label_text

    # Table filling
    def fill_books_table(self, books):
        self.ui.books_table.clearContents()
        self.ui.books_table.setRowCount(0)
        if books:
            self.ui.books_table.setRowCount(len(books))
            for row in range(len(books)):
                for column in range(self.ui.books_table.columnCount()):
                    item = QTableWidgetItem(str(books[row][column]))
                    self.ui.books_table.setItem(row, column, item)

    def fill_readers_table(self, reader):
        self.ui.readers_table.clearContents()
        if reader:
            reader = reader[0]
            for column in range(len(reader)):
                item = QTableWidgetItem(str(reader[column]))
                self.ui.readers_table.setItem(0, column, item)

    def fill_rooms_table(self):
        readers_count = lq.current_readers_count(self.cursor)
        self.ui.info_text.setText(f'Количество читателей: {readers_count}')

        self.ui.rooms_table.clearContents()
        rows = lq.get_rooms_table(self.cursor)
        if rows:
            self.ui.rooms_table.setRowCount(len(rows))
            for row in range(len(rows)):
                for column in range(len(rows[0])):
                    self.ui.rooms_table.setItem(row, column,
                                                QTableWidgetItem(str(rows[row][column])))

    # Tables initializing
    def configure_books_table(self):
        labels = [
            'Шифр',
            'Название',
            'Автор',
            'В наличии'
        ]
        self.ui.books_table.setColumnCount(len(labels))
        self.ui.books_table.setHorizontalHeaderLabels(labels)
        self.ui.books_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.books_table.cellDoubleClicked.connect(self.change_cipher)

        self.ui.books_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.books_table.customContextMenuRequested.connect(self.books_table_context_menu)

    def configure_readers_table(self):
        labels = [
            'Номер билета',
            'Фамилия',
            'Номер телефона',
            'Читальный зал'
        ]

        self.ui.readers_table.setColumnCount(len(labels))
        self.ui.readers_table.setRowCount(1)
        self.ui.readers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.readers_table.setHorizontalHeaderLabels(labels)

    def configure_rooms_table(self):
        labels = [
            'Читальный зал',
            'Вместительность',
            'Читателей'
        ]
        self.ui.rooms_table.setColumnCount(len(labels))
        self.ui.rooms_table.setHorizontalHeaderLabels(labels)
        self.ui.rooms_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def books_table_context_menu(self, pos):
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

    # Reports
    def get_report_date(self):
        cur_year, cur_month = lq.get_current_year_and_month(self.cursor)
        first_year = lq.get_first_year(self.cursor)
        self.get_date_form = GetDateForm()
        self.get_date_form.signal.signal.connect(self.month_report)
        self.get_date_form.init_input_forms(first_year, cur_year, cur_month)
        self.get_date_form.show()

    def availability_note(self):
        books = self.available_book_search_query()
        filename, ok = QFileDialog.getSaveFileName(self, 'Save report',
                                                   os.getcwd(), 'PDF (*.pdf)')
        if ok:
            cipher, title, author, room = self.get_book_search_query()
            query = self.make_query_label(cipher, title, author, room)
            availability_note = Report(filename)
            availability_note.availability_report_title(query)
            availability_note.available_books_table(books)
            availability_note.save()

    def month_report(self, year, month):
        readers_count = lq.readers_count(self.cursor, year, month)
        new_readers_count = lq.new_readers_for_month_count(self.cursor, year, month)
        taken_books = lq.books_taken_for_month(self.cursor, year, month)
        inactive_readers = lq.inactive_readers_for_month(self.cursor, year, month)
        print(readers_count)
        print(new_readers_count)
        for book in taken_books:
            print(book)
        for reader in inactive_readers:
            print(reader)
        filename, ok = QFileDialog.getSaveFileName(self, 'Save report',
                                                   os.getcwd(), 'PDF (*.pdf)')
        if ok:
            month_report = Report(filename)
            month_report.month_report_title(year, month)
            month_report.readers_count_info(readers_count, new_readers_count)
            month_report.books_table(taken_books)
            month_report.readers_table(inactive_readers)
            month_report.save()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
