import tkinter as tk
from tkinter import ttk, W, FLAT, simpledialog, PhotoImage
from typing import Any, List, Tuple, Dict
from enum import Enum
from globals import NOTE, FOLDER
from contextmenu import PopupMenu

class TreeAction(Enum):
    INSERT = 1
    RENAME = 2
    DELETE = 3
    SELECT = 4

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
        pop.addCommand( "Rename selected Item...", self._onRenameItem, True )
        pop.addCommand( "Delete selected Item", self._onDeleteItem )
        return pop

    def setTreeCallback( self, callback_func ) -> None:
        """
        callback_func has to accept 5 arguments:
        - item id (iid)
        - id of tree entry (id of note or parent)
        - kind of action (rename, insert, delete) -> see class TreeAction
        - in case of renaming the name of the item to rename and in case of inserting the name of the folder to insert
        - kind of item: NOTE or FOLDER
        Callbacks will be performed before any changes of the tree.
        """
        self._cb = callback_func

    def addFolder( self, iid_parent:str, id:int, text:str, image:PhotoImage=None, alphabetically:bool=True ) -> str:
        """
        Adds a folder tree item either at the end of the child list or corresponding to its alphabetical value
        """
        if alphabetically: return self._insertAlphabetically( iid_parent, id, text, image, False )
        else: return self.insert( iid_parent, 'end', text=text, values=id, tags=(FOLDER), image=image )

    def addNote( self, iid_parent: str, id: int, text: str, image: PhotoImage=None, alphabetically:bool=True ) -> str:
        """
        Adds a note tree item either at the end of the child list or corresponding to its alphabetical value
        """
        if alphabetically: return self._insertAlphabetically( iid_parent, id, text, image, True )
        else: return self.insert( iid_parent, 'end', text=text, values=id, tags=(NOTE), image=image )

    def _insertAlphabetically( self, iid_parent:str, id:int, text:str, image:PhotoImage=None, isNote:bool=True ) -> str:
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
                return self.insert( iid_parent, index, text=text, values=id, tags='note' if isNote else 'folder', image=image )
            index += 1
        return ( self.addNote( iid_parent, id, text, image, False ) if isNote else self.addFolder( iid_parent, id, text, image, False ) )


    def remove( self, iid:str ):
        """
        Removes the given Item from the tree
        """
        self.delete( (iid,) )

    #################### callbacks for tree actions ########################
    def _onInsertFolder( self ):
        #only folders can be inserted this way. Notes are inserted by saving the new or edited note.
        self._doCallback( TreeAction.INSERT )
        # # get selected folder, ask for new folder's name and insert it as child of the selected folder.
        # iid, id, label = self.getSelectedTreeItem()
        # s = simpledialog.askstring( "New folder", "Name of new folder:", initialvalue="" )
        # if s:
        #     self.addFolder( iid, -1, s )
        #     self._doCallback( )

    def _onRenameItem( self ):
        self._doCallback( TreeAction.RENAME )
        # iid, id, label = self.getSelectedTreeItem()
        # s = simpledialog.askstring( "Rename Folder", "Change name to:", initialvalue=label )
        # if len( s ) > 0:
        #     self.item( iid, text=s )
        #     self._doCallback( iid, id, TreeAction.RENAME, s )

    def _onDeleteItem( self ):
        self._doCallback( TreeAction.DELETE )
        # iid, id, label = self.getSelectedTreeItem()
        # self._doCallback( iid, id, TreeAction.DELETE, label )

    ####################################################################################

    def _doCallback( self, action:TreeAction ) -> None:
        iid, id, label, noteorfolder = self.getSelectedTreeItem()
        if self._cb:
            self._cb( iid, id, action, label, noteorfolder )

    def _onTreeViewRightClicked( self, event ):
        iid, id, label, noteorfolder = self.getSelectedTreeItem()
        print( "onTreeViewRightClicked, iid=", iid )
        if id > 0:
            # if there's a selection, we ask for renaming, deleting or inserting
            self._popmen.show( event )

    def _onTreeItemClicked( self, event ):
        #bound to virtual TreeviewSelect event
        self._doCallback( TreeAction.SELECT )

    def getSelectedId( self ) -> Tuple[str, int]:
        iid = self.selection()
        if len( iid ) == 0:
            return ( '', 0 )
        dic = self.item( iid )
        id: int = int( dic['values'][0] )
        return ( iid, id )

    def getSelectedTreeItem(self) -> Tuple[str, id, str, str]:
        iid = self.selection()
        if len( iid ) == 0:
            return ( '0', 0, '', '' )
        dic = self.item( iid[0] )
        id: int = int( dic['values'][0] )
        tags:List = dic['tags']
        return ( iid, id, dic['text'], tags[0] )

def test():
    root = tk.Tk()
    root.rowconfigure( 0, weight=1 )
    root.columnconfigure( 0, weight=2 )

    t = NotesTree( root )
    t.grid( row=0, column=0, sticky='nswe' )

    t.addFolder( '', 3, text='php Debugger' )
    t.addFolder( '', 4, text='miniconda3' )
    top = t.addFolder( '', 1, text='Apache Webserver' )
    t.addFolder( top, 2, text='restart' )
    t.addFolder( '', 5, text='Minibagger' )
    t.addFolder( '', 7, text='C++' )
    t.addFolder( '', 8, text='Zorro' )

    children = t.get_children( '' )
    print( children )

    item = t.getSelectedTreeItem()
    print( item )

    root.mainloop()

if __name__ == '__main__':
    test()