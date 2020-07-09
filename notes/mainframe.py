from tkinter import *
from tkinter import ttk
from tkinter.font import families
from tkinter import simpledialog
from tkinter import PhotoImage
from mywidgets import ToolTip
from noteeditor import NoteEditor
from notestree import NotesTree


class MainFrame(Frame):
    def __init__(self, parent, cnf={}, **kw):
        Frame.__init__(self, parent, cnf, **kw)
        self._toolbar = self._createToolBar(self, 0)
        self._panedWin, self._leftPane, self._rightPane = self._createPanedWindow(self, 1, 0)
        self.tree = self._createTree( self._leftPane )
        self._edi = self._createNoteEditor( self._rightPane )
        self._statusbar = self._createStatusBar(self, 2)
        self.rowconfigure(1, weight=1)
        self.columnconfigure( 0, weight=1 )

    def _createToolBar(self, parent, row:int) -> Frame:
        #images from "https://icons8.com/icons/"
        tb = Frame(self)
        tb.grid(row=row, column=0, sticky='nwe', padx=3, pady=3)
        self._createToolButton( tb, 0, "/home/martin/Projects/python/notes/images/new_folder_30.png", "Create new top level folder", self._onNewFolder )
        self._createToolButton( tb, 1, "/home/martin/Projects/python/notes/images/new_30.png", "Create new note", self._onNew )
        self._createToolButton( tb, 2, "/home/martin/Projects/python/notes/images/search_30.png", "Search in notes", self._onSearch )
        self._createToolButton( tb, 3, "/home/martin/Projects/python/notes/images/save_30.png", "Save local", self._onSaveLocal )
        self._createToolButton( tb, 4, "/home/martin/Projects/python/notes/images/save_to_cloud_30.png", "Save all notes to server",  self._onSaveRemote )
        self._createToolButton( tb, 5, "/home/martin/Projects/python/notes/images/saveas_30.png", "Save as (locally)", self._onSaveAs )
        Label( tb, width=10 ).grid( row=0, column=6, padx=2, pady=2 )
        self._createToolButton( tb, 7, "/home/martin/Projects/python/notes/images/bold_24.png", "Selected text to bold", self._onBold )
        self._createToolButton( tb, 8, "/home/martin/Projects/python/notes/images/italic_24.png", "Selected text to italic", self._onItalic )

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
        tree = NotesTree( parent )
        # tree['columns'] = ('id')
        # tree['displaycolumns'] = []
        # tree.heading('#0', text='All Notes', anchor=W)
        # tree.column("#0", minwidth=100 )
        top = tree.addFolder( '', 1, text='Apache Webserver' )
        tree.addFolder( top, 2, text='restart' )
        tree.addFolder( '', 3, text='php Debugger' )
        tree.addFolder( '', 4, text ='miniconda3' )
        # tree.bind("<Button-3>", self._onTreeViewClicked)
        # tree.bind('<<TreeviewSelect>>', self._onTreeItemClicked)
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

    def _onNewFolder( self ):
        s = simpledialog.askstring( "New top level folder", "Name of new folder:", initialvalue="" )
        if s:
            self.tree.addFolder( '', 0, s )

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