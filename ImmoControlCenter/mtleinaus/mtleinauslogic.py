from typing import List

import datehelper
from constants import einausart
from interfaces import XVerwaltung
#from mietverhaeltnis.mietverhaeltnislogic import MietverhaeltnisLogic
from mtleinaus.mtleinausdata import MtlEinAusData
from verwaltung.verwaltunglogic import VerwaltungLogic


class MtlEinAusLogic:
    def __init__(self):
        self._db:MtlEinAusData = MtlEinAusData()

    def existsEinAusSet( self, art:einausart, jahr:int ) -> bool:
        try:
            return self._db.existsEinAusArt( art, jahr )
        except Exception as ex:
            # Exception user-freundlich machen:
            raise Exception( "Fehler beim Prüfen des EinAus-Sets für Jahr '%d':\n%s" % (jahr, str( ex )) )

    def createFolgejahrSet( self ) -> int:
        """
        Ermittelt das Folgjahr <jahr>.
        Wird diese Methode im Januar 2022 aufgerufen, und für 2022 ist noch kein Folge-Set angelegt,
        dann gilt 2022 als <jahr>
        Prüft, ob für <jahr> bereits ein Set angelegt ist.
        Wenn ja, Exception.
        Wenn nein, legt diese Methode
        1.) für jedes Mietverhältnis, das in <jahr> wenigstens teilweise aktiv ist,
        einen Mietesatz in Tabelle mtleinaus an.
        2.) für jede Verwaltung, die in <jahr> wenigstens teilweise aktiv ist, einen
        HGV-Satz in Tabelle mtleinaus an.
        Macht abschließend einen Commit.
        :return: das neu angelegte Jahr
        """
        from mietverhaeltnis.mietverhaeltnislogic import MietverhaeltnisLogic # wg. Zirkelreferenz in
                                                                        # mietverhaeltnislogic.py
        folgejahr = datehelper.getCurrentYear() # aktuelles jahr
        # mit aktuellem Jahr prüfen (wenn Meth. im Jan. des neuen Jahres aufgerufen wird:
        if self.existsEinAusSet( einausart.MIETE, folgejahr ):
            folgejahr += 1
        if self.existsEinAusSet( einausart.MIETE, folgejahr ):
            # Das MtlEinAus-Set existiert auch schon fürs Folgejahr - dann ist der Aufruf dieser Methode nicht zulässig
            raise Exception( "Das Folgejahr '%d' existiert bereits." % folgejahr )

        mvlogic = MietverhaeltnisLogic()
        mvlist = mvlogic.getAktiveMietverhaeltnisseKurz( folgejahr )
        for mv in mvlist:
            self.insertMtlEinAusFuerMieter( mv.mv_id, folgejahr )

        vwlogic = VerwaltungLogic()
        vwglist: List[XVerwaltung] = vwlogic.getAktiveVerwaltungen( folgejahr )
        for vwg in vwglist:
            self.insertMtlEinAusFuerVerwaltung( vwg.vwg_id, folgejahr )

        return folgejahr

    def insertMtlEinAusFuerMieter( self, mv_id:str, jahr:int ):
        try:
            self._db.insertMtlEinAus( mv_id, einausart.MIETE, jahr )
        except Exception as ex:
            raise Exception( "Fehler bei der Anlage des Jahressets für Mietverhaeltnis '%s':\n%s"
                             % (mv_id, str( ex )) )

    def insertMtlEinAusFuerVerwaltung( self, vwg_id:str, jahr:int ):
        try:
            self._db.insertMtlEinAus( vwg_id, einausart.HGV, jahr )
        except Exception as ex:
            raise Exception( "Fehler bei der Anlage des Jahressets für Verwaltung '%s':\n%s"
                             % (vwg_id, str( ex )) )


def test():
    logic = MtlEinAusLogic()
    #logic.createFolgejahrSet()