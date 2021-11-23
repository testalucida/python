from typing import Any

from PySide2.QtWidgets import QApplication, QWidget

from business import BusinessLogic
from icccontroller import IccController
from interfaces import XMietverhaeltnis, XMietobjektExt
from mietobjekt.mietobjektauswahl import MietobjektAuswahl
from mietobjekt.mietobjektview import MietobjektView
from mietverhaeltnis.mieterwechselgui import MieterwechselView


class MietobjektController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self._view:MietobjektView = None
        self._mietobjekt:XMietobjektExt = ""
        self._mietobjektAuswahl = MietobjektAuswahl()

    def createView( self ) -> QWidget:
        #zuerst über den Auswahldialog bestimmen, welche Daten für die View selektiert werden müssen
        mobj_id = self._mietobjektAuswahl.selectMietobjekt()
        if not mobj_id: return None
        busi:BusinessLogic = BusinessLogic.inst()
        self._mietobjekt = busi.getMietobjektExt( mobj_id )
        self._view = MietobjektView( self._mietobjekt )
        self._view.save.connect( self.writeChanges )
        return self._view

    def isChanged( self ) -> bool:
        return False
        # todo
        # changedObj = self._view.getMietobjektCopyWithChanges()
        # return False if changedObj == self._mietobjekt else True

    def getChanges( self ) -> Any:
        return None

    def clearChanges( self ) -> None:
        self._view.clear()

    def writeChanges( self, changes:Any=None ) -> bool:
        #wird von _askWhatToDo gerufen
        # if self._validateMieterwechsel():
        #     self._view.applyChanges()
        #     try:
        #         BusinessLogic.inst().processMieterwechsel( self._mietverhaeltnisVorher.mv_id,
        #                                                    self._view.getAltesMietverhaeltnisMietEnde(),
        #                                                    self._mietverhaeltnisNachher )
        #         return True
        #     except Exception as ex:
        #         self.showErrorMessage( "Mieterwechsel: Speichern fehlgeschlagen", str( ex ) )
        #         return False
        # return False
        return True

    def getViewTitle( self ) -> str:
        return "Master- und Mietobjektdaten zum Mietobjekt " + self._mietobjekt.mobj_id


def test():
    app = QApplication()
    c = MietobjektController()
    d = c.createDialog( None )
    d.exec_()

if __name__ == "__main__":
    test()