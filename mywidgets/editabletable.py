from tkinter import *
from tkinter import ttk, messagebox
from mywidgets import TableView, ToolTip, MyText
from actions import Action
#from dataclasses import dataclass #comes with python 3.7

#xxxdefinition.json
"""
example for defining a xxx.json structure for usage in EditableTable
The file's ending must be .json
------------------------------------------------------------------
{
  "_comment": "check json using https://jsonformatter.curiousconcept.com/",
  "columns": [
    {
      "_comment": "ID der Satzes in der Tabelle sonstige_ein_aus",
      "heading": "ID",
      "isvisible": false,
      "width": -1,
      "dbname": "sea_id",
      "editwidget": null
    },
    {
      "_comment": "Jahr, in dem diese Ein-/Auszahlung veranlagt wird",
      "heading": "VJ",
      "isvisible": true,
      "width": 4,
      "dbname": "vj",
      "editwidget": {
        "class": "mywidgets.MyCombobox",
        "choice_values": [
          2018,
          2019,
          2020,
          2021,
          2022
        ],
        "init_value": 2019,
        "width": 5,
        "wstretch": false,
        "height": -1
      }
    },
    {
      "_comment": "Betrag",
      "heading": "Betrag",
      "isvisible": true,
      "width": -1,
      "dbname": "betrag",
      "editwidget": {
        "class": "mywidgets.FloatEntry",
        "choice_values": null,
        "init_value": null,
        "width": 8,
        "wstretch": false,
        "height": -1
      }
    },
    {
      "_comment": "Art der Ein-/Auszahlung",
      "heading": "Art",
      "isvisible": true,
      "width": -1,
      "dbname": "art",
      "editwidget": {
        "class": "mywidgets.MyCombobox",
        "choice_values": [
          "Grundsteuer",
          "Hausgeldnachzahlung (Eigentümer->Verw.)",
          "Hausgeldrückzahlung (Verw.->Eigentümer)",
          "Nebenkostennachzahlung (Mieter->Verm.)",
          "Nebenkostenrückzahlung (Verm.->Mieter)",
          "Sonderumlage",
          "Ablöse"
        ],
        "init_value": "'Nebenkostennachzahlung (Mieter->Verm.)'",
        "width": 41,
        "wstretch": false,
        "height": -1
      }
    },
    {
      "_comment": "Zyklus der Ein-/Auszahlung",
      "heading": "Zyklus",
      "isvisible": true,
      "width": -1,
      "dbname": "zyklus",
      "editwidget": {
        "class": "mywidgets.MyCombobox",
        "choice_values": [
          "einmalig",
          "jährlich"
        ],
        "init_value": "'einmalig'",
        "width": 16,
        "wstretch": false,
        "height": -1
      }
    },
    {
      "_comment": "Bemerkung zur Ein-/Auszahlung",
      "heading": "Bemerkung",
      "isvisible": true,
      "width": -1,
      "dbname": "bemerkung",
      "editwidget": {
        "class": "mywidgets.MyText",
        "choice_values": null,
        "init_value": null,
        "width": 35,
         "wstretch": true,
        "height": 2
      }
    }
  ]
}
"""

class Mappings:
    def __init__(self):
        self._mappingList:list = []

    def add(self, tvcolname:str, dbcolname:str, isvisible:bool, iseditable:bool):
        dic = {"heading": tvcolname, "dbname": dbcolname,
               "isvisible": isvisible, "iseditable": iseditable}
        self._mappingList.append(dic)

    def getColumnCount(self) -> int:
        return len(self._mappingList)

    def getColumnHeaders(self) -> list:
        headers = []
        for mapping in self._mappingList:
            headers.append(mapping['heading'])
        return headers

    def getHeading(self, dbname:str) -> str:
        for mapping in self._mappingList:
            if mapping['dbname'] == dbname:
                return mapping['heading']
        raise ValueError(''.join(('dbname ', dbname, ' not found in mappings.')))

    def getDbColumnName(self, heading:str) -> str:
        for mapping in self._mappingList:
            if mapping['heading'] == heading:
                return mapping['dbname']
        raise ValueError(''.join(('heading ', heading, ' not found in mappings.')))

    def getHiddenColumns(self) -> list:
        l = []
        for mapping in self._mappingList:
            if mapping['isvisible'] == False:
                l.append(mapping['heading'])
        return l

    def getMappings(self) -> dict:
        mapped = {}
        for mapping in self._mappingList:
            mapped[mapping['dbname']] = mapping['heading']
        return mapped

# #+++++++++++++++++++++++++++++++++++++++++++++++
#
# class ActionCallbackResponse:
#     def __init__(self, title: str, msg: str):
#         self._title = title
#         self._msg = msg
#
#     def getTitle(self): return self._title
#
#     def getMessage(self): return self._msg
#
#+++++++++++++++++++++++++++++++++++++++++++++++

class GenericEditableTable(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._mappings = Mappings()
        self._tv = None
        self._edit = None
        self._actionCallback = None
        self._rowEditingId = None
        self._fitlist = list()

    def configureTable(self, columnDefs: list):
        editwidgetlist = []
        for col in columnDefs:
            editwidget = col['editwidget']
            isEditable = False if editwidget is None else True
            self._mappings.add(col['heading'], col['dbname'],
                               col['isvisible'], isEditable)
            if editwidget:
                editwidget['label'] = col['heading']
                editwidget['dbname'] = col['dbname']
                editwidgetlist.append(editwidget)
        #create TableView and EditRow:
        self._createGui(editwidgetlist)

        for col in columnDefs:
            heading = col['heading']
            width = col['width']
            if width > 0:
                self._tv.setColumnWidth(heading, width)
            align = col['align']
            if align: #translate from align to 'anchor'
                if align == 'left': align = 'w'
                elif align == 'right': align = 'e'
                self._tv.alignColumn(heading, align)
            fit = col['fit']
            if fit:
                self._fitlist.append(heading)
            stretch = col['stretch']
            if stretch:
                self._tv.setColumnStretch(heading, stretch)

        self._tv.registerSelectionCallback(self.tvselectionCallback)
        self._edit.registerActionCallback(self.editRowCallback)

    def _createGui(self, widgets: list) -> None:
        """
        create the GUI: a Tableview at top, a GernericEditRow below
        """
        self._tv = TableView(self)
        self._tv.setColumns(self._mappings.getColumnHeaders())
        colNameList = self._mappings.getHiddenColumns()
        self._tv.setColumnsHidden(colNameList)
        self._tv.grid(column=0, row=0, sticky='nswe')

        self._edit = GenericEditRow(self, widgets)
        self._edit.grid(column=0, row=1, sticky='nswe', padx=3, pady=3)

        # self.bind('<FocusIn>', self.onFocus)
        # self._tv.bind('<FocusIn>', self.onFocus)

    def onFocus(self, evt):
        print("got focus: ", evt.widget)

    def setRows(self, data: list) -> None:
        """
        sets one or more rows. Existing rows will previously be removed.
        :param data:
        :return:
        """
        self.clear()
        self.appendRows(data)

    def appendRows(self, data: list) -> None:
        #data contains one or more dictionaries using dbcolumn-names for keys.
        #we have to create a copy of that list using dictionaries whose keys are
        #tvcolumn-names.
        mapped = self._mappings.getMappings()
        newlist = list()
        for row in data:
            d = dict()
            for k, v in row.items():
                try:
                    d[mapped[k]] = v
                except:
                    pass
            newlist.append(d)
        self._tv.appendRows(newlist)
        self._checkFitlist()

    def appendRow(self, data: dict) -> None:
        self._tv.appendRow(data)
        self._checkFitlist()

    def _checkFitlist(self):
        for colName in self._fitlist:
            self._tv.makeColumnWidthFit(colName)

    def getRowValuesAsDict(self, itemId: str) -> dict:
        """
        get values of the table row (as opposite of the edit row)
        :param itemId: identification of row
        :return: a dictionary with columns's dbname as key and
        its appropriate value.
        """
        colnames = self._tv.getColumnNames()
        rowvalues = self._tv.getRowValues(itemId)
        dic = dict()
        for n in range(len(colnames)):
            dbname = self._mappings.getDbColumnName(colnames[n])
            dic[dbname] = rowvalues[n]
        return dic

    def updateRow2(self, itemId: str, colName: str, newVal: any) -> None:
        """
        see TableView.updateRow2()
        """
        self._tv.updateRow2(itemId, colName, newVal)

    def updateRow1(self, row: int, colName: str, newVal: any) -> None:
        """
        see TableView.updateRow1()
        """
        self._tv.updateRow1(row, colName, newVal)

    def setColumnStretch(self, columnName: str, stretchable: bool) -> None:
        self._tv.setColumnStretch(columnName, stretchable)

    def makeColumnWidthFit(self, columnName: str) -> None:
        self._tv.makeColumnWidthFit(columnName)

    def alignColumn(self, columnName: str, anchor: str) -> None:
        self._tv.alignColumn(columnName, anchor)

    def setFocus(self):
        self._tv.focus()

    def selectRow(self, rownr: int) -> None:
        #self._tv.focus_set()
        self._tv.selectRow(rownr)

    def tvselectionCallback(self, evt: Event, trigger: str, iid: str, rowdata: list) -> None:
        """
        transfer values of selected row into the edit fields of the
        assigned GenericEditRow
        :param evt: Select event
        :param trigger: one of 'leftmousesingle', 'leftmousedouble',
        'returnkey', 'treeviewselect'
        iid: identification of selected row
        :param rowdata: data of selected row: list of lists containing column headers and values
        :return: None
        """
        if trigger == 'leftmousedouble' or trigger == 'returnkey':
            for col in rowdata:
                dbname = self._mappings.getDbColumnName(col[0])
                self._edit.setValue(dbname, col[1])

            self._rowEditingId = iid

    def registerActionCallback(self, callbackFnc):
        self._actionCallback = callbackFnc

    def editRowCallback(self, action: int, values: dict) -> None:
        """
        callback controller
        :param action: OK, Cancel, Delete
        :param values: values of the edit fields in the edit row
        :return: None
        """
        if self._actionCallback:
            self._actionCallback(action, self._rowEditingId,
                                 values,
                                 self.getRowValuesAsDict(self._rowEditingId))

    def askyesno(self, title: str, msg: str, withWarnIcon: bool = False) -> bool:
        if withWarnIcon:
            return messagebox.askyesno(title, msg, icon='warning')
        else:
            return messagebox.askyesno(title, msg)

    def showInfo(self, title: str, msg: str):
        messagebox.showinfo(title, msg)

    def showError(self, title: str, msg: str):
        messagebox.showerror(title, msg)

    def clear(self):
        self._tv.clear()
        self._edit.clear()
        self._rowEditingId = None

    def cancelEditing(self):
        self._edit.clear()
        self._rowEditingId = None

    def deleteRow(self, itemId: str):
        self._tv.delete(self._rowEditingId)
        self._edit.clear()
        self._rowEditingId = None

#+++++++++++++++++++++++++++++++++++++++++++++++

class GenericEditRow(ttk.Frame):
    def __init__(self, parent, widgetDefs: list):
        ttk.Frame.__init__(self, parent)
        self._lostList = list()
        self._actionCallback = None
        self._createUI(widgetDefs)
        for col in range(len(widgetDefs)):
            if widgetDefs[col]['wstretch'] == True:
                self.columnconfigure(col, weight=1)

    def _createUI(self, widgetList: list) -> None:
        mypadx = 3
        mypady = 3
        self['relief'] = "sunken"

        col = 0
        for w in widgetList: #each w is a dictionary
            #create the label:
            labeltext = w['label']
            lbl = ttk.Label(self, text=labeltext)
            lbl.grid(column=col, row=0, sticky='nwe', padx=mypadx, pady=mypady)

            #instantiate the desired class for editing
            inst = self._createInstance(self, w['class'])

            #set instance's myId (custom attribute):
            inst.setMyId( w['dbname'])

            #if we have a Combobox check for choice_values:
            choice_values = w['choice_values']
            if choice_values:
                inst['values'] = choice_values

            #set initial value?
            initValue = w['init_value']
            if initValue:
                inst.setValue(initValue)

            width = w['width']
            if width > -1:
                inst['width'] = width

            height = w['height']
            if height > -1:
                inst['height'] = height

            inst.grid(column=col, row=1, sticky='nwe', padx=mypadx, pady=mypady)
            col += 1

        self._createButtons(col, mypadx, mypady)

    def _createButtons(self, column: int, padx: int, pady: int):
        # Frame containing buttons:
        btnFrame = ttk.Frame(self)
        btnFrame.grid(column=column, row=0, rowspan=2, sticky=(S, W), padx=padx, pady=3)

        # Button style
        s = ttk.Style()
        s.theme_use('clam')
        s.configure("My.TButton",
                    padding=0,
                    relief="flat",
                    borderwith=0 )

        # Button "Übernehmen"
        self.okpng = PhotoImage(file="/home/martin/Projects/python/mywidgets/images/ok_25x25.png")
        self.okBtn = ttk.Button(btnFrame, image=self.okpng, style="My.TButton",
                                command=self._onOk)
        self.okBtn.grid(column=0, row=0, sticky=(N, W))
        ToolTip(self.okBtn, 'Werte in Tabelle übernehmen')

        # Button "Cancel"
        self.cancelpng = PhotoImage(file="/home/martin/Projects/python/mywidgets/images/reset_25x25.png")
        self.cancelBtn = ttk.Button(btnFrame, image=self.cancelpng, style="My.TButton",
                                   command=self._onCancel)
        self.cancelBtn.grid(column=1, row=0, sticky=(N, W))
        ToolTip(self.cancelBtn, 'Änderung abbrechen')

        # Button "Löschen"
        self.binpng = PhotoImage(file="/home/martin/Projects/python/mywidgets/images/bin_25x25_3.png")
        self.deleteBtn = ttk.Button(btnFrame, image=self.binpng, style="My.TButton",
                                    command=self._onDelete)
        self.deleteBtn.grid(column=2, row=0, sticky=(N, W))
        ToolTip(self.deleteBtn, 'Diesen Satz aus der Tabelle löschen')

    def _createInstance(self, parent: ttk.Frame, cls: str) -> any: #returns an instance of desired class
        parts = cls.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m(parent)

    def _onOk(self):
        self._callback(Action.OK)

    def _onDelete(self):
        self._callback(Action.DELETE)

    def _onCancel(self):
        self._callback(Action.CANCEL)

    def _callback(self, action):
        if self._actionCallback:
            self._actionCallback(action, self.getValues())

    def registerActionCallback(self, actionCallback) -> None:
        """
        register a method or function to be called when one of the three
        action buttons (ok, delete, cancel) is pressed
        :param actionCallback:
        :return:
        """
        self._actionCallback = actionCallback

    def getValues(self) -> dict:
        """
        :return: A dictionary with key = myID and its corresponding value.
        Each edit field is represented by an dictionary item.
        """
        dic = dict()
        for entry in self._lostList:
            dic[entry[0]] = entry[1]
        for obj in self.children.values():
            if hasattr(obj, 'getMyId'):
                dic[obj.getMyId()] = obj.getValue()
        return dic

    def setValue(self, widgetId: str, newValue: any) -> None:
        for obj in self.children.values():
            if hasattr(obj, 'getMyId'): # and obj.myId == widgetId:
                if obj.getMyId() == widgetId:
                    obj.setValue(newValue)
                    return
        #we don't know the given widgetId. We store it and give it back later on.
        self._lostList.append((widgetId, newValue))

    def clear(self):
        for obj in self.children.values():
            if hasattr(obj, 'getMyId'):
                obj.clear()
        self._lostList.clear()
