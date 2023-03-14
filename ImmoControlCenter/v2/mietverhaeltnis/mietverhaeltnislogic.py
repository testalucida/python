from typing import List

import datehelper
from v2.icc.interfaces import XMietverhaeltnis, XMieterwechsel, XMietverhaeltnisKurz, XSollMiete
from v2.mietverhaeltnis.mietverhaeltnisdata import MietverhaeltnisData
from v2.mtleinaus.mtleinauslogic import MtlEinAusLogic
from v2.sollmiete.sollmietelogic import SollmieteLogic


class MietverhaeltnisLogic:
    """
    Stellt die Funktionen zur Selektion, Neuanlage, Änderung und Kündigung von Mietverhältnissen bereit.
    Außerdem eine Methode zur Ermittlung der Daten für einen Mieterwechsel.
    **BEACHTE***
    Die Methoden dieser Klasse machen keine Commits!!
    Diese müssen in den übergeordneten UCC-Klassen gemacht werden.
    ***
    Exceptions aus der Datenbank werden von den Methoden dieser Klasse aufgefangen und
    in Exceptions mit user-lesbaren Meldungen umgewandelt. (Work in progress ;-))
    ************
    """
    def __init__( self ):
        self._db:MietverhaeltnisData = MietverhaeltnisData()

    def getAktuellesMietverhaeltnis( self, mv_id:str ) -> XMietverhaeltnis:
        try:
            return self._db.getAktuellesMietverhaeltnis( mv_id )
        except Exception as ex:
            raise Exception( "Fehler beim Lesen des Aktuellen Mietverhältnisses für '%s':\n'%s' " % (mv_id, str(ex)) )

    def getAktuellesMietverhaeltnisByMietobjekt( self, mobj_id:str ) -> XMietverhaeltnis:
        try:
            mv_id = self._db.getAktuelleMV_IDzuMietobjekt( mobj_id )
            xmv = self._db.getAktuellesMietverhaeltnis( mv_id )
            return xmv
        except Exception as ex:
            raise Exception( "Fehler beim Lesen des Aktuellen Mietverhältnisses zu Mietobjekt '%s':\n'%s' " %
                             ( mobj_id, str(ex)) )

    def getMietverhaeltnisListe( self, mobj_id:str ) -> List[XMietverhaeltnis]:
        try:
            return self._db.getMietverhaeltnisse( mobj_id )
        except Exception as ex:
            raise Exception( "Fehler beim Lesen der Liste der Mietverhältnisse zu Mietobjekt '%s':\n'%s' " %
                             ( mobj_id, str(ex)) )

    def getMietverhaeltnisById( self, id:int ) -> XMietverhaeltnis:
        """
        Liefert das Mietverhältnis mit der Mietverhältnis-ID <id>
        :param id:
        :return:
        """
        return self._db.getMietverhaeltnisById( id )

    def getKuendigungsdatumParts( self, mv_id:str ) -> (int, int, int) or None :
        dic = self._db.getAktuellesMietverhaeltnisVonBis( mv_id )
        bis = dic["bis"]
        if bis:
            return datehelper.getDateParts( bis )
        else:
            return None

    def getMieterwechseldaten( self, mobj_id:str ) -> XMieterwechsel:
        """
        Liefert die Daten, die für einen Mieterwechsel notwendig sind:
        Das aktuelle Mietverhältnis und ENTWEDER das schon für die Zukunft angelegte oder, wenn es
        kein solches gibt, ein leeres XMietverhaeltnis-Objekt.
        :param mobj_id:
        :return:
        """
        mv_id = self._db.getAktuelleMV_IDzuMietobjekt( mobj_id )
        xmv_akt: XMietverhaeltnis = self.getAktuellesMietverhaeltnis( mv_id )
        xmv_next: XMietverhaeltnis = self._db.getFutureMietverhaeltnis( mobj_id )
        if not xmv_next:
            xmv_next = XMietverhaeltnis()
            xmv_next.mobj_id = mobj_id
        return XMieterwechsel( xmv_akt, xmv_next )

    def getAktiveMietverhaeltnisseKurz( self, jahr:int ) -> List[XMietverhaeltnisKurz]:
        """
        Liefert alle Mietverhältnisse, die im Jahr <jahr> aktiv sind.
        Das sind auch die, die in <jahr> enden oder anfangen.
        :param jahr:
        :return:
        """
        return self._db.getAktiveMietverhaeltnisseKurz( jahr, orderby="mv_id" )

    def _create_mv_id( self, name:str, vorname:str ) -> str:
        def replaceUmlauteAndBlanks( s:str ) -> str:
            s = s.lower()
            s = s.replace( "ä", "ae" )
            s = s.replace( "ö", "oe" )
            s = s.replace( "ü", "ue" )
            s = s.replace( "ß", "ss" )
            s = s.replace( " ", "" )
            return s
        name = replaceUmlauteAndBlanks( name )
        vorname = replaceUmlauteAndBlanks( vorname )
        return name + "_" + vorname

    def createMietverhaeltnis( self, xmv:XMietverhaeltnis ):
        """
        Prüft die für die Neuanlage notwendigen Daten für das Mietverhältnis.
        (Die für die Anlage des Sollmieten-Satzes notwendigen Daten werden in sollmietelogic geprüft.)
        Macht einen Insert in Tabelle mietverhaeltnis und ruft sollmietelogic.createSollmiete() auf.
        :param xmv:
        :return:
        """
        msg = self.validateMietverhaeltnisDaten( xmv )
        if msg:
            raise Exception( "Daten des neuen Mietverhältnisses fehlerhaft:\n%s" % msg )
        xmv.mv_id = self._create_mv_id( xmv.name, xmv.vorname )

        #prüfen, ob schon ein Mietverhältnis mit dieser mv_id existiert:
        try:
            if self._db.existsAktivesOderZukuenftigesMietverhaeltnis( xmv.mv_id ):
                raise Exception( "Anlage Mietverhältnis fehlgeschlagen:\nEs existiert ein aktives Mietverhälntis für "
                                 "mv_id '%s'." % xmv.mv_id )
        except Exception as ex:
            raise Exception( "Fehler bei der Dublettenprüfung bei Anlage Mietverhältnis für '%s':\n'%s'"
                             % (xmv.mv_id, str(ex) ) )

        # MV-Satz anlegen:
        try:
            self._db.insertMietverhaeltnis( xmv )
            xmv.id = self._db.getMaxId( "mietverhaeltnis", "id" )
        except Exception as ex:
            raise Exception( "Bei der Anlage des Mietverhältnisses für '%s' ist der DB-Insert "
                             "in die Tabelle 'mietverhaeltnis' fehlgeschlagen:\n'%s'"
                             % (xmv.mv_id, str(ex) ) )

        # Sollmiete-Satz anlegen:
        xsm = XSollMiete()
        xsm.mv_id = xmv.mv_id
        xsm.von = xmv.von
        xsm.bis = xmv.bis
        xsm.netto = xmv.nettomiete
        xsm.nkv = xmv.nkv
        sml = SollmieteLogic()
        try:
            sml.createSollmiete( xsm )
            xsm.sm_id = self._db.getMaxId( "sollmiete", "sm_id" )
        except Exception as ex:
            raise Exception( "Bei der Anlage des Mietverhältnisses für '%s' ist der DB-Insert "
                             "in die Tabelle 'sollmiete' fehlgeschlagen:\n'%s'"
                             % (xsm.mv_id, str( ex )) )

        # MtlEinAus-Satz anlegen:
        meinauslogic = MtlEinAusLogic()
        jahr = int(xmv.von[:4])
        try:
            #meinauslogic.insertMtlEinAusFuerMieter( xmv.mv_id, jahr )
            pass
        except Exception as ex:
            raise Exception( "Bei der Anlage des Mietverhältnisses für '%s' ist der DB-Insert "
                             "in die Tabelle 'mtleinaus' fehlgeschlagen:\n'%s'"
                             % (xmv.mv_id, str( ex )) )


    def kuendigeMietverhaeltnis( self, mv_id: str, kuenddatum: str ):
        """
        Kündigung in Tabelle mietverhaeltnis eintragen -
        aber nur, wenn sich das Kündigungsdatum geändert hat.
        Der Update auf sollmiete muss hier erfolgen, da es fachlich falsch ist,
        ein MV ohne den zugehörigen Sollmietensatz zu kündigen.
        """
        if not datehelper.isValidIsoDatestring( kuenddatum ):
            raise Exception( "Mietende: kein gültiges Datumsformat" )
        # aktives Mietverhältnis lesen
        try:
            d = self._db.getAktuellesMietverhaeltnisVonBis( mv_id )
            if kuenddatum and d["von"] > kuenddatum:
                raise Exception( "MietverhaeltnisLogic.kuendigeMietverhaeltnis( '%s', '%s' ): " \
                                 "Mietverhältnis-von ('%s') > Mietverhältnis-bis: Nicht erlaubt"\
                                % (mv_id, d["von"], kuenddatum) )
            if kuenddatum == d["bis"]:
                return
        except Exception as ex:
            raise Exception( "Kündigung des Mietverhältnisses von '%s' fehlgeschlagen:\n'%s'"
                             % (mv_id, str(ex) ) )
        # aktive Sollmiete lesen
        smlogic = SollmieteLogic()
        sm: XSollMiete = smlogic.getCurrentSollmiete( mv_id )
        if kuenddatum and sm.von > kuenddatum:
            raise Exception( "BusinessLogic.kuendigeMietverhaeltnis( '%s', '%s' ): "
                             "Sollmiete-von ('%s') > Sollmiete-bis nicht erlaubt" %
                             (mv_id, sm.von, kuenddatum) )

        # Mietverhältnis beenden
        self._db.updateMietverhaeltnis2( d["id"], "bis", kuenddatum )
        # Sollmietensatz beenden
        smlogic.beendeSollmiete( sm.sm_id, kuenddatum )

    def updateMietverhaeltnis( self, xmv:XMietverhaeltnis ):
        """
        Ändert ein Mietverhältnis.
        Macht einen Update in die <mietverhaeltnis>.
        Die Sollmiete ist zwar Bestandteil dieses Models, aber wird über diese Methode nicht geändert.
        Die mv_id kann über diese Funktion nicht geändert werden.
        :param xmv: das Mietverhältnis-Objekt mit den geänderten Daten.
        :return:
        """
        try:
            xmv_akt = self._db.getMietverhaeltnisById( xmv.id )
            if xmv_akt.equals( xmv ):
                return
            self._db.updateMietverhaeltnis( xmv )
        except Exception as ex:
            return str( ex )

    def validateMietverhaeltnisDaten( self, xmv:XMietverhaeltnis ) -> str:
        if not xmv.von:
            return "Mietbeginn fehlt"
        if not datehelper.isValidIsoDatestring( xmv.von ):
            return "Mietbeginn: kein gültiges Datumsformat. Muss 'yyyy-mm-dd' sein."
        if xmv.bis and not datehelper.isValidIsoDatestring( xmv.bis ):
            return "Mietende: kein gültiges Datumsformat. Muss 'yyyy-mm-dd' sein."
        if not xmv.name:
            return "Name des Mieters fehlt"
        if not xmv.vorname:
            return "Vorame des Mieters fehlt"
        if not xmv.mobj_id:
            return "Objekt fehlt"
        return ""

def test():
    mv = MietverhaeltnisLogic()
    ret = mv.getKuendigungsdatumParts( "yilmaz_yasar" )
    print( ret )

if __name__ == "__main__":
    test()