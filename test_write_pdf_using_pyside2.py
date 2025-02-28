from PySide2.QtWidgets import QPushButton, QLineEdit, QApplication, QFormLayout, QWidget, QTextEdit, QMessageBox, QSpinBox, QFileDialog
from PySide2.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot


from reportlab.pdfgen.canvas import Canvas

import os, csv

import textwrap
from datetime import datetime

from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    """
    error = Signal(str)
    finished = Signal()


class Generator(QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handle worker thread setup, signals
    and wrap-up.

    :param data: The data to add to the PDF for generating.
    """

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            filename, _ = os.path.splitext(self.data['sourcefile'])
            folder = os.path.dirname(self.data['sourcefile'])

            template = PdfReader("template.pdf", decompress=False).pages[0]
            template_obj = pagexobj(template)

            with open(self.data['sourcefile'], 'r', newline='') as f:
                reader = csv.DictReader(f)

                for n, row in enumerate(reader, 1):
                    fn = f'{filename}-{n}.pdf'
                    outfile = os.path.join(folder, fn)
                    canvas = Canvas(outfile)

                    xobj_name = makerl(canvas, template_obj)
                    canvas.doForm(xobj_name)

                    ystart = 443

                    # Prepared by
                    canvas.drawString(170, ystart, row.get('name', ''))

                    # Date: Todays date
                    today = datetime.today()
                    canvas.drawString(410, ystart, today.strftime('%F'))

                    # Device/Program Type
                    canvas.drawString(230, ystart-28, row.get('program_type', ''))

                    # Product code
                    canvas.drawString(175, ystart-(2*28), row.get('product_code', ''))

                    # Customer
                    canvas.drawString(315, ystart-(2*28), row.get('customer', ''))

                    # Vendor
                    canvas.drawString(145, ystart-(3*28), row.get('vendor', ''))

                    ystart = 250

                    # Program Language
                    canvas.drawString(210, ystart, "Python")

                    canvas.drawString(430, ystart, row.get('n_errors', ''))

                    comments = row.get('comments', '').replace('\n', ' ')
                    if comments:
                        lines = textwrap.wrap(comments, width=65) # 45
                        first_line = lines[0]
                        remainder = ' '.join(lines[1:])

                        lines = textwrap.wrap(remainder, 75) # 55
                        lines = lines[:4]  # max lines, not including the first.

                        canvas.drawString(155, 223, first_line)
                        for n, l in enumerate(lines, 1):
                            canvas.drawString(80, 223 - (n*28), l)

                    canvas.save()

        except Exception as e:

            self.signals.error.emit(str(e))
            return

        self.signals.finished.emit()


class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.threadpool = QThreadPool()

        self.sourcefile = QLineEdit()
        self.sourcefile.setDisabled(True)  # must use the file finder to select a valid file.

        self.file_select = QPushButton("Select CSV...")
        self.file_select.pressed.connect(self.choose_csv_file)

        self.generate_btn = QPushButton("Generate PDF")
        self.generate_btn.pressed.connect(self.generate)

        layout = QFormLayout()
        layout.addRow(self.sourcefile, self.file_select)
        layout.addRow(self.generate_btn)

        self.setLayout(layout)

    def choose_csv_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select a file", filter="CSV files (*.csv)")
        if filename:
            self.sourcefile.setText(filename)

    def generate(self):
        if not self.sourcefile.text():
            return  # If the field is empty, ignore.

        self.generate_btn.setDisabled(True)

        data = {
            'sourcefile': self.sourcefile.text(),
        }
        g = Generator(data)
        g.signals.finished.connect(self.generated)
        g.signals.error.connect(print)  # Print errors to console.
        self.threadpool.start(g)

    def generated(self):
        self.generate_btn.setDisabled(False)
        QMessageBox.information(self, "Finished", "PDFs have been generated")


app = QApplication([])
w = Window()
w.show()
app.exec_()
