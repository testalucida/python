#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from libs import *
#from utils import *
import utils
import os

from wvframe import WV
from wvcontroller import WvController

def main():
    from tkinter import PhotoImage
    root = Tk()
    icon = PhotoImage(file=utils.getScriptPath() + "/images/haus_18x16.png")
    root.call('wm', 'iconphoto', root._w, icon)

    if 'win' not in sys.platform:
        style = ttk.Style()
        style.theme_use('clam')

    wv = WV(root)
    wv.setNotebookTab(0)

    ctrl = WvController(wv)
    ctrl.startWork()

    wv.setStatusText("Angemeldeter Benutzer: " + utils.getUser())

    #width = root.winfo_screenwidth()
    #width = root.winfo_width()
    #height = int(root.winfo_screenheight()/2)
    #root.geometry('%sx%s' % (900, height))

    #wv.bind("<Visibility>", show)

    root.option_add('*Dialog.msg.font', 'Helvetica 11')

    wv.mainloop()

if __name__ == '__main__':
    print("path: ", sys.path)
    print("current work directory: ", os.getcwd())
    print("scriptpath: ", utils.getScriptPath())
    main()

"""
todo

- Anlage V: in einem Dialog in Textform ausgeben
- Tab Page Jahresdaten implementieren (für *eine* Wohnung)
- Dialog Jahresdaten implementieren (Vergleich *aller* Wohnungen)
- Bug: Wohnung löschen geht nicht
- Bug: Löschen der letzten Rechnung: Fehler wird gemeldet, 
       letzte Rechnung bleibt stehen, ist beim neuen LAden
       dann aber doch weg
- zusätzliche Plausi bei Mtl. Ein-Auszahlungen: Es darf keine Änderung
  von Miete, NK, HG WÄHREND eines Monats geben, sonst laufen die Jahresdaten
  und die AnlageV-Berechnung falsch.
"""
