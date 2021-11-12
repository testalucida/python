from typing import Any

from PySide2.QtWidgets import QApplication, QWidget

from business import BusinessLogic
from icccontroller import IccController
from interfaces import XMietverhaeltnis
from mietobjekt.mietobjektauswahl import MietobjektAuswahl
from mietverhaeltnis.mieterwechselgui import MieterwechselView


class MieterwechselController( IccController ):
    def __init__( self ):
        IccController.__init__( self )
        self._mobj_id:str = ""
        self._view:MieterwechselView = None
        self._mietverhaeltnisVorher:XMietverhaeltnis = None
        self._mietverhaeltnisNachher:XMietverhaeltnis = None
        self._mietobjektAuswahl = MietobjektAuswahl()

    def createView( self ) -> QWidget:
        #zuerst über den Auswahldialog bestimmen, welche Daten für die View selektiert werden müssen
        self._mobj_id:str = self._mietobjektAuswahl.selectMietobjekt()
        if not self._mobj_id: return
        self._view = MieterwechselView()
        self._view.mieterwechsel_save.connect( self.writeChanges )
        busi: BusinessLogic = BusinessLogic.inst()
        self._mietverhaeltnisVorher, self._mietverhaeltnisNachher = busi.getMieterwechseldaten( self._mobj_id )
        self._view.setAltesMietverhaeltnis( self._mietverhaeltnisVorher )
        self._view.setNeuesMietverhaeltnis( self._mietverhaeltnisNachher )
        return self._view

    def _validateMieterwechsel( self ) -> bool:
        v = self._view
        mietEnde_akt = v.getAltesMietverhaeltnisMietEnde()  # das Mietende ist das einzige Attribut, das
                                                            # beim alten Mietverhältnis verändert werden kann
        if not mietEnde_akt:
            self.showErrorMessage( "Validierung fehlerhaft",
                                  "Das Ende des aktuellen Mietverhältnisses fehlt oder ist fehlerhaft." )
            return False
        xmv_neu_cpy = v.getNeuesMietverhaeltnisCopyWithChanges()
        if xmv_neu_cpy.von == "":
            self.showErrorMessage( "Validierung fehlerhaft", "Der Beginn des Mietverhältnisses fehlt" )
            return False
        if mietEnde_akt > xmv_neu_cpy.von:
            self.showErrorMessage( "Validierung fehlerhaft", "Das Ende des aktuellen Mietverhältnisses muss VOR "
                                                            "dem Anfang des neuen Mietverhältnisses liegen." )
            return False
        if xmv_neu_cpy.name == "" or xmv_neu_cpy.vorname == "":
            self.showErrorMessage( "Validierung fehlerhaft", "Vor- und Nachname müssen eingegeben werden." )
            return False
        if xmv_neu_cpy.nettomiete <= 0:
            self.showErrorMessage( "Validierung fehlerhaft", "Nettomiete fehlt." )
            return False
        if xmv_neu_cpy.nkv <= 0:
            self.showErrorMessage( "Validierung fehlerhaft", "Nebenkostenvorauszahlung fehlt." )
            return False
        return True

    def isChanged( self ) -> bool:
        xmv_neu = self._view.getNeuesMietverhaeltnisCopyWithChanges()
        return False if xmv_neu.equals( self._mietverhaeltnisNachher ) else True

    def getChanges( self ) -> Any:
        return None

    def clearChanges( self ) -> None:
        pass

    def writeChanges( self, changes:Any=None ) -> bool:
        #wird von _askWhatToDo gerufen
        if self._validateMieterwechsel():
            self._view.applyChanges()
            try:
                BusinessLogic.inst().processMieterwechsel( self._mietverhaeltnisVorher.mv_id,
                                                           self._view.getAltesMietverhaeltnisMietEnde(),
                                                           self._mietverhaeltnisNachher )
                return True
            except Exception as ex:
                self.showErrorMessage( "Mieterwechsel: Speichern fehlgeschlagen", str( ex ) )
                return False
        return False


    def getViewTitle( self ) -> str:
        return "Mieterwechsel " + self._mobj_id


def test():
    app = QApplication()
    c = MieterwechselController()
    c.startWork()

if __name__ == "__main__":
    test()