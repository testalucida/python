
from typing import Dict, List

from databasecommon import DatabaseCommon
from interfaces import XMietobjektExt, XGeplant


class GeplantData( DatabaseCommon ):
    """
    Datenzugriffe auf die Tabelle <geplant>
    """
    def __init__(self):
        DatabaseCommon.__init__( self )

    def getPlanungen( self, jahr:int=None ) -> List[XGeplant]:
        sql = "select id, mobj_id, leistung, firma, kosten, kostenvoranschlag, jahr, monat, bemerkung " \
              "from geplant "
        if jahr:
            sql += "where jahr = %d" % jahr
        objlist = self.readAllGetObjectList( sql, XGeplant )
        return objlist