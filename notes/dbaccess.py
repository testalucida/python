import sqlite3
from typing import Any, List, Tuple

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
        return self.getMaxId( "folder", "id" )

    def insertNote( self, parent_id:int, text:str, header:str, style="", commit:bool=True ) -> int:
        sql = "insert into note (parent_id, text, header, style) values (%d, '%s', '%s', '%s');" % (parent_id, text, header, style)
        self._doWrite( sql, commit )
        return self.getMaxId( "note", "id" )

    def updateNote( self, id:int, text:str, header:str, style:str="", commit:bool=True ) -> None:
        sql = "update note set text='%s', header='%s', style='%s' where id = %d" % (id, text, header, style)
        self._doWrite( sql, commit )

    def insertTag( self, tag:str, commit:bool=True ):
        sql = "insert into tag (tag) values ('%s');" % (tag,)
        self._doWrite( sql, commit )
        return self.getMaxId( "tag", "tag_id" )

    def insertRefTagNote( self, note_id:int, tag_id:int, commit:bool=True ) -> None:
        sql = "insert into ref_tag_note (note_id, tag_id) values (%d, %d);" % (note_id, tag_id)
        self._doWrite( sql, commit )

    def getFolders( self, parent_id:int=0 ) -> List[Tuple]:
        sql = "select id, parent_id, text from folder where parent_id = %d" % (parent_id,)
        return self._doRead( sql )

    def getNotes( self, parent_id:int=0 ) -> List[Tuple]:
        sql = "select n.id, n.parent_id, n.text, n.header, t.tag " \
              "from note n " \
              "left outer join ref_tag_note rtn on rtn.note_id = n.id " \
              "left outer join tag t on t.tag_id = rtn.tag_id " \
              "where n.parent_id = %d;" % (parent_id,)
        return self._doRead( sql )

    def getTags( self ) -> List[Tuple]:
        sql = "select tag_id, tag from tag "
        return self._doRead( sql )

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
    # db.insertNote( 0, "This is note 1", "Incredible Header" )
    #db.insertFolder( 1, "bla", "", True)
    #id = db.getMaxId( "folder", "id" )
    #id = db.insertFolder( 1, "Harr Harr" )
    #print( id )
    # db.insertTag( "webserver" )
    # db.insertTag( "krautwickel" )
    print( "Folders:\n", db.getFolders() )
    print( "Notes:\n", db.getNotes() )
    print( "Tags:\n", db.getTags() )
    db.close()

if __name__ == '__main__':
    test()