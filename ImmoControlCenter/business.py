from enum import  IntEnum
from dbaccess import DbAccess
from typing import List, Dict, Tuple
from constants import einausart
from interfaces import XSonstAus, XSonstAusSummen, XZahlung, XSollHausgeld, XSollMiete
#from monthlist import monthList, monatsletzter
#from datehelper import monthList, monatsletzter, getLastMonth
from datehelper import *
from datetime import datetime

#---------------------------------------------------------------------
class Zahlart( IntEnum ):
    BRUTTOMIETE = 0,
    NKA = 1,
    HGV = 2,
    HGA = 3,
    SONSTAUS = 4

zahlartstrings = ("bruttomiete", "nka", "hgv", "hga", "sonstaus")
id_names = ( "meinaus_id", "nka_id", "meinaus_id", "hga_id", "saus_id" )
#---------------------------------------------------------------------
class InsertOrUpdate( IntEnum ):
    INSERT = 0,
    UPDATE = 1
#----------------------------------------------------------------------

class BusinessLogic:
    __instance = None

    def __init__(self):
        if BusinessLogic.__instance != None:
            raise Exception( "You can't instantiate BusinessLogic more than once." )
        else:
            BusinessLogic.__instance = self
        self._db: DbAccess
        self._masterundmietobjekte:List[Dict] = None
        #self._kreditorleistungen:List[Dict] = None

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
        #self._kreditorleistungen = self._db.getKreditorleistungen()

    def terminate(self):
        self._db.close()

    def getMietzahlungenMitSollUndSummen( self, jahr:int, monat:int ) -> List[Dict]:
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
                # TODO
                #  das ist wahrscheinlich falsch. Beispiel fehlende Murasov am Jahresanfang: alle im Alphabet
                # nach Murasov waren auf 0 gestanden.
                # Wahrscheinlich ist es besser, es so zu programmieren, dass man sich nicht auf die Konsistenz
                # von mieten und sollwerte verlässt.
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

    def insertSonstigeAuszahlung( self, x:XSonstAus ) -> None:
        # typischerweise ist hier zwar master_name, aber nicht master_id besetzt.
        # Also erst die master_id ermitteln
        if x.master_id == 0:
            x.master_id = self._db.getMasterId( x.master_name )
        if x.master_id < 0:
            raise Exception( "couldn't get master_id for master_name '%s' " % (x.master_name))
        self._db.insertSonstAus( x, False )
        x.saus_id = self._db.getMaxId( "sonstaus", "saus_id" )
        self._writeZahlungFromXSonstAus( x, insert=True )
        self._db.commit()
        self._checkKreditorleistung( x.master_id, x.mobj_id, x.kreditor, x.buchungstext )

    def _writeZahlungMtlEinAus( self, meinaus_id:int, jahr:int, monat:str, betrag:float ):
        """
        Könnte sein, dass es schon einen Satz in zahlung mit der geg. meinaus_id gibt.
        Z.B. wenn die Miete in 2 Tranchen bezahlt wird.
        Der entsprechende Monatsbetrag in mtleinaus wird dann mit der Summe aus 1. und 2. Teilzahlung upgedatet.
        Also: wenn mit der 1. Zahlung 100 und mit der 2. Zahlung 50 Euro bezahlt werden, gibt es in mtleinaus
        einen Update mit Monatswert = 150.
        Wir dürfen in zahlung dann keinen zweiten Satz mit Betrag 150 anlegen, denn es gibt ja schon einen Satz
        mit Betrag = 100.
        ==> den ersten Satz löschen wir und legen dann einen neuen mit Wert 150 an.
        :param meinaus_id:
        :param jahr:
        :param monat:
        :param betrag:
        :return:
        """
        d = self._db.getMasterUndMietobjekt( meinaus_id )
        z: XZahlung = XZahlung()
        z.betrag = betrag
        z.jahr = jahr
        z.monat = monat
        z.mobj_id = d["mobj_id"]
        z.master_id = d["master_id"]
        z.meinaus_id = meinaus_id
        z.write_time = datetime.now().strftime( "%Y-%m-%d:%H.%M.%S" )
        if "mv_id" in d.keys():
            self._deleteZahlung( meinaus_id, Zahlart.BRUTTOMIETE, monat )
            z.zahl_art = zahlartstrings[Zahlart.BRUTTOMIETE]
        else:
            self._deleteZahlung( meinaus_id, Zahlart.HGV, monat )
            z.zahl_art = zahlartstrings[Zahlart.HGV]
            if z.betrag > 0: z.betrag = z.betrag * (-1)

        self._db.insertZahlung( z, False)

    def _writeZahlungFromXSonstAus( self, x:XSonstAus, insert:bool ):
        z:XZahlung = XZahlung()
        z.betrag = x.betrag if x.betrag < 0 else x.betrag*(-1)
        z.jahr = x.buchungsjahr
        z.mobj_id = x.mobj_id
        z.master_id = x.master_id
        z.saus_id = x.saus_id
        z.write_time = datetime.now().strftime( "%Y-%m-%d:%H.%M.%S" )
        z.zahl_art = zahlartstrings[Zahlart.SONSTAUS.value]
        if insert:
            self._db.insertZahlung( z, False )
        else:
            self._db.updateZahlung( z.saus_id, id_names[Zahlart.SONSTAUS.value], z, False )

    def _deleteZahlung( self, id:int, art:Zahlart, monat:str=None ):
        id_name = id_names[art.value]
        zahl_art = zahlartstrings[art.value]
        self._db.deleteZahlung( id, id_name, monat, zahl_art, commit=False )

    def _checkKreditorleistung( self, master_id:int, mobj_id:str, kreditor:str, buchungstext:str ) -> None:
        """
        Prüft, ob eine gegebene Kreditorleistung schon in der Datenbank existiert.
        Wenn nicht, wird sie angelegt.
        :param master_id:
        :param mobj_id:
        :param kreditor:
        :param buchungstext:
        :return:
        """
        if self._db.existsKreditorleistung( master_id, mobj_id, kreditor, buchungstext ) < 1:
            self._db.insertKreditorleistung( master_id, mobj_id, kreditor, buchungstext )

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
            y = self._db.getJahrFromMtlEinAus( meinaus_id )
            for monat, betrag in change.items():
                self._db.updateMtlEinAus( meinaus_id, monat, betrag, False )
                self._writeZahlungMtlEinAus( meinaus_id, y, monat, betrag )
        self._db.commit()

    def updateSonstigeAuszahlung( self, x:XSonstAus ) -> None:
        self._db.updateSonstAus( x, False )
        self._writeZahlungFromXSonstAus( x, insert=False )
        self._db.commit()
        self._checkKreditorleistung( x.master_id, x.mobj_id, x.kreditor, x.buchungstext )

    def deleteSonstigeAuszahlung( self, x:XSonstAus ) -> None:
        self._db.deleteSonstAus( x.saus_id, False )
        self._deleteZahlung( x.saus_id, Zahlart.SONSTAUS )
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
            self._db.insertSollHausgeld( d, False )
        self._db.commit()

    def getAlleSollHausgelder( self ) -> List[XSollHausgeld]:
        return self._db.getAlleSollHausgelder()

    def getLetztenMonat( self ) -> Tuple[int, str]:
        # monat = datetime.datetime.now().month
        # monat = 12 if monat == 1 else monat-1
        # smonat = monthList[monat-1]
        # return monat, smonat
        return getLastMonth()

    def getMonatsletzter( self, monatidx:int ) -> int:
        smonat = monthList[monatidx-1]
        return monatsletzter[smonat]

    # def getServiceLeistungen( self ) -> List[XServiceLeistung]:
    #     dictlist:List[Dict] = self._db.getServiceleistungen()
    #     li = list()
    #     for d in dictlist:
    #         x:XServiceLeistung = XServiceLeistung( d )
    #         li.append( x )
    #     li = sorted( li, key=lambda service: service.kreditor.casefold() )
    #     return li

    def getMasterobjekte( self ) -> List[str]:
        """
        Liefert eine Liste aller masterobjekt-Einträge
        :return:
        """
        if self._masterundmietobjekte is None:
            self._masterundmietobjekte = self._db.getMasterUndMietobjekte()
        masterobjekte:List[str] = []
        name = ""
        for d in self._masterundmietobjekte:
            if name != d["master_name"]:
                name = d["master_name"]
                masterobjekte.append( name )

        return masterobjekte

    def getMietobjekte( self, master_name:str ) -> List[str]:
        """
        Ermittelt zu einem masterobjekt alle mietobjekte mobj_id
        :param master_id:
        :return:
        """
        if self._masterundmietobjekte is None:
            self._masterundmietobjekte = self._db.getMasterUndMietobjekte()
        master_id = self.getMasteridFromMastername( master_name )
        mietobjekte:List[str] = [] #["",]
        for d in self._masterundmietobjekte:
            if d["master_id"] == master_id:
                mietobjekte.append( d["mobj_id"] )
        # if len( mietobjekte ) == 2:  #außer "alle" nur 1 Eintrag
        #     mietobjekte.remove( "**alle**" )
        return mietobjekte

    def getMasteridFromMastername( self, master_name:str ) -> int:
        if self._masterundmietobjekte:
            for d in self._masterundmietobjekte:
                if d["master_name"] == master_name:
                    return d["master_id"]

    def getKreditoren( self, master_name:str ) -> List[str]:
        return self._db.getKreditoren( master_name )

    def getAlleKreditoren( self ) -> List[str]:
        return self._db.getAlleKreditoren()

    def getBuchungstexte( self, kreditor:str ) -> List[str]:
        return self._db.getBuchungstexte( kreditor )

    def getBuchungstexteFuerMasterobjekt( self, master_name:str, kreditor:str ) -> List[str]:
        return self._db.getBuchungstexteFuerMasterobjekt( master_name, kreditor )

    def getBuchungstexteFuerMietobjekt( self, mobj_id:str, kreditor:str ) -> List[str]:
        return self._db.getBuchungstexteFuerMasterobjekt( mobj_id, kreditor )

    def getSonstigeAusgabenUndSummen( self, jahr:int ) -> Tuple[List[XSonstAus], XSonstAusSummen]:
        sonstauslist:List[XSonstAus] = self._db.getSonstigeAusgaben( jahr )
        # Summe der Ausgaben berechnen
        summen = XSonstAusSummen()
        for aus in sonstauslist:
            betrag = int( round( aus.betrag ) )
            summen.summe_aus += betrag
            if aus.werterhaltend:
                summen.summe_werterhaltend += betrag
            if aus.umlegbar:
                summen.summe_umlegbar += betrag
        return sonstauslist, summen

    def insertSollmieten( xlist:List[XSollMiete] ):
        pass

    def updateSollmieten( xlist:List[XSollMiete] ) -> int:
        pass

    def insertSollHausgelder( self, xlist:List[XSollHausgeld] ) -> int:
        for x in xlist:
            self._db.insertSollHausgeld( x, False )
        self._db.commit()

    def updateSollHausgelder( self, xlist:List[XSollHausgeld] ) -> int:
        for x in xlist:
            self._db.updateSollHausgeld( x, False )
        self._db.commit()

def test():
    busi = BusinessLogic.inst()

    li = busi.getAlleSollHausgelder()

    li = busi.getMasterobjekte()
    print( li )
    idx, monat = busi.getLetztenMonat()
    letzter = busi.getMonatsletzter( 2 )

    # li = busi.getServiceLeistungen()
    # for x in li:
    #     print( x.kreditor )
    #busi.initSollhausgeld( "2019-01-01" )
    #mz = busi.getMietzahlungenMitSummen( 2020, 7 )
    #busi.createMtlEinAusJahresSet( 2021 )
    busi.terminate()

if __name__ == "__main__":
    test()

