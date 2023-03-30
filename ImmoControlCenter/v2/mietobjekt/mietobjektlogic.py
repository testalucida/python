from typing import Iterable, List
from v2.icc.icclogic import IccLogic, IccTableModel
from v2.icc.interfaces import XMietobjektAuswahl, XMietobjektExt, XMietverhaeltnis, XSollHausgeld

##########################   MietobjektTableModel   ###################
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
        dic = self._data.getVerwalterNameTelMailto( xmo.master_name )
        if dic:
            if xmo.weg_name and len( xmo.weg_name ) > 0:
                # es ist eine echte Verwaltung
                tel = "" if not dic["telefon_1"] else dic["telefon_1"]
                xmo.verwalter = dic["name"] + " (" + tel + ") "
                if dic["mailto"]:
                    xmo.verwalter += ("\n" + dic["mailto"])
            else:
                # Kleiststr, Eich, Scheidt: ganzes Haus, es gibt nur einen Hauswart
                xmo.hauswart = dic["name"]
                xmo.hauswart_telefon = dic["telefon_1"]
                xmo.hauswart_mailto = dic["mailto"]
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
        xmo.weg_name = xsh.weg_name
        xmo.hgv_netto = xsh.netto
        xmo.ruezufue = xsh.ruezufue
        xmo.hgv_brutto = xsh.brutto
        return xmo

def test():
    logic = MietobjektLogic()
    xext = logic.getMietobjektExt( "kleist_01" )
    xext.print()