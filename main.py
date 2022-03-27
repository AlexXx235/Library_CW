import sys
import os
import library_queries as lq
from get_date import GetDateForm
from login import LoginWindow
from add_book_copies import AddBookCopiesForm
from forms.main_form import Ui_MainWindow
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableWidgetItem, QHeaderView, QInputDialog,
                             QMessageBox, QMenu, QAction, QFileDialog)
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator, QIntValidator, QColor, QBrush, QIcon
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

    def initializeUI(self):
        self.setWindowIcon(QIcon('images/icons/book.png'))
        self.set_validators()
        self.initialize_book_page()
        self.initialize_copies_page()
        self.initialize_readers_page()
        self.create_menu()

        self.showMaximized()

    def get_connection(self, connection, role):
        self.role = role
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.initializeUI()

    def create_menu(self):
        menu_bar = self.menuBar()
        reports_menu = menu_bar.addMenu('Отчеты')

        month_report_act = QAction('Отчет за месяц', self)
        month_report_act.setStatusTip('Отчет о работе библиотеки за текущий месяц')
        month_report_act.triggered.connect(self.get_report_date)

        reports_menu.addAction(month_report_act)

    # Pages initialing
    def initialize_book_page(self):
        if self.role == '`librarian`@`%`':
            self.ui.add_book_widget.hide()
            self.ui.books_page_menu_v_box.removeItem(self.ui.books_page_menu_v_box.itemAt(3))
        self.ui.availability_report_btn.clicked.connect(self.availability_note)
        self.ui.search_book_cipher_le.textChanged.connect(self.control_filters)
        self.ui.book_search_btn.clicked.connect(self.book_search)
        self.ui.add_book_btn.clicked.connect(self.add_book)

        self.init_room_combo_box(self.ui.search_book_room_combo_box)
        self.configure_books_table()

    def initialize_copies_page(self):
        if self.role == '`librarian`@`%`':
            self.ui.add_copies_widget.hide()
            self.ui.copies_page_menu_v_box.removeItem(self.ui.copies_page_menu_v_box.itemAt(3))
        self.ui.search_readers_copies_btn.clicked.connect(self.book_copies_by_reader_search)
        self.ui.add_copies_btn.clicked.connect(self.add_book_copies)
        self.ui.search_copies_btn.clicked.connect(self.book_copies_search)
        self.init_room_combo_box(self.ui.search_copies_room_comb_box)
        self.configure_copies_table()
        self.configure_readers_copies_table()

    def initialize_readers_page(self):
        self.ui.add_reader_btn.clicked.connect(self.add_reader)
        self.ui.search_readers_btn.clicked.connect(self.readers_search)
        self.ui.reader_by_copy_search_btn.clicked.connect(self.reader_search_by_copy)
        self.init_room_combo_box(self.ui.reader_room_combo_box)
        self.configure_rooms_table()
        self.configure_readers_table()
        self.fill_rooms_table()

    # Common functions
    def set_validators(self):
        # Validators
        phone_validator = QRegExpValidator(QRegExp('89[0-9]{9}'))
        number_validator = QIntValidator(0, 999999999)
        surname_validator = QRegExpValidator(QRegExp('[А-Яа-яA-Za-z]{1,128}'))

        # Book page
        self.ui.search_book_cipher_le.setValidator(number_validator)
        self.ui.add_book_cipher_le.setValidator(number_validator)

        # Book copy page
        current_year = int(lq.get_current_year(self.cursor))
        self.ui.add_copies_cipher_le.setValidator(number_validator)
        self.ui.search_copies_cipher_le.setValidator(number_validator)
        self.ui.search_readers_copies_card_number_le.setValidator(number_validator)
        self.ui.add_copies_count_sb.setMinimum(1)
        self.ui.add_copies_count_sb.setMaximum(25)
        self.ui.search_copies_from_year_sb.setMinimum(0)
        self.ui.search_copies_from_year_sb.setMaximum(current_year)
        self.ui.search_copies_till_year_sb.setMinimum(0)
        self.ui.search_copies_till_year_sb.setMaximum(current_year)
        self.ui.search_copies_till_year_sb.setValue(current_year)

        # Reader page
        self.ui.reader_card_number_le.setValidator(number_validator)
        self.ui.reader_copy_inv_number_le.setValidator(number_validator)
        self.ui.reader_phone_number_le.setValidator(phone_validator)
        self.ui.reader_name_le.setValidator(surname_validator)
        self.ui.reader_surname_le.setValidator(surname_validator)

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

    def book_copies_search(self):
        cipher, year_from, year_till, room_name = self.get_book_copies_search_query()
        self.set_readers_copies_search_query(cipher, year_from, year_till, room_name)
        copies = lq.filtered_book_copy_search(self.cursor, cipher, year_from, year_till, room_name)
        self.fill_book_copies_table(copies)

    def book_copies_by_reader_search(self):
        card_number = self.ui.search_readers_copies_card_number_le.text()
        self.ui.readers_copies_table_query.setText(f'Книги читателя с номером читательского билета: {card_number}')
        if card_number == '':
            QMessageBox.critical(self, 'Неправильный ввод',
                                 'Заполните поле "Номер билета".',
                                 QMessageBox.Ok)
        else:
            copies = lq.get_book_copies_by_reader(self.cursor, card_number)
            self.fill_readers_copies_table(copies)

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
                self.add_copies_form.add_row_to_table()

    def add_book_copies(self):
        cipher = self.ui.add_copies_cipher_le.text()
        if cipher != '':
            if lq.cipher_exists(self.cursor, cipher):
                count = self.ui.add_copies_count_sb.value()
                self.add_copies_form = AddBookCopiesForm(self.cursor)
                self.add_copies_form.ui.cipher_le.setText(cipher)
                self.add_copies_form.set_row_count(count)
            else:
                QMessageBox.critical(self, 'Неверный шифр',
                                     'Книги с таким шифром не существует.',
                                     QMessageBox.Ok)

    def delete_book(self):
        QMessageBox.information(self, 'Отказано',
                                'Книга будет удалена автоматически, когда будут'
                                ' удалены все ее экземпляры.', QMessageBox.Ok)

    def delete_book_copy(self, row):
        inv_number = self.ui.copies_table.item(row, 1).text()
        if lq.copy_loaned(self.cursor, inv_number):
            QMessageBox.warning(self, 'Книга на руках',
                                'Вы не можете удалить книгу, пока она'
                                ' закреплена за читателем.', QMessageBox.Ok)
        elif lq.last_copy(self.cursor, inv_number):
            answer = QMessageBox.question(self, 'Последняя копия',
                                          'Это последний экземпляр книги. Продолжить?',
                                          QMessageBox.Ok | QMessageBox.Cancel)
            if answer == QMessageBox.Ok:
                lq.start_transaction(self.cursor)
                try:
                    cipher = lq.get_copy_cipher(self.cursor, inv_number)
                    lq.delete_book_copy(self.cursor, inv_number)
                    lq.delete_book(self.cursor, cipher)
                    self.ui.copies_table.removeRow(row)
                except Error as err:
                    lq.rollback(self.cursor)
                    QMessageBox.critical(self, 'Упс! Что-то пошло не так',
                                         f'{err.msg}', QMessageBox.Ok)
                else:
                    lq.commit(self.cursor)
        else:
            answer = QMessageBox.question(self, 'Подтверждение',
                                          'Информация о книге будет безвозвратно утеряна. Продолжить?',
                                           QMessageBox.Ok | QMessageBox.Cancel)
            if answer == QMessageBox.Ok:
                try:
                    lq.delete_book_copy(self.cursor, inv_number)
                    self.ui.copies_table.removeRow(row)
                except Error as err:
                    QMessageBox.critical(self, 'Упс! Что-то пошло не так',
                                         f'{err.msg}', QMessageBox.Ok)

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

    def loan_book(self, row):
        inv_number = self.ui.copies_table.item(row, 1).text()
        if lq.copy_loaned(self.cursor, inv_number):
            QMessageBox.critical(self, 'Книга на руках',
                                 'Данный экземпляр уже закреплен за пользователем',
                                 QMessageBox.Ok)
            return
        card_number, ok = QInputDialog.getText(self, 'Укажите читателя',
                                               'Введите номер читательского билета: ')
        if ok and card_number != '':
            if lq.reader_exists(self.cursor, card_number):
                try:
                    lq.loan_book(self.cursor, card_number, inv_number)
                except Error as err:
                    QMessageBox.critical(self, 'Упс! Что-то пошло не так',
                                         f'{err.msg}', QMessageBox.Ok)
                else:
                    loaned_back_color = QColor()
                    loaned_back_color.setRgb(234, 234, 234)
                    loaned_back_brush = QBrush(loaned_back_color)
                    for column in range(self.ui.copies_table.columnCount()):
                        self.ui.copies_table.item(row, column).setBackground(loaned_back_brush)
            else:
                QMessageBox.critical(self, 'Ошибка',
                                     'Читателя с таким номером билета не существует.',
                                     QMessageBox.Ok)

    def return_book(self, row):
        inv_number = self.ui.readers_copies_table.item(row, 3).text()
        lq.return_book(self.cursor, inv_number)
        self.ui.readers_copies_table.removeRow(row)

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

    def get_book_copies_search_query(self):
        cipher = self.ui.search_copies_cipher_le.text()
        year_from = self.ui.search_copies_from_year_sb.value()
        year_till = self.ui.search_copies_till_year_sb.value()
        room_name = self.ui.search_copies_room_comb_box.currentText()
        return cipher, year_from, year_till, room_name

    def available_book_search_query(self):
        cipher, title, author, room = self.get_book_search_query()
        label_text = self.make_query_label(cipher, title, author, room)
        self.set_query_label(label_text)
        return lq.filtered_available_book_search(self.cursor, cipher=cipher, title=title,
                                       author=author, room=room)

    def set_readers_copies_search_query(self, cipher, year_from, year_till, room_name):
        query = 'Экземпляры по запросу: '
        if cipher != '':
            query += f'Шифр = {cipher},'
        query += f' Год издания {year_from} - {year_till},'
        query += f' Читальный зал: {room_name}'
        self.ui.copies_table_query.setText(query)

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

    # Reader actions
    def get_reader_query(self):
        card_number = self.ui.reader_card_number_le.text()
        name = self.ui.reader_name_le.text()
        surname = self.ui.reader_surname_le.text()
        phone_number = self.ui.reader_phone_number_le.text()
        room_name = self.ui.reader_room_combo_box.currentText()
        return card_number, name, surname, phone_number, room_name

    def readers_search(self):
        card_number, name, surname, phone_number, room_name = self.get_reader_query()
        readers = lq.filtered_readers_search(self.cursor, card_number, name, surname, phone_number, room_name)
        self.fill_readers_table(readers)
        self.set_readers_query_label()

    def set_readers_query_label(self):
        card_number, name, surname, phone_number, room_name = self.get_reader_query()
        if card_number + name + surname + phone_number + room_name == lq.any_room_text:
            self.ui.readers_table_query.setText('Все читатели')
        else:
            query = 'Читатели по запросу:'
            if card_number != '':
                query += f' Номер билета: {card_number},'
            if name != '':
                query += f' Имя: {name},'
            if surname != '':
                query += f' Фамилия: {surname},'
            if phone_number != '':
                query += f' Номер телефона: {phone_number},'
            query += f' Читальный зал: {room_name}'
            self.ui.readers_table_query.setText(query)

    def add_reader(self):
        card_number, name, surname, phone_number, room_name = self.get_reader_query()
        if card_number == '' or name =='' or surname == '' or phone_number == '':
            QMessageBox.warning(self, 'Некорректный ввод',
                                      'Необходимо заполнить все поля',
                                      QMessageBox.Ok)
        if room_name == lq.any_room_text:
            QMessageBox.critical(self, 'Выберите зал',
                                 'Для добавления пользователя нужно выбрать конкретный зал',
                                 QMessageBox.Ok)
        elif lq.room_not_full(self.cursor, room_name):
            lq.add_reader(self.cursor, card_number, name, surname, phone_number, room_name)
            self.fill_rooms_table()
        else:
            QMessageBox.critical(self, 'Нет места',
                                 'Выбранный читальный зал полон.',
                                 QMessageBox.Ok)

    def delete_reader(self, row):
        card_number = self.ui.readers_table.item(row, 0).text()
        lq.delete_reader(self.cursor, card_number)
        self.ui.readers_table.removeRow(row)
        self.fill_rooms_table()

    def reader_search_by_copy(self):
        inv_number = self.ui.reader_copy_inv_number_le.text()
        if inv_number != '':
            reader = lq.get_reader_by_copy_number(self.cursor, inv_number)
            self.fill_readers_table(reader)
            self.ui.readers_table_query.setText(f'Читатель за которым закреплен экземпляр: {inv_number}')

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

    def fill_readers_table(self, readers):
        self.ui.readers_table.clearContents()
        self.ui.readers_table.setRowCount(1)
        if readers:
            rows_count = len(readers)
            self.ui.readers_table.setRowCount(rows_count)
            column_count = self.ui.readers_table.columnCount()
            for row in range(rows_count):
                for column in range(column_count):
                    item = QTableWidgetItem(str(readers[row][column]))
                    self.ui.readers_table.setItem(row, column, item)

    def fill_rooms_table(self):
        readers_count = lq.current_readers_count(self.cursor)
        self.ui.rooms_table_info.setText(f'Всего читателей: {readers_count}')

        self.ui.readers_statistics_table.clearContents()
        rows = lq.get_rooms_table(self.cursor)
        rows_count = len(rows)
        columns_count = self.ui.readers_statistics_table.columnCount()
        self.ui.readers_statistics_table.setRowCount(rows_count)
        for row in range(rows_count):
            for column in range(columns_count):
                item = QTableWidgetItem(str(rows[row][column]))
                self.ui.readers_statistics_table.setItem(row, column, item)

    def fill_book_copies_table(self, copies):
        loaned_back_color = QColor()
        loaned_back_color.setRgb(234, 234, 234)
        loaned_back_brush = QBrush(loaned_back_color)
        row_count = len(copies)
        column_count = self.ui.copies_table.columnCount()
        self.ui.copies_table.clearContents()
        self.ui.copies_table.setRowCount(row_count)
        for row in range(row_count):
            for column in range(column_count):
                item = QTableWidgetItem(str(copies[row][column]))
                if copies[row][-1]:
                    item.setBackground(loaned_back_brush)
                self.ui.copies_table.setItem(row, column, item)

    def fill_readers_copies_table(self, copies):
        row_count = len(copies)
        column_count = self.ui.readers_copies_table.columnCount()
        self.ui.readers_copies_table.clearContents()
        self.ui.readers_copies_table.setRowCount(row_count)
        for row in range(row_count):
            for column in range(column_count):
                item = QTableWidgetItem(str(copies[row][column]))
                self.ui.readers_copies_table.setItem(row, column, item)

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

    def configure_copies_table(self):
        labels = [
            'Шифр',
            'Инв. Номер',
            'Год издания',
            'Читальный зал'
        ]
        self.ui.copies_table.setColumnCount(len(labels))
        self.ui.copies_table.setHorizontalHeaderLabels(labels)
        self.ui.copies_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.copies_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.copies_table.customContextMenuRequested.connect(self.copies_table_context_menu)

    def configure_readers_copies_table(self):
        labels = [
            'Шифр',
            'Название',
            'Автор',
            'Инв. Номер',
            'Год издания',
            'Читальный зал',
            'Дата взятия'
        ]
        self.ui.readers_copies_table.setColumnCount(len(labels))
        self.ui.readers_copies_table.setHorizontalHeaderLabels(labels)
        self.ui.readers_copies_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.readers_copies_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.readers_copies_table.customContextMenuRequested.connect(self.readers_copies_table_context_menu)

    def configure_readers_table(self):
        labels = [
            'Номер билета',
            'ФИО',
            'Номер телефона',
            'Читальный зал',
            'Дата регистрации'
        ]
        self.ui.readers_table.setColumnCount(len(labels))
        self.ui.readers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.readers_table.setHorizontalHeaderLabels(labels)
        self.ui.readers_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.readers_table.customContextMenuRequested.connect(self.readers_table_context_menu)

    def configure_rooms_table(self):
        labels = [
            'Читальный зал',
            'Вместительность',
            'Читателей'
        ]
        self.ui.readers_statistics_table.setColumnCount(len(labels))
        self.ui.readers_statistics_table.setHorizontalHeaderLabels(labels)
        self.ui.readers_statistics_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def books_table_context_menu(self, pos):
        row = self.ui.books_table.currentRow()
        if 0 <= row < self.ui.books_table.rowCount():
            context_menu = QMenu()
            change_cipher_act = QAction('Изменить шифр')
            change_cipher_act.triggered.connect(lambda: self.change_cipher(row, 0))
            delete_book_act = QAction('Удалить книгу')
            delete_book_act.triggered.connect(self.delete_book)

            context_menu.addAction(change_cipher_act)
            context_menu.addSeparator()
            context_menu.addAction(delete_book_act)

            context_menu.exec_(self.ui.books_table.viewport().mapToGlobal(pos))

    def copies_table_context_menu(self, pos):
        row = self.ui.copies_table.currentRow()
        if 0 <= row < self.ui.copies_table.rowCount():
            context_menu = QMenu()
            loan_book_act = QAction('Выдать книгу')
            loan_book_act.triggered.connect(lambda: self.loan_book(row))

            delete_book_copy_act = QAction('Списать книгу')
            delete_book_copy_act.triggered.connect(lambda: self.delete_book_copy(row))

            if self.role == '`admin_role`@`%`':
                context_menu.addAction(loan_book_act)
            context_menu.addAction(delete_book_copy_act)

            context_menu.exec_(self.ui.copies_table.viewport().mapToGlobal(pos))

    def readers_copies_table_context_menu(self, pos):
        row = self.ui.readers_copies_table.currentRow()
        if 0 <= row < self.ui.readers_copies_table.rowCount():
            context_menu = QMenu()
            return_book_act = QAction('Вернуть книгу')
            return_book_act.triggered.connect(lambda: self.return_book(row))

            if self.role == '`admin_role`@`%`':
                context_menu.addAction(return_book_act)

            context_menu.exec_(self.ui.readers_copies_table.viewport().mapToGlobal(pos))

    def readers_table_context_menu(self, pos):
        row = self.ui.readers_table.currentRow()
        if 0 <= row < self.ui.readers_table.rowCount():
            context_menu = QMenu()
            delete_reader_act = QAction('Удалить читателя')
            delete_reader_act.triggered.connect(lambda: self.delete_reader(row))

            if self.role == '`admin_role`@`%`':
                context_menu.addAction(delete_reader_act)

            context_menu.exec_(self.ui.readers_table.viewport().mapToGlobal(pos))

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
            availability_note.set_timestamp(lq.get_timestamp(self.cursor))
            availability_note.save()

    def month_report(self, year, month):
        readers_count = lq.readers_count(self.cursor, year, month)
        new_readers_count = lq.new_readers_for_month_count(self.cursor, year, month)
        taken_books = lq.books_taken_for_month(self.cursor, year, month)
        inactive_readers = lq.inactive_readers_for_month(self.cursor, year, month)
        filename, ok = QFileDialog.getSaveFileName(self, 'Save report',
                                                   os.getcwd(), 'PDF (*.pdf)')
        if ok:
            month_report = Report(filename)
            month_report.month_report_title(year, month)
            month_report.readers_count_info(readers_count, new_readers_count)
            month_report.books_table(taken_books)
            month_report.readers_table(inactive_readers)
            month_report.set_timestamp(lq.get_timestamp(self.cursor))
            month_report.save()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
