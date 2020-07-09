from mainframe import MainFrame
from noteeditor import NoteEditor
from notestree import NotesTree

class Controller:
    def __init__( self, mainframe:MainFrame ):
        self._mainframe = mainframe
        self._tree:NotesTree = mainframe.tree
        self._toolbar = mainframe.toolbar
        self._edi:NoteEditor = mainframe.edi
        self._status = mainframe.statusbar

    def startWork( self ):
        # todo: fetch notes and folders from sqlite
        pass