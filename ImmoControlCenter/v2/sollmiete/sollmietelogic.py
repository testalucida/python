import datehelper
from v2.icc.interfaces import XSollMiete
from v2.sollmiete.sollmietedata import SollmieteData


class SollmieteLogic:
    """
    Stellt die Funktionen zur Selektion, Neuanlage, Änderung und Beendigung von Sollmiete-Intervallen bereit.
    (Jeder Satz in der Tabelle sollmiete stellt ein Gültigkeits-Intervall dar.)
    **BEACHTE***
    Die Methoden dieser Klasse machen keine Commits und keine Exception-Behandlung!!
    Dies muss in den übergeordneten UCC-Klassen geschehen.
    ************
    """
    def __init__( self ):
        self._db:SollmieteData = SollmieteData()

    def getLetzteSollmiete( self, mv_id: str ) -> XSollMiete:
        return self._db.getLetzteSollmiete( mv_id )

    def _validate( self, xsm:XSollMiete ) -> str:
        if not xsm.mv_id:
            return "mv_id fehlt."
        if not xsm.von:
            return "Beginn des Sollmietenzeitraums fehlt."
        if not datehelper.isValidIsoDatestring( xsm.von ):
            return "Beginn des Sollmietenzeitraums hat kein gültiges Datumsformat. Muss 'yyyy-mm-dd' sein."
        if xsm.bis:
            if not datehelper.isValidIsoDatestring( xsm.bis ):
                return "Ende des Sollmietenzeitraums nicht im Format 'yyyy-mm-dd' angegeben."
        if not xsm.netto:
            return "Nettomiete fehlt."
        if not xsm.nkv:
            return "Nebenkostenvorauszahlung fehlt."

    def updateSollmiete( self, nettomiete, nkv ):
        # todo
        raise NotImplementedError( "SollmieteLogic.updateSollmiete()" )

    def createSollmiete( self, xsm:XSollMiete ):
        msg = self._validate( xsm )
        if msg:
            raise Exception( "Anlage Sollmiete fehlgeschlagen:\n%s" % msg )
        self._db.insertSollmiete( xsm )
        sm_id = self._db.getMaxId( "sollmiete", "sm_id" )
        xsm.sm_id = sm_id

    def beendeSollmiete( self, sm_id:int, bis:str ):
        self._db.terminateSollmiete( sm_id, bis )
