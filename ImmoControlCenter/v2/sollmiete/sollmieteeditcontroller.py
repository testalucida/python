from PySide2.QtWidgets import QApplication, QDialog

from base.messagebox import ErrorBox
from v2.icc.icccontroller import IccController
from v2.icc.iccwidgets import IccCheckTableViewFrame, IccTableView
from v2.icc.interfaces import XMtlZahlung, XEinAus, XSollMiete


#############  SollMieteController  #####################
from v2.sollmiete.sollmieteeditview import SollMieteEditView, SollMieteEditDialog
from v2.sollmiete.sollmietelogic import SollmieteLogic
from v2.sollmiete.sollmieteview import SollMieteView, SollMieteDialog


class SollMieteEditController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self._logic = SollmieteLogic()
        self._tableViewFrame:IccCheckTableViewFrame = None
        self._tv:IccTableView = None
        #self._x:XSollMiete = None # hier wird eine neue/geänderte Sollmiete geparkt

    def createGui( self ) -> IccCheckTableViewFrame:
        pass

    def handleFolgeSollmiete( self, currentSoll:XSollMiete ):
        """
        currentSoll ist die derzeitige Sollmiete.
        Von der Geschäftslogik holen wir erstmal ein passendes Folge-Sollmiete-Objekt und zeigen das dann zur
        Änderung im SollMieteEditDialog an.
        :param currentSoll: derzeitige Sollmiete
        :return:
        """
        assert( currentSoll.sm_id > 0 )
        folgeX:XSollMiete = self._logic.getFolgeSollmiete( currentSoll )
        self.showSollMieteEditDialog( folgeX )

    def showSollMieteEditDialog( self, x:XSollMiete ):
        """
        Zeigt den SollmieteEditDialog, um ein neues Sollmiete-Intervall anzulegen bzw. ein schon für die Zukunft
        angelegtes zu bearbeiten.
        :param x: XSollMiete-Objekt, das hier bearbeitet werden soll
        :return:
        """
        def validate() -> bool:
            msg = self._logic.validate( x )
            if msg:
                box = ErrorBox( "Validierungsfehler", msg, "" )
                box.exec_()
                return False
            else:
                return True
        v = SollMieteEditView( x )
        dlg = SollMieteEditDialog( v )
        dlg.setBeforeAcceptFunction( validate )
        if dlg.exec_() == QDialog.Accepted:
            # Wenn wir hier landen, wurde die Validierung bereits positiv erledigt.
            v.applyChanges()
            try:
                self._logic.saveFolgeSollmiete( x )
            except Exception as ex:
                box = ErrorBox( "Fehler beim Speichern der Sollmiete", str(ex), "" )
                box.exec_()

def test():
    app = QApplication()
    ctrl = SollMieteEditController()
    #ctrl.showSollMieteEditDialog( "lukas_franz", 2022, 5 )

    app.exec_()