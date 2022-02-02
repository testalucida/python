from typing import Dict, List

from databasecommon import DatabaseCommon
from interfaces import XHandwerkerKurz


class IccData( DatabaseCommon ):
    """
    Enthält die DB-Zugriffe für Miet- UND Masterobjekte
    """
    def __init__(self):
        DatabaseCommon.__init__( self )

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
