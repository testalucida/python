from PySide2.QtCore import Slot
from PySide2.QtWidgets import QApplication, QDialog

from v2.icc.icccontroller import IccController
from v2.icc.iccwidgets import IccCheckTableViewFrame
from v2.icc.interfaces import XSollHausgeld
from v2.sollhausgeld.sollhausgeldeditcontroller import SollHausgeldEditController
from v2.sollhausgeld.sollhausgeldlogic import SollHausgeldLogic
from v2.sollhausgeld.sollhausgeldview import SollHausgeldView, SollHausgeldDialog

#############  SollMieteController  #####################
class SollHausgeldController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self._logic = SollHausgeldLogic()

    def createGui( self ) -> IccCheckTableViewFrame:
        pass


    def showHgvAndRueZuFue( self, mobj_id:str, jahr:int, monthNumber:int ):
        """
        Zeigt die SollHausgeld-View mit den gewünschten Daten
        :param mobj_id:
        :param jahr:
        :param monthNumber: 1 -> Januar, ... , 12 -> Dezember
        :return:
        """
        x:XSollHausgeld = self._logic.getSollHausgeldAm( mobj_id, jahr, monthNumber )
        v = SollHausgeldView( x )
        dlg = SollHausgeldDialog( v )
        dlg.setWindowTitle( "Soll-Hausgeld für '%s' (%s)" % (x.weg_name, x.mobj_id) )
        dlg.edit_clicked.connect( lambda: self.onEditSollHausgeld( x, v ) )
        if dlg.exec_() == QDialog.Accepted:
            # Die Bemerkung könnte geändert sein. Keine Validierung, direkt an die Logik zum Speichern übergeben.
            v.applyChanges()
            self._logic.updateSollHausgeldBemerkung( x.shg_id, x.bemerkung )


    def onEditSollHausgeld( self, x: XSollHausgeld, view: SollHausgeldView ):
        """
        Im SollHausgeldDialog wurde der Button "Folge-Soll erfassen oder ändern..." gedrückt.
        Wir instanzieren den SollHausgeldEditController und lassen ihn die Anlage eines neuen
        Hausgeld-Intervalls behandeln
        :param x: das derzeitige XSollHausgeld-Objekt
        :param view: die SollHausgeldView, in der o.a. Button gedrückt wurde.
        :return:
        """
        def onBisChanged( bis: str ):
            view.setBis( bis )
        shgEditCtrl = SollHausgeldEditController()
        shgEditCtrl.endofcurrentsoll_modified.connect( onBisChanged )
        shgEditCtrl.handleFolgeSollHausgeld( x )

def test():
    app = QApplication()
    ctrl = SollHausgeldController()
    ctrl.showHgvAndRueZuFue( "remigius", 2023, 3 )
