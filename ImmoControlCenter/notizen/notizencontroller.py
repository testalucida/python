import copy
from typing import List, Any

from PySide2.QtCore import QModelIndex
from PySide2.QtWidgets import QApplication, QDialog, QWidget

from business import BusinessLogic
from datehelper import currentDateIso, getCurrentTimestampIso
from interfaces import XNotiz
from icc.icccontroller import IccController
from notizen.notizengui import NotizenView, NotizEditDialog
from notizen.notizentablemodel import NotizenTableModel
from qtderivates import AuswahlDialog


class NotizenController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self._view:NotizenView() = None
        self._model:NotizenTableModel = None
        self._notizInProcess:XNotiz = None

    def createView( self ) -> QWidget:
        self._model = BusinessLogic.inst().getNotizenModel()
        v = NotizenView( self._model )
        v.getNotizenTableViewWidget().createItem.connect( self.onCreateNotiz )
        v.getNotizenTableViewWidget().editItem.connect( self.onEditNotiz )
        v.getNotizenTableViewWidget().deleteItem.connect( self.onDeleteNotiz )
        v.getNotizenTableViewWidget().getTableView().ctvDoubleClicked.connect( self.onEditNotiz )
        v.saveNotiz.connect( self.onSaveNotizen )
        self._model.setSortable( True )
        self._view = v
        return v

    def onCreateNotiz( self ):
        x = XNotiz()
        x.erfasst_am = currentDateIso()
        if self._editAndValidateNotiz( x ):
            # übernehmen in Tabelle und aktivieren des Save-Buttons
            self._model.insert( x )
            self._view.setSaveButtonEnabled()

    def onEditNotiz( self, index: QModelIndex ):
        self._notizInProcess = x = self._getNotiz( index )
        notizCopy = copy.copy( x )
        if self._editAndValidateNotiz( x ):
            if self._isDifferent( notizCopy, x ):
                # übernehmen in Tabelle und aktivieren des Save-Buttons
                x.lwa = getCurrentTimestampIso()
                self._model.update( x )
                self._view.setSaveButtonEnabled()

    def onDeleteNotiz( self, index: QModelIndex ):
        x = self._getNotiz( index )
        # aus Tabelle löschen und aktivieren des Save-Buttons
        self._model.delete( x )
        self._view.setSaveButtonEnabled()

    def onSaveNotizen( self ):
        self.writeChanges()

    def _editAndValidateNotiz( self, x:XNotiz ) -> bool:
        """
        Öffnet den NoDialog mit dem übergebenen Offenen Posten.
        Wird im Dlg OK gedrückt, werden die eingegebenen (geänderten) Daten geprüft.
        Sind sie in Ordnung, werden die geänderten Daten in den Offenen Posten übernommen
        und der Dialog wird geschlossen.
        :param x:
        :return:
        """
        def getAlleFirmen():
            firmenlist = BusinessLogic.inst().getAlleKreditoren()
            firma = self._chooseBezugFromList( firmenlist )
            edidlg.getEditor().setBezug( firma )
        def getAlleVerwalter():
            vwlist = BusinessLogic.inst().getAlleVerwalter()
            vw = self._chooseBezugFromList( vwlist )
            edidlg.getEditor().setBezug( vw )
        def getAlleMieter():
            mieterlist = BusinessLogic.inst().getAlleMieter()
            mieter = self._chooseBezugFromList( mieterlist )
            edidlg.getEditor().setBezug( mieter )
        def validateNotiz() -> bool:
            xcopy:XNotiz = edidlg.getEditor().getNotizCopyWithChanges()
            msg = BusinessLogic.inst().validateNotiz( xcopy )
            if msg:
                # Validation nicht ok, denn es gibt eine Meldung.
                # Meldung ausgeben und Dialog offen lassen.
                self._view.showException( "Validierungsfehler", msg )
                return False
            else:
                # Validation ok. Zurück zum Aufrufer.
                edidlg.getEditor().guiToData()
                return True

        edidlg = NotizEditDialog( x )
        edidlg.setValidationFunction( validateNotiz )
        edidlg.getEditor().bezugAuswahlFirmaPressed.connect( getAlleFirmen )
        edidlg.getEditor().bezugAuswahlVwPressed.connect( getAlleVerwalter )
        edidlg.getEditor().bezugAuswahlMieterPressed.connect( getAlleMieter )
        edidlg.resize( 600, 400 )
        if edidlg.exec_() == QDialog.Accepted:
            return True
        else:
            return False

    def _chooseBezugFromList( self, l:List[str] ) -> str:
        dlg = AuswahlDialog()
        for i in l:
            dlg.appendItem( i )
        if dlg.exec_() == QDialog.Accepted:
            sel = dlg.getSelection()
            return sel[0][0]
        return ""

    def _isDifferent( self, n1:XNotiz, n2:XNotiz ) -> bool:
        if n1.bezug != n2.bezug or \
            n1.ueberschrift != n2.ueberschrift or \
            n1.text != n2.ueberschrift or \
            n1.erledigt != n2.erledigt:
                return True
        return False


    def getViewTitle( self ) -> str:
        return "Notizen"

    def _getNotiz( self, index: QModelIndex ) -> XNotiz:
        return self._model.getXNotiz( index.row() )

    def isChanged( self ) -> bool:
        return self._view.getTableModel().isChanged()

    def getChanges( self ) -> Any:
        return self._view.getTableModel().getChanges()

    def writeChanges( self, changes:Any=None ) -> bool:
        try:
            BusinessLogic.inst().saveNotizen( self._model )
            self._view.setSaveButtonEnabled( False )
            return True
        except Exception as exc:
            self._view.showException( "Fehler beim Speichern", str( exc ) )
            return False

    def clearChanges( self ) -> None:
        self._view.getTableModel().clearChanges()


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