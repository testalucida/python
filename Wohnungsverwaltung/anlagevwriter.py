from tkinter import *
from tkinter import Tk, Button, Canvas, font
from functools import partial
import json
from anlagevlayout import zeilen

class AnlageVWriter:
    def __init__(self, parent, col: int, row: int):
        self._canvas = Canvas(parent, width=788, height=1120) # A4
        self._canvas.grid(column=col, row=row, sticky='nswe', padx=0, pady=0)
        self._font = font.Font(family="Helvetica", size=12, weight="bold")
        self._data = None

    def startWork_(self, layout_filename: str, data_filename: str):
        self.write(25, 20, 'topline')
        self.write('6.1c', '0.5c', '217/235')
        xmin = '2.35c'
        x = 90
        y = 75
        #self.write(x, y, 'Kendel')
        self.write(xmin, '1.9c', 'Kendel')
        y = 100
        #self.write(x, y, 'Paulchen')
        self.write(xmin, '2.7c', 'Paulchen')
        y = 125
        #self.write(x+80, y, 'Steuernummer')
        self.write('2.35c', '2.7c', 'Paulchen')
        y = 220
        self.write(x, y, 'Straße')
        y = 250
        self.write(x, y, 'PLZ')
        y = 287
        self.write(x+25, y, 'Einheitswert-Aktenzeichen')
        self.write('8.0c', '7.6c', 'Einheitswert')
        y = 332 # zeile 7
        self.write(x, y, '2')
        y = 362 # zeile 8
        self.write(x, y, '53')

    def startWork(self, data_filename: str):
        self._openAnlageData(data_filename)
        self.write(25, 20, 'topline')
        self.write('6.1c', '0.5c', '217/235')

        anlv_zeilen = self._data['zeilen']

        for z, v in zeilen.items():
            print('z: ', z, 'v: ', v)



        for zeile, value_list in anlv_zeilen.items():
            print(zeile, value_list)

    def get_values_to_print(self, znr: int):
        return

    def createTestTemplate(self):
        y = 20
        for x in range(0, 200, 10):
            if x % 10 == 0:
                self._canvas.create_text(x, y, font=('courier', 10), text='|')
                self._canvas.create_text(x, y+20, font=('courier', 8), text=str(x))
            else:
                self._canvas.create_text(x, y, font=('courier', 10), text='.')

    def print_in_cm(self):
        y = 'c1'
        self._canvas.create_text('1.0c', '2.0c', text='testtext')
        self._canvas.create_text('2.0c', '3.0c', text='testtext')


    def create_postscript(self):
        self._canvas.postscript(file='temp.ps', colormode='color')

    def write(self, x: int or str, y: int or str, s: str) -> None:
        self._canvas.create_text(x, y, font=self._font, anchor='sw', text=s)

    def _openAnlageData(self, filename):
        f = open(filename)
        self._data = json.load(f)

def test():
    root = Tk()
    # root.rowconfigure(0, weight=1)
    # root.columnconfigure(0, weight=1)

    avw = AnlageVWriter(root, 0, 1)

    b = Button(root, text='Create Postscript', command=avw.create_postscript)
    b.grid(column=0, row=0)

    avw.startWork("/home/martin/Projects/python/Wohnungsverwaltung/anlagevdata_2018.json")
    #avw.createTestTemplate()
    #avw.print_in_cm()

    root.mainloop()

if __name__ == '__main__':
    test()