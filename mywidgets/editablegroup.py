from tkinter import *
from tkinter import ttk
from abc import ABC, abstractmethod
from functools import partial
from enum import Enum, IntEnum
from mywidgets import MyCombobox, TextEntry, MyLabel, ToolTip

EditableGroupAction = IntEnum('EditableGroupAction', 'new edit choose save')

class EditSaveFunctionBar(ttk.Frame):
    """
    Class provides a ttk.Frame containing 4 Buttons choose, edit, new, save
    """
    def __init__(self, parent, callback):
        ttk.Frame.__init__(self, parent)
        self._callback = callback
        self._createButtons()

    def _createButtons(self):
        # Button style
        s = ttk.Style()
        s.theme_use('clam')
        s.configure("My.TButton",
                    padding=0,
                    relief="flat",
                    borderwith=0)

        # Button "Choose"
        self.dropdownpng = PhotoImage(file="/home/martin/Projects/python/mywidgets/images/dropdown_22x22.png")
        self.chooseBtn = ttk.Button(self, image=self.dropdownpng, style="My.TButton",
                                    command=partial(self._callback, EditableGroupAction.choose))
        self.chooseBtn.grid(column=0, row=0, sticky=(S, E))
        ToolTip(self.chooseBtn, 'Gewünschten Datensatz aus einer Liste wählen')

        # Button "Edit"
        self.editpng = PhotoImage(file="/home/martin/Projects/python/mywidgets/images/edit_22x22.png")
        self.editBtn = ttk.Button(self, image=self.editpng, style="My.TButton",
                                  command=partial(self._callback, EditableGroupAction.edit))
        self.editBtn.grid(column=1, row=0, sticky=(S, E))
        ToolTip(self.editBtn, 'Daten ändern')

        # Button "New"
        self.newpng = PhotoImage(file="/home/martin/Projects/python/mywidgets/images/plus_22x22.png")
        self.newBtn = ttk.Button(self, image=self.newpng, style="My.TButton",
                                 command=partial(self._callback, EditableGroupAction.new))
        self.newBtn.grid(column=2, row=0, sticky=(S, E))
        ToolTip(self.newBtn, 'Neuen Datensatz anlegen')

        # Button "Save"
        self.savepng = PhotoImage(file="/home/martin/Projects/python/mywidgets/images/save_22x22.png")
        self.saveBtn = ttk.Button(self, image=self.savepng, style="My.TButton",
                                  command=partial(self._callback, EditableGroupAction.save))
        self.saveBtn.grid(column=3, row=0, sticky=(S, E))
        ToolTip(self.saveBtn, 'Änderungen speichern')

class EditableGroup(ttk.Frame, ABC):
    def __init__(self, parent, title: str = None):
        ttk.Frame.__init__(self, parent)
        self._functionBar = None
        self._groupLabel = None
        self._groupBox = None
        self._xgroupdata = None
        self._actionCallback = None

        padx = pady = 5
        self._functionBar = self._createLabelAndFunctionBar(title, padx, pady)
        self._functionBar.grid(column=0, row=0, sticky='swe', padx=padx, pady=0)
        #self._createFunctionBar(title, padx, pady)
        self._createGroupBox(padx, pady)
        self.createGroupBoxContent()
        self.columnconfigure(0, weight=1)

    def _createLabelAndFunctionBar(self, title:str, padx:int, pady:int):
        f = ttk.Frame(self)
        f.columnconfigure(1, weight=1)

        self._groupLabel = MyLabel(f, text=title, column=0, row=0, sticky='sw', pady=0)
        funcbar = EditSaveFunctionBar(f, self._onAction)
        funcbar.grid(column=1, row=0, sticky='se', pady=0)
        return f

    def _createFunctionBar(self, title: str, padx, pady) -> None:
        fb = ttk.Frame(self)
        fb.grid(column=0, row=0, sticky='ne', padx=padx, pady=0)
        #self._groupLabel = MyLabel(fb, text=title, column=0, row=0, sticky='sw', pady=0)

        # cbo = MyCombobox(fb)
        # cbo.setReadonly(True)
        # cbo.setItems(('item1', 'item2'))
        # cbo.grid(column=1, row=0, padx=(3, 0), pady=3, sticky='ne')
        # self._cbo = cbo

        buttonframe = self._createButtonFrame(fb)
        buttonframe.grid(column=2, row=0, padx=10, pady=(0, 3), sticky='nw')

        self._functionBar = fb

    def _createButtonFrame(self, parent):
        # Frame containing buttons:
        frame = ttk.Frame(parent)

        # Button style
        s = ttk.Style()
        s.theme_use('clam')
        s.configure("My.TButton",
                    padding=0,
                    relief="flat",
                    borderwith=0 )

        # Button "Choose"
        self.dropdownpng = PhotoImage(file="/home/martin/Projects/python/mywidgets/images/dropdown_22x22.png")
        self.chooseBtn = ttk.Button(frame, image=self.dropdownpng, style="My.TButton",
                                  command=partial(self._onAction, EditableGroupAction.choose))
        self.chooseBtn.grid(column=0, row=0, sticky=(N, W))
        ToolTip(self.chooseBtn, 'Gewünschten Datensatz aus einer Liste wählen')

        # Button "Edit"
        self.editpng = PhotoImage(file="/home/martin/Projects/python/mywidgets/images/edit_22x22.png")
        self.editBtn = ttk.Button(frame, image=self.editpng, style="My.TButton",
                                  command=partial(self._onAction, EditableGroupAction.edit))
        self.editBtn.grid(column=1, row=0, sticky=(N, W))
        ToolTip(self.editBtn, 'Daten ändern')

        # Button "New"
        self.newpng = PhotoImage(file="/home/martin/Projects/python/mywidgets/images/plus_22x22.png")
        self.newBtn = ttk.Button(frame, image=self.newpng, style="My.TButton",
                                 command=partial(self._onAction, EditableGroupAction.new))
        self.newBtn.grid(column=2, row=0, sticky=(N, W))
        ToolTip(self.newBtn, 'Neuen Datensatz anlegen')

        # Button "Save"
        self.savepng = PhotoImage(file="/home/martin/Projects/python/mywidgets/images/save_22x22.png")
        self.saveBtn = ttk.Button(frame, image=self.savepng, style="My.TButton",
                                  command=partial(self._onAction, EditableGroupAction.save))
        self.saveBtn.grid(column=3, row=0, sticky=(N, W))
        ToolTip(self.saveBtn, 'Änderungen speichern')

        return frame

    def _createGroupBox(self, padx, pady):
        gp = ttk.Frame(self, relief='groove', borderwidth=1)
        gp.grid(column=0, row=1, sticky='nswe', padx=padx, pady=0)
        self._groupBox = gp

    def _onAction(self, action: EditableGroupAction):
        if self._actionCallback:
            self._actionCallback(action)

    def registerActionCallback(self, cb):
        self._actionCallback = cb

    def setGroupTitle(self, title:str) -> None:
        self._groupLabel.setValue(title)

    def setComboItems(self, items: list or tuple):
        self._cbo.setItems(items)

    def getComboItems(self) -> list or tuple:
        return self._cbo.getItems()

    def getSelectedComboIndex(self) -> int:
        return self._cbo.getCurrentIndex()

    def getGroupBoxFrame(self) -> ttk.Frame:
        return self._groupBox

    @abstractmethod
    def createGroupBoxContent(self) -> None:
        # when you're adding your widgets to the box you will need to
        # specify the appropriate parent (this groupbox).
        # You can get it by calling self.getGroupBoxFrame()
        pass


class XAdresse:
    def __init__(self):
        self.name = ''
        self.vorname = ''
        self.strasse = ''
        self.plz = ''
        self.ort = ''
        self.telefon = ''
        self.email = ''

class AddressGroup(EditableGroup):
    def __init__(self, parent):
        EditableGroup.__init__(self, parent, 'Adressdaten')
        self._rbHerr = None
        self._rbFrau = None
        self._rbFirma = None
        self._teName = None
        self._teVorname = None
        self._teStrasse = None
        self._tePlz = None
        self._teOrt = None

    def createGroupBoxContent(self) -> None:
        box = self.getGroupBoxFrame()
        padx = pady = 3
        topy = 12
        row = 0

        v = IntVar()
        self._rbFrau = ttk.Radiobutton(box, text='Frau', variable=v, value=1)
        self._rbFrau.grid(column=1, row=row, sticky='nsw', padx=padx, pady=(topy, pady))

        self._rbHerr = ttk.Radiobutton(box, text='Herr', variable=v, value=2)
        self._rbHerr.grid(column=2, row=row, sticky='nsw', padx=padx, pady=(topy, pady))

        self._rbFirma = ttk.Radiobutton(box, text='Firma', variable=v, value=3)
        self._rbFirma.grid(column=3, row=row, sticky='nsw', padx=padx, pady=(topy, pady))

        row += 1
        l = MyLabel(box, text='Name:', column=0, row=row, sticky='ne',
                    padx=padx, pady=pady, align='e')
        self._teName = TextEntry(box, column=1, row=row, sticky='nwe', padx=padx, pady=pady)
        self._teName.grid(columnspan=3)

        row += 1
        MyLabel(box, text='ggf. Vorname:', column=0, row=row, sticky='ne',
                padx=padx, pady=pady, align='e')
        self._teVorname = TextEntry(box, column=1, row=row, sticky='nwe', padx=padx, pady=pady)
        self._teVorname.grid(columnspan=3)

        row += 1
        l = MyLabel(box, text='Straße:', column=0, row=row, sticky='ne',
                    padx=padx, pady=pady, align='e')
        self._teStrasse = TextEntry(box, column=1, row=row, sticky='nwe', padx=padx, pady=pady)
        self._teStrasse.setWidth(35)
        self._teStrasse.grid(columnspan=3)

        row += 1 #PLZ/Ort
        l = MyLabel(box, text='PLZ / Ort:', column=0, row=row, sticky='ne',
                    padx=padx, pady=pady, align='e')
        f = ttk.Frame(box)
        self._tePlz = TextEntry(f, column=0, row=0, sticky='nw', padx=padx, pady=pady)
        self._tePlz.setWidth(6)
        self._teOrt = TextEntry(f, column=1, row=0, sticky='ne', padx=padx, pady=pady)
        f.grid(column=1, columnspan=3, row=row, sticky='nswe', padx=0, pady=0)
        self._teOrt.setWidth(30)
        #self._teOrt.grid(columnspan=3)

    def getData(self) -> XAdresse:
        pass

class VermieterGroup(AddressGroup):
    def __init__(self, parent):
        AddressGroup.__init__(self, parent)
        self.setGroupTitle('Vermieterdaten')
        self._teSteuernummer = None #TextEntry

    def createGroupBoxContent(self) -> None:
        AddressGroup.createGroupBoxContent(self)
        box = self.getGroupBoxFrame()
        padx = pady = 3
        l = MyLabel(box, text='Steuernummer:', column=0, row=5, sticky='nw', padx=padx, pady=pady)
        self._teSteuernummer = TextEntry(box, column=1, row=5, sticky='nwe', padx=padx, pady=(pady, pady+3))
        self._teSteuernummer.grid(columnspan=3)

def test():
    from tkinter import  Tk
    from tkinter import ttk

    root = root = Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    style = ttk.Style()
    style.theme_use('clam')

    g = VermieterGroup(root)
    g.grid(column=0, row=0, sticky='nswe', padx=10, pady=10)


    root.mainloop()

if __name__ == '__main__':
    test()