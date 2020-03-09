import tkinter as tk
from tkinter import ttk

try:
    from mywidgets import TextEntry, IntEntry, FloatEntry, MyLabel, \
        MyCombobox, MyText
except ImportError:
    print("couldn't import my widgets.")

class JahresdatenView(ttk.Frame):
    def __init__(self, parent: ttk.Frame):
        ttk.Frame.__init__(self, parent)

        self._lblIdent = None

        self.columnconfigure(0, weight=1)
        self._createUI()

    def _createUI(self):
        padx = 10
        pady = 5
        self._lblIdent = self._createWohnungIdent(padx, pady)

    def _createWohnungIdent(self, padx, pady) -> ttk.Label:
        lbl = MyLabel(self, text='', column=0, row=0, sticky='nswe',
                      anchor='center', padx=padx, pady=pady)
        lbl.setBackground('whg_short.TLabel', 'gray')
        lbl.setForeground('whg_short.TLabel', 'white')
        lbl.setFont('Helvetica 14 bold')
        lbl['relief'] = 'sunken'
        lbl.setTextPadding('whg_short.TLabel', 10, 10)
        return lbl


def test():
    import sys
    #from PIL import Image
    #
    # filename = "./images/haus_18x16.png"
    # img = Image.open(filename)
    # img.save("./images/haus.ico")

    print("path: ", sys.path)
    root = tk.Tk()
    #root.geometry('600x300')
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    if 'win' not in sys.platform:
        style = ttk.Style()
        style.theme_use('clam')

    root.option_add('*Dialog.msg.font', 'Helvetica 11')

    jv = JahresdatenView(root)
    jv.grid(column=0, row=0, sticky='nswe', padx=10, pady=10)

    png = tk.PhotoImage(file="./images/haus_18x16.png")
    root.tk.call('wm', 'iconphoto', root._w, png)

    # haus_ico = Image.open("./images/test.xpm")
    # root.iconbitmap(haus_ico)

    root.mainloop()

if __name__ == '__main__':
    test()