from typing import Iterable, List

from v2.icc.constants import ValueMapperHelper, Heizung
from v2.icc.icclogic import IccLogic, IccTableModel
from v2.icc.interfaces import XMietobjektAuswahl, XMietobjektExt, XMietverhaeltnis, XSollHausgeld, XVerwalter

##########################   MietobjektTableModel   ###################
from v2.masterobjekt.masterobjektdata import MasterobjektData
from v2.mietobjekt.mietobjektdata import MietobjektData
from v2.mietverhaeltnis.mietverhaeltnislogic import MietverhaeltnisLogic
from v2.sollhausgeld.sollhausgeldlogic import SollHausgeldLogic


class MietobjektTableModel( IccTableModel ):
    def __init__( self, rowlist:Iterable[XMietobjektAuswahl] ):
        IccTableModel.__init__( self, rowlist )
        self.setKeyHeaderMappings2(
            ( "master_name", "mobj_id", "name" ),
            ( "Haus", "Wohnung", "Mieter" ) )

##########################   MietobjektLogic   ###################
class MietobjektLogic( IccLogic ):
    def __init__( self ):
        IccLogic.__init__( self )
        self._data = MietobjektData()

    def getMietobjektTableModel( self ) -> MietobjektTableModel:
        def setName( x:XMietobjektAuswahl ):
            x.name = self.getNachnameVornameFromMv_id( x.mv_id )
            return x
        l:List[XMietobjektAuswahl] = self._data.getMietobjekte()
        l = [setName( x ) for x in l]
        tm = MietobjektTableModel( l )
        return tm

    def getMietobjektExt( self, mobj_id: str ) -> XMietobjektExt:
        xmo: XMietobjektExt = self._data.getMietobjektExt( mobj_id )
        xmo.heizung = ValueMapperHelper.getDisplay( Heizung, xmo.heizung )
        xvw:XVerwalter = self._data.getVerwalterDetails( xmo.vw_id )
        if xvw and xvw.vw_id:
            # es gibt eine Verwaltung
            xmo.verwalter_mailto = xvw.mailto
            xmo.verwalter_telefon = xvw.telefon_1
            if xvw.telefon_2:
                if xmo.verwalter_telefon:
                    xmo.verwalter_telefon += "\n"
                xmo.verwalter_telefon += xvw.telefon_2
            xmo.verwalter_bemerkung = xvw.bemerkung
            xmo.verwalter_ap = xvw.ansprechpartner_1
            if xvw.ansprechpartner_2:
                if xmo.verwalter_ap:
                    xmo.verwalter_ap += "\n"
                xmo.verwalter_ap += xvw.ansprechpartner_2

        xmv: XMietverhaeltnis = MietverhaeltnisLogic().getAktuellesMietverhaeltnisByMietobjekt( xmo.mobj_id )
        if not xmv:
            xmv = XMietverhaeltnis()
        else:
            xmo.mv_id = xmv.mv_id
            xmo.mieter = xmv.vorname + " " + xmv.name
            if xmv.telefon:
                xmo.telefon_mieter = xmv.telefon
            if xmv.mobil:
                if xmv.telefon:
                    xmo.telefon_mieter += ", "
                xmo.telefon_mieter += xmv.mobil
            if xmv.mailto:
                xmo.mailto_mieter = xmv.mailto

            xmo.nettomiete = xmv.nettomiete
            xmo.nkv = xmv.nkv
            xmo.kaution = xmv.kaution
        xsh: XSollHausgeld = SollHausgeldLogic().getCurrentSollHausgeld( xmo.mobj_id )
        #xmo.verwalter = xsh.vw_id
        #xmo.weg_name = xsh.weg_name
        if xsh: # Wohnung könnte derzeit nicht vermietet sein, dann ist xsh None
            xmo.hgv_netto = xsh.netto
            xmo.ruezufue = xsh.ruezufue
            xmo.hgv_brutto = xsh.brutto
        return xmo

    # def getMietobjektExt( self, mobj_id: str ) -> XMietobjektExt:
    #     xmo: XMietobjektExt = self._data.getMietobjektExt( mobj_id )
    #     dic = self._data.getVerwalterNameTelMailto( xmo.master_name )
    #     if dic:
    #         if xmo.weg_name and len( xmo.weg_name ) > 0:
    #             # es ist eine echte Verwaltung
    #             tel = "" if not dic["telefon_1"] else dic["telefon_1"]
    #             xmo.verwalter = dic["name"] + " (" + tel + ") "
    #             if dic["mailto"]:
    #                 xmo.verwalter += ("\n" + dic["mailto"])
    #         else:
    #             # Kleiststr, Eich, Scheidt: ganzes Haus, es gibt nur einen Hauswart
    #             xmo.hauswart = dic["name"]
    #             xmo.hauswart_telefon = dic["telefon_1"]
    #             xmo.hauswart_mailto = dic["mailto"]
    #     xmv: XMietverhaeltnis = MietverhaeltnisLogic().getAktuellesMietverhaeltnisByMietobjekt( xmo.mobj_id )
    #     if not xmv:
    #         xmv = XMietverhaeltnis()
    #     else:
    #         xmo.mv_id = xmv.mv_id
    #         xmo.mieter = xmv.vorname + " " + xmv.name
    #         if xmv.telefon:
    #             xmo.telefon_mieter = xmv.telefon
    #         if xmv.mobil:
    #             if xmv.telefon:
    #                 xmo.telefon_mieter += ", "
    #             xmo.telefon_mieter += xmv.mobil
    #         if xmv.mailto:
    #             xmo.mailto_mieter = xmv.mailto
    #
    #         xmo.nettomiete = xmv.nettomiete
    #         xmo.nkv = xmv.nkv
    #         xmo.kaution = xmv.kaution
    #     xsh: XSollHausgeld = SollHausgeldLogic().getCurrentSollHausgeld( xmo.mobj_id )
    #     #xmo.verwalter = xsh.vw_id
    #     #xmo.weg_name = xsh.weg_name
    #     if xsh: # Wohnung könnte derzeit nicht vermietet sein, dann ist xsh None
    #         xmo.hgv_netto = xsh.netto
    #         xmo.ruezufue = xsh.ruezufue
    #         xmo.hgv_brutto = xsh.brutto
    #     return xmo

    def saveMietobjektExt( self, x:XMietobjektExt ) -> str:
        """
        Speichert die Änderungen an einem XMietobjektExt - Objekt, sofern es welche gegeben hat.
        Wenn die Validierung nicht ok ist, wird eine Meldung zurückgegeben.
        Wenn Validierung == OK, wird die Speicher-Methode aufgerufen. Wenn das Speichern schiefgeht, wird
        von der Speicher-Methode eine Exception geworfen, die hier nicht aufgefangen wird (muss im Controller 
        geschehen).
        :param x:
        :return: 
        """
        def validate() -> str:
            msg_ = ""
            return msg_

        xOld = self.getMietobjektExt( x.mobj_id )
        if x.equals( xOld ): return "" # keine Änderungen
        msg = validate()
        if msg: return msg # Fehler beim Validieren
        # Validierung ok, jetzt Speichern:
        self._data.updateMietobjekt1( x.mobj_id, x.whg_bez, x.container_nr, x.bemerkung_mietobjekt )
        masterdata = MasterobjektData()
        masterdata.updateMasterobjekt1( x.master_id, x.hauswart, x.hauswart_telefon, x.hauswart_mailto,
                                        x.heizung, x.energieeffz, x.veraeussert_am, x.bemerkung_masterobjekt )
        self._data.commit()
        return ""

def test():
    logic = MietobjektLogic()
    xext = logic.getMietobjektExt( "kleist_01" )
    xext.print()