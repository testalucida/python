from tkinter import *
from tkinter import ttk
from tkinter.font import families
from tkinter import simpledialog
from tkinter import PhotoImage
from mywidgets import ToolTip
from noteeditor import NoteEditor

print ('sys.version: ', sys.version)
print ('sys.executable: ', sys.executable)
print ('sys.path: ', sys.path)

# class OverlayInput( object ):
#     '''
#     create a overlay input for a given widget
#     '''
#     def __init__( self, widget, text="" ):
#         self._widget = widget
#         self._text = text
#         self._tw:Toplevel
#         self._input:Entry
#
#     def enter(self, event=None):
#         x = y = 0
#         x, y, cx, cy = self._widget.bbox("insert")
#         x += self.widget.winfo_rootx() + 25
#         y += self.widget.winfo_rooty() + 20
#         # creates a toplevel window
#         self._tw = Toplevel(self.widget)
#         # Leaves only the label and removes the app window
#         self.tw.wm_overrideredirect(True)
#         self.tw.wm_geometry("+%d+%d" % (x, y))
#         label = Label(self.tw, text=self.text, justify='left',
#                       background='white', relief='solid', borderwidth=1,
#                       font=("arial", "10", "normal"))
#         label.pack(ipadx=1)
#
#     def close(self, event=None):
#         if self.tw:
#             self.tw.destroy()
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++

class MainFrame(Frame):
    def __init__(self, parent, cnf={}, **kw):
        Frame.__init__(self, parent, cnf, **kw)
        self._toolbar = self._createToolBar(self, 0)
        self._panedWin, self._leftPane, self._rightPane = self._createPanedWindow(self, 1, 0)
        self._tree = self._createTree(self._leftPane)
        self._edi = self._createNoteEditor( self._rightPane )
        self._statusbar = self._createStatusBar(self, 2)
        self.rowconfigure(1, weight=1)
        self.columnconfigure( 0, weight=1 )

    def _createToolBar(self, parent, row:int) -> Frame:
        #images from "https://icons8.com/icons/"
        tb = Frame(self)
        tb.grid(row=row, column=0, sticky='nwe', padx=3, pady=3)
        self._createToolButton( tb, 0, "/home/martin/Projects/python/notes/images/new_30.png", "Create new note or structure", self._onNew )
        self._createToolButton( tb, 1, "/home/martin/Projects/python/notes/images/search_30.png", "Search in notes", self._onSearch )
        self._createToolButton( tb, 2, "/home/martin/Projects/python/notes/images/save_30.png", "Save local", self._onSaveLocal )
        self._createToolButton( tb, 3, "/home/martin/Projects/python/notes/images/save_to_cloud_30.png", "Save all notes to server",  self._onSaveRemote )
        self._createToolButton( tb, 4, "/home/martin/Projects/python/notes/images/saveas_30.png", "Save as (locally)", self._onSaveAs )
        Label( tb, width=10 ).grid( row=0, column=5, padx=2, pady=2 )
        self._createToolButton( tb, 6, "/home/martin/Projects/python/notes/images/bold_24.png", "Selected text to bold", self._onBold )
        self._createToolButton( tb, 7, "/home/martin/Projects/python/notes/images/italic_24.png", "Selected text to italic", self._onItalic )

        return tb

    def _createToolButton( self, parent, col, path_to_image:str, tooltip:str=None, command=None ) -> Button:
        img = PhotoImage( file=path_to_image )
        btn = Button( parent, image=img, relief=FLAT )
        btn.image = img
        btn.grid( row=0, column=col, padx=2, pady=2 )
        if tooltip:
            ToolTip( btn, text=tooltip )
        if command:
            btn['command'] = command
        return btn

    def _createPanedWindow(self, parent, row:int, column:int):
        pw = ttk.PanedWindow(parent, orient=HORIZONTAL)
        #pw.rowconfigure(0, weight=1)
        #pw.columnconfigure(1, weight=1)
        pw.grid( row=row, column=column, sticky='nswe' )
        lp = Frame( pw, width=150 )
        lp.columnconfigure( 0, weight=1 )
        lp.rowconfigure( 0, weight=1 )
        lp.grid( row=0, column=0, sticky='nswe')
        pw.add( lp )

        rp = Frame( pw )
        rp.grid( row=0, column=1, sticky='nswe' )
        rp.columnconfigure( 0, weight=1 )
        rp.rowconfigure( 0, weight=1 )
        pw.add( rp )
        return [pw, lp, rp]

    def _createTree(self, parent):
        tree = ttk.Treeview(parent)
        tree['columns'] = ('id')
        tree['displaycolumns'] = []
        tree.heading('#0', text='All Notes', anchor=W)
        tree.column("#0", minwidth=100 )
        top = tree.insert('', 0, text='Apache Webserver')
        tree.insert(top, 0, text='restart')
        tree.insert('', 0, text='php Debugger')
        tree.insert('', 0, text = 'miniconda3')
        tree.bind("<Button-3>", self._onTreeViewClicked)
        tree.bind('<<TreeviewSelect>>', self._onTreeItemClicked)
        tree.grid( column=0, row=0, sticky='nswe' )
        return tree

    def _createNoteEditor( self, parent ) -> NoteEditor:
        edi = NoteEditor( parent )
        edi.grid( row=0, column=0, sticky='nswe' )
        return edi

    def _createStatusBar(self, parent, row:int):
        sb = ttk.Label(parent, text='', relief=SUNKEN)
        sb.grid(column=0, row=row, sticky='swe')
        return sb

    def _onNew( self ):
        print( "onNew" )

    def _onSearch( self ):
        print( "onSearch" )

    def _onSaveAs( self ):
        print( "onSaveAs")

    def _onSaveLocal( self ):
        print( "onSaveLocal" )

    def _onSaveRemote( self ):
        print( "onSaveRemote")

    def _onBold( self ):
        print( "onBold" )

    def _onItalic( self ):
        print( "onItalic" )

    def _onTreeViewClicked( self, event ):
        id:int = self.getSelectedTreeItem()
        print( "onTreeViewRightClicked" )
        s = simpledialog.askstring( "Rename Folder", "Change name to:", initialvalue="default" )
        print( s )

    def _onTreeItemClicked(self, event):
        print( "onTreeItemClicked" )
        #bound to virtual TreeviewSelect event
        id = self.getSelectedTreeItem()
        if id > 0:
            pass

    def getSelectedTreeItem(self) -> int:
        item = self._tree.selection()
        dic = self._tree.item(item)
        try:
            id: int = dic['values'][0]
            if id > 0:  # valid wohnung item clicked;
                return id
        except IndexError:  # straße- or ort-item clicked
            return -1

def main():
    root = Tk()
    root.title( "Notes" )
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    f = MainFrame(root)
    f.grid( row=0, column=0, sticky='nswe', padx=3, pady=3)

    root.mainloop()

def dummy_callback():
    print( "callback" )

def testPng():
    root = Tk()
    root.geometry( "960x600" )
    root.title( "Show a .png image" )
    # root.rowconfigure( 0, weight=1 )
    # root.columnconfigure( 0, weight=1 )
    img = PhotoImage( file="/home/martin/Projects/python/notes/images/save_30.png" )
    btn = Button( root, image=img, relief=FLAT )
    btn.image = btn
    btn.grid( row=0, column=0, sticky='nw', padx=3, pady=3 )
    btn['command'] = dummy_callback

    root.mainloop()

def testFont():
    root = Tk()
    root.title( "Finally Pycharm working with tkinter" )
    available = families()
    print( len(available) )
    print( "availabe: ", available)
    f = MainFrame(root)
    f.grid( row=0, column=0)

    root.mainloop()


if __name__ == "__main__":
    #testPng()
    main()