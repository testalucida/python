import tkinter as tk
from tkinter import Toplevel, Label
from tkinter import ttk, W, FLAT, simpledialog, PhotoImage
from typing import Any, List, Tuple, Dict
from enum import Enum
from globals import NOTE, FOLDER
from contextmenu import PopupMenu
from note import Note

class TreeAction(Enum):
    INSERT_FOLDER = 1
    RENAME = 2
    DELETE = 3
    SELECT = 4
    UNSELECT = 5
    MOVE = 6

class TreeItem:
    iid:str = ""
    item:Dict = None
    id:int = 0
    label:str = ""
    tags:str = ""
    isNote:bool = False
#
# class InsertPointer( object ):
#     def __init__( self, mainwin ):
#         # self.wm_attributes('-transparentcolor','black')
#         # self.wm_attributes( '-transparentcolor', root['bg'] )
#         self._frame = mainwin
#         self._frame.bind( "<Button-1>", self._onLeftMouse )
#         self._frame.bind( "<B1-Motion>", self._onMouseMove )
#         self._frame.bind( "<ButtonRelease-1>", self._onMouseRelease )
#         self._insertPtr:InsertPointer = None
#
#
#     def _onLeftMouse( self, event ):
#         print( "_onMouseMove")
#
#     def _onMouseMove( self, event ):
#         print( "_onMouseMove")
#
#     def _onMouseRelease( self, event ):
#         print( "_onMouseRelease" )
#
#     def setPosition(self, x: int, y: int) -> None:
#         self.geometry("+%d+%d" % (x , y ))
#
#     def _createPointer( self ):
#         # Leaves only the label and removes the app window
#         self.wm_overrideredirect( True )
#         # self.wm_geometry( "+%d+%d" % ( self._frame.winfo_rootx() + x, self._frame.winfo_rooty() + y ) )
#         label = Label( self, text="Arrow", justify='left',
#                        background='white', relief='solid', borderwidth=1,
#                        font=("arial", "10", "normal") )
#         label.pack( ipadx=1 )
#

class NotesTree( ttk.Treeview ):
    def __init__( self, parent, **kwargs ):
        ttk.Treeview.__init__( self, parent, **kwargs )
        self['columns'] = ( 'id', )
        self['displaycolumns'] = []
        self.heading( '#0', text='All Notes', anchor=W )
        self.column( "#0", minwidth=100 )
        self.bind( "<Button-3>", self._onTreeViewRightClicked )
        #self.bind( "<B1-Motion>", self._onMouseMove, add='+' )
        self.bind( '<<TreeviewSelect>>', self._onTreeItemClicked )
        #self._popmen:PopupMenu # = self._createPopup()
        self._cb = None

    def setTreeCallback( self, callback_func ) -> None:
        """
        callback_func has to accept 2 arguments:
        - kind of action (rename, insert, delete) -> see class TreeAction
        - a list containing the selected TreeItem objects
        Callbacks will be performed before any changes of the tree.
        """
        self._cb = callback_func

    def addFolder( self, iid_parent:str, id:int, text:str, image:PhotoImage=None, alphabetically:bool=True ) -> str:
        """
        Adds a folder tree item either at the end of the child list or corresponding to its alphabetical value
        and returns its item id.
        """
        if alphabetically: return self._insertAlphabetically( iid_parent, id, text, image, False )
        else:
            if image: return self.insert( iid_parent, 'end', text=text, values=id, tags=(FOLDER,), image=image )
            else: return self.insert( iid_parent, 'end', text=text, values=id, tags=(FOLDER,) )

    def addNote( self, iid_parent: str, id: int, text: str, image: PhotoImage=None, alphabetically:bool=True ) -> str:
        """
        Adds a note tree item either at the end of the child list or corresponding to its alphabetical value.
        In any case after the folders.
        text: header of the note
        """
        if alphabetically: return self._insertAlphabetically( iid_parent, id, text, image, True )
        else: return self.insert( iid_parent, 'end', text=text, values=id, tags=(NOTE,), image=image )

    def updateLabel( self, iid:str, label:str ) -> None:
        self.item( iid, text=label )

    def openFolder( self, parent=None ) -> None:
        self.item( parent, open=True )  # open parent
        for child in self.get_children( parent ):
            self.openFolder( child )  # recursively open children

    def _insertAlphabetically( self, iid_parent: str, id: int, text: str, image: PhotoImage = None,
                               isNote: bool = True ) -> str:
        """
        Inserts a new item under the given parent at a position according to its alphabetical value
        """
        index = self._getIndex( iid_parent, text, isNote )

        if image:
            return self.insert( iid_parent, index, text=text, values=id,
                                tags='note' if isNote else 'folder', image=image )
        else:
            return self.insert( iid_parent, index, text=text, values=id,
                                tags='note' if isNote else 'folder' )


    # def _insertAlphabetically( self, iid_parent:str, id:int, text:str, image:PhotoImage=None, isNote:bool=True ) -> str:
    #     """
    #     Inserts a new item under the given parent at a position according to its alphabetical value
    #     """
    #     tl = text.lower()
    #     children:Tuple = self.get_children( iid_parent )
    #     index:int = 0
    #     for iid in children:
    #         item:Dict = self.item( iid )
    #         if isNote and item['tags'][0] == FOLDER:
    #             index += 1
    #             continue
    #         else:
    #             t = item['text'].lower()
    #             if tl < t:
    #                 if image:
    #                     return self.insert( iid_parent, index, text=text, values=id, tags='note' if isNote else 'folder', image=image )
    #                 else:
    #                     return self.insert( iid_parent, index, text=text, values=id, tags='note' if isNote else 'folder')
    #             index += 1
    #     return ( self.addNote( iid_parent, id, text, image, False ) if isNote else self.addFolder( iid_parent, id, text, image, False ) )

    def _getIndex( self, parent_iid:str, label2insert:str, isNote:bool=True ) -> int:
        tl = label2insert.lower()
        children: Tuple = self.get_children( parent_iid )
        index: int = 0
        for iid in children:
            item: Dict = self.item( iid )
            if isNote and item['tags'][0] == FOLDER:
                pass
            else:
                t = item['text'].lower()
                if tl < t:
                    break
            index += 1
        return index

    def remove( self, iid:str ):
        """
        Removes the given Item from the tree
        """
        self.delete( (iid,) )

    def moveItem( self, iid:str, new_parent_iid:str ):
        item = self.item( iid )
        idx = self._getIndex( new_parent_iid, item['text'] )
        self.move( iid, new_parent_iid, idx )

    def setSelection( self, iid:str ) -> None:
        self.unsetSelection()
        self.selection_add( (iid,) )

    def unsetSelection( self ) -> None:
        #print( "NotesTree.unselectSelection ")
        self.selection_remove( self.selection() )


    #################### callbacks for tree actions ########################
    def _onInsertFolder( self ):
        #only folders can be inserted this way. Notes are inserted by saving the new or edited note.
        self._doCallback( TreeAction.INSERT_FOLDER )
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

    def _onMoveItem( self ):
        self._doCallback( TreeAction.MOVE )

    ####################################################################################

    def _doCallback( self, action:TreeAction ) -> None:
        treeItems:List[TreeItem] = self.getSelectedTreeItems()
        if self._cb:
            self._cb( action, treeItems )

    # def _onMouseMove( self, event ):
    #     tuple:Tuple = self.getSelectedTreeItem()
    #     if tuple[3] == FOLDER: return
    #     moveto = self.index( self.identify_row( event.y ) )
    #     for s in self.selection():
    #         self.move( s, '', moveto )

    def _onTreeViewRightClicked( self, event ):
        iids = self.getSelectedTreeItems()
        n = len( iids )
        if n == 0: return

        pop = PopupMenu( self )
        if len( iids ) == 1:
            # if there's a selection, we ask for renaming, deleting or inserting
            pop.addCommand( "Insert Folder...", self._onInsertFolder, True )
            pop.addCommand( "Rename selected Item...", self._onRenameItem, True )
            pop.addCommand( "Delete selected Item", self._onDeleteItem, True )
            pop.addCommand( "Move selected Item to Folder...", self._onMoveItem )
        else:
            pop.addCommand( "Delete selected Items", self._onDeleteItem )

        pop.show( event )

    def _onTreeItemClicked( self, event ):
        #bound to virtual TreeviewSelect event
        action:TreeAction
        if self.existsSelection():
            action = TreeAction.SELECT
        else:
            action = TreeAction.UNSELECT
        #print( "NotesTree._onTreeItemClicked - action: ", "SELECT" if action == 4 else "UNSELECT" )
        self._doCallback( action )

    def getSelectedId( self ) -> Tuple[str, int]:
        iid = self.selection()
        if len( iid ) == 0:
            return ( '', 0 )
        dic = self.item( iid )
        id: int = int( dic['values'][0] )
        return ( iid, id )

    def existsSelection( self ) -> bool:
        return True if len( self.selection() ) > 0 else False

    def getSelectedTreeItemAsTuple(self) -> Tuple[str, id, str, str]:
        """
        Gets the first selected item.
        The returned tuple contains iid, id, label and tags.
        """
        iids = self.selection() #returns a list with selected iids or an empty list
        if len( iids ) > 0:
            iid = iids[0]
        else:
            return ( '0', 0, '', '' )
        item = self.item( iid )
        id: int = int( item['values'][0] )
        tags:List = item['tags']
        return ( iid, id, item['text'], tags[0] )

    def getFirstSelectedTreeItem( self ) -> TreeItem or None:
        iids: Tuple = self.selection()
        if len( iids ) > 0:
            item = self.item( iids[0] )
            treeItem = TreeItem()
            treeItem.iid = iids[0]
            treeItem.item = item
            treeItem.id = int( item['values'][0] )
            treeItem.label = item['text']
            treeItem.isNote = True if item['tags'][0] == NOTE else False
            return treeItem
        return None

    def getSelectedTreeItems(self) -> List[TreeItem]:
        """
        Returns the selected items, Note and/or Folder objects
        """
        selectedItems:List[TreeItem] = []
        iids:Tuple = self.selection()
        for iid in iids:
            item = self.item( iid )
            treeItem:TreeItem = TreeItem()
            treeItem.iid = iid
            treeItem.item = item
            treeItem.id = int( item['values'][0] )
            treeItem.label = item['text']
            treeItem.isNote = True if item['tags'][0] == NOTE else False
            selectedItems.append( treeItem )

        return selectedItems


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

    item = t.getSelectedTreeItemAsTuple()
    print( item )

    root.mainloop()

if __name__ == '__main__':
    test()