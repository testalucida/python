from tkinter import *
from tkinter import ttk
from typing import Dict, List
from mywidgets import ScrolledCanvas

testdict = \
{
    "vj": 2018,
    "zeilen": {
        "1": [
            {
                "name": "Name",
                "value": "Kendel"
            }
        ],
        "2": [
            {
                "name": "Vorname",
                "value": "Martin"
            }
        ],
        "3": [
            {
                "name": "Steuernummer",
                "value": "217/235/50499"
            },
            {
                "name": "lfd. Nr.",
                "value": "1"
            }
        ],
        "4": [
            {
                "name": "Stra\u00dfe, Hausnummer",
                "value": "Mendelstr. 24 / 3. OG rechts (Whg 8 - S\u00fcd)"
            },
            {
                "name": "Angeschafft am",
                "value": "13.05.1997"
            }
        ],
        "5": [
            {
                "name": "Postleitzahl",
                "value": "90429"
            },
            {
                "name": "Ort",
                "value": "N\u00fcrnberg"
            }
        ],
        "6": [
            {
                "name": "Einheitswert-Aktenzeichen",
                "value": "24101153470240083"
            }
        ],
        "7": [
            {
                "name": "Als Ferienwohnung genutzt",
                "value": "2"
            },
            {
                "name": "An Angeh\u00f6rige vermietet",
                "value": "2"
            }
        ],
        "8": [
            {
                "name": "Gesamtwohnfl\u00e4che",
                "value": "52"
            }
        ],
        "9": [
            {
                "name": "Mieteinnahmen ohne Umlagen",
                "value": "4920"
            }
        ],
        "13": [
            {
                "name": "Umlagen, verrechnet mit Erstattungen",
                "value": "1200"
            }
        ],
        "21": [
            {
                "name": "Summe der Einnahmen",
                "value": "6120"
            }
        ],
        "33": [
            {
                "name": "linear",
                "value": "X"
            },
            {
                "name": "degressiv",
                "value": " "
            },
            {
                "name": "prozent",
                "value": ""
            },
            {
                "name": "wie_vorjahr",
                "value": "X"
            },
            {
                "name": "betrag",
                "value": "1126"
            }
        ],
        "39": [
            {
                "name": "voll_abzuziehende",
                "value": "0"
            }
        ],
        "41": [
            {
                "name": "gesamtaufwand_vj",
                "value": "0"
            },
            {
                "name": "anteil_vj",
                "value": "0"
            }
        ],
        "42": [
            {
                "name": "vj_minus_4",
                "value": "0"
            }
        ],
        "43": [
            {
                "name": "vj_minus_3",
                "value": "0"
            }
        ],
        "44": [
            {
                "name": "vj_minus_2",
                "value": "0"
            }
        ],
        "45": [
            {
                "name": "vj_minus_1",
                "value": "860"
            }
        ],
        "46": [
            {
                "name": "grundsteuer_txt",
                "value": "Grundsteuer"
            },
            {
                "name": "grundsteuer",
                "value": "44"
            }
        ],
        "47": [
            {
                "name": "hausgeld",
                "value": "Hausgeld OHNE Zuf\u00fchrg. R\u00fccklagen"
            },
            {
                "name": "verwaltungskosten",
                "value": "991"
            }
        ],
        "49": [
            {
                "name": "sonst_kost",
                "value": "Porto, Fahrtkosten, H&G etc."
            },
            {
                "name": "sonstige",
                "value": "68"
            }
        ],
        "22": [
            {
                "name": "summe_werbungskosten",
                "value": "3089"
            }
        ],
        "50": [
            {
                "name": "summe_werbungskosten",
                "value": "3089"
            }
        ],
        "23": [
            {
                "name": "ueberschuss",
                "value": "3031"
            }
        ],
        "24": [
            {
                "name": "zurechng_mann",
                "value": "3031"
            },
            {
                "name": "zurechng_frau",
                "value": "0"
            }
        ]
    }
}

class AnlageVData:
    def __init__(self, datadict):
        #self._keys = "zeilen"
        self._vj = datadict['vj']
        self._datadict = datadict['zeilen']
        self._rowdict = dict()
        self._makeTable(datadict['zeilen'])

    def _makeTable(self, datadict:Dict):
        r = 0
        for key, val in datadict.items():
            #print(key, ": ")
            if self._isIterable(val):
                for v in val:
                    self._rowdict[r] = [key, v['name'], v['value'], "Keine Erläuterung.\n"
                                                                    "Diese folgt später.\n"
                                                                    "Vielleicht."]
                    r += 1
                    #print( "\t", v)
            else: raise KeyError("Key " + key + " is not iterable")

        # for k, v in self._rowdict.items():
        #     print(k, v)

    def _isIterable(self, val: any) -> bool:
        try:
            iter(val)
        except Exception:
            return False
        else:
            return True

    def getValue(self, row:int, col:int) -> any:
        li:List = self._rowdict[row]
        return li[col]

    def getValues(self, row:int) -> List:
        return self._rowdict[row]

    def getRows(self) -> int:
        return len(self._rowdict)

    def getColumns(self) -> int:
        return len(self._rowdict[0])

# class Columns:
#     def __init__(self):
#         self.C1 = "Z#"
#         self.C2 = "Bezeichnung"
#         self.C3 = "Wert"
#         self.C4 = "Erläuterung"

class AnlageVTableView(ScrolledCanvas):
    def __init__(self, parent):
        ScrolledCanvas.__init__(self, parent)
        self._headers = ("Z#", "Feldbezeichnung", "Eingetragener Wert", "Erläuterung")
        self._colW = (5, 35, 35, 50)
        self._data = None
        self._rowlist = [] #list of ttk.Frames representing a row each

    def setData(self, data:AnlageVData) -> None:
        cols = data.getColumns()
        self._provideHeaders(cols)
        rows = data.getRows()
        for r in range(rows):
            f = ttk.Frame(self.getParent())
            f.grid(row=r+1, column=0, columnspan=cols, sticky='nswe', padx=1, pady=1)
            #self._rowlist.append(f)
            self._provideColumnValues(f, data.getValues(r))

    def _provideHeaders(self, cols:int):
        f = ttk.Frame(self.getParent())
        f.grid(row=0, column=0, columnspan=cols, sticky='nswe', padx=1, pady=1)
        s = ttk.Style()
        s.configure("header.Label", ipady=5, background="#000000")
        for c in range(cols):
            #lbl = ttk.Label(f, text=self._headers[c], width=self._colW[c], style="header.Label")
            lbl = Label(f, text=self._headers[c], width=self._colW[c], height=2)
            lbl.grid(row=0, column=c, sticky='nswe', padx=1, pady=1)

    def _provideColumnValues(self, parent:ttk.Frame, values:List) -> None:
        c = 0
        s = ttk.Style()
        s.configure( "my.Label", background="#ffffff")
        for cellval in values:
            lbl = ttk.Label(parent, text=cellval, width = self._colW[c], style="my.Label")
            lbl.grid(row=0, column=c, sticky='nswe', padx = 1, pady = 1)
            c += 1

# class AnlageVTableView(TableView):
#     def __init__(self, parent):
#         TableView.__init__(self, parent)
#         self._headers = ["Z#", "Bezeichnung", "Wert", "Erläuterung"]
#         self.setColumns(self._headers)
#         self.setColumnWidth(self._headers[0], 30)
#         self.setColumnWidth(self._headers[3], 80)
#         self.setColumnStretch(self._headers[0], False)
#         self.setColumnStretch(self._headers[1], False)
#         self.setColumnStretch(self._headers[2], False)
#         self.alignColumn(self._headers[2], 'e')
#
# def wrap(string, length=20):
#     return '\n'.join(textwrap.wrap(string, length))


def test():
    avdata = AnlageVData(testdict)
    root = Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.geometry('1000x800')
    atv = AnlageVTableView(root)
    atv.grid(row=0, column=0, sticky='nswe', padx=3, pady=3)
    atv.setData(avdata)
    root.mainloop()

if __name__ == '__main__':
    test()