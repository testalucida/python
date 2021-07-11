from typing import List, Dict

from PySide2.QtCore import QModelIndex
from PySide2.QtWidgets import QApplication, QDialog, QWidget

from business import BusinessLogic
from datehelper import currentDateIso
from generictable_stuff.generictableviewdialog import EditableTableViewWidget
from interfaces import XOffenerPosten
from mdichildcontroller import MdiChildController
from offene_posten.offenepostengui import OffenerPostenEditDialog, OffenePostenView
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
        v.saveChangesSignal.connect( self.onSaveChanges )
        self._view = v
        return v

    def onCreateOffenerPosten( self ):
        x = XOffenerPosten()
        x.erfasst_am = currentDateIso()
        if self._editAndValidateOffenerPosten( x ):
            # übernehmen in Tabelle und aktivieren des Save-Buttons
            self._model.insert( x )
            self._view.setSaveButtonEnabled()

    def onEditOffenerPosten( self, index: QModelIndex ):
        self._oposInProcess = x = self._getOffenerPosten( index )
        if self._editAndValidateOffenerPosten( x ):
            # übernehmen in Tabelle und aktivieren des Save-Buttons
            self._model.update( x )
            self._view.setSaveButtonEnabled()

    def onDeleteOffenerPosten( self, index: QModelIndex ):
        x = self._getOffenerPosten( index )
        # aus Tabelle löschen und aktivieren des Save-Buttons
        self._model.delete( x )
        self._view.setSaveButtonEnabled()

    def onSaveChanges( self ):
        self.save()

    def _editAndValidateOffenerPosten( self, x:XOffenerPosten ) -> bool:
        """
        Öffnet den OffenePostenDialog mit dem übergebenen Offenen Posten.
        Wird im Dlg OK gedrückt, werden die eingegebenen (geänderten) Daten geprüft.
        Sind sie in Ordnung, werden die geänderten Daten in den Offenen Posten übernommen
        und der Dialog wird geschlossen.
        :param x:
        :return:
        """
        def getAllFirmen():
            firmenlist = BusinessLogic.inst().getAlleKreditoren()
            firma = self._chooseDebiKrediFromList( firmenlist )
            edidlg.getEditor().setDebiKredi( firma )
        def getAllVerwalter():
            vwlist = BusinessLogic.inst().getAlleVerwalter()
            vw = self._chooseDebiKrediFromList( vwlist )
            edidlg.getEditor().setDebiKredi( vw )
        def validateOpos() -> bool:
            xcopy:XOffenerPosten = edidlg.getEditor().getOposCopyWithChanges()
            msg = BusinessLogic.inst().validateOffenerPosten( xcopy )
            if msg:
                # Validation nicht ok, denn es gibt eine Meldung.
                # Meldung ausgeben und Dialog offen lassen.
                self._view.showException( "Validierungsfehler", msg )
                return False
            else:
                # Validation ok. Zurück zum Aufrufer.
                edidlg.getEditor().guiToData()
                return True

        edidlg = OffenerPostenEditDialog( x )
        edidlg.setValidationFunction( validateOpos )
        edidlg.chooseFirmaSignal.connect( getAllFirmen )
        edidlg.chooseVerwalterSignal.connect( getAllVerwalter )
        if edidlg.exec_() == QDialog.Accepted:
            return True
        else:
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
        try:
            BusinessLogic.inst().saveOffenePosten( self._model )
            self._view.setSaveButtonEnabled( False )
        except Exception as exc:
            self._view.showException( "Fehler beim Speichern", str( exc ) )

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