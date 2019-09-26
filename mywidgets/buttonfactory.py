from tkinter import *
from tkinter import ttk
from functools import partial
from mywidgets import ToolTip

class ButtonFactory:
    images = list()
    def getNewButton(parent, tooltip:str = None,
                     callback = None, callbackparm = None, ) -> ttk.Button:
        s = ttk.Style()
        s.theme_use('clam')
        s.configure("My.TButton",
                    padding=0,
                    relief="flat",
                    borderwith=0)
        newpng = PhotoImage(file="/home/martin/Projects/python/mywidgets/images/plus_22x22.png")
        newBtn = ttk.Button(parent, image=newpng, style="My.TButton",
                                 command=partial(callback, callbackparm))
        ButtonFactory.images.append(newpng)
        ToolTip(newBtn, tooltip)
        return newBtn