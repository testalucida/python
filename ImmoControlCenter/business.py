from dbaccess import DbAccess
from typing import List, Dict
from constants import einausart
from interfaces import XSonstAus, XServiceLeistung

class BusinessLogic:
    __instance = None

    def __init__(self):
        if BusinessLogic.__instance != None:
            raise Exception( "You can't instantiate BusinessLogic more than once." )
        else:
            BusinessLogic.__instance = self
        self._db: DbAccess

    @staticmethod
    def inst() -> __instance:
        if BusinessLogic.__instance == None:
            BusinessLogic()
            BusinessLogic.inst()._prepare()
        return BusinessLogic.__instance

    def _prepare(self):
        try:
            f = open( "use_test_db" )
            dbname = "immo_TEST.db"
            f.close()
        except:
            dbname = "immo.db"

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
        # Beide Listen müssen nach mv_id sortiert sein.
        n = 0
        for m in mieten:
            solldict = sollwerte[n]
            if solldict["mv_id"] == m["mv_id"]:
                if solldict["mv_id"] == m["mv_id"]:
                    if solldict["brutto"] != m["soll"]:
                        m["soll"] = solldict["brutto"]
                    n += 1
            else: # Mietverh. besteht in diesem Monat noch nicht oder nicht mehr
                m["soll"] = 0
        return mieten

    def getHausgeldVorauszahlungenMitSollUndSummen( self, jahr:int, monat:int ) -> List[Dict]:
        hgvlist:List[Dict] = self._db.getHausgeldvorauszahlungenMitSummen( jahr )
        #sollwerte versorgen:
        return self.provideSollHGV( hgvlist, jahr, monat )

    def provideSollHGV( self, hgvlist: List[Dict], jahr: int, monat: int ) -> List[Dict]:
        sollwerte = self._db.getSollHausgelderMonat( jahr, monat )
        # Achtung: hgv (nach weg_name) und sollwerte (nach vwg_id)
        # sind unterschiedlich sortiert
        for hgv in hgvlist:
            for soll in sollwerte:
                hgv["soll"] = 0
                if soll["vwg_id"] == hgv["vwg_id"]:
                    hgv["soll"] = soll["netto"] + soll["ruezufue"]
                    break
        return hgvlist

    def getExistingJahre( self, eaart:einausart ) -> List[int]:
        return self._db.getJahre( eaart )

    def existsEinAusArt(self, eaart: einausart, jahr: int) -> bool:
        return self._db.existsEinAusArt( eaart, jahr )

    def createMtlEinAusJahresSet( self, jahr:int ) -> None:
        """
        legt
        1.) für jedes Mietverhältnis, das in <jahr> wenigstens teilweise aktiv ist,
        einen Mietesatz in Tabelle mtleinaus an.
        2.) für jede Verwaltung, die in <jahr> wenigstens teilweise aktiv ist, einen
        HGV-Satz in Tabelle mtleinaus an.
        Macht abschließend einen Commit.
        """
        mvlist:List[Dict] = self._db.getMietverhaeltnisseEssentials( jahr )
        for mv in mvlist:
            self._db.insertMtlEinAus( mv["mv_id"], einausart.MIETE, jahr, commit=False )

        vwglist: List[Dict] = self._db.getVerwaltungen( jahr )
        for vwg in vwglist:
            self._db.insertMtlEinAus( vwg["vwg_id"], einausart.HGV, jahr, commit=False )
        self._db.commit()

    def updateMietzahlungen( self, changes: Dict[int, Dict] ) -> None:
        self._updateMtlEinAus( changes )

    def updateHausgeldvorauszahlungen( self, changes: Dict[int, Dict] ) -> None:
        self._updateMtlEinAus( changes )

    def _updateMtlEinAus( self, changes:Dict[int, Dict] ) -> None:
        """
        Ändert Monatszahlungen, wie von <changes> vorgegeben.
        Der Key in changes ist die meinaus_id, value ist ein anderes dictionary, dessen Key der Monat und dessen
        Value die Mietzahlung (float) dieses Monats ist.
         Aufbau von changes:
        {
            12345 <meinaus_id>: {
                                    'mai': 445,90,
                                    'jun': 444,00
                                },
            3456 <meinaus_id>: {
                                    'jan': 440,00,
                                    'mrz': 445,20
                                }
        }
        """
        for meinaus_id, change in changes.items():
            for monat, betrag in change.items():
                self._db.updateMtlEinAus( meinaus_id, monat, betrag, False )
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

    def initSollhausgeld( self, von:str, bis:str=None ):
        """
        Legt einen Satz je Mietobjekt in der Tabelle sollhausgeld an.
        Die Spalten netto und ruezufue werden auf 0 gestellt.
        Alle Sätze werden mit den übergebenen <von> und <bis> - Werten initialisiert
        :param von:
        :param bis:
        :return:
        """
        objekte = self._db.getMietobjekteKurz()
        for obj in objekte:
            d = {
                "mobj_id": obj["mobj_id"],
                "von": von ,
                "bis": bis,
                "netto": 0,
                "ruezufue": 0
            }
            self._db.insertSollhausgeld( d, False )
        self._db.commit()

    def getServiceLeistungen( self ) -> List[XServiceLeistung]:
        dictlist:List[Dict] = self._db.getServiceleistungen()
        li = list()
        for d in dictlist:
            x:XServiceLeistung = XServiceLeistung( d )
            li.append( x )
        li = sorted( li, key=lambda service: service.kreditor.casefold() )
        return li

    #def compareDics( self, d1:Dict, d2:Dict ) -> int:

def test():
    busi = BusinessLogic.inst()
    li = busi.getServiceLeistungen()
    for x in li:
        print( x.kreditor )
    #busi.initSollhausgeld( "2019-01-01" )
    #mz = busi.getMietzahlungenMitSummen( 2020, 7 )
    #busi.createMtlEinAusJahresSet( 2021 )
    busi.terminate()

if __name__ == "__main__":
    test()

