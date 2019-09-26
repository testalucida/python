from tkinter import *
from tkinter import ttk
from functools import partial
from mywidgets import ToolTip

class ButtonFactory:
    def getNewButton(parent, tooltip:str = None,
                     callback = None, callbackparm = None, ) -> ttk.Button:
        s = ttk.Style()
        s.theme_use('clam')
        s.configure("My.TButton",
                    padding=0,
                    relief="flat",
                    borderwith=0)
        parent.newpng = PhotoImage(file="/home/martin/Projects/python/mywidgets/images/plus_22x22.png")
        newBtn = ttk.Button(parent, image=parent.newpng, style="My.TButton",
                                 command=partial(callback, callbackparm))
        ToolTip(newBtn, tooltip)
        return newBtn