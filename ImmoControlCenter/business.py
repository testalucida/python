from dbaccess import DbAccess
from typing import List, Dict

class BusinessLogic:
    def __init__(self):
        self._db: DbAccess

    def prepare(self):
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

    def existsEinAusArt(self, einausart: str, jahr: int) -> bool:
        return self._db.existsEinAusArt( einausart, jahr )

    def createMtlEinAusJahresSet( self, einausart:str, jahr:int ) -> None:
        objlist:List = self._db.getMietobjekte()
        for obj in objlist:
            self._db.insertMtlEinAus( obj, einausart, jahr, commit=False )
        self._db.commit()



def test():
    busi = BusinessLogic()
    busi.prepare()
    busi.createMtlEinAusJahresSet( "miete", 2020 )
    busi.terminate()

if __name__ == "__main__":
    test()

