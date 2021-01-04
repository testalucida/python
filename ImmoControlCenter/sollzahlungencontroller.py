from enum import IntEnum

from PySide2.QtWidgets import QAction, QWidget

from business import BusinessLogic
from constants import SollType
from mdichildcontroller import MdiChildController
from sollzahlungenview import SollzahlungenView
from sollzahlungentablemodel import SollzahlungenTableModel, SollmietenTableModel, SollHGVTableModel

class SollzahlungenController( MdiChildController ):
    """
    Controller für Soll-Mieten und Soll-HG-Vorauszahlungen
    """
    def __init__( self, soll_type: SollType ):
        MdiChildController.__init__( self )
        self._type:SollType = soll_type
        self._view:SollzahlungenView = None
        self._nextSollAction = QAction( "Folge-Soll erfassen" )
        self._tm:SollzahlungenTableModel = None

    def save( self ):
        pass

    def createView( self ) -> QWidget:
        view = self._view = SollzahlungenView( self._type )
        if self._type == SollType.MIETE_SOLL:
            self._tm = SollmietenTableModel()
        else:
            sollHG = BusinessLogic.inst().getAlleSollHausgelder()
            self._tm = SollHGVTableModel( sollHG )
            view.setSollzahlungenTableModel( self._tm )
        return view

    def getViewTitle( self ) -> str:
        return "Soll-Mieten" if self._type == SollType.MIETE_SOLL else "Soll-Hausgelder"

def test():
    import sys
    from PySide2 import QtWidgets
    app = QtWidgets.QApplication( sys.argv )
    c = SollzahlungenController( SollType.HAUSGELD_SOLL )
    v = c.createView()
    v.show()
    sys.exit( app.exec_() )

if __name__ == "__main__":
    test()