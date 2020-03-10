from tkinter import *
from tkinter import ttk
from typing import List
from interfaces import Vergleichswert

try:
    from mywidgets import TextEntry, IntEntry, FloatEntry, MyLabel, \
        MyCombobox, MyText
except ImportError:
    print("couldn't import my widgets.")

############ OutputLabel #################
class OutputLabel(ttk.Label):
    def __init__(self, parent, id:Vergleichswert, year:int,
                 column: int, row: int,
                 padx: int, pady: int,
                 sticky:str = None):
        ttk.Label.__init__(self, parent)
        self.grid(column=column, row=row, sticky='nw', padx=padx, pady=pady)
        self._id = id
        self._year = year
        self._fatFont = ('courier', 11, 'bold')
        self._bigfatFont = ('courier', 13, 'bold')
        self._regularFont = ('courier', 11)
        self._configureStyles()
        self['anchor'] = 'e'
        self['style'] = 'black.TLabel'
        self['width'] = 10

    def _configureStyles(self):
        #default, white background:
        s = ttk.Style()
        s.configure('black.TLabel', font=self._regularFont)
        s.configure('black.TLabel', background='white')
        s.configure('black.TLabel', foreground='black')
        #white background, bold black font
        s = ttk.Style()
        s.configure('blackfat.TLabel', font=self._fatFont)
        s.configure('blackfat.TLabel', background='white')
        s.configure('blackfat.TLabel', foreground='black')
        # white background, big bold black font
        s.configure('blackbigfat.TLabel', font=self._bigfatFont)
        s.configure('blackbigfat.TLabel', background='white')
        s.configure('blackbigfat.TLabel', foreground='black')
        #white background, red font
        s = ttk.Style()
        s.configure('red.TLabel', font=self._regularFont)
        s.configure('red.TLabel', background='white')
        s.configure('red.TLabel', foreground='red')
        #white background, bold red font
        s = ttk.Style()
        s.configure('redfat.TLabel', font=self._fatFont)
        s.configure('redfat.TLabel', background='white')
        s.configure('redfat.TLabel', foreground='red')

    def locate(self, col:int, row:int) -> None:
        self.grid(column=col, row=row)

    def getId(self) -> Vergleichswert:
        return self._id

    def getYear(self) -> int:
        return self._year

    def setValue(self, val:int or float):
        if type(val) is int:
            self['text'] = str(val)
        else:
            self['text'] = "{0:.2f}".format(val)

    def getValue(self) -> str:
        val = self['text']
        if "." in val or "," in val:
            return "{0:.2f}".format(val)
        else: return val

    def getFloatValue(self) -> float:
        return float(self['text'])

    def getIntValue(self) -> int:
        return int(self['text'])

    def clear(self):
        self['text'] = ''

    def setBlackFont(self, bold:bool = False):
        if bold:
            self['style'] = 'blackfat.TLabel'
        else:
            self['style'] = 'black.TLabel'

    def setBigFatBlackFont(self):
        self['style'] = 'blackbigfat.TLabel'

    def setRedFont(self, bold:bool = False):
        if bold:
            self['style'] = 'redfat.TLabel'
        else:
            self['style'] = 'red.TLabel'

############ JahresdatenBaseView #########
class JahresdatenBaseView(ttk.Frame):
    def __init__(self, parent: ttk.Frame, yearlist:List[int]):
        ttk.Frame.__init__(self, parent)
        self._yearlist = yearlist
        numberOfYears = len(yearlist)
        self._rowList = []

        padx = 20
        pady = 5
        self._outputLabelframe:LabelFrame = self._createUI(padx, pady)

    def _createUI(self, padx, pady) -> ttk.Frame:
        self._createStyles()

        lf = ttk.Frame(self)
        lf.grid(column=0, row=0, sticky='nswe', padx=10, pady=10)

        ###### Year header  #######################
        c = r = 0
        for i in range(len(self._yearlist)):
            year = str(self._yearlist[i])
            lbl = MyLabel(lf, text=year, column=1+i, row=r,
                    sticky='swe', anchor='center',
                    padx=padx, pady=pady)
            lbl['style'] = 'year.TLabel'

        r += 1
        ####regelmäßige Ein-/Auszahlungen##############
        lbl = MyLabel(lf, text='Regelmäßige\nEin-/Auszahlungen', column=c, row=r,
                      sticky='nw', anchor='w', padx=1, pady=pady)
        lbl['style'] = 'fat.TLabel'

        r += 1
        lbl = MyLabel(lf, text='Nettomiete', column=c, row=r, sticky='nw',
                      anchor='w', padx=padx, pady=pady)
        self._createOut(lf, Vergleichswert.nettomiete, r, pady)

        r += 1
        lbl = MyLabel(lf, text='NK-Voraus', column=c, row=r, sticky='nw',
                      anchor='w', padx=padx, pady=pady)
        self._createOut(lf, Vergleichswert.nk_voraus, r, pady)

        r += 1
        lbl = MyLabel(lf, text='HG-Voraus', column=c, row=r, sticky='nw',
                      anchor='w', padx=padx, pady=pady)
        self._createOut(lf, Vergleichswert.hg_voraus, r, pady)

        r += 1
        ####### sonstige Ein-/Auszahlungen ################
        lbl = MyLabel(lf, text='Sonstige\nEin-/Auszahlungen', column=c, row=r,
                      sticky='nw', anchor='w', padx=1, pady=(20, pady))
        lbl['style'] = 'fat.TLabel'

        r += 1
        lbl = MyLabel(lf, text='Rechnungen und\nEntnahme Rücklagen', column=c, row=r, sticky='nw',
                      anchor='w', padx=padx, pady=pady)
        self._createOut(lf, Vergleichswert.rechng, r, 10)

        r += 1
        lbl = MyLabel(lf, text='NK-Abrechnung', column=c, row=r, sticky='nw',
                      anchor='w', padx=padx, pady=pady)
        self._createOut(lf, Vergleichswert.nk_abrechng, r, pady)

        r += 1
        lbl = MyLabel(lf, text='HG-Abrechnung', column=c, row=r, sticky='nw',
                      anchor='w', padx=padx, pady=pady)
        self._createOut(lf, Vergleichswert.hg_abrechng, r, pady)

        r += 1
        ###### Ergebnis ###################
        lbl = MyLabel(lf, text='Ergebnis', column=c, row=r,
                      sticky='nw', anchor='w', padx=1, pady=25)
        lbl['style'] = 'bigfat.TLabel'
        self._rowList.append((r, 22))
        self._createOut(lf, Vergleichswert.ergebnis, r, 22)

        r += 1
        #########  Sonderumlagen #####################
        lbl = MyLabel(lf, text='Sonderumlagen', column=c, row=r,
                      sticky='nw', anchor='w', padx=1, pady=25)
        lbl['style'] = 'fat.TLabel'
        self._rowList.append((r, 22))
        self._createOut(lf, Vergleichswert.sonderumlage, r, 22)

        r += 1
        #########  Ein-/Auszahlungen je qm #####################
        lbl = MyLabel(lf, text='Ein-/Auszahlungen\nje qm u. Monat', column=c, row=r,
                      sticky='nw', anchor='w', padx=1, pady=pady)
        lbl['style'] = 'fat.TLabel'

        r += 1
        lbl = MyLabel(lf, text='Nettomiete', column=c, row=r, sticky='nw',
                      anchor='w', padx=padx, pady=pady)
        self._createOut(lf, Vergleichswert.nettomiete_qm, r, pady)

        r += 1
        lbl = MyLabel(lf, text='NK', column=c, row=r, sticky='nw',
                      anchor='w', padx=padx, pady=pady)
        self._createOut(lf, Vergleichswert.nk_qm, r, pady)

        r += 1
        lbl = MyLabel(lf, text='HG netto', column=c, row=r, sticky='nw',
                      anchor='w', padx=padx, pady=pady)
        self._createOut(lf, Vergleichswert.hg_netto_qm, r, pady)

        r += 1
        lbl = MyLabel(lf, text='Rücklagen', column=c, row=r, sticky='nw',
                      anchor='w', padx=padx, pady=pady)
        self._createOut(lf, Vergleichswert.rueck_qm, r, pady)

        r += 1
        lbl = MyLabel(lf, text='HG gesamt', column=c, row=r, sticky='nw',
                      anchor='w', padx=padx, pady=pady)
        self._createOut(lf, Vergleichswert.hg_ges_qm, r, pady)

        return lf

    def clear(self):
        for ch_type, ch in self._outputLabelframe.children.items():
            if type(ch) is OutputLabel:
                ch.clear()

    def setValue(self, vw:Vergleichswert, year:int, newVal:int) -> None:
        for ch_type, ch in self._outputLabelframe.children.items():
            if type(ch) is OutputLabel \
                    and ch.getId() == vw \
                    and ch.getYear() == year:

                if newVal < 0:
                    bold = True if vw == Vergleichswert.ergebnis else False
                    ch.setRedFont(bold)
                    newVal *= -1

                ch.setValue(newVal)

    def _createStyles(self):
        s = ttk.Style()
        s.configure('italic.TLabel', font=('courier', 13, 'italic'))
        s.configure('fat.TLabel', font=('courier', 11, 'bold'))
        s.configure('bigfat.TLabel', font=('courier', 12, 'bold'))
        s.configure('year.TLabel', foreground='green')
        s.configure('year.TLabel', font=('courier', 13, ('italic', 'bold')))

    def _createOut(self, parent:ttk.Frame, id:Vergleichswert, row:int, pady:int):
        padx = 20
        for c in range(len(self._yearlist)):
            lbl = OutputLabel(parent, id, self._yearlist[c], 1+c, row, padx, pady)
            if id == Vergleichswert.hg_voraus \
                    or id == Vergleichswert.rechng\
                    or id == Vergleichswert.hg_netto_qm\
                    or id == Vergleichswert.rueck_qm:
                lbl.setRedFont(False)
            if id == Vergleichswert.ergebnis:
                #lbl.setBigFatBlackFont()
                lbl.setBlackFont(True)
            if id == Vergleichswert.hg_ges_qm:
                lbl.setRedFont(True)

def test():
    import sys
    #from PIL import Image
    #
    # filename = "./images/haus_18x16.png"
    # img = Image.open(filename)
    # img.save("./images/haus.ico")

    print("path: ", sys.path)
    root = Tk()
    #root.geometry('600x300')
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    style = ttk.Style()
    style.theme_use('clam')

    jv = JahresdatenBaseView(root, (2020, 2019))
    jv.grid(column=0, row=0, sticky='nswe', padx=10, pady=10)

    jv.setValue(Vergleichswert.nettomiete, 2019, 1234)
    jv.setValue(Vergleichswert.nk_voraus, 2019, 3567)
    jv.setValue(Vergleichswert.hg_voraus, 2019, 2214)
    jv.setValue(Vergleichswert.rechng, 2019, 398)
    jv.setValue(Vergleichswert.nk_abrechng, 2019, 127)
    jv.setValue(Vergleichswert.hg_abrechng, 2019, -220)
    jv.setValue(Vergleichswert.ergebnis, 2019, 455)
    jv.setValue(Vergleichswert.sonderumlage, 2019, 500)
    jv.setValue(Vergleichswert.nettomiete_qm, 2019, 7.3)
    jv.setValue(Vergleichswert.nk_qm, 2019, 2.05)
    jv.setValue(Vergleichswert.hg_netto_qm, 2019, 2.12)
    jv.setValue(Vergleichswert.rueck_qm, 2019, 0.8)
    jv.setValue(Vergleichswert.hg_ges_qm, 2019, 2.92)

    #png = tk.PhotoImage(file="./images/haus_18x16.png")
    #root.tk.call('wm', 'iconphoto', root._w, png)

    # haus_ico = Image.open("./images/test.xpm")
    # root.iconbitmap(haus_ico)

    root.mainloop()

if __name__ == '__main__':
    test()