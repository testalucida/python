from typing import Any

from PySide2.QtWidgets import QApplication, QWidget

from icc.icccontroller import IccController
from interfaces import XMieterwechsel
from messagebox import ErrorBox, InfoBox
from mietobjekt.mietobjektauswahl import MietobjektAuswahl
from mietverhaeltnis.mieterwechselgui import MieterwechselView
from mietverhaeltnis.mietverhaeltnislogic import MietverhaeltnisLogic
from mietverhaeltnis.mietverhaeltnisservices import MietverhaeltnisServices
from returnvalue import ReturnValue


class MieterwechselController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self._mobj_id:str = ""
        self._xmieterwechsel:XMieterwechsel = None
        self._view:MieterwechselView = None
        self._mietobjektAuswahl = MietobjektAuswahl()

    def createView( self ) -> QWidget:
        #zuerst über den Auswahldialog bestimmen, welche Daten für die View selektiert werden müssen
        self._mobj_id:str = self._mietobjektAuswahl.selectMietobjekt()
        if not self._mobj_id: return None
        self._view = MieterwechselView()
        self._view.mieterwechsel_save.connect( self.writeChanges )
        #busi: BusinessLogic = BusinessLogic.inst()
        # self._mietverhaeltnisVorher, self._mietverhaeltnisNachher = busi.getMieterwechseldaten( self._mobj_id )
        # self._view.setAltesMietverhaeltnis( self._mietverhaeltnisVorher )
        # self._view.setNeuesMietverhaeltnis( self._mietverhaeltnisNachher )
        # xmieterwechsel = busi.getMieterwechseldaten( self._mobj_id )
        mvlogic = MietverhaeltnisLogic()
        self._xmieterwechsel = mvlogic.getMieterwechseldaten( self._mobj_id )
        self._view.setMieterwechselData( self._xmieterwechsel )
        print( "MieterwechselController.createView() beendet. ChangeFlag = ", self._view.isChanged() )
        return self._view

    def isChanged( self ) -> bool:
        #xmw_gui = self._view.getMieterwechselDataCopyWithChanges()
        #return False if xmw_gui.equals( self._xmieterwechsel ) else True
        return self._view.isChanged()

    def getChanges( self ) -> Any:
        return None

    def clearChanges( self ) -> None:
        pass

    def writeChanges( self, changes:Any=None ) -> bool:
        self._view.applyChanges()  # Änderungen von der GUI in XMieterwechsel übernehmen
        retval:ReturnValue = MietverhaeltnisServices.processMieterwechsel( self._view.getMieterwechselData() )
        if not retval.missionAccomplished():
            box = ErrorBox( "Fehler beim Mieterwechsel", retval.exceptiontype, retval.errormessage )
            box.exec_()
            return False
        box = InfoBox( "Mieterwechsel", "Verarbeitung erfolgreich.", "", "OK" )
        box.exec_()
        self._view.setSaveButtonEnabled( False )
        return True

    def getViewTitle( self ) -> str:
        return "Mieterwechsel " + self._mobj_id


def test():
    app = QApplication()
    c = MieterwechselController()
    v = c.createView()
    v.show()
    app.exec_()

if __name__ == "__main__":
    test()