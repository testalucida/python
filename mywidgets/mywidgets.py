from tkinter import *
from tkinter import ttk, scrolledtext
from tkinter import font
from abc import ABC, abstractmethod

#+++++++++++++++++++++++++++++++++++++++++++++++++++++

class ToolTip(object):
    '''
    create a tooltip for a given widget
    '''

    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.close)

    def enter(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(self.tw, text=self.text, justify='left',
                      background='white', relief='solid', borderwidth=1,
                      font=("arial", "10", "normal"))
        label.pack(ipadx=1)

    def close(self, event=None):
        if self.tw:
            self.tw.destroy()

#+++++++++++++++++++++++++++++++++++++++++++++++++++++

class GetterSetter(ABC):
    @abstractmethod
    def getValue(self) -> any:
        pass

    @abstractmethod
    def setValue(self, val: any) -> None:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

 #+++++++++++++++++++++++++++++++++++++++++++++++++++++

class TextEntry(ttk.Entry, GetterSetter):
    def getValue(self) -> any:
        return self.get()

    def setValue(self, val: str) -> None:
        self.clear()
        self.insert(0, val)

    def clear(self) -> None:
        self.delete(0, 'end')

# +++++++++++++++++++++++++++++++++++++++++++++++++++++

class ScrollableText(scrolledtext.ScrolledText, GetterSetter):
    def getValue(self) -> any:
        return self.get()

    def setValue(self, val: str) -> None:
        self.clear()
        self.insert('1.0', val)

    def clear(self) -> None:
        self.delete('1.0', 'end')

# +++++++++++++++++++++++++++++++++++++++++++++++++++++

class FloatEntry(ttk.Entry, GetterSetter):
    def __init__(self, parent):
        ttk.Entry.__init__(self, parent, validate="key")
        vcmd = (self.register(self.onValidate), '%P', '%S')
        # valid percent substitutions (from the Tk entry man page)
        # note: you only have to register the ones you need; this
        # example registers them all for illustrative purposes
        #
        # %d = Type of action (1=insert, 0=delete, -1 for others)
        # %i = index of char string to be inserted/deleted, or -1
        # %P = value of the entry if the edit is allowed
        # %s = value of entry prior to editing
        # %S = the text string being inserted or deleted, if any
        # %v = the type of validation that is currently set
        # %V = the type of validation that triggered the callback
        #      (key, focusin, focusout, forced)
        # %W = the tk name of the widget
        self['validatecommand'] = vcmd

    def onValidate(self, P, S):
        if S >= '0' and S <= '9':
            return True
        try:
            num = float(P)
            return True
        except:
            return False

    def setFloat(self, floatvalue: float) -> None:
        if not isinstance(floatvalue, float):
            raise ValueError("".join(str(floatvalue),
                                     " is not a valid float value"))
        self.clear()
        self.insert(0, str(floatvalue))

    def getValue(self) -> any:
        return self.get()

    def setValue(self, val: float) -> None:
        self.setFloat(val)

    def clear(self) -> None:
        self.delete(0, 'end')

#+++++++++++++++++++++++++++++++++++++++++++++++

class IntEntry(ttk.Entry, GetterSetter):
    def __init__(self, parent):
        ttk.Entry.__init__(self, parent, validate="key")
        vcmd = (self.register(self.onValidate), '%P', '%S')
        # valid percent substitutions (from the Tk entry man page)
        # note: you only have to register the ones you need; this
        # example registers them all for illustrative purposes
        #
        # %d = Type of action (1=insert, 0=delete, -1 for others)
        # %i = index of char string to be inserted/deleted, or -1
        # %P = value of the entry if the edit is allowed
        # %s = value of entry prior to editing
        # %S = the text string being inserted or deleted, if any
        # %v = the type of validation that is currently set
        # %V = the type of validation that triggered the callback
        #      (key, focusin, focusout, forced)
        # %W = the tk name of the widget
        self['validatecommand'] = vcmd

    def onValidate(self, P, S):
        if S >= '0' and S <= '9':
            return True

        return False

    def setInt(self, intvalue: int) -> None:
        if not isinstance(intvalue, int):
            raise ValueError("".join(str(intvalue),
                                     " is not a valid float value"))
        self.clear()
        self.insert(0, str(intvalue))

    def getValue(self) -> any:
        return self.get()

    def setValue(self, val: int) -> None:
        self.setInt(val)

    def clear(self) -> None:
        self.delete(0, 'end')


#+++++++++++++++++++++++++++++++++++++++++++++++

class MyCombobox(ttk.Combobox, GetterSetter):
    def getCurrentIndex(self) -> int:
        return self.current()

    def setIndex(self, idx: int) -> None:
        self.current(idx)

    def getValue(self) -> any:
        return self.get()

    def setValue(self, val: any) -> None:
        self.set(val)

    def clear(self) -> None:
        self.set(0)

#+++++++++++++++++++++++++++++++++++++++++++++++

class TableView(ttk.Treeview):
    def __init__(self, parent):
        ttk.Treeview.__init__(self, parent, show='headings')
        self.grid(sticky='nswe')
        self.bind('<Button-1>', self._onTableRowSelected)
        self._selectionCallback = None

    def setColumns(self, columnNames: list):
        self.heading("#0", text='Nr', anchor='w')
        self.column('#0', anchor='w', width=22, stretch=0)
        self['columns'] = columnNames
        for col in columnNames:
            self.heading(col, text=col)
            self.column(col, anchor='w', width=100)

    def registerSelectionCallback(self, callback):
        """
        the function or method to register for callbacks has to have
        2 arguments: event and list.
        event: the select event
        list: containing dictionaries with keys 'columnname' and 'cellvalue'.
        values are provided with data of selected row
        """
        self._selectionCallback = callback

    def setColumnWidth(self, columnName: str, w: int):
        self.column(columnName, width=w)

    def setColumnStretch(self, columnName: str, stretch: bool) -> None:
        stretchable = 1 if stretch else 0
        self.column(columnName, stretch=stretchable)

    def setColumnsHidden(self, columnNameList: list) -> None:
        #exclude columns in columnNameList from treeview's 'columns'
        #and set the new list as 'displaycolumns'
        dcols = [x for x in self['columns'] if x not in columnNameList]
        self['displaycolumns'] = dcols

    def showRowNumbers(self, yesno: bool):
        if yesno:
            self['show'] = 'tree headings'
        else:
            self['show'] = 'headings'

    def alignColumn(self, columnName: str, anchor: str) -> None:
        self.column(columnName, anchor=anchor)

    def makeColumnWidthFit(self, columnName: str) -> None:
        self.setColumnStretch(columnName, False)
        f = font.Font(family='arial', size=13) # todo: how to get actual font??
        cols = self['columns'] #cols is a tuple containing column headings
        colnr = cols.index(columnName)
        (maxw, h)  = (f.measure(columnName), f.metrics("linespace"))

        itemIds = self.get_children() # all row-Item-Identifiers ['I0001', 'I0002',..]
        for id in itemIds: #iterate through all rows
            item: dict = self.item(id) #item identifies a row with all its attributes
            val = item['values'][colnr]
            #val represents a cell value.
            #measure it and store its width into colinfolist
            (w, h) = (f.measure(str(val)), f.metrics("linespace"))
            if w > maxw:
                maxw = w

        #self.column(colnr)['width'] = maxw
        self.setColumnWidth(columnName, maxw)

    def updateRow1(self, row: int, colName: str, newVal: any) -> None:
        """
        changes the value of a given column's cell. The cell will be identified
        by its row number and column name (attribut 'heading')
        :param row: row number, starting with 0
        :param colName: valid 'heading' within 'columns'
        :param newVal: the value the cell is to be set to
        :return: None
        """
        itemIds = self.get_children()
        r = 0
        for id in itemIds:
            if r == row:
                self.updateRow2(id, colName, newVal)
                return
            r += 1
        raise ValueError(''.join(('no such row: ', row )))

    def updateRow2(self, itemId: str, colName: str, newVal: any) -> None:
        """
        changes the value of a given column's cell.
        The cell is identified by the rows itemId and
        the columns name (attribut 'heading')
        :param itemId: internal id like 'I001'. This determines the row.
        You get this itemId as one of the informations in an event object
        or by iterating over the tables rows by self.get_children().
        :param colName: the displayed heading of the column to be changed
        :param newVal:
        :return:
        """
        self.set(itemId, colName, newVal)

    def appendRows(self, data: list) -> None:
        """
        provides this tableview with one or more rows of data.
        :param data: contains one or more dictionaries, each
            representing the data for one table row.
            The key values correspond to tableview's headings.
        :return:
        """
        #first delete all previous items:
        self.clear()
        cols = self['columns'] #list of headings of this TableView
        for dic in data:
            values = list()
            for col in cols:
                values.append(dic[col])
            self.appendRow(values)

    def clear(self) -> None:
        #delete all rows
        children = self.get_children()
        for child in children:
            self.delete(child)

    def appendRow(self, data: list):
        rowNr = self.getRowCount() + 1
        self.insert('', 'end', text=str(rowNr), values=data)

    def getAllRows(self, item='') -> list:
        children = self.get_children((item))
        for child in children:
            children += self.getAllRows(child)
        return children

    def getRowCount(self) -> int:
        return len(self.getAllRows())

    def getRowValues(self, iid: str) -> list:
        row = self.item(iid)
        return row['values']

    def getColumnNames(self) -> list:
        return self['columns']

    def _onTableRowSelected(self, evt: Event) -> None:
        """
        called when a row has been selected.
        creates a list of dictionaries with keys 'columnname' and 'cellvalue'
        and values provided with the selected row's column values.
        Invokes the registered SelectionCallback method.
        :param evt:  select event
        :return:  list of dictionaries
        """
        colnames = self.getColumnNames()
        iid = self.identify('item', evt.x, evt.y)
        if iid == '': #column header clicked
            return

        rowvalues = self.getRowValues(iid)
        if len(colnames) != len(rowvalues):
            pass
        li = list()
        dic = dict()
        for c in range(len(colnames)):
            dic['columnname'] = colnames[c]
            dic['cellvalue'] = rowvalues[c]
            li.append(dic)
        if self._selectionCallback:
            self._selectionCallback(evt, li)

#++++++++++++++++++++++++++++++++++++++++++++++++

class Kannweg:
    def __init__(self):
        print("Kannweg instance created.")

    def setVal(self, val: str) -> None:
        self._val = val
        print("Kannweg instance set to: ", val)

    def getVal(self):
        return self._val