from dbaccess import DbAccess
from typing import List, Dict

class BusinessLogic:
    def __init__(self):
        self._db: DbAccess

    def prepare(self):
        self._db = DbAccess()
        self._db.open()

    def terminate(self):
        self._db.close()

    def getMietzahlungen(self, jahr:int ) -> List[Dict]:
        return self._db.getMietzahlungen( jahr )

