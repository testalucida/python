from typing import List, Dict

from databasecommon import DatabaseCommon
from interfaces import XVerwaltung


class VerwaltungData( DatabaseCommon ):
    def __init__( self ):
        DatabaseCommon.__init__( self )

    def getAktiveVerwaltungen( self, jahr: int, orderby: str = None ) -> List[XVerwaltung]:
        """
        Liefert alle Verwaltungen, die im Jahr <jahr> aktiv waren/sind.
        Das beinhaltet auch die, die in <jahr> enden bzw. anfangen.
        :param jahr:
        :param orderby:
        :return:
        """
        vgldat_von = str( jahr ) + "-01-01"
        vgldat_bis = str( jahr ) + "-12-31"
        sql = "select vwg_id, mobj_id, vw_id, weg_name, von, coalesce( bis, '' ) as bis " \
              "from verwaltung " \
              "where von < '%s' and (bis is NULL or bis = '' or bis > '%s') " % ( vgldat_bis, vgldat_von )
        if orderby:
            sql += "order by %s" % orderby
        return self.readAllGetObjectList( sql, XVerwaltung )