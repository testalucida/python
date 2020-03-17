import tkinter as tk
from tkinter import ttk
from typing import List
from jahresdatenbaseview import JahresdatenBaseView
from jahresdatenprovider import JahresdatenCollection


try:
    from mywidgets import TextEntry, IntEntry, FloatEntry, MyLabel, \
        MyCombobox, MyText
except ImportError:
    print("couldn't import mywidgets.")

class JahresdatenView(ttk.Frame):
    def __init__(self, parent: ttk.Frame):
        ttk.Frame.__init__(self, parent)
        self._jahresdatenbaseview:JahresdatenView = None
        self._button:ttk.Button = None
        self._jahresdatenCallback = None
        self.columnconfigure(0, weight=1)
        self._createUI()

    def _createUI(self):
        padx = 10
        pady = 5
        view = JahresdatenBaseView(self)
        view.grid(column=0, row=0, sticky='nswe', padx=padx, pady=pady)
        self._jahresdatenbaseview = view

        btn = ttk.Button(self, text="Jahresübersicht ermitteln", command=self._onJahresdatenClick)
        btn.grid(column=0, row=1, sticky='nswe', padx=padx, pady=pady)
        self._button = btn
        self.setButtonEnabled(False)

    def registerOnJahresdatenCallback(self, cbfunc):
        self._jahresdatenCallback = cbfunc

    def setValues(self, jdcoll_list:List[JahresdatenCollection]) -> None:
        self._jahresdatenbaseview.setValues(jdcoll_list)
        self.setButtonEnabled(False)

    def _onJahresdatenClick(self):
        if self._jahresdatenCallback:
            self._jahresdatenCallback()

    def clear(self):
        self._jahresdatenbaseview.clear()

    def setButtonEnabled(self, enabled:bool):
        if enabled:
            self._button['state'] = 'normal'
        else:
            self._button['state'] = 'disabled'

g_jv:JahresdatenView = None

def callback():
    from jahresdatenprovider import JahresdatenProvider
    import utils

    prov = JahresdatenProvider()
    prov.connect(utils.getUser())
    l: List[JahresdatenCollection] = prov.getJahresdaten(1, 2018, 2020)
    global g_jv
    g_jv.setValues(l)

def test():
    import sys
    # from jahresdatenprovider import JahresdatenProvider
    # import utils
    #from PIL import Image
    #
    # filename = "./images/haus_18x16.png"
    # img = Image.open(filename)
    # img.save("./images/haus.ico")

    # prov = JahresdatenProvider()
    # prov.connect(utils.getUser())
    #l: List[JahresdatenCollection] = prov.getJahresdaten(1, 2019, 2020)

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
    jv.registerOnJahresdatenCallback(callback)
    global g_jv
    g_jv = jv
    #jv.setValues(l)

    png = tk.PhotoImage(file="./images/haus_18x16.png")
    root.tk.call('wm', 'iconphoto', root._w, png)

    # haus_ico = Image.open("./images/test.xpm")
    # root.iconbitmap(haus_ico)

    root.mainloop()

if __name__ == '__main__':
    test()