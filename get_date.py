from get_date_form import Ui_get_date_form
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QObject, pyqtSignal


months = {
    'Январь': '01',
    'Февраль': '02',
    'Март': '03',
    'Апрель': '04',
    'Май': '05',
    'Июнь': '06',
    'Июль': '07',
    'Август': '08',
    'Сентябрь': '09',
    'Октябрь': '10',
    'Ноябрь': '11',
    'Декабрь': '12',
}


class Signal(QObject):
    signal = pyqtSignal(int, int)


class GetDateForm(QWidget):
    def __init__(self):
        super(GetDateForm, self).__init__()
        self.ui = Ui_get_date_form()
        self.ui.setupUi(self)
        self.ui.create_report_btn.clicked.connect(self.get_date)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)
        self.signal = Signal()

    def init_input_forms(self, first_year, current_year, current_month):
        self.ui.month_combo_box.addItems(months)
        self.ui.month_combo_box.setCurrentIndex(current_month - 1)

        self.ui.year_spin_box.setMinimum(first_year)
        self.ui.year_spin_box.setMaximum(current_year)
        self.ui.year_spin_box.setValue(current_year)

    def get_date(self):
        year = self.ui.year_spin_box.value()
        month = int(months[self.ui.month_combo_box.currentText()])
        self.hide()
        self.signal.signal.emit(year, month)
        self.close()