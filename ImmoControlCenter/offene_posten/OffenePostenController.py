from typing import List

from PySide2.QtCore import QModelIndex
from PySide2.QtWidgets import QApplication, QDialog, QWidget

from business import BusinessLogic
from datehelper import currentDateIso
from generictable_stuff.generictableviewdialog import GenericEditableTableView
from interfaces import XOffenerPosten
from mdichildcontroller import MdiChildController
from offene_posten.offenepostengui import OffenePostenDialog, OffenerPostenEditDialog, OffenePostenView
from offene_posten.offenepostentablemodel import OffenePostenTableModel
from qtderivates import AuswahlDialog


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

    def onCreateOffenerPosten( self ):
        x = XOffenerPosten()
        x.erfasst_am = currentDateIso()
        if self._editAndValidateOffenerPosten( x ):
            # save
            pass

    def onEditOffenerPosten( self, index: QModelIndex ):
        x = self._getOffenerPosten( index )
        if self._editAndValidateOffenerPosten( x ):
            # save
            pass

    def onDeleteOffenerPosten( self, index: QModelIndex ):
        x = self._getOffenerPosten( index )
        # delete

    def _editAndValidateOffenerPosten( self, x:XOffenerPosten ) -> bool:
        def getAllFirmen():
            firmenlist = BusinessLogic.inst().getAlleKreditoren()
            firma = self._chooseDebiKrediFromList( firmenlist )
            edi.getEditor().setDebiKredi( firma )
        def getAllVerwalter():
            vwlist = BusinessLogic.inst().getAlleVerwalter()
            vw = self._chooseDebiKrediFromList( vwlist )
            edi.getEditor().setDebiKredi( vw )
        edi = OffenerPostenEditDialog( x )
        edi.chooseFirmaSignal.connect( getAllFirmen )
        edi.chooseVerwalterSignal.connect( getAllVerwalter )
        if edi.exec_() == QDialog.Accepted:
            edi.getEditor().changesToModel()
            msg = BusinessLogic.inst().validateOffenerPosten( x )
            if msg:
                # Validation nicht ok, denn es gibt eine Meldung.
                # Meldung ausgeben und Dialog offen lassen.
                pass
            else:
                # Validation ok. Zurück zum Aufrufer.
                edi.accept()
                return True
        else:
            edi.reject()
            return False

    def _chooseDebiKrediFromList( self, l:List[str] ) -> str:
        dlg = AuswahlDialog()
        for i in l:
            dlg.appendItem( i )
        if dlg.exec_() == QDialog.Accepted:
            sel = dlg.getSelection()
            return sel[0][0]
        return ""

    def getViewTitle( self ) -> str:
        return "Offene Posten"

    def save( self ):
        pass

    def _getOffenerPosten( self, index:QModelIndex ) -> XOffenerPosten:
        return self._model.getXOffenerPosten( index.row() )

def test():
    app = QApplication()
    c = OffenePostenController()
    # dlg = c.createOffenePostenDialog()
    # dlg.exec_()
    v = c.createView()
    v.show()
    app.exec_()

if __name__ == "__main__":
    test()