from tkinter import *
from tkinter import ttk
from mywidgets import TableView, ToolTip
#from dataclasses import dataclass #comes with python 3.7

#xxxdefinition.json
"""
example for defining a xxx.json structure for usage in EditableTable
The file's ending must be .json
------------------------------------------------------------------
{
  "_comment": "check json using https://jsonformatter.curiousconcept.com/",
  "columns":[
    {
      "_comment": "ID des Satzes in der Tabelle mtl_ein_aus",
      "heading": "ID",
      "isvisible": false,
      "width": -1,
      "dbname": "mea_id",
      "editwidget": null
    },
    {
      "_comment": "Gültig-Ab-Datum dieses Satzes",
      "heading": "Gültig ab",
      "isvisible": true,
      "width": -1,
      "dbname": "gueltig_ab",
      "editwidget":
        {
          "class": "mycalendar.DateEntry",
          "choice_values": null,
          "set": "setDate($)",
          "init_value": null,
          "delete": "clear()",
          "width": 12,
          "wstretch": false,
          "height": -1
        }
    },
    {
      "_comment": "Netto-Miete",
      "heading": "Netto-Miete",
      "isvisible": true,
      "width": -1,
      "dbname": "miete_netto",
      "editwidget":
        {
          "class": "mywidgets.FloatEntry",
          "choice_values": null,
          "set": "setFloat($)",
          "init_value": null,
          "delete": "clear()",
          "width": 8,
          "wstretch": false,
          "height": -1
        }
    },
    {
      "_comment": "Nebenkosten-Abschlag",
      "heading": "NK-Abschlag",
      "isvisible": true,
      "width": -1,
      "dbname": "nk_abschlag",
      "editwidget":
        {
          "class": "mywidgets.FloatEntry",
          "choice_values": null,
          "set": "setFloat($)",
          "init_value": null,
          "delete": "clear()",
          "width": 8,
          "wstretch": false,
          "height": -1
        }
    },
    {
      "_comment": "Hausgeld-Abschlag netto - ohne Zuführung Rücklage (Zahlung Vermieter an Verwalter)",
      "heading": "HG-Abschl.netto",
      "isvisible": true,
      "width": -1,
      "dbname": "hg_netto_abschlag",
      "editwidget":
        {
          "class": "mywidgets.FloatEntry",
          "choice_values": null,
          "set": "setFloat($)",
          "init_value": null,
          "delete": "clear()",
          "width": 8,
          "wstretch": false,
          "height": -1
        }
    },
    {
      "_comment": "Zuführung Rücklage (Zahlung Vermieter an Verwalter)",
      "heading": "Rücklage",
      "isvisible": true,
      "width": -1,
      "dbname": "ruecklage_zufuehr",
      "editwidget":
        {
          "class": "mywidgets.FloatEntry",
          "choice_values": null,
          "set": "setFloat($)",
          "init_value": null,
          "delete": "clear()",
          "width": 8,
          "wstretch": false,
          "height": -1
        }
    },
    {
      "_comment": "Bemerkung",
      "heading": "Bemerkung",
      "isvisible": true,
      "width": -1,
      "dbname": "bemerkung",
      "editwidget":
        {
          "class": "tkinter.scrolledtext.ScrolledText",
          "choice_values": null,
          "set": "insert(0, $)",
          "init_value": null,
          "delete": "delete('1.0', 'end')",
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

#+++++++++++++++++++++++++++++++++++++++++++++++

class GenericEditableTable(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._mappings = Mappings()
        self._tv = None
        self._edit = None

    def configureTable(self, columnDefs: list):
        editwidgetlist = []
        for col in columnDefs:
            editwidget = col['editwidget']
            isEditable = False if editwidget is None else True
            self._mappings.add(col['heading'], col['dbname'], col['isvisible'], isEditable)
            if editwidget:
                editwidget['label'] = col['heading']
                editwidget['dbname'] = col['dbname']
                editwidgetlist.append(editwidget)

        self._createGui(editwidgetlist)
        for col in columnDefs:
            width = col['width']
            if width > 0:
                self._tv.setColumnWidth(col['heading'], width)

        self._tv.registerSelectionCallback(self.tvselectionCallback)

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

    def appendRows(self, data: list) -> None:
        #data contains one or more dictionaries using dbcolumn-names for keys.
        #we have to create a copy of list using dictionaries whose keys are
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

    def tvselectionCallback(self, evt: Event, rowdata: list) -> None:
        """
        transfer values of selected row into the edit fields of the
        assigned GenericEditRow
        :param evt: Select event
        :param row: data of selected row
        :return: None
        """
        for dic in rowdata:
            dbname = self._mappings.getDbColumnName(dic['columnname'])
            self._edit.setValue(dbname, dic['cellvalue'])


#+++++++++++++++++++++++++++++++++++++++++++++++

class GenericEditRow(ttk.Frame):
    def __init__(self, parent, widgetDefs: list):
        ttk.Frame.__init__(self, parent)
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

            #instantiate the desired class for input and store a reference in itself:
            inst = self._createInstance(self, w['class'])

            #set instance's myId (custom attribute):
            inst.myId = w['dbname'] # w.myId

            #if we have a Combobox check for choice_values:
            choice_values = w['choice_values']
            if choice_values:
                inst['values'] = choice_values

            #set-method:
            #inst.setmethod = "".join((w['set'], '(', w['set_args'], ')'))
            inst.setmethod = w['set']
            #looks like so: 'insert(0, $)'
            # Note: only one $ may be given
            # Note: string args must be given in quotes

            #set initial value?
            initValue = w['init_value']
            if initValue:
                setmeth = inst.setmethod.replace('$', str(initValue))
                invocation_code = ''.join(('inst.', setmeth ))
                eval(invocation_code)

            #delete-method (to clear widget's input)
            deletemethod = w['delete']
            if deletemethod:
                inst.deletemethod = deletemethod

            width = w['width']
            if width > -1:
                inst['width'] = width

            height = w['height']
            if height > -1:
                inst['height'] = height

            inst.grid(column=col, row=1, sticky='nwe', padx=mypadx, pady=mypady)
            col += 1

            inst.inst = inst # w.inst

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
        self.okBtn = ttk.Button(btnFrame, image=self.okpng, style="My.TButton")
        self.okBtn.grid(column=0, row=0, sticky=(N, W))
        ToolTip(self.okBtn, 'Werte in Tabelle übernehmen')

        # Button "Reset"
        self.resetpng = PhotoImage(file="/home/martin/Projects/python/mywidgets/images/reset_25x25.png")
        self.resetBtn = ttk.Button(btnFrame, image=self.resetpng, style="My.TButton")
        self.resetBtn.grid(column=1, row=0, sticky=(N, W))
        ToolTip(self.resetBtn, 'Änderungen zurücksetzen')

        # Button "Löschen"
        self.binpng = PhotoImage(file="/home/martin/Projects/python/mywidgets/images/bin_25x25_3.png")
        self.deleteBtn = ttk.Button(btnFrame, image=self.binpng, style="My.TButton")
        self.deleteBtn.grid(column=2, row=0, sticky=(N, W))
        ToolTip(self.deleteBtn, 'Diesen Satz aus der Tabelle löschen')

    def _createInstance(self, parent: ttk.Frame, cls: str) -> any: #returns an instance of desired class
        parts = cls.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m(parent)

    def getValues(self) -> list:
        """
        :return: a list of dictionaries. Each dictionary represents an
        edit field. Its keys are 'myId' and 'value'.
        """
        retlist = list()
        dic = dict()
        for obj in self.children.values():
                if hasattr(obj, 'myId'):
                    dic['myId'] = obj.myId
                    dic['value'] = obj.getValue()


    def setValue(self, widgetId: str, newValue: any) -> None:
        for obj in self.children.values():
                if hasattr(obj, 'myId'): # and obj.myId == widgetId:
                    if obj.myId == widgetId:
                        # do we have to delete the old value?
                        if hasattr(obj, 'delete'):
                            invocation_code = ''.join(('obj.', obj.deletemethod))
                            eval(invocation_code)
                        newValue = ''.join(("'", newValue, "'"))
                        setmeth = obj.setmethod.replace('$', newValue)
                        invocation_code = ''.join(('obj.', setmeth))
                        try:
                            eval(invocation_code)
                        except:
                            print("Exception on eval(", invocation_code, "): ",
                                  sys.exc_info()[0], sys.exc_info()[1])
