from typing import List, Dict

import datehelper

from v2.icc.constants import EinAusArt
from v2.icc.iccdata import IccData
from v2.icc.interfaces import XGrundbesitzabgabe


class SammelabgabeData( IccData ):
    def __init__(self):
        IccData.__init__( self )

    def getSammelabgaben( self, jahr:int ) -> List[XGrundbesitzabgabe]:
        sql = "select id, master_name, grundsteuer, abwasser, strassenreinigung, bemerkung " \
              "from sammelabgabe_detail " \
              "where jahr = %d " % jahr
        xlist = self.readAllGetObjectList( sql, XGrundbesitzabgabe )
        return xlist

