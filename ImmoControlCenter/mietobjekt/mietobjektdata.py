
from typing import Dict, List

from base.databasecommon import DatabaseCommon
from interfaces import XMietobjektExt, XMasterobjekt, XMietobjekt


class MietobjektData( DatabaseCommon ):
    """
    Enthält die DB-Zugriffe für Miet- UND Masterobjekte
    """
    def __init__(self):
        DatabaseCommon.__init__( self )

    def getMasterobjektNamen( self ) -> List[str]:
        sql = "select master_name " \
              "from masterobjekt " \
              "where master_name not like '%*' " \
              "order by master_name "
        tuplelist = self.read( sql )
        masterlist = [t[0] for t in tuplelist]
        return masterlist

    def getMietobjekteKurzZuMaster( self, master_name:str ) -> List[Dict]:
        """
        Liefert folgende Mietobjekt-Informationen für alle aktiven Mietobjekte des übergebenen Masterobjekts:
        - mobj_id
        - master_id
        - whg_bez
        :return:
        """
        sql = "select mobj.mobj_id, master.master_id, mobj.whg_bez " \
              "from masterobjekt master " \
              "left outer join mietobjekt mobj on mobj.master_id = master.master_id " \
              "where aktiv = 1 " \
              "and master.master_name = '%s' " % master_name
        sql += \
              "and mobj.mobj_id > ' ' and mobj.mobj_id not like '%*%' " \
              "order by mobj.mobj_id "
        return self.readAllGetDict( sql )

    def getMietobjekteKurz( self, master_name:str=None ) -> List[Dict]:
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

    def getMietobjektNamen( self, master_name:str ) -> List[str]:
        sql = "select mobj.mobj_id " \
              "from mietobjekt mobj " \
              "inner join masterobjekt master on master.master_id = mobj.master_id " \
              "where master.master_name = '%s' " \
              "and mobj.aktiv = 1 " \
              "order by mobj.mobj_id " % master_name
        tuplelist = self.read( sql )
        return [t[0] for t in tuplelist]

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

    def updateMasterobjekt( self, x:XMasterobjekt ) -> int:
        sql = "update masterobjekt " \
              "set strasse_hnr = '%s', " \
              "plz = '%s', " \
              "ort = '%s', " \
              "gesamt_wfl = %d, " \
              "anz_whg = %d, " \
              "veraeussert_am = '%s', " \
              "bemerkung = '%s', " \
              "hauswart = '%s', " \
              "hauswart_telefon = '%s', " \
              "hauswart_mailto = '%s' " \
              "where master_id = %d " % ( x.strasse_hnr, x.plz, x.ort, x.gesamt_wfl, x.anz_whg, x.veraeussert_am,
                                          x.bemerkung, x.hauswart, x.hauswart_telefon, x.hauswart_mailto, x.master_id )
        return self.write( sql )

    def updateMietobjekt( self, x:XMietobjekt ) -> int:
        sql = "update mietobjekt " \
              "set whg_bez = '%s', " \
              "qm = %d, " \
              "container_nr = '%s', " \
              "bemerkung = '%s' " \
              "where mobj_id = '%s'" % ( x.whg_bez, x.qm, x.container_nr, x.bemerkung, x.mobj_id )
        return self.write( sql )