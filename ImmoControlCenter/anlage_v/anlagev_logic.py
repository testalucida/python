from typing import List, Dict

from anlage_v.anlagev_dataacess import AnlageV_DataAccess


class AnlageV_Logic:
    __instance = None

    def __init__(self):
        if AnlageV_Logic.__instance != None:
            raise Exception( "You can't instantiate BusinessLogic more than once." )
        else:
            AnlageV_Logic.__instance = self
        self._db: AnlageV_DataAccess
        self._masterundmietobjekte:List[Dict] = None
        #self._kreditorleistungen:List[Dict] = None

    @staticmethod
    def inst() -> __instance:
        if AnlageV_Logic.__instance == None:
            AnlageV_Logic()
            AnlageV_Logic.inst()._prepare()
        return AnlageV_Logic.__instance

    def _prepare(self):
        dbname = "../immo.db"
        #dbname = "/home/martin/Vermietung/ImmoControlCenter/immo.db"

        self._db = AnlageV_DataAccess( dbname )
        self._db.open()

    def terminate(self):
        self._db.close()