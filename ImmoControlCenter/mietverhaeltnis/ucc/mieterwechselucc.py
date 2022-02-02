from interfaces import XMieterwechsel
from mietverhaeltnis.mietverhaeltnislogic import MietverhaeltnisLogic
from returnvalue import ReturnValue
from transaction import *


class MieterwechselUcc:
    def __init__( self, xmw:XMieterwechsel ):
        self._xmw:XMieterwechsel = xmw

    def processMieterwechsel( self ) -> ReturnValue:
        """
        Am UC Mieterwechsel sind zwei Mietverhältnisse beteiligt: ein "aktuelles", das aktiv oder inaktiv sein kann, und
        eines, das frühestens "heute" (CURRENT DATE) beginnt. Letzteres kann neu angelegt bzw. nach Anlage geändert werden.
        Ersteres wird im Folgenden das "aktive" genannt, letzteres "Folge-MV".
        Wenn der eingetragene Mietbeginn des Folge-MV erreicht ist, gilt es als "aktives", und es kann ein neues "Folge-MV"
        eingetragen werden.
        D.h., zu einem Folge-MV (Mietbeginn noch nicht erreicht) kann kein weiteres Folge-MV eingetragen werden.
        Ablauf des UC:
        a) Neuanlage des Folge-MV
        Beendet das aktuelle Mietverhältnis gem. Ende-Datum im Model XMieterwechsel.mietverhaeltnis_alt.
        Legt ein Folge-MV an an gem. Daten im Model XMieterwechsel.mietverhaeltnis_next.
        b) Änderung eines bereits angelegten Folge-MV:
        Macht ggf. einen Update auf das Ende-Datum des aktiven MV gem. Ende-Datum im Model XMieterwechsel.mietverhaeltnis_alt.
        Macht ggf. einen Update auf die geänderten Daten des Folge-MV gem. Daten im Model XMieterwechsel.mietverhaeltnis_next.

        Der Ucc fängt Exceptions auf und wandelt sie in einen String um, den er als ReturnValue-Objekt zurückgibt
        """
        # Übergebene Daten validieren (nur Fehler, die den Wechsel selbst betreffen):
        msg = self._validateMieterwechselData()
        if msg > "": return ReturnValue.fromError( msg ) # Validierung nicht ok, Message zurückgeben
        BEGIN_TRANSACTION()
        mvlogic = MietverhaeltnisLogic()
        # bisheriges Mietverhältnis kündigen bzw. Kündigungsdatum verschieben:
        try:
            mvlogic.kuendigeMietverhaeltnis( self._xmw.mietverhaeltnis_alt.mv_id,
                                             self._xmw.mietverhaeltnis_alt.bis )
        except Exception as ex:
            ROLLBACK_TRANSACTION()
            return ReturnValue.fromException( ex )
        # Änderung oder Neuanlage des Folge-Mietverhaeltnisses:
        if self._xmw.mietverhaeltnis_next.id > 0:  # es ist keine Neuanlage, nur ein Update auf das Folge-Mietverhältnis
            try:
                mvlogic.updateMietverhaeltnis( self._xmw.mietverhaeltnis_next )
            except Exception as ex:
                ROLLBACK_TRANSACTION()
                return ReturnValue.fromException( ex )
        else: # neues Mietverhältnis anlegen
            try:
                mvlogic.createMietverhaeltnis( self._xmw.mietverhaeltnis_next )
            except Exception as ex:
                ROLLBACK_TRANSACTION()
                return ReturnValue.fromException( ex )
        COMMIT_TRANSACTION()
        return ReturnValue()

    def _validateMieterwechselData( self ) -> str:
        """
        Es werden nur die Daten geprüft, die für den *Wechsel* relevant sind.
        Die übrigen Daten werden in MietverhaeltnisLogic bzw. SollmieteLogic geprüft
        :return:
        """
        if not self._xmw.mietverhaeltnis_alt.bis: return "Mietende des bisherigen Mietverhältnisses fehlt."
        if self._xmw.mietverhaeltnis_next.von <= self._xmw.mietverhaeltnis_alt.bis:
                                                   return "Das aktuelle Mietverhältnis muss VOR dem Anfang" \
                                                          "des Folge-Mietverhältnisses enden. Überlappunten sind nicht " \
                                                          "zulässig."
        return ""