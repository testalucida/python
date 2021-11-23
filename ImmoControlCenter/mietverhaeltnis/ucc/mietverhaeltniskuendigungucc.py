from interfaces import XMietverhaeltnis
from mietverhaeltnis.mietverhaeltnislogic import MietverhaeltnisLogic
from returnvalue import ReturnValue
from transaction import *


class MietverhaeltnisKuendigungUcc:
    def __init__( self, xmv:XMietverhaeltnis ):
        """
        UCC wird verwendet, um ein Mietverhältnis zu kündigen, oder das Kündigungsdatum eines gekündigten
        Mietverhältnisses zu ändern oder die Kündigung aufzuheben.
        :param xmv: das Mietverhältnis, das gekündigt werden soll.
        """
        self._xmv = xmv

    def processMietverhaeltnisKuendigung( self ):
        """
        Instanziert MietverhaeltnisLogic und ruft die kuendigeMietverhaeltnis()-Methode auf
        :return:
        """
        mvlogic = MietverhaeltnisLogic()
        BEGIN_TRANSACTION()
        try:
            mvlogic.kuendigeMietverhaeltnis( self._xmv.mv_id, self._xmv.bis )
            COMMIT_TRANSACTION()
        except Exception as ex:
            ROLLBACK_TRANSACTION()