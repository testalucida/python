from tkinter import *
from tkinter import ttk
from functools import partial
from mywidgets import ToolTip

class ButtonFactory:
    images = list()

    def getNewButton(parent, tooltip:str = None,
                     callback = None, callbackparm = None, ) -> ttk.Button:
        newpng = PhotoImage(file="/home/martin/Projects/python/mywidgets/images/plus_22x22.png")
        ButtonFactory.images.append(newpng)

        return ButtonFactory._getButton(parent, newpng, tooltip, callback, callbackparm)

    def getEditButton(parent, tooltip:str = None,
                     callback = None, callbackparm = None, ) -> ttk.Button:
        png = PhotoImage(file="/home/martin/Projects/python/mywidgets/images/edit_22x22.png")
        ButtonFactory.images.append(png)

        return ButtonFactory._getButton(parent, png, tooltip, callback, callbackparm)

    def _getButton(parent, image: PhotoImage, tooltip:str = None,
                   callback = None, callbackparm = None, ) -> ttk.Button:
        s = ttk.Style()
        s.theme_use('clam')
        s.configure("My.TButton",
                    padding=0,
                    relief="flat",
                    borderwith=0)

        btn = ttk.Button(parent, image=image, style="My.TButton",
                            command=partial(callback, callbackparm))
        if tooltip:
            ToolTip(btn, tooltip)

        return btn