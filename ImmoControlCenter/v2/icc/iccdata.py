from typing import List
from base.databasecommon import DatabaseCommon
from v2.icc.definitions import DATABASE
from v2.icc.constants import EinAusArt
from v2.icc.interfaces import XHandwerkerKurz, XEinAus, XMietverhaeltnisKurz


class IccData( DatabaseCommon ):
    """
    Enthält die DB-Zugriffe für Miet- UND Masterobjekte
    """
    def __init__(self):
        DatabaseCommon.__init__( self, DATABASE )

    def getMietverhaeltnisseKurz( self, jahr: int, orderby: str = None ) -> List[XMietverhaeltnisKurz]:
        """
        Liefert zu allen Mietverhältnissen, die in <jahr> aktiv sind, die Werte der Spalten mv_id, mobj_id, von, bis.
        Geliefert werden also neben den "Langläufern" MV, die während <jahr> enden und MV, die während MV beginnen.
        :param jahr:
        :param orderby:
        :return:
        """
        sql = "select id, mv_id, mobj_id, von, bis " \
              "from mietverhaeltnis " \
              "where substr(von, 0, 5) <= '%s' " \
              "and (bis is NULL or bis = '' or substr(bis, 0, 5) >= '%s') " % (jahr, jahr)
        if orderby:
            sql += "order by %s " % (orderby)
        return self.readAllGetObjectList( sql, XMietverhaeltnisKurz )

    def getKreditoren( self ) -> List[str]:
        sql = "select distinct kreditor from kreditorleistung order by kreditor "
        tuplelist = self.read( sql )
        return [t[0] for t in tuplelist]

    def getHandwerkerKurz( self, orderby:str=None ) -> List[XHandwerkerKurz]:
        """
        Selektiert alle Handwerkerdaten aus der Tabelle <handwerker>.
        :param orderby: Wenn angegeben, muss der Inhalt dem Spaltennamen entsprechen, nach dem sortiert werden soll.
                        Defaultmäßig wird nach dem Namen sortiert.
        :return:
        """
        if not orderby: orderby = "name"
        sql = "select id, name, branche, adresse from handwerker order by %s " % orderby
        xlist = self.readAllGetObjectList( sql, XHandwerkerKurz )
        return xlist
