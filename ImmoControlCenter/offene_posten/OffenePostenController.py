from PySide2.QtCore import QModelIndex
from PySide2.QtWidgets import QApplication, QDialog, QWidget

from business import BusinessLogic
from generictable_stuff.generictableviewdialog import GenericEditableTableView
from interfaces import XOffenerPosten
from mdichildcontroller import MdiChildController
from offene_posten.offenepostengui import OffenePostenDialog, OffenerPostenEditDialog, OffenePostenView
from offene_posten.offenepostentablemodel import OffenePostenTableModel


class OffenePostenController( MdiChildController ):
    def __init__( self ):
        self._view:OffenePostenView() = None
        self._model:OffenePostenTableModel = None

    def createView( self ) -> QWidget:
        self._model = BusinessLogic.inst().getOposModel()
        v = OffenePostenView( self._model )
        v.createOposSignal.connect( self.onCreateOffenerPosten )
        v.editOposSignal.connect( self.onEditOffenerPosten )
        v.deleteOposSignal.connect( self.onDeleteOffenerPosten )
        self._view = v
        return v

    # def createOffenePostenDialog( self, parent=None ) -> OffenePostenDialog:
    #     self._model = BusinessLogic.inst().getOposModel()
    #     self._dlg = OffenePostenDialog( self._model, parent )
    #     d = self._dlg
    #     d.createItem.connect( self.onCreateOffenerPosten )
    #     d.editItem.connect( self.onEditOffenerPosten )
    #     d.deleteItem.connect( self.onDeleteOffenerPosten )
    #     return self._dlg
    #
    # def showOffenePostenDialog( self, modal:bool=False, parent=None ):
    #     dlg = self.createOffenePostenDialog( parent )
    #     if modal:
    #         dlg.setModal( True )
    #         rc = dlg.exec_()
    #     else:
    #         #dlg.setModal( False )
    #         rc = dlg.open()
    #
    #     if rc == QDialog.Accepted:
    #         # save changes by calling BusinessLogic
    #         # ... todo
    #         dlg.accept()
    #     else:
    #         dlg.reject()

    def onCreateOffenerPosten( self ):
        x = XOffenerPosten()
        edi = OffenerPostenEditDialog()
        if edi.exec_() == QDialog.Accepted:
            # call BusinessLogic to create new OffenerPosten
            print( "OffenePostenController.onCreateOffenerPosten(): create new Opos" )
            edi.accept()
        else:
            edi.reject()



    def getViewTitle( self ) -> str:
        return "Offene Posten"

    def save( self ):
        pass

    def onEditOffenerPosten( self, index:QModelIndex ):
        pass

    def onDeleteOffenerPosten( self, index:QModelIndex ):
        pass

    def _getOffenerPosten( self, index:QModelIndex ) -> XOffenerPosten:
        return self._model.getXOffenerPosten( index.row() )

def test():
    app = QApplication()
    c = OffenePostenController()
    # dlg = c.createOffenePostenDialog()
    # dlg.exec_()
    v = c.createView()
    app.exec_()

if __name__ == "__main__":
    test()