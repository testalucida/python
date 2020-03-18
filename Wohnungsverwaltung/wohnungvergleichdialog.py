from tkinter import Tk, Toplevel
from tkinter import ttk
from typing import List, Dict
from jahresdatenbaseview import JahresdatenBaseView
from jahresdatencontroller import JahresdatenCollection

class WohnungVergleichDialog(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        self.title("Wohnungsvergleich")
        self._jahresdatenbaseview = None
        self._createUI()

    def _createUI(self):
        padx = 10
        pady = 5
        view = JahresdatenBaseView(self)
        view.grid(column=0, row=0, sticky='nswe', padx=padx, pady=pady)
        self._jahresdatenbaseview = view

    def setValues(self, jdcoll_list:List[JahresdatenCollection]) -> None:
        self._jahresdatenbaseview.setValues(jdcoll_list)

if __name__ == '__main__':
    from jahresdatenprovider import JahresdatenProvider
    import utils

    prov = JahresdatenProvider()
    prov.connect(utils.getUser())
    l: List[JahresdatenCollection] = prov.getJahresdatenAlleWohnungen(2020)

    root = Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    dlg = WohnungVergleichDialog(root)
    #dlg.grid(column=0, row=0, sticky='nswe', padx=10, pady=10)
    dlg.setValues(l)

    root.mainloop()
