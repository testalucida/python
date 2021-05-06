import sqlite3

from PySide2.QtWidgets import QApplication, QWidget

from dbaccess import DbAccess


class Erbschaft_DataAccess( DbAccess ):
    def __init__( self, dbname: str ):
        DbAccess.__init__( self, dbname )

class Erbschaft_Logic:
    def __init__(self):
        dbname = "/home/martin/Vermietung/ImmoControlCenter/immo.db"
        self._db = Erbschaft_DataAccess( dbname )

class Erbschaft_Controller():
    def __init__( self, view ):
        self._view = view

class VerteilungView( QWidget ):
    def __init__( self, parent=None ):
        QWidget.__init__( self, parent )
        dbname = "/home/martin/Vermietung/ImmoControlCenter/immo.db"
        self._con = sqlite3.connect( dbname )
        self._cursor = self._con.cursor()

def main():
    app = QApplication()

    app.exec_()

if __name__ == "__main__":
    main()