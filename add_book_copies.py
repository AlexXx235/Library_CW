import library_queries as lq
from PyQt5.QtWidgets import (QWidget, QHeaderView, QComboBox, QLineEdit, QSpinBox,
                             QMessageBox)
from PyQt5.QtGui import QIntValidator
from mysql.connector import Error, errorcode
from forms.add_book_copies_form import Ui_add_book_copies_form


class AddBookCopiesForm(QWidget):
    def __init__(self, cursor):
        super(AddBookCopiesForm, self).__init__()
        self.ui = Ui_add_book_copies_form()
        self.ui.setupUi(self)
        self.cursor = cursor
        self.initializeUI()

    def initializeUI(self):
        self.rooms = lq.get_rooms(self.cursor)
        self.current_year = lq.get_current_year(self.cursor)
        self.configure_input_form()
        self.configure_copies_table()
        self.ui.add_btn.clicked.connect(self.add_copies)
        self.show()

    def configure_input_form(self):
        self.ui.cipher_le.setValidator(QIntValidator(0, 999999999))
        self.ui.count_sb.lineEdit().setEnabled(False)
        self.ui.count_sb.setMinimum(1)
        self.ui.count_sb.setMaximum(25)
        self.ui.count_sb.valueChanged.connect(self.valueChanged_slot)

    def configure_copies_table(self):
        labels = [
            'Инв. номер',
            'Год издания',
            'Читальный зал'
        ]
        self.ui.copies_table.setColumnCount(len(labels))
        self.ui.copies_table.setHorizontalHeaderLabels(labels)
        self.ui.copies_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def valueChanged_slot(self):
        value = self.ui.count_sb.value()
        rows_count = self.ui.copies_table.rowCount()
        print(value, rows_count)
        delta = abs(value - rows_count)
        if value > rows_count:
            for _ in range(delta):
                self.add_row_to_table()
        elif value < rows_count:
            for _ in range(delta):
                self.ui.copies_table.removeRow(value)

    def fill_row(self, row):
        combo_box = QComboBox()
        combo_box.addItems(self.rooms)

        inv_number_le = QLineEdit()
        inv_number_le.setFrame(False)
        inv_number_le.setValidator(QIntValidator(0, 999999999))

        release_year_sb = QSpinBox()
        release_year_sb.setFrame(False)
        release_year_sb.setRange(0, int(self.current_year))
        release_year_sb.setValue(int(self.current_year))

        self.ui.copies_table.setCellWidget(row, 0, inv_number_le)
        self.ui.copies_table.setCellWidget(row, 1, release_year_sb)
        self.ui.copies_table.setCellWidget(row, 2, combo_box)

    def add_row_to_table(self):
        index = self.ui.copies_table.rowCount()
        self.ui.copies_table.insertRow(index)
        self.fill_row(index)

    def set_row_count(self, count):
        self.ui.count_sb.setValue(count)

    def add_copies(self):
        cipher = self.ui.cipher_le.text()
        if not lq.cipher_exists(self.cursor, cipher):
            QMessageBox.critical(self, 'Неверный шифр',
                                 'Книги с таким шифром не существует!',
                                 QMessageBox.Ok)
            return
        count = self.ui.copies_table.rowCount()
        for i in range(count):
            inv_number = self.ui.copies_table.cellWidget(i, 0).text()
            release_year = self.ui.copies_table.cellWidget(i, 1).value()
            room_name = self.ui.copies_table.cellWidget(i, 2).currentText()
            if inv_number == '':
                lq.rollback(self.cursor)
                QMessageBox.critical(self, 'Неверный ввод',
                                     'Инвентаризационный номер не может быть пустым!',
                                     QMessageBox.Ok)
                return
            else:
                try:
                    lq.add_book_copy(self.cursor, inv_number, cipher, room_name, release_year)
                except Error as err:
                    lq.rollback(self.cursor)
                    if err.errno == errorcode.ER_DUP_ENTRY:
                        QMessageBox.critical(self, 'Попытка дублирования',
                                             'Книга с таким инвентаризационным номером уже существует!',
                                             QMessageBox.Ok)
                    elif err.errno == errorcode.ER_NO_REFERENCED_ROW or err.errno == errorcode.ER_NO_REFERENCED_ROW_2:
                        QMessageBox.critical(self, 'Неверный шифр',
                                             'Книги с таким шифром не существует!',
                                             QMessageBox.Ok)
                    else:
                        QMessageBox.critical(self, 'Упс! Что-то пошло не так',
                                             err.msg,
                                             QMessageBox.Ok)
                    return
        lq.commit(self.cursor)
        self.close()
