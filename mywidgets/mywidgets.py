from tkinter import *
from tkinter import ttk, scrolledtext, Text
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
    _myId: str

    @abstractmethod
    def getValue(self) -> any:
        pass

    @abstractmethod
    def setValue(self, val: any) -> None:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

    def getMyId(self) -> str:
        return  self._myId

    def setMyId(self, myId: str) -> None:
        self._myId = myId

#+++++++++++++++++++++++++++++++++++++++++++++++++++++

class ConvenianceMethods:

    def setWidth(self, w: int) -> None:
        self['width'] = w

    def setStyle(self, stylename: str) -> None:
        self['style'] = stylename

    def setBackground(self, stylename: str, color: str) -> None:
        style = ttk.Style()
        style.configure(stylename, fieldbackground=color)
        self['style'] = stylename

    def setForeground(self, stylename: str, color: str) -> None:
        style = ttk.Style()
        style.configure(stylename, foreground=color)
        self['style'] = stylename

    def setFont(self, font: str) -> None:
        """
        sets the font of this widget
        :param font: font given in a string like so: 'Helvetica 18 bold'
        :return: None
        """
        self.configure(font=font)

    def setReadonly(self, readonly: bool):
        state = 'readonly' if readonly else 'normal'
        self['state'] = state

    def setEnabled(self, enabled: bool):
        self['state'] = 'normal' if enabled else 'disabled'

    def setTextPadding(self, name: str, *pads) -> None:
        """
        sets the padding around the text
        :param name: name of the style, e.g. 'My.TCombobox'
        :param pads: first arg: pad left, secnd arg: pad top and so on.
        if only one pad arg is given it will be used for all 4 sides.
        if two pad args are given the first one will be used for pad left
        and pad right, the second for pad top and pad bottom.
        if three pad args are given, the first and the third will be used for pad left
        and pad right, the second will be used for pad top and pad bottom.
        :return: None
        """
        padlist = list()
        for pad in pads:
            padlist.append(pad)
        style = ttk.Style()
        style.configure(name, padding = padlist)
        self['style'] = name


#+++++++++++++++++++++++++++++++++++++++++++++++++++++

class MyLabel(ttk.Label, ConvenianceMethods):
    def __init__(self, parent,
                 text: str = None,
                 column: int = None, row: int = None,
                 sticky: str = None, anchor: str = None,
                 padx:int = None, pady: int = None ):
        ttk.Label.__init__(self, parent, text=text)
        ConvenianceMethods.__init__(self)
        if not column is None and column >= 0:
            self.grid(column=column)
        if not row is None and row >= 0:
            self.grid(row=row)
        if sticky:
            self.grid(sticky=sticky)
        if anchor:
            self['anchor'] = anchor
        if padx:
            self.grid(padx=padx)
        if pady:
            self.grid(pady=pady)

    def setBackground(self, stylename: str, color: str) -> None:
        ttk.Style().configure(stylename, background=color)
        self['style'] = stylename

    def setValue(self, value: str) -> None:
        self['text'] = value

#++++++++++++++++++++++++++++++++++++++++++++++++++++++

class ModifyTracer:
    def __init__(self):
        self._sv = StringVar()
        self._sv.trace("w", self._onModify)
        self['textvariable'] = self._sv
        self._cbfnc = None

    def registerModifyCallback(self, cbfnc) -> None:
        self._cbfnc = cbfnc

    def _onModify(self, name, index, mode):
        if self._cbfnc:
            #print('ModifyTracer._onModify: TextEntry modified - performing callback')
            self._cbfnc(self, name, index, mode)
#++++++++++++++++++++++++++++++++++++++++++++++++++++++

class TextEntry(ttk.Entry, GetterSetter, ConvenianceMethods, ModifyTracer):
    def __init__(self, parent,
                 column: int = None, row: int = None,
                 sticky: str = None,
                 padx:int = None, pady: int = None ):
        ttk.Entry.__init__(self, parent)
        ConvenianceMethods.__init__(self)
        ModifyTracer.__init__(self)
        if not column is None and column >= 0:
            self.grid(column=column)
        if not row is None and row >= 0:
            self.grid(row=row)
        if sticky:
            self.grid(sticky=sticky)
        if padx:
            self.grid(padx=padx)
        if pady:
            self.grid(pady=pady)

    def getValue(self) -> any:
        return self.get()

    def setValue(self, val: str) -> None:
        self.clear()
        if val:
            self.insert(0, val)

    def clear(self) -> None:
        self.delete(0, 'end')

# +++++++++++++++++++++++++++++++++++++++++++++++++++++

class MyText(Text, GetterSetter):
    def __init__(self, parent):
        Text.__init__(self, parent)
        self._myId = None

    def getValue(self) -> any:
        return self.get('1.0', 'end')

    def setValue(self, val: str) -> None:
        self.clear()
        if val:
            self.insert('1.0', val)

    def clear(self) -> None:
        self.delete('1.0', 'end')

# +++++++++++++++++++++++++++++++++++++++++++++++++++++

class FloatEntry(ttk.Entry, GetterSetter, ConvenianceMethods, ModifyTracer):
    def __init__(self, parent):
        ttk.Entry.__init__(self, parent, validate="key")
        ConvenianceMethods.__init__(self)
        ModifyTracer.__init__(self)
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
        self.setAlign('right')
        self.setTextPadding('Float.TEntry', 1, 1, 3, 1)

    def onValidate(self, P, S):
        if S >= '0' and S <= '9':
            return True
        try:
            num = float(P)
            return True
        except:
            return False

    def setAlign(self, alignment: str):
        """
        sets the text alignment. Default is 'right'
        :param alignment: one of ('left', 'center', 'right')
        :return: None
        """
        self['justify'] = alignment

    def setFloat(self, floatvalue: float) -> None:
        self.clear()
        if floatvalue:
            f = float(floatvalue) #could be int as well
            self.insert(0, str(f))

    def getValue(self) -> any:
        return self.get()

    def setValue(self, val: float or str) -> None:
        if type(val) == str: #might be '123.45'
            val = float(val)
        self.setFloat(val)

    def clear(self) -> None:
        self.delete(0, 'end')

#+++++++++++++++++++++++++++++++++++++++++++++++

class IntEntry(ttk.Entry, GetterSetter, ConvenianceMethods, ModifyTracer):
    def __init__(self, parent):
        ttk.Entry.__init__(self, parent, validate="key")
        ConvenianceMethods.__init__(self)
        ModifyTracer.__init__(self)
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

    def setValue(self, val: int or str) -> None:
        self.clear()
        if val:
            if type(val) == str: #might be '123'
                val = int(val)
            self.setInt(val)

    def clear(self) -> None:
        self.delete(0, 'end')

#+++++++++++++++++++++++++++++++++++++++++++++++

class MyCombobox(ttk.Combobox, GetterSetter, ConvenianceMethods, ModifyTracer):
    def __init__(self, parent):
        ttk.Combobox.__init__(self, parent)
        ConvenianceMethods.__init__(self)
        ModifyTracer.__init__(self)

    def getCurrentIndex(self) -> int:
        return self.current()

    def setIndex(self, idx: int) -> None:
        self.current(idx)

    def getValue(self) -> any:
        return self.get()

    def setValue(self, val: any) -> None:
        self.set(val)

    def clear(self) -> None:
        self.set('')

    def setItems(self, itemlist: list or tuple) -> None:
        self['values'] = itemlist

#+++++++++++++++++++++++++++++++++++++++++++++++

class TableView(ttk.Treeview):
    def __init__(self, parent):
        ttk.Treeview.__init__(self, parent, show='headings')
        self.grid(sticky='nswe')
        self.bind('<Button-1>', self._onLeftMouse)
        self.bind('<Double-1>', self._onLeftMouseDouble)
        self.bind('<Return>', self._onReturn)
        self.bind("<<TreeviewSelect>>", self._onTreeviewSelect, "+")
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
        3 arguments: event, itemId and list.
        event: the select event
        itemId: identification of selected row
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

    def updateRow(self, iid: str, newValues: dict) -> None:
        for colName, newVal in newValues.items():
            self.updateRow2(iid, colName, newVal)

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

    def appendRows(self, rowlist: list) -> None:
        """
        provides this tableview with one or more rows of data.
        :param rowlist: contains one or more dictionaries, each
            representing the data for one table row.
            The key values correspond to tableview's headings.
        :return:
        """
        cols = self['columns'] #list of headings of this TableView
        for dic in rowlist:
            values = list()
            for col in cols:
                values.append(dic[col])
            self.appendRow(values)

    def clear(self) -> None:
        #delete all rows
        children = self.get_children()
        for child in children:
            self.delete(child)

    def appendRow(self, data: list) -> None:
        rowNr = self.getRowCount() + 1
        self.insert('', 'end', text=str(rowNr), values=data)

    def getAllRows(self, item='') -> list:
        children = self.get_children((item))
        for child in children:
            children += self.getAllRows(child)
        return children

    def getRowCount(self) -> int:
        return len(self.getAllRows())

    def getRowIid(self, rownr: int) -> str:
        children = self.get_children()
        return children[rownr]

    def getRowValues(self, iid: str) -> list:
        row = self.item(iid)
        return row['values']

    def selectRow(self, rownr: int) -> None:
        iid = self.getRowIid(rownr)
        self.selection_set(iid)
        self.focus(iid) #that will usually not work

    def getColumnNames(self) -> list:
        return self['columns']

    def _onLeftMouse(self, evt: Event) -> None:
        self._onTableRowSelected(evt, 'leftmousesingle')

    def _onLeftMouseDouble(self, evt: Event) -> None:
        self._onTableRowSelected(evt, 'leftmousedouble')

    def _onTreeviewSelect(self, evt: Event) -> None:
        self._onTableRowSelected(evt, 'treeviewselect')

    def _onReturn(self, evt: Event) -> None:
        self._onTableRowSelected(evt, 'returnkey')

    def _onTableRowSelected(self, evt: Event, trigger: str) -> None:
        """
        called when a row has been selected.
        creates a list of lists containing columnnames and cell values
        Invokes the registered SelectionCallback method.
        :param evt:  select event
        :param trigger: one of 'leftmousesingle', 'leftmousedouble',
        'returnkey', 'treeviewselect'
        :return:  list of dictionaries
        """
        iid = self.identify('item', evt.x, evt.y) #row or column header clicked
        if iid == '': #column header clicked or selection by arrow keys
            iid = self.focus() #selection changed by arrow keys
            if iid == '': #column header clicked
                return

        valuelist = list(zip(self.getColumnNames(), self.getRowValues(iid)))

        if self._selectionCallback:
            self._selectionCallback(evt, trigger, iid, valuelist)

#++++++++++++++++++++++++++++++++++++++++++++++++


def main():
    root = Tk()

    txt = MyText(root)
    txt.setMyId('v_bla')
    txt.grid(column=0, row=0, sticky='nswe')

    txt.setValue('bac')
    txt.clear()
    txt.insert('1.0', 'abcde')
    txt.setValue('the old brown fox jumps over the lazy dog.')
    #print('myId: ', txt.getMyId())

    root.mainloop()

if __name__ == '__main__':
    main()