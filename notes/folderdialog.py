from tkinter import Tk, Frame, PhotoImage
from typing import List, Tuple, Dict
from dialogbase import DialogBase
from notestree import NotesTree
from business import BusinessLogic

class FolderDialog( DialogBase ):
    def __init__( self, parent ):
        DialogBase.__init__( self, parent )
        self.tree = NotesTree( self.clientArea )

##############################################################

class FolderDialogController:
    def __init__( self, dialogparent:Frame, folderImage:PhotoImage ):
        self._dlg = FolderDialog( dialogparent )
        self._dlg.setOkCancelCallback( self.okCancelCallback )
        self._imgFolder = folderImage
        self._business = BusinessLogic()
        self._folder_id_iid_ref: Dict = { 0: '' }  # key: id, value: iid

    def okCancelCallback( self, ok:bool ):
        print( "okCancelCallback: ", ok )

    def startWork( self ):
        self._provideFolders()

    def _provideFolders( self, parent_id:int, parent_iid:str ):
        folders: List[Tuple] = self._business.getFolders( parent_id )
        for f in folders:
            id, parent_id, text = f
            iid = self._dlg.tree.addFolder( parent_iid, id, text, self._imgFolder )
            self._folder_id_iid_ref[id] = iid
            # each id could have subfolders:
            self._provideFolders( id, iid )


def test():
    root = Tk()
    c = FolderDialogController( root )
    root.mainloop()

if __name__ == '__main__':
    test()
