from interfaces import XMietverhaeltnis, XSollMiete
from mietverhaeltnis.mietverhaeltnislogic import MietverhaeltnisLogic
from mtleinaus.mtleinauslogic import MtlEinAusLogic
from sollmiete.sollmietelogic import SollmieteLogic
from base.transaction import *


class MietverhaeltnisUcc:
    def __init__( self, xmv:XMietverhaeltnis ):
        self._xmv = xmv

    def saveMietverhaeltnis( self ):
        """
        Es kann sich um ein neues oder ein schon bestehendes MV handeln.
        Wenn neu:
            Fügt das übergebene Mietverhältnis und die Sollmiete in die Datenbank ein
        Wenn schon existent:
            Macht einen Update auf das schon bestehende Mietverhaeltnis und auf die Sollmiete.
        :param xmv:
        :return:
        """
        xmv = self._xmv
        mvlogic = MietverhaeltnisLogic()
        mealogic = MtlEinAusLogic()
        smlogic = SollmieteLogic()
        BEGIN_TRANSACTION()
        if xmv.id == 0:
            try:
                mvlogic.createMietverhaeltnis( xmv )
                xsm = XSollMiete()
                xsm.von = xmv.von
                xsm.bis = xmv.bis
                xsm.mv_id = xmv.mv_id
                xsm.netto = xmv.nettomiete
                xsm.nkv = xmv.nkv
                smlogic.createSollmiete( xsm )
                jahr = int( xmv.von[0:4] )
                mealogic.insertMtlEinAusFuerMieter( xmv.mv_id, jahr )
                COMMIT_TRANSACTION()
            except Exception as ex:
                ROLLBACK_TRANSACTION()
                raise Exception( "MietverhaeltnisUcc.saveMietverhaeltnis():\n"
                                 "Beim Anlegen des Mietverhältnisses ist ein Fehler aufgetreten:\n" + str(ex) )
        else:
            try:
                mvlogic.updateMietverhaeltnis( xmv )
                smlogic.updateSollmiete( ?? )
                COMMIT_TRANSACTION()
            except Exception as ex:
                ROLLBACK_TRANSACTION()
                raise Exception( "MietverhaeltnisUcc.saveMietverhaeltnis():\n"
                                 "Beim Ändern des Mietverhältnisses ist ein Fehler aufgetreten:\n" + str( ex ) )

