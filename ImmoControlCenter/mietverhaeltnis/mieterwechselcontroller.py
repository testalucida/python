from typing import List, Dict, Tuple

from PySide2.QtWidgets import QApplication, QDialog

from business import BusinessLogic
from interfaces import XMietverhaeltnis
from mietverhaeltnis.mieterwechselgui import MietobjektAuswahldialog, MieterwechselDialog


class MieterwechselController:
    def __init__( self ):
        pass

    def startWork( self ):
        dlg = MietobjektAuswahldialog()
        itemtext_list, mobj_list = BusinessLogic.inst().getAllMietobjekte()
        dlg.appendItemList( itemtext_list )
        if dlg.exec_() == QDialog.Accepted:
            auswahl:List[Tuple] = dlg.getSelection()
            itemtext = auswahl[0][0]
            mobj_id = ""
            for n in range( len( itemtext_list ) ):
                if itemtext_list[n] == itemtext:
                    mobj_id = mobj_list[n]
                    break
            self._doWechsel( mobj_id )

    def _doWechsel( self, mobj_id:str ):
        def validateMieterwechsel( ):
            mietEnde_akt = dlg.getAktuellesMietverhaeltnisMietEnde() # das Mietende ist das einzige Attribut, das
                                                        #beim alten Mietverhältnis verändert werden kann
            if not mietEnde_akt:
                dlg.showErrorMessage( "Validierung fehlerhaft", "Das Ende des aktuellen Mietverhältnisses fehlt oder ist fehlerhaft." )
                return False
            xmv_neu_cpy = dlg.getNeuesMietverhaeltnisCopyWithChanges()
            if xmv_neu_cpy.von == "":
                dlg.showErrorMessage( "Validierung fehlerhaft", "Der Beginn des Mietverhältnisses fehlt" )
                return False
            if mietEnde_akt > xmv_neu_cpy.von:
                dlg.showErrorMessage( "Validierung fehlerhaft", "Das Ende des aktuellen Mietverhältnisses muss VOR "
                                                                "dem Anfang des neuen Mietverhältnisses liegen." )
                return False
            if xmv_neu_cpy.name == "" or xmv_neu_cpy.vorname == "":
                dlg.showErrorMessage( "Validierung fehlerhaft", "Vor- und Nachname müssen eingegeben werden." )
                return False
            if xmv_neu_cpy.nettomiete <= 0:
                dlg.showErrorMessage( "Validierung fehlerhaft", "Nettomiete fehlt." )
                return False
            if xmv_neu_cpy.nkv <= 0:
                dlg.showErrorMessage( "Validierung fehlerhaft", "Nebenkostenvorauszahlung fehlt." )
                return False
            return True

        busi:BusinessLogic = BusinessLogic.inst()
        mv_id = busi.getAktuelleMietverhaeltnisId( mobj_id )
        xmv_akt:XMietverhaeltnis = busi.getAktuellesMietverhaeltnis( mv_id )
        xmv_neu = XMietverhaeltnis()
        dlg = MieterwechselDialog( "Mieterwechsel:  " + mobj_id )
        dlg.setAktuellesMietverhaeltnis( xmv_akt )
        dlg.setNeuesMietverhaeltnis( xmv_neu )
        dlg.setValidationFunction( validateMieterwechsel )
        if dlg.exec_() == QDialog.Accepted:
            print( "accepted")
        else: print( "aborted" )


def test():
    app = QApplication()
    c = MieterwechselController()
    c.startWork()

if __name__ == "__main__":
    test()