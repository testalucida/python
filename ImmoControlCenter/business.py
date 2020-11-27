from dbaccess import DbAccess
from typing import List, Dict
from constants import einausart

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

    def getMietzahlungenMitSollUndSummen( self, jahr:int, monat:int ):
        mieten:List[Dict] = self._db.getMietzahlungenMitSummen( jahr )
        # sollwerte versorgen:
        return self.provideSollmieten( mieten, jahr, monat )

    def provideSollmieten( self, mieten:List[Dict], jahr:int, monat:int ) -> List[Dict]:
        sollwerte: List[Dict] = self.getSollmietenMonat( jahr, monat )
        # <sollwerte> enthält je Mietverhältnis genau 1 Satz mit den Werten netto, nkv und brutto.
        # Diese müssen je MV in <mieten> in die Spalte <soll> eingearbeitet werden.
        n = 0
        for m in mieten:
            solldict = sollwerte[n]
            if solldict["mv_id"] == m["mv_id"]:
                if solldict["mv_id"] == m["mv_id"]:
                    if solldict["brutto"] != m["soll"]:
                        m["soll"] = solldict["brutto"]
                    n += 1
        return mieten

    def getHausgeldVorauszahlungen( self, jahr:int, monat:int ) -> List[Dict]:
        return self._db.getHausgeldvorauszahlungen( jahr )

    def getExistingJahre( self, eaart:einausart ) -> List[int]:
        return self._db.getJahre( eaart )

    def existsEinAusArt(self, eaart: einausart, jahr: int) -> bool:
        return self._db.existsEinAusArt( eaart, jahr )

    def createMtlEinAusJahresSet( self, jahr:int ) -> None:
        """
        legt für jedes Mietverhältnis, das in <jahr> wenigstens teilweise aktiv ist,
        einen Miete- und einen HGV-Satz in Tabelle mtleinaus an.
        Achtung: Macht KEINEN commit
        """
        objlist:List = self._db.getMietverhaeltnisseEssentials( jahr )
        for obj in objlist:
            self._db.insertMtlEinAus( obj, einausart.MIETE, jahr, commit=False )
            self._db.insertMtlEinAus( obj, einausart.HGV, jahr, commit=False )
        self._db.commit()

    def getSollmietenMonat( self, jahr:int, monat:int ) -> List[Dict]:
        return self._db.getSollmietenMonat( jahr, monat )

    def getSollmieten(self, jahr:int ) -> Dict:
        """liefert alle im jahr aktiven Mietverhältnisse mit den in diesem Jahr gültigen Sollmieten.
           Je Mietverhältnis werden soviele Sollmieten geliefert, wie in diesem Jahr gültig waren.
           Die Daten werden in Form eines Dictionary geliefert:
           {
               "charlotte": (
                               {
                                   "von": "2019-03-01"
                                   "bis": "2019-12-31"
                                   "netto": 300
                                   "nkv": 150
                               },
                               {
                                   "von": "2020-02-01"  ##beachte: Zeitenräume können Lücken enthalten (Leerstand)
                                   "bis": ""
                                   "netto": 350
                                   "nkv": 150
                               }
                            )
           }
        """
        dictlist = self._db.getSollmieten( jahr )
        dod = {}
        key = ""
        soll_list = []
        for d in dictlist:
            if key != d["mv_id"]:
                key = d["mv_id"]
                soll_list = []
                dod[key] = soll_list
            solldict = {k: v for (k, v) in d.items() if k != 'mv_id'}
            soll_list.append(solldict)
        return dod


def test():
    busi = BusinessLogic.inst()
    mz = busi.getMietzahlungenMitSummen( 2020, 7 )
    #busi.createMtlEinAusJahresSet( "miete", 2020 )
    busi.terminate()

if __name__ == "__main__":
    test()

