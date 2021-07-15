
from PySide2.QtWidgets import QApplication, QDialog, QWidget

from business import BusinessLogic
from constants import einausart
from mdichildcontroller import MdiChildController
from rendite.renditegui import RenditeView
from rendite.renditetablemodel import RenditeTableModel


class RenditeController( MdiChildController ):
    def __init__( self ):
        MdiChildController.__init__( self )
        self._view:RenditeView() = None
        self._model:RenditeTableModel = None

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
        v.setBetrachtungsjahre( jahre )
        v.setBetrachtungsjahr( jahr )
        v.betrachtungsjahrChanged.connect( self._onBetrachtungsjahrChanged )
        self._model.setSortable( True )
        self._view = v
        return v

    def _onBetrachtungsjahrChanged( self, jahr:int ):
        self._model = BusinessLogic.inst().getRenditeTableModel( jahr )
        self._view.setTableModel( jahr )
        self._model.setSortable( True )

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