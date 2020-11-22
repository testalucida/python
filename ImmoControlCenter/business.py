from dbaccess import DbAccess
from typing import List, Dict

class BusinessLogic:
    __instance = None

    def __init__(self):
        if BusinessLogic.__instance != None:
            raise Exception( "You can't instantiate BusinessLogic more than once." )
        else:
            BusinessLogic.__instance = self
        self._db: DbAccess

    @staticmethod
    def inst():
        if BusinessLogic.__instance == None:
            BusinessLogic()
            BusinessLogic.inst()._prepare()
        return BusinessLogic.__instance

    def _prepare(self):
        try:
            f = open( "use_test_db" )
            dbname = "immo_TEST.db"
        except:
            dbname = "immo.db"
        finally:
            f.close()

        self._db = DbAccess( dbname )
        self._db.open()

    def terminate(self):
        self._db.close()

    def getMietzahlungen(self, jahr:int ) -> List[Dict]:
        return self._db.getMietzahlungen( jahr )

    def getHausgeldVorauszahlungen( self, jahr:int ) -> List[Dict]:
        return self._db.getHausgeldvorauszahlungen( jahr )

    def existsEinAusArt(self, einausart: str, jahr: int) -> bool:
        return self._db.existsEinAusArt( einausart, jahr )

    def createMtlEinAusJahresSet( self, einausart:str, jahr:int ) -> None:
        objlist:List = self._db.getMietobjekte()
        for obj in objlist:
            self._db.insertMtlEinAus( obj, einausart, jahr, commit=False )
        self._db.commit()

    def getSollmieten(self, jahr:int ) -> Dict:
        """liefert alle im jahr aktiven Mietobjekte mit den in diesem Jahr gültigen Sollmieten.
           Je Objekt werden soviele Sollmieten geliefert, wie in diesem Jahr gültig waren.
           Die Daten werden in Form eines Dictionary geliefert:
           {
               "charlotte": (
                               {
                                   "von": "2019-03-01"
                                   "bis": "2019-12-31"
                                   "netto_miete": 300
                                   "nk_voraus": 150
                               },
                               {
                                   "von": "2020-02-01"  ##beachte: Zeitenräume können Lücken enthalten (Leerstand)
                                   "bis": ""
                                   "netto_miete": 350
                                   "nk_voraus": 150
                               }
                            )
           }
        """
        dictlist = self._db.getSollmieten( jahr )
        dod = {}
        key = ""
        soll_list = []
        for d in dictlist:
            if key != d["mietobjekt_id"]:
                key = d["mietobjekt_id"]
                soll_list = []
                dod[key] = soll_list
            solldict = {k: v for (k, v) in d.items() if k != 'mietobjekt_id'}
            soll_list.append(solldict)
        return dod


def test():
    busi = BusinessLogic.inst()
    busi.getMietzahlungen( 2019 )
    #busi.createMtlEinAusJahresSet( "miete", 2020 )
    busi.terminate()

if __name__ == "__main__":
    test()

