from typing import List, Dict

from PySide2.QtCore import QModelIndex
from PySide2.QtWidgets import QApplication, QDialog, QWidget

from business import BusinessLogic
from datehelper import currentDateIso
from interfaces import XNotiz
from mdichildcontroller import MdiChildController
from notizen.notizengui import NotizenView
from notizen.notizentablemodel import NotizenTableModel
from offene_posten.offenepostengui import OffenerPostenEditDialog, OffenePostenView


class NotizenController( MdiChildController ):
    def __init__( self ):
        self._view:NotizenView() = None
        self._model:NotizenTableModel = None

    def createView( self ) -> QWidget:
        self._model = BusinessLogic.inst().getNotizenModel()
        v = NotizenView( self._model )
        v.getNotizenTableView().createItem.connect( self.onCreateNotiz )
        v.getNotizenTableView().deleteItem.connect( self.onDeleteNotiz )
        v.saveNotiz.connect( self.onSaveNotizen )
        self._view = v
        return v

    def onCreateNotiz( self ):
        print( "createNotiz" )

    def onDeleteNotiz( self ):
        print( "deleteNotiz" )

    def onSaveNotizen( self ):
        print( "saveNotizen" )


    def getViewTitle( self ) -> str:
        return "Notizen"

    def save( self ):
        try:
            BusinessLogic.inst().saveNotizen( self._model )
            self._view.setSaveButtonEnabled( False )
        except Exception as exc:
            self._view.showException( "Fehler beim Speichern", str( exc ) )

    def _getNotiz( self, index: QModelIndex ) -> XNotiz:
        return self._model.getXNotiz( index.row() )


def test():
    app = QApplication()
    c = NotizenController()
    # dlg = c.createOffenePostenDialog()
    # dlg.exec_()
    v = c.createView()
    v.show()
    app.exec_()

if __name__ == "__main__":
    test()