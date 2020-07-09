import tkinter as tk
from tkinter import ttk, W, FLAT, simpledialog, PhotoImage, messagebox
from typing import Any, List, Tuple, Dict
from enum import Enum

from contextmenu import PopupMenu

class TreeAction(Enum):
    INSERT = 1
    RENAME = 2
    DELETE = 3

class NotesTree( ttk.Treeview ):
    def __init__( self, parent, **kwargs ):
        ttk.Treeview.__init__( self, parent, **kwargs )
        self['columns'] = ( 'id' )
        self['displaycolumns'] = []
        self.heading( '#0', text='All Notes', anchor=W )
        self.column( "#0", minwidth=100 )
        self.bind( "<Button-3>", self._onTreeViewRightClicked )
        self.bind( '<<TreeviewSelect>>', self._onTreeItemClicked )
        self._popmen = self._createPopup()
        self._cb = None

    def _createPopup( self ) -> PopupMenu:
        pop = PopupMenu( self )
        pop.addCommand( "Insert Folder...", self._onInsertFolder, True )
        pop.addCommand( "Rename selected Folder...", self._onRenameFolder, True )
        pop.addCommand( "Delete selected Folder", self._onDeleteFolder )
        return pop

    def setTreeCallback( self, callback_func ) -> None:
        """
        callback_func has to accept 4 arguments:
        - item id (iid)
        - id of tree entry (id of note or parent)
        - kind of action (rename, insert, delete) -> see class TreeAction
        - in case of renaming or inserting the name of the folder
        Callbacks will be performed before any changes of the tree.
        """
        self._cb = callback_func

    def addFolder( self, iid_parent:str, id:int, text:str, image:PhotoImage=None ) -> str:
        """
        Adds a folder tree item at the end of the child list
        """
        return self.insert( iid_parent, 'end', text=text, values=id, tags=('folder') )

    def addNote( self, iid_parent: str, id: int, text: str, image: PhotoImage = None ) -> str:
        """
        Adds a note tree item at the end of the child list
        """
        return self.insert( iid_parent, 'end', text=text, values=id, tags=('note') )

    def insertAlphabetically( self, iid_parent:str, id:int, text:str, image:PhotoImage=None ) -> str:
        """
        Inserts a new item under the given parent at a position according to its alphabetical value
        """
        tl = text.lower()
        children:Tuple = self.get_children( iid_parent )
        index:int = 0
        for iid in children:
            item:Dict = self.item( iid )
            t = item['text'].lower()
            if tl < t:
                return self.insert( iid_parent, index, text=text, values=id )
            index += 1
        return self.addFolder( iid_parent, id, text )


    def remove( self, iid:str ):
        """
        Removes the given Item from the tree
        """
        self.delete( (iid,) )

    #################### callbacks for tree actions ########################
    def _onInsertFolder( self ):
        print( "_onInsertFolder" )
        # get selected folder, ask for new folder's name and insert it as child of the selected folder.
        iid, id, label = self.getSelectedTreeItem()
        s = simpledialog.askstring( "New folder", "Name of new folder:", initialvalue="" )
        if s:
            self.addFolder( iid, -1, s )
            self._doCallback( )

    def _onRenameFolder( self ):
        iid, id, label = self.getSelectedTreeItem()
        s = simpledialog.askstring( "Rename Folder", "Change name to:", initialvalue=label )
        if len( s ) > 0:
            self.item( iid, text=s )
            self._doCallback( iid, id, TreeAction.RENAME, s )

    def _onDeleteFolder( self ):
        if messagebox.askyesno( "Confirmation Prompt",
                                "Really delete this folder and all its content?",
                                icon='warning' ):
            iid, id, label = self.getSelectedTreeItem()
            self._doCallback( iid, id, TreeAction.DELETE, label )

    ####################################################################################

    def _doCallback( self, iid:Any, id:int, action:TreeAction, foldername:str=None ) -> None:
        if self._cb:
            self._cb( iid, id, action, foldername )

    def _onTreeViewRightClicked( self, event ):
        iid, id, label = self.getSelectedTreeItem()
        print( "onTreeViewRightClicked, iid=", iid )
        if id > 0:
            # if there's a selection, we ask for renaming, deleting or inserting
            self._popmen.show( event )

    def _onTreeItemClicked(self, event):
        print( "onTreeItemClicked" )
        #bound to virtual TreeviewSelect event
        iid, id, label = self.getSelectedTreeItem()
        if id > 0:
            pass

    def getSelectedId( self ) -> Tuple:
        iid = self.selection()
        if len( iid ) == 0:
            return ('0', 0, '' )
        dic = self.item( iid )
        id: int = int( dic['values'][0] )
        return ( iid, id )

    def getSelectedTreeItem(self) -> Tuple:
        iid = self.selection()
        if len( iid ) == 0:
            return ( '0', 0, '' )
        dic = self.item( iid[0] )
        id: int = int( dic['values'][0] )
        return ( iid, id, dic['text'] )

def test():
    root = tk.Tk()
    root.rowconfigure( 0, weight=1 )
    root.columnconfigure( 0, weight=2 )

    t = NotesTree( root )
    t.grid( row=0, column=0, sticky='nswe' )

    top = t.addFolder( '', 1, text='Apache Webserver' )
    t.addFolder( top, 2, text='restart' )
    t.addFolder( '', 4, text='miniconda3' )
    t.addFolder( '', 5, text='Minibagger' )
    t.addFolder( '', 3, text='php Debugger' )
    t.insertAlphabetically( '', 7, text='C++' )
    t.insertAlphabetically( '', 8, text='Zorro' )

    children = t.get_children( '' )
    print( children )

    root.mainloop()

if __name__ == '__main__':
    test()