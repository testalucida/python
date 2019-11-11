from tkinter import Tk, ttk
import sys
import os

scriptpath = os.path.realpath(__file__)
scriptdir = scriptpath.replace('/main.py', '')
#print('scriptdir is: ', scriptdir)
mywidgetspath = scriptdir.replace('Wohnungsverwaltung', 'mywidgets')
#print('mywidgets path is: ', mywidgetspath)

sys.path.append(mywidgetspath)

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

    root.option_add('*Dialog.msg.font', 'Helvetica 11')

    wv.mainloop()

if __name__ == '__main__':
    main()

"""
todo

- Menüpunkt "Anlagen V für ausgewählte Wohnungen erstellen" implementieren

- wenn im Baum auf einen Eintrag geklickt wird, der keine
  Wohnung ist: Tabs löschen (Methode clearView in jeden Controller
  einbauen)

- EditableTable: wenn Zellinhalt nicht komplett gezeigt wird,
  ein Fenster mit dem ganzen Inhalt aufmachen, wenn der 
  Mauszeiger über die Zelle fährt
  
- Anlage V: in einem Dialog in Textform ausgeben

"""
