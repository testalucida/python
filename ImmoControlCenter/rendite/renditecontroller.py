from PySide2.QtCore import QPoint
from PySide2.QtWidgets import QApplication, QWidget, QAction

from business import BusinessLogic
from constants import einausart
from generictable_stuff.generictableviewdialog import GenericTableViewDialog
from mdichildcontroller import MdiChildController
from rendite.ausgabentablemodel import AusgabenTableModel
from rendite.renditegui import RenditeView
from rendite.renditetablemodel import RenditeTableModel


class RenditeController( MdiChildController ):
    def __init__( self ):
        MdiChildController.__init__( self )
        self._view:RenditeView() = None
        self._model:RenditeTableModel = None
        self._jahr = 0

    def createView( self ) -> QWidget:
        busi:BusinessLogic = BusinessLogic.inst()
        jahre = busi.getExistingJahre( einausart.MIETE )
        jahr = 0
        if len( jahre ) > 0:
            if len( jahre ) > 1:
                jahr = jahre[1] # das aktuelle minus 1 - für das liegen die Daten komplett vor
            else:
                jahr = jahre[0]
        self._model = busi.getRenditeTableModel( jahr )
        v = RenditeView( self._model )
        v.setWindowTitle( "Erträge der Objekte" )
        v.setBetrachtungsjahre( jahre )
        v.setBetrachtungsjahr( jahr )
        v.betrachtungsjahrChanged.connect( self._onBetrachtungsjahrChanged )
        tv = v.getRenditeTableView()
        tv.detaillierteAusgabenSignal.connect( self._onDetaillierteAusgaben )
        tv.setAlternatingRowColors( True )
        tv.setSortingEnabled( True )
        self._model.setSortable( True )
        self._view = v
        self._jahr = jahr
        return v

    def _onDetaillierteAusgaben( self, action:QAction, point:QPoint, row:int  ):
        model:AusgabenTableModel = BusinessLogic.inst().getDetaillierteAusgaben( self._model, row, self._jahr )
        dlg = GenericTableViewDialog( model )
        dlg.setWindowTitle( "Detaillierte Ausgaben" )
        dlg.exec_()

    def _onBetrachtungsjahrChanged( self, jahr:int ):
        self._model = BusinessLogic.inst().getRenditeTableModel( jahr )
        self._view.setTableModel( jahr )
        self._model.setSortable( True )
        self._jahr = jahr

    def getViewTitle( self ) -> str:
        return "Renditebetrachtung"

    def save( self ):
        pass


def test():
    app = QApplication()
    c = RenditeController()
    # dlg = c.createOffenePostenDialog()
    # dlg.exec_()
    v = c.createView()
    v.show()
    app.exec_()

if __name__ == "__main__":
    test()