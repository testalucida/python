import sqlite3
from typing import Any, List, Tuple
from globals import NOTE, FOLDER
from note import Note

class DbAccess:
    def __init__( self ):
        self._con = None
        self._cursor = None

    def open( self ) -> None:
        self._con = sqlite3.connect( 'notes.db' )
        self._cursor = self._con.cursor()

    def close( self ) -> None:
        self._cursor.close()
        self._con.close()

    def getMaxId( self, table:str, id_name:str ) -> int:
        sql = "select max(%s) from %s" %(id_name, table)
        records = self._doRead( sql )
        return records[0][0]

    def insertFolder( self, parent_id:int, text:str,  commit:bool=True ) -> int:
        sql = "insert into folder (parent_id, text) values (%d, '%s');" % (parent_id, text)
        self._doWrite( sql, commit )
        return self.getMaxId( FOLDER, "id" )

    def updateFolderParent( self, folder_id: int, parent_id: int, commit: bool = True ) -> None:
        sql = "update folder set parent_id= " + str( parent_id ) + \
              " where id = " + str( folder_id )
        self._doWrite( sql, commit )

    def updateFolderLabel( self, folder_id: int, label: str, commit: bool = True ) -> None:
        dblabel = label.replace( "'", "''" )
        sql = "update folder set text= '" + dblabel + \
              "' where id = " + str( folder_id )
        self._doWrite( sql, commit )

    def insertNote( self, parent_id:int, text:str, header:str, style="", commit:bool=True ) -> int:
        header = header.replace( "'", "''" )
        text = text.replace( "'", "''" )
        sql = "insert into note (parent_id, text, header, style) values (%d, '%s', '%s', '%s');" % (parent_id, text, header, style)
        self._doWrite( sql, commit )
        return self.getMaxId( NOTE, "id" )

    def updateNote( self, note:Note, commit:bool=True ) -> None:
        header = note.header.replace( "'", "''" )
        text = note.text.replace( "'", "''" )
        sql = "update note set text='%s', header='%s', style='%s' where id = %d" \
              % (text, header, note.style, note.id)
        self._doWrite( sql, commit )

    def updateNoteParent( self, note_id: int, parent_id: int, commit: bool = True ) -> None:
        sql = "update note set parent_id= " + str( parent_id ) + \
              " where id = " + str( note_id )
        self._doWrite( sql, commit )

    def deleteNote( self, id:int, commit:bool=True ):
        sql = "delete from note where id = " + str( id )
        self._doWrite( sql, commit )

    def deleteNotes( self, parent_id:int, commit:bool=True ):
        sql = "delete from note where parent_id = " + str( parent_id )
        self._doWrite( sql, commit )

    def deleteFolder( self, folder_id:int, commit:bool=True ):
        sql = "delete from folder where id = " + str( folder_id )
        self._doWrite( sql, commit )

    def insertTag( self, tag:str, commit:bool=True ) -> int:
        tag = tag.replace( "'", "''" )
        sql = "insert into tag (tag) values ('%s');" % (tag,)
        self._doWrite( sql, commit )
        return self.getMaxId( "tag", "tag_id" )

    def insertRefTagNote( self, note_id:int, tag_id:int, commit:bool=True ) -> None:
        sql = "insert into ref_tag_note (note_id, tag_id) values (%d, %d);" % (note_id, tag_id)
        self._doWrite( sql, commit )

    def deleteTagNoteReferences( self, note_id:int, commit:bool=True ) -> None:
        sql = "delete from ref_tag_note where note_id = " + str( note_id )
        self._doWrite( sql, commit )

    def deleteUnreferencedTags( self, commit:bool=True ) -> None:
        """
        checks if there are tags which are not referenced by any record in ref_tag_note
        and deletes them
        """
        sql = "delete from tag where tag.tag_id not in (select ref_tag_note.tag_id from ref_tag_note )"
        self._doWrite( sql, commit )

    def commit( self ):
        self._con.commit()

    def getNote( self, id:int ) -> Note:
        sql = "select id, parent_id, header, text, coalesce(style, '') from note where id = " + str( id )
        record:List[Tuple] = self._doRead( sql )
        note:Note = Note()
        note.id, note.parent_id, note.header, note.text, note.style = record[0]
        return note

    def getAllNoteIds( self ) -> List[int]:
        sql = "select id from note"
        records: List[Tuple] = self._doRead( sql )
        idlist:List[int] = []
        for r in records:
            idlist.append( r[0] )
        return idlist

    def getNoteFolderId( self, note_id:int ) -> int:
        sql = "select parent_id from note where id = " + str( note_id )
        record:List[Tuple] = self._doRead( sql )
        return record[0][0]

    def getNoteFolder( self, note_id:int ) -> (int, str):
        sql = "select f.id, f.text from folder f " \
              "inner join note n on n.parent_id = f.id where n.id = " + str( note_id )
        record: List[Tuple] = self._doRead( sql )
        if record:
            return ( record[0][0], record[0][1] )
        else:
            return ( -1, "" )

    def getFolders( self, parent_id:int=0 ) -> List[Tuple]:
        sql = "select id, parent_id, text from folder where parent_id = %d" % (parent_id,)
        return self._doRead( sql )

    def getAllFolderIds( self ) -> List[int]:
        sql = "select id from folder"
        records = self._doRead()
        idlist:List[int] = []
        for r in records:
            idlist.append( r[0] )
        return idlist


    def getHeaders( self ) -> List[Tuple]:
        sql = "select id, parent_id, header from note;"
        return self._doRead( sql )

    # def getAllFolders( self ):
    #     sql = "select id, parent_id, text from folder;"
    #     return self._doRead( sql )

    def getNotes( self, parent_id:int=0 ) -> List[Tuple]:
        sql = "select n.id, n.parent_id, n.text, n.header, t.tag " \
              "from note n " \
              "left outer join ref_tag_note rtn on rtn.note_id = n.id " \
              "left outer join tag t on t.tag_id = rtn.tag_id " \
              "where n.parent_id = %d;" % (parent_id,)
        return self._doRead( sql )

    def getTags( self ) -> List[str]:
        sql = "select tag from tag order by tag asc"
        records:List[Tuple] = self._doRead( sql )
        return [x[0] for x in records]

    def getTagId( self, tag:str ) -> int:
        sql = "select tag_id from tag where tag = '%s'" % (tag,)
        record: List[Tuple] = self._doRead( sql )
        return record[0][0]

    def getTagsForNote( self, note_id:int ) -> List[str]:
        sql = "select tag from tag t inner join ref_tag_note r on t.tag_id = r.tag_id where r.note_id = " + str( note_id )
        records: List[Tuple] = self._doRead( sql )
        return [x[0] for x in records]

    def _doRead( self, sql:str ) -> List[Tuple]:
        self._cursor.execute( sql )
        records = self._cursor.fetchall()
        return records

    def _doWrite( self, sql:str, commit:bool ) -> None:
        self._cursor.execute( sql )
        if commit:
            self._con.commit()

# =============================================================================
# crsr.execute("CREATE TABLE employees( \
#                  id integer PRIMARY KEY, \
#                  name text, \
#                  salary real, \
#                  department text, \
#                  position text, \
#                  hireDate text)")
#
# con.commit()
# =============================================================================

def test():
    db = DbAccess()
    db.open()
    id:int = db.getNoteFolderId( 1 )
    id, text = db.getNoteFolder( 1 )
    # db.insertNote( 0, "This is note 1", "Incredible Header" )
    #db.insertFolder( 1, "bla", "", True)
    #id = db.getMaxId( "folder", "id" )
    #id = db.insertFolder( 1, "Harr Harr" )
    #print( id )
    # db.insertTag( "webserver" )
    # db.insertTag( "krautwickel" )
    print( "Folders:\n", db.getFolders() )
    print( "Headers:\n", db.getHeaders() )
    print( "Notes:\n", db.getNotes() )
    print( "Tags:\n", db.getTags() )
    db.close()

if __name__ == '__main__':
    test()