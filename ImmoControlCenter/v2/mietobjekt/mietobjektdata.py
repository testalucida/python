from typing import List

from v2.icc.iccdata import IccData
from v2.icc.interfaces import XMietobjektAuswahl, XMietobjektExt


class MietobjektData( IccData ):
    def __init__(self):
        IccData.__init__( self )

    def getMietobjekte( self ) -> List[XMietobjektAuswahl]:
        """
        Liefert Mietobjekte mit den *aktuellen* Mietern (oder ohne, wenn gerade nicht vermietet ist)
        :return:
        """
        sql = "select mobj.master_name, mobj.mobj_id, mv.mv_id " \
              "from mietobjekt mobj " \
              "inner join mietverhaeltnis mv on mv.mobj_id = mobj.mobj_id " \
              "where mobj.aktiv = 1 " \
              "and mv.von <= current_date " \
              "and (mv.bis is NULL or mv.bis = '' or mv.bis >= current_date) " \
              "UNION " \
              "select mobj.master_name, mobj.mobj_id, '' " \
              "from mietobjekt mobj " \
              "where mobj.aktiv = 1 " \
              "and mobj.mobj_id not in " \
              "(select mv.mobj_id " \
              "from mietverhaeltnis mv " \
              "where mv.von <= current_date " \
              "and (mv.bis is NULL or mv.bis = '' or mv.bis >= current_date)) " \
              "order by mobj.master_name, mobj.mobj_id "

        l:List[XMietobjektAuswahl] = self.readAllGetObjectList( sql, XMietobjektAuswahl )
        return l

    def getMietobjektExt( self, mobj_id:str ) -> XMietobjektExt:
        """
        Liefert alle Daten zu einer mobj_id aus den Tabellen masterobjekt und mietobjekt.
        Liefert keine Verwaltungs- bzw. Verwalterdaten.
        :param mobj_id:
        :return:
        """
        sql = "select m.master_id, m.master_name, m.strasse_hnr, m.plz, m.ort, m.gesamt_wfl, m.anz_whg, m.veraeussert_am," \
              "m.hauswart, m.hauswart_telefon, m.hauswart_mailto, m.bemerkung as bemerkung_masterobjekt, " \
              "o.mobj_id, o.whg_bez, o.qm, o.container_nr, o.bemerkung as bemerkung_mietobjekt," \
              "vwg.vw_id as verwalter, vwg.weg_name " \
              "from mietobjekt o " \
              "inner join masterobjekt m on m.master_name = o.master_name " \
              "left outer join verwaltung vwg on vwg.master_name = o.master_name " \
              "where o.mobj_id = '%s' " % mobj_id
        return self.readOneGetObject( sql, XMietobjektExt )




def testExt():
    data = MietobjektData()
    xext = data.getMietobjektExt( "kleist_12" )
    xext.print()

def test():
    data = MietobjektData()
    l = data.getMietobjekte()
    print( l )