from dbaccess import DbAccess
from globals import NOTE, FOLDER
from libs import *
from note import Note

class BusinessLogic:
    def __init__( self ):
        self._db = DbAccess()

    def getFolders( self, parent_id:int ) -> List[Tuple]:
        # Returns a list of all folders belonging to a given parent_id
        # Each folder is represented by a Tuple containing parent_id, folder_id, text.
        self._db.open()
        folders = self._db.getFolders( parent_id )
        # for f in folders:
        #     print( f )
        self._db.close()
        return folders

    def getNote( self, note_id:int ) -> Note:
        self._db.open()
        note:Note = self._db.getNote( note_id )
        self._db.close()
        return note

    def getAllNoteIds( self ) -> List[int]:
        self._db.open()
        idlist = self._db.getAllNoteIds()
        self._db.close()
        return idlist

    def getAllFolderIds( self ) -> List[int]:
        self._db.open()
        idlist = self._db.getAllNoteIds()
        self._db.close()
        return idlist

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
        return self.createFolder( name, 0, True )

    def createFolder( self, name:str, parent_id:int, commit:bool=True ) -> int:
        self._db.open()
        id: int = self._db.insertFolder( parent_id, text=name, commit=commit )
        self._db.commit()
        self._db.close()
        return id

    def insertNote( self, note:Note ) -> Note:
        """
        Inserts a new created note and returns its id
        """
        self._db.open()
        #1. insert header, text etc. into note
        #2. check if all tags exist in tag
        #3. possibly insert missing tags into tag
        #4. insert references between tags and notes into ref_tag_not
        #5. provides the given note with the new note's id and returns the given note object
        id:int = self._db.insertNote( note.parent_id, note.text, note.header, note.style, False )
        self._db.commit()
        self._db.close()
        note.id = id
        return note

    def changeFolderParent( self, folder_id:int, newParent_id:int ) -> None:
        self._db.open()
        self._db.updateFolderParent( folder_id, newParent_id )
        self._db.close()

    def changeNoteParent( self, note_id:int, newParent_id:int ) -> None:
        self._db.open()
        self._db.updateNoteParent( note_id, newParent_id )
        self._db.close()

    def updateNote( self, note:Note ) -> None:
        self._db.open()
        self._db.updateNote( note )
        self._db.close()

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

        self._db.deleteFolder( id )

def test():
    b = BusinessLogic()
    folders = b.getFolders()
    print( folders )
    #id:int = b.insertNote( 2, "Header Header Header", "Text Text Text" )
    #b.deleteItem( 2, FOLDER )

if __name__ == '__main__': test()