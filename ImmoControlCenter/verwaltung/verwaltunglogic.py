from typing import List

from interfaces import XVerwaltung
from verwaltung.verwaltungdata import VerwaltungData


class VerwaltungLogic:
    def __init__(self):
        self._db = VerwaltungData()

    def getAktiveVerwaltungen( self, jahr:int ) -> List[XVerwaltung]:
        return self._db.getAktiveVerwaltungen( jahr )