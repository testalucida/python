from typing import Any

import jsonpickle
from PySide2.QtWidgets import QApplication, QWidget

from business import BusinessLogic
from icc.icccontroller import IccController
from interfaces import XMietobjektExt
from mietobjekt.mietobjektauswahl import MietobjektAuswahl
from mietobjekt.mietobjektlogic import MietobjektLogic
from mietobjekt.mietobjektucc import MietobjektUcc
from mietobjekt.mietobjektview import MietobjektView
from returnvalue import ReturnValue


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
        return self._view.isChanged()

    def getChanges( self ) -> Any:
        return None

    def clearChanges( self ) -> None:
        pass

    def writeChanges( self, changes:Any=None ) -> bool:
        x:XMietobjektExt = self._view.getMietobjektCopyWithChanges()
        ucc = MietobjektUcc()
        msg = ucc.modifyObjekt( x )
        if msg:
            self.showErrorMessage( "Fehler beim Speichern der Daten", msg )
            return False
        self._view.resetChangeFlag()
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