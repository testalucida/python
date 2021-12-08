
from typing import Dict, List

from databasecommon import DatabaseCommon
from interfaces import XMietobjektExt


class MietobjektData( DatabaseCommon ):
    def __init__(self):
        DatabaseCommon.__init__( self )

    def getMietobjekteKurz( self ) -> List[Dict]:
        """
        Liefert folgende Informationen für alle aktiven Mietobjekte:
        - mobj_id
        - master_id
        - whg_bez
        :return:
        """
        sql = "select mobj_id, master_id, whg_bez " \
              "from mietobjekt " \
              "where aktiv = 1 " \
              "and mobj_id > ' ' and mobj_id not like '%*%' " \
              "order by mobj_id "
        return self.readAllGetDict( sql )

    def getMietobjekte( self ) -> List[XMietobjektExt]:
        """
        Liefert eine Liste von erweiterten Mietobjekt-Daten (Sammlung von Miet- u. Masterobjekt-Daten)
        :return:
        """
        sql = "select m.master_id, m.master_name, m.strasse_hnr, m.plz, m.ort, m.gesamt_wfl, m.anz_whg, m.veraeussert_am," \
              "m.hauswart, m.hauswart_telefon, m.hauswart_mailto, m.bemerkung as bemerkung_masterobjekt, " \
              "o.mobj_id, o.whg_bez, o.qm, o.container_nr, o.bemerkung as bemerkung_mietobjekt " \
              "from mietobjekt o " \
              "inner join masterobjekt m on m.master_id = o.master_id "
        raise NotImplementedError( "MietobjektData.getMietobjekte()" )

    def getMietobjekt( self, mobj_id: str ) -> XMietobjektExt:
        """
        Liefert alle Daten zu einer mobj_id aus den Tabellen masterobjekt und mietobjekt
        :param mobj_id:
        :return:
        """
        sql = "select m.master_id, m.master_name, m.strasse_hnr, m.plz, m.ort, m.gesamt_wfl, m.anz_whg, m.veraeussert_am," \
              "m.hauswart, m.hauswart_telefon, m.hauswart_mailto, m.bemerkung as bemerkung_masterobjekt, " \
              "o.mobj_id, o.whg_bez, o.qm, o.container_nr, o.bemerkung as bemerkung_mietobjekt " \
              "from mietobjekt o " \
              "inner join masterobjekt m on m.master_id = o.master_id " \
              "where mobj_id = '%s' " % mobj_id
        x:XMietobjektExt = self.readOneGetObject( sql, XMietobjektExt )
        return x