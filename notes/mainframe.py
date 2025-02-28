from tkinter import *
from tkinter import ttk
from tkinter.font import families
from tkinter import simpledialog
from tkinter import PhotoImage
from enum import Enum
import sys
if not 'mywidgets' in sys.path: sys.path.append('/home/martin/Projects/python/mywidgets')
from mywidgets import ToolTip
from noteeditor import NoteEditor
from notestree import NotesTree


class ToolAction( Enum ):
    NEW_TOPFOLDER = 1
    NEW_NOTE = 2
    SEARCH = 3
    SAVE_LOCAL = 4
    SAVE_REMOTE = 5
    SAVE_AS = 6
    FONT_BOLD = 7
    FONT_ITALIC = 8
    MARK_AS_LINK = 9
    FONT_RED = 10
    FONT_GREEN = 11
    FONT_BLUE = 12
    FONT_BLACK = 13

class MainFrame(Frame):
    def __init__(self, parent, cnf={}, **kw):
        Frame.__init__(self, parent, cnf, **kw)
        self.toolbar = self._createToolBar(self, 0)
        #parent.bind( '<Control-slash>', self._onSaveLocal )
        self._panedWin, self._leftPane, self._rightPane = self._createPanedWindow(self, 1, 0)
        self.tree = self._createTree( self._leftPane )
        self.edi: NoteEditor = self._createNoteEditor( self._rightPane )
        self.statusbar = self._createStatusBar(self, 2)
        self.rowconfigure(1, weight=1)
        self.columnconfigure( 0, weight=1 )
        self._toolActionCallback = None

    def _createToolBar(self, parent, row:int) -> Frame:
        #images from "https://icons8.com/icons/"
        tb = Frame(self)
        tb.grid(row=row, column=0, sticky='nwe', padx=3, pady=3)
        self._createToolButton( tb, 0, "/home/martin/Projects/python/notes/images/new_folder_30.png", "Create new top level folder", self._onNewTopFolder )
        self._createToolButton( tb, 1, "/home/martin/Projects/python/notes/images/new_30.png", "Create new note", self._onNewNote )
        self._createToolButton( tb, 2, "/home/martin/Projects/python/notes/images/search_30.png", "Search in notes", self._onSearch )
        self._createToolButton( tb, 3, "/home/martin/Projects/python/notes/images/save_30.png", "Save local", self._onSaveLocal )
        self._createToolButton( tb, 4, "/home/martin/Projects/python/notes/images/save_to_cloud_30.png", "Save all notes to server",  self._onSaveRemote )
        #self._createToolButton( tb, 5, "/home/martin/Projects/python/notes/images/saveas_30.png", "Save as (locally)", self._onSaveAs )
        Label( tb, width=10 ).grid( row=0, column=6, padx=2, pady=2 )
        self._createToolButton( tb, 7, "/home/martin/Projects/python/notes/images/bold_24.png", "Selected text to bold", self._onBold )
        self._createToolButton( tb, 8, "/home/martin/Projects/python/notes/images/italic_24.png", "Selected text to italic", self._onItalic )
        self._createToolButton( tb, 9, "/home/martin/Projects/python/notes/images/link_24.png", "Selected text to hyperlink", self._onLink )
        self._createToolButton( tb, 10, "/home/martin/Projects/python/notes/images/red_24.png", "Selected text to red", self._onRed )
        self._createToolButton( tb, 11, "/home/martin/Projects/python/notes/images/blue_24.png", "Selected text to blue", self._onBlue )
        self._createToolButton( tb, 12, "/home/martin/Projects/python/notes/images/green_24.png", "Selected text to green", self._onGreen )
        self._createToolButton( tb, 13, "/home/martin/Projects/python/notes/images/black_24.png", "Selected text to black", self._onBlack )
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

    def _onNewTopFolder( self ):
        self._doToolActionCallback( ToolAction.NEW_TOPFOLDER )

    def _onNewNote( self ):
        self._doToolActionCallback( ToolAction.NEW_NOTE )

    def _onSearch( self ):
        self._doToolActionCallback( ToolAction.SEARCH )

    def _onSaveAs( self ):
        self._doToolActionCallback( ToolAction.SAVE_AS )

    def _onSaveLocal( self ):
        self._doToolActionCallback( ToolAction.SAVE_LOCAL )

    def _onSaveRemote( self ):
        self._doToolActionCallback( ToolAction.SAVE_REMOTE )

    def _onBold( self ):
        self._doToolActionCallback( ToolAction.FONT_BOLD )

    def _onItalic( self ):
        self._doToolActionCallback( ToolAction.FONT_ITALIC )

    def _onLink( self ):
        self._doToolActionCallback( ToolAction.MARK_AS_LINK )

    def _onRed( self ):
        self._doToolActionCallback( ToolAction.FONT_RED )

    def _onBlue( self ):
        self._doToolActionCallback( ToolAction.FONT_BLUE )

    def _onGreen( self ):
        self._doToolActionCallback( ToolAction.FONT_GREEN )

    def _onBlack( self ):
        self._doToolActionCallback( ToolAction.FONT_BLACK )

    def _doToolActionCallback( self, action:ToolAction ):
        if self._toolActionCallback:
            self._toolActionCallback( action )

    def setToolActionCallback( self, callback ):
        """
        register a callback function which is called whenever a toolbar button is hit.
        This function has to accept one argument, the ToolAction value
        """
        self._toolActionCallback = callback
