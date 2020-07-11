from dbaccess import DbAccess
from globals import NOTE, FOLDER
from libs import *

class BusinessLogic:
    def __init__( self ):
        self._db = DbAccess()

    def getFolders( self, parent_iid:int ) -> List[Tuple]:
        # Returns a list of all folders belonging to a given parent_id
        # Each folder is represented by a Tuple containing parent_id, folder_id, text.
        self._db.open()
        folders = self._db.getFolders( parent_iid )
        # for f in folders:
        #     print( f )
        self._db.close()
        return folders

    def getNoteFolderId( self, note_id:int ) -> int:
        self._db.open()
        id:int = self._db.getNoteFolderId( note_id )
        self._db.close()
        return id

    def getNoteFolder( self, note_id:int ) -> (int, str):
        self._db.open()
        id, text = self._db.getNoteFolder( note_id )
        self._db.close()
        return ( id, text )

    def getHeaders( self ) -> List[Tuple]:
        self._db.open()
        headers = self._db.getHeaders()
        self._db.close()
        return headers

    def createTopLevelFolder( self, name:str ) -> int:
        self._db.open()
        id: int = self._db.insertFolder( 0, text=name, commit=True )
        self._db.commit()
        self._db.close()
        return id

    def insertNote( self, parent_id:int, header:str, text:str, style:str=None, tags:str=None ) -> int:
        self._db.open()
        #1. insert header and text into note
        #2. check if all tags exist in tag
        #3. possibly insert missing tags into tag
        #4. insert references between tags and notes into ref_tag_not
        id:int = self._db.insertNote( parent_id, text, header, style, False )
        self._db.commit()
        self._db.close()
        return id

    def deleteItem( self, id:int, itemspec:str ) -> None:
        self._db.open()
        if itemspec == NOTE:
            self._db.deleteNote( id )
        else:
            self._deleteFolder( id )
        self._db.commit()
        self._db.close()

    def _deleteFolder( self, id:int ):
        #First delete all notes of folder id.
        #Then get a list of all child folders and call this function
        #with each child folder id recursively.
        self._db.deleteNotes( id, False )
        childfolders:List[tuple] = self._db.getFolders( id )
        if len( childfolders ) > 0:
            for folder in childfolders:
                self._deleteFolder( folder[0] )
        else:
            self._db.deleteFolder( id )

def test():
    b = BusinessLogic()
    folders = b.getFolders()
    print( folders )
    #id:int = b.insertNote( 2, "Header Header Header", "Text Text Text" )
    #b.deleteItem( 2, FOLDER )

if __name__ == '__main__': test()