import sys
from add_book_copies import AddBookCopiesForm
from PyQt5.QtWidgets import QApplication


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AddBookCopiesForm()
    sys.exit(app.exec_())