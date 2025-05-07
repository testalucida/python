from tkinter import *
from tkinter import Tk, Frame, PhotoImage
from typing import List, Tuple, Dict
from dialogbase import DialogBase
from notestree import NotesTree, TreeItem
from business import BusinessLogic
from images import ImageFactory

class FolderDialog( DialogBase ):
    def __init__( self, parent=None ):
        DialogBase.__init__( self, parent )
        self.title = "Select a Folder as Move Target"
        self.setValidationCallback( self.onValidation )
        self.tree = NotesTree( self.clientArea )
        self.tree.grid( row=0, column=0, sticky='nswe', padx=2, pady=2 )
        folderprovider = FolderProvider()
        self._id_iid_ref = folderprovider.provideFolders( self.tree )
        self.tree.openFolder( '' )

    def onValidation( self ) -> str or None:
        folder: TreeItem = self.tree.getFirstSelectedTreeItem()
        if not folder:
            return "No folder selected."

    def getSelectedFolder( self ) -> TreeItem:
        return self.tree.getFirstSelectedTreeItem()


##############################################################

class FolderProvider:
    def __init__( self ):
        self._business = BusinessLogic()
        self._business.initDatabase()
        self._folder_id_iid_ref: Dict = { 0: '' }  # key: id, value: iid
        self._folderImage = ImageFactory.getInstance().imgFolder

    def provideFolders( self, tree: NotesTree ) -> Dict: #key: id, value: iid
        folder_id_iid_ref: Dict = { 0: '' }
        self._provideFolders( tree, folder_id_iid_ref, 0, '' )
        return folder_id_iid_ref

    def _provideFolders( self, tree:NotesTree, folder_id_iid_ref:Dict, parent_id:int, parent_iid:str ):
        folders: List[Tuple] = self._business.getFolders( parent_id )
        for f in folders:
            id, parent_id, text = f
            iid = tree.addFolder( parent_iid, id, text, self._folderImage )
            folder_id_iid_ref[id] = iid
            # each id could have subfolders:
            self._provideFolders( tree, folder_id_iid_ref, id, iid )

dlg:FolderDialog

def onOkCancel( ok:bool ):
    global dlg
    if ok:
        ti:TreeItem = dlg.getSelectedFolder()
        print( ti.id, ", ", ti.iid, ", ", ti.label )

def showDialog():
    global dlg
    dlg = FolderDialog( )
    dlg.setOkCancelCallback( onOkCancel )


def test():
    root = Tk()
    btn = Button( root, text="show dialog", command=showDialog )
    btn.grid( row=0, column=0 )
    root.mainloop()

if __name__ == '__main__':
    test()
