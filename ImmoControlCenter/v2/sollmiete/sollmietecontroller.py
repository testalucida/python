from PySide2.QtCore import Slot
from PySide2.QtWidgets import QApplication, QDialog

from v2.icc.icccontroller import IccController
from v2.icc.iccwidgets import IccCheckTableViewFrame, IccTableView
from v2.icc.interfaces import XMtlZahlung, XEinAus, XSollMiete
from v2.sollmiete.sollmieteeditcontroller import SollMieteEditController
from v2.sollmiete.sollmietelogic import SollmieteLogic
from v2.sollmiete.sollmieteview import SollMieteView, SollMieteDialog

#############  SollMieteController  #####################
class SollMieteController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self._logic = SollmieteLogic()

    def createGui( self ) -> IccCheckTableViewFrame:
        pass


    def showSollMieteAndNkv( self, mv_id:str, jahr:int, monthNumber:int ):
        """
        Zeigt die Sollmiete-View mit den gewünschten Daten
        :param mv_id: Mieter, der beauskunftet werden soll
        :param jahr:
        :param monthNumber: 1 -> Januar, ... , 12 -> Dezember
        :return:
        """
        x:XSollMiete = self._logic.getSollmieteAm( mv_id, jahr, monthNumber )
        v = SollMieteView( x )
        # dlg = SollMieteDialog( v, self.getMainWindow() )
        # dlg.show()
        dlg = SollMieteDialog( v )
        dlg.setWindowTitle( "Sollmiete und NKV für '%s' (%s)" % (x.mv_id, x.mobj_id) )
        dlg.edit_clicked.connect( lambda: self.onEditSollmiete( x, v ) )
        if dlg.exec_() == QDialog.Accepted:
            # Die Bemerkung könnte geändert sein. Keine Validierung, direkt an die Logik zum Speichern übergeben.
            v.applyChanges()
            self._logic.updateSollmieteBemerkung( x.sm_id, x.bemerkung )

    def onEditSollmiete( self, x:XSollMiete, view:SollMieteView ):
        def onBisChanged( bis:str ):
            view.setBis( bis )
        smEditCtrl = SollMieteEditController()
        smEditCtrl.endofcurrentsoll_modified.connect( onBisChanged )
        smEditCtrl.handleFolgeSollmiete( x )

def test():
    app = QApplication()
    ctrl = SollMieteController()
    ctrl.showSollMieteAndNkv( "lukas_franz", 2023, 3 )

    app.exec_()