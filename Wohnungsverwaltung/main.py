from tkinter import *
from tkinter import ttk
import sys
import os

scriptpath = os.path.realpath(__file__)
scriptdir = scriptpath.replace('/main.py', '')
print('scriptdir is: ', scriptdir)
mywidgetspath = scriptdir.replace('Wohnungsverwaltung', 'mywidgets')
print('mywidgets path is: ', mywidgetspath)

sys.path.append(mywidgetspath)

from wvframe import WV
from wvcontroller import WvController

def main():
    print("path: ", sys.path)
    root = Tk()

    if 'win' not in sys.platform:
        style = ttk.Style()
        style.theme_use('clam')

    wv = WV(root)
    wv.setNotebookTab(0)
    firstshow: bool = True

    global scriptpath
    isTest = True if 'Projects/python' in scriptpath else False
    ctrl = WvController(wv)
    ctrl.startWork()

    wv.setStatusText("Bereit")

    #width = root.winfo_screenwidth()
    #width = root.winfo_width()
    #height = int(root.winfo_screenheight()/2)
    #root.geometry('%sx%s' % (900, height))

    #wv.bind("<Visibility>", show)

    wv.mainloop()

if __name__ == '__main__':
    main()