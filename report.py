from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('Times', 'Times.ttf'))


title_style = ParagraphStyle('Title', fontSize=14, fontName='Times', alignment=1, spaceAfter=10*mm)
info_style = ParagraphStyle('Info', fontSize=12, fontName='Times', spaceAfter=5*mm)
table_title_style = ParagraphStyle('Table title', fontSize=10, fontName='Times',
                                   spaceBefore=10*mm, spaceAfter=3*mm)
common_table_style = TableStyle([('FONT', (0, 0), (-1, -1), 'Times'),
                                 ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                 ('BOX', (0, 0), (-1, -1), 0.25, colors.black)])


class Report(SimpleDocTemplate):
    styles = {
        'Title': title_style,
        'Info': info_style,
        'Table title': table_title_style
    }

    def __init__(self, filename):
        super(Report, self).__init__(filename,
                                     pagesize=A4,
                                     leftMargin=30*mm,
                                     rightMargin=15*mm,
                                     topMargin=20*mm,
                                     bottomMargin=20*mm)
        self.elements = []

    def month_report_title(self, year, month):
        title_p = Paragraph('Отчет о работе библиотеки за {0:0>2}-{1}'.format(month, year), Report.styles['Title'])
        self.elements.append(title_p)

    def availability_report_title(self, query):
        title_p = Paragraph('Справка о наличии книг', Report.styles['Title'])
        query_p = Paragraph(query, Report.styles['Table title'])
        self.elements.append(title_p)
        self.elements.append(query_p)

    def available_books_table(self, rows):
        if rows:
            headers = [
                'Шифр',
                'Название',
                'Автор',
                'Год издания',
                'Читальный зал'
            ]
            data = [headers]
            data.extend(rows)
            table = Table(data)
            table.setStyle(common_table_style)
            self.elements.append(table)
        else:
            empty_p = Paragraph('По вашему запросу ничего не найдено', Report.styles['Info'])
            self.elements.append(empty_p)

    def readers_count_info(self, count, new):
        count_p = Paragraph(f'Количество читателей: {count}', Report.styles['Info'])
        new_p = Paragraph(f'Новых читателей: {new}', Report.styles['Info'])
        self.elements.append(count_p)
        self.elements.append(new_p)

    def books_table(self, rows):
        title = Paragraph('Какие книги и сколько раз брали:', Report.styles['Table title'])
        self.elements.append(title)

        headers = [
            'Шифр',
            'Название',
            'Автор',
            'Год издания',
            'Читальный зал',
            'Раз брали'
        ]
        data = [headers]
        data.extend(rows)
        table = Table(data)
        table.setStyle(common_table_style)
        self.elements.append(table)

    def readers_table(self, rows):
        title = Paragraph('Какие читатели не брали книг:', Report.styles['Table title'])
        self.elements.append(title)

        headers = [
            'Номер билета',
            'Фамилия',
            'Номер телефона',
            'Читальный зал'
        ]
        data = [headers]
        data.extend(rows)
        table = Table(data)
        table.setStyle(common_table_style)
        self.elements.append(table)

    def save(self):
        self.build(self.elements)


if __name__ == '__main__':
    report = Report('test.pdf')
    report.month_report_title(2021, 9)
    report.readers_count_info(6, 3)
    report.books_table([[123, 'Пупа', 'Лупа', 2012, '№1', 2]])
    report.readers_table([[1213, 'Алексеев', '89112463358', '№1']])
    report.save()
