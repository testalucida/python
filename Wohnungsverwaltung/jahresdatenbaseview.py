from tkinter import *
from tkinter import ttk
from typing import List
from interfaces import Vergleichswert
from jahresdatenprovider import JahresdatenProvider, \
    Jahresdaten, JahresdatenCollection
import utils
try:
    from mywidgets import TextEntry, IntEntry, FloatEntry, MyLabel, \
        MyCombobox, MyText
except ImportError:
    print("couldn't import my widgets.")

############ OutputLabel #################
class OutputLabel(ttk.Label):
    def __init__(self, parent, id:Vergleichswert, whg_id:int, year:int,
                 column: int, row: int,
                 padx: int, pady: int,
                 sticky:str = None):
        ttk.Label.__init__(self, parent)
        self.grid(column=column, row=row, sticky='nw', padx=padx, pady=pady)
        self._id = id
        self._whg_id = whg_id
        self._year = year
        self._fatFont = ('courier', 11, 'bold')
        self._bigfatFont = ('courier', 13, 'bold')
        self._regularFont = ('courier', 11)
        self._configureStyles()
        self['anchor'] = 'e'
        self['style'] = 'black.TLabel'
        self['width'] = 8

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

    def getWhgId(self) -> int:
        return self._whg_id

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
    def __init__(self, parent: ttk.Frame):
        ttk.Frame.__init__(self, parent)
        self._jdcoll_list:List[JahresdatenCollection] = None
        self._nWhg = 0 # number of properties to display
        self._nYears = 0
        self._yearlist:List[int] = None

        self._padx = 20
        self._pady = 3
        self._outputLabelframe:ttk.Frame = None
        self._createStyles()

    def setValues(self, jdcoll_list:List[JahresdatenCollection]) -> None:
        """

        :param jdcoll_list: list of JahresdatenCollection objects.
                            Each JahresdatenCollection refers to one property
                            and n years. A year is represented by a Jahresdaten object
        :return: None
        """
        self._jdcoll_list = jdcoll_list
        self._nWhg = len(jdcoll_list)
        self._nYears = jdcoll_list[0].getYearCount()
        self._yearlist = jdcoll_list[0].getYears()
        self._createUI(self._padx, self._pady)
        for jdcoll in jdcoll_list:
            self._setValues(jdcoll)

    def _setValues(self, jdcoll:JahresdatenCollection) -> None:
        whg_id = jdcoll.getWhgId()
        for jd in jdcoll.getJahresdatenList():
            j = jd.jahr
            self.setValue(Vergleichswert.nettomiete, whg_id, j, jd.netto_miete)
            self.setValue(Vergleichswert.nk_voraus, whg_id, j, jd.nk_abschlag)
            self.setValue(Vergleichswert.hg_voraus, whg_id, j, jd.hg_brutto)
            self.setValue(Vergleichswert.rechng, whg_id, j, jd.rechng)
            self.setValue(Vergleichswert.sonst_kosten, whg_id, j, jd.sonst_kosten)
            self.setValue(Vergleichswert.nk_abrechng, whg_id, j, jd.nk_abrechng)
            self.setValue(Vergleichswert.hg_abrechng, whg_id, j, jd.hg_abrechng)
            self.setValue(Vergleichswert.ergebnis, whg_id, j, jd.ergebnis)
            self.setValue(Vergleichswert.sonderumlage, whg_id, j, jd.sonderumlagen)
            self.setValue(Vergleichswert.nettomiete_qm, whg_id, j, jd.netto_miete_qm)
            self.setValue(Vergleichswert.nk_qm, whg_id, j, jd.nk_qm)
            self.setValue(Vergleichswert.hg_ges_qm, whg_id, j, jd.hg_ges_qm)
            self.setValue(Vergleichswert.rueck_qm, whg_id, j, jd.ruecklage_qm)

    def _createUI(self, padx, pady) -> None:
        r = c = 0
        lf = ttk.Frame(self)
        lf.grid(column=c, row=r, sticky='nswe', padx=10, pady=10)

        ########### Wohnung and Year header  #######################
        col = 1
        for i in range(self._nWhg):
            ident = self._jdcoll_list[i].getWohnungIdent()
            col_span = self._nYears
            lbl = MyLabel(lf, text=ident, column=col, row=r,
                          sticky='nwe', anchor='center',
                          padx=padx, pady=pady)
            lbl.grid(columnspan = col_span)
            col += col_span

        r += 1
        col = 1
        for n in range(self._nWhg):
            for i in range(self._nYears):
                year = str(self._yearlist[i])
                lbl = MyLabel(lf, text=year, column=col, row=r,
                              sticky='swe', anchor='center',
                              padx=padx, pady=pady)
                lbl['style'] = 'year.TLabel'
                col += 1

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
        lbl = MyLabel(lf, text='sonst. Kosten', column=c, row=r, sticky='nw',
                      anchor='w', padx=padx, pady=pady)
        self._createOut(lf, Vergleichswert.sonst_kosten, r, pady)

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
        py = (25,0)
        lbl = MyLabel(lf, text='Ergebnis', column=c, row=r,
                      sticky='nw', anchor='w', padx=1, pady=py)
        lbl['style'] = 'bigfat.TLabel'
        #self._rowList.append((r, 22))
        self._createOut(lf, Vergleichswert.ergebnis, r, py)

        r += 1
        #########  Sonderumlagen #####################
        py = (15,0)
        lbl = MyLabel(lf, text='Sonderumlagen', column=c, row=r,
                      sticky='nw', anchor='w', padx=1, pady=py)
        lbl['style'] = 'fat.TLabel'
        self._createOut(lf, Vergleichswert.sonderumlage, r, py)

        r += 1
        #########  Ein-/Auszahlungen je qm #####################
        py = (15,3)
        lbl = MyLabel(lf, text='Ein-/Auszahlungen\nje qm u. Monat', column=c, row=r,
                      sticky='nw', anchor='w', padx=1, pady=py)
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
        lbl = MyLabel(lf, text='HG gesamt', column=c, row=r, sticky='nw',
                      anchor='w', padx=padx, pady=pady)
        self._createOut(lf, Vergleichswert.hg_ges_qm, r, pady)

        r += 1
        lbl = MyLabel(lf, text='davon Rücklagen', column=c, row=r, sticky='nw',
                      anchor='w', padx=padx, pady=pady)
        self._createOut(lf, Vergleichswert.rueck_qm, r, pady)

        if self._nWhg > 1:
            col = self._nYears
            for n in range(self._nWhg - 1):
                ttk.Separator(lf, orient=VERTICAL).\
                    grid(column=col, row=0, rowspan=r+1, sticky='nse')
                col += self._nYears

        self._outputLabelframe = lf

    def clear(self):
        if self._outputLabelframe:
            self._outputLabelframe.destroy()
            self._outputLabelframe = None
        #     for ch_type, ch in self._outputLabelframe.children.items():
        #         if type(ch) is OutputLabel or type(ch) is MyLabel:
        #             ch.clear()
                    ##ch.destroy()
        self._jdcoll_list = None
        self._nWhg = 0
        self._nYears = 0
        self._yearlist = None

    def setValue(self, vw:Vergleichswert, whg_id:int, year:int, newVal:int) -> None:
        for ch_type, ch in self._outputLabelframe.children.items():
            if type(ch) is OutputLabel \
                    and ch.getId() == vw \
                    and ch.getWhgId() == whg_id \
                    and ch.getYear() == year:

                if newVal < 0:
                    bold = True if vw == Vergleichswert.ergebnis else False
                    ch.setRedFont(bold)
                    newVal *= -1

                ch.setValue(newVal)
                break

    def _createStyles(self):
        s = ttk.Style()
        s.configure('italic.TLabel', font=('courier', 13, 'italic'))
        s.configure('fat.TLabel', font=('courier', 11, 'bold'))
        s.configure('bigfat.TLabel', font=('courier', 12, 'bold'))
        s.configure('year.TLabel', foreground='green')
        s.configure('year.TLabel', font=('courier', 13, ('italic', 'bold')))

    def _createOut(self, parent:ttk.Frame, id:Vergleichswert, row:int, pady:int or List):
        padx = 20
        col = 1
        for w in range(self._nWhg):
            whg_id = self._jdcoll_list[w].getWhgId()
            for c in range(self._nYears):
                lbl = OutputLabel(parent, id, whg_id, self._yearlist[c], col, row, padx, pady)
                if id == Vergleichswert.hg_voraus \
                        or id == Vergleichswert.rechng\
                        or id == Vergleichswert.hg_ges_qm\
                        or id == Vergleichswert.rueck_qm:
                    lbl.setRedFont(False)
                if id == Vergleichswert.ergebnis:
                    #lbl.setBigFatBlackFont()
                    lbl.setBlackFont(True)
                if id == Vergleichswert.hg_ges_qm:
                    lbl.setRedFont(True)
                col += 1

def test():
    import sys

    print("path: ", sys.path)

    prov = JahresdatenProvider()
    prov.connect(utils.getUser())
    #l:List[JahresdatenCollection] = prov.getJahresdatenAlleWohnungen(2019, 2019)
    # l = prov.getJahresdaten(6, 2018, 2020)
    l = prov.getJahresdaten(6, 2018, 2020)

    root = Tk()
    #root.geometry('600x300')
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    style = ttk.Style()
    style.theme_use('clam')

    jv = JahresdatenBaseView(root)
    jv.grid(column=0, row=0, sticky='nswe', padx=10, pady=10)
    jv.setValues(l)

    root.mainloop()

if __name__ == '__main__':
    test()