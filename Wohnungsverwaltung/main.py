from tkinter import *
from tkinter import ttk
import sys
import os

cwd = os.getcwd()
print("current directory is: " + cwd)
mywidgetspath = cwd.replace('Wohnungsverwaltung', 'mywidgets')
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

    ctrl = WvController(wv)
    ctrl.startWork()

    wv.setStatusText("Bereit")

    #width = root.winfo_screenwidth()
    #width = root.winfo_width()
    #height = int(root.winfo_screenheight()/2)
    #root.geometry('%sx%s' % (900, height))

    root.mainloop()

if __name__ == '__main__':
    main()