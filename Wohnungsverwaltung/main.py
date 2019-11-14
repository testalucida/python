#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from libs import *
from utils import *

from wvframe import WV
from wvcontroller import WvController

def main():
    #print("path: ", sys.path)
    root = Tk()

    if 'win' not in sys.platform:
        style = ttk.Style()
        style.theme_use('clam')

    wv = WV(root)
    wv.setNotebookTab(0)

    ctrl = WvController(wv)
    ctrl.startWork()

    wv.setStatusText("Bereit")

    #width = root.winfo_screenwidth()
    #width = root.winfo_width()
    #height = int(root.winfo_screenheight()/2)
    #root.geometry('%sx%s' % (900, height))

    #wv.bind("<Visibility>", show)

    root.option_add('*Dialog.msg.font', 'Helvetica 11')

    wv.mainloop()

if __name__ == '__main__':
    main()

"""
todo

- Anlage V: in einem Dialog in Textform ausgeben
- Tab Page Wohnungsdaten implementieren
- Tab Page Vermietung implementieren

"""
