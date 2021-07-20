import itertools
import os
import sys
from enum import  IntEnum

from PySide2.QtCore import QAbstractItemModel, Qt

from abrechnungentablemodel import NkAbrechnungenTableModel, HgAbrechnungenTableModel
from anlage_v.anlagev_interfaces import XSammelAbgabeDetail
from buchungstextmatchmodel import BuchungstextMatchModel
from dbaccess import DbAccess
from typing import List
from constants import einausart, Zahlart, zahlartstrings
from interfaces import XSonstAus, XSonstAusSummen, XZahlung, XSollHausgeld, XSollMiete, XBuchungstextMatch, \
    XNkAbrechnung, XAbrechnung, XHgAbrechnung, XMietverhaeltnis, XOffenerPosten, XNotiz, XZahlung2, XRendite, XAusgabe
#from monthlist import monthList, monatsletzter
#from datehelper import monthList, monatsletzter, getLastMonth
from datehelper import *
from datetime import datetime

#---------------------------------------------------------------------
# class Zahlart( IntEnum ):
#     BRUTTOMIETE = 0,
#     NKA = 1,
#     HGV = 2,
#     HGA = 3,
#     SONSTAUS = 4
#
# zahlartstrings = ("bruttomiete", "nka", "hgv", "hga", "sonstaus")
from notizen.notizentablemodel import NotizenTableModel
from rendite.ausgabentablemodel import AusgabenTableModel
from offene_posten.offenepostentablemodel import OffenePostenTableModel
from rendite.renditetablemodel import RenditeTableModel

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
        dbname = ""
        f = open( "./resources.txt", "r" )
        lines = f.readlines()
        for l in lines:
            if l.startswith( "databasepath" ):
                parts = l.split( "=" )
                dbname = parts[1][:-1]  # truncate newline
                f.close()
        if dbname == "":
            raise Exception( "BusinessLogic: cant find databasepath in resources.txt" )
        dbname += "immo.db"
        #dbname = "/home/martin/Vermietung/ImmoControlCenter/immo.db"
        print( "BusinessLogic._prepare(): trying to connect to database '%s'..." % (dbname) )
        self._db = DbAccess( dbname )
        #self._db = DbAccess()
        self._db.open()
        print( "BusinessLogic.prepare(): ...connected to '%s'" % (dbname) )

    def terminate(self):
        self._db.close()

    def getLetzteBuchung( self ) -> Tuple[str, str]:
        return self._db.getLetzteBuchung()

    def setLetzteBuchung( self, datum:str, text:str ):
        self._db.deleteLetzteBuchung( False )
        self._db.insertLetzteBuchung( datum, text )

    def getBuchungstextMatches( self, searchstring:str ) -> BuchungstextMatchModel:
        s_low = searchstring.lower()
        lst:List[XBuchungstextMatch] = list()
        dictlist:List[Dict] = self._db.getKreditorleistungen()
        for d in dictlist:
            txt = d["buchungstext"].lower()
            if s_low in txt:
                x = XBuchungstextMatch()
                x.master_id = d["master_id"]
                x.master_name = d["master_name"]
                x.mobj_id = d["mobj_id"]
                x.kreditor = d["kreditor"]
                x.buchungstext = d["buchungstext"]
                x.umlegbar = d["umlegbar"]
                lst.append( x )
        model = BuchungstextMatchModel( lst )
        return model

    def getMietzahlungenMitSollUndSummen( self, jahr:int, monat:int ) -> List[Dict]:
        mieten:List[Dict] = self._db.getMietzahlungenMitSummen( jahr )
        # sollwerte versorgen:
        return self.provideSollmieten( mieten, jahr, monat )

    def getNettomieteUndNkv( self, mv_id:str, jahr:int, monat:int ) -> (float, float):
        return self._db.getMieteBestandteile( mv_id, jahr, monat )

    def provideSollmieten( self, mieten:List[Dict], jahr:int, monat:int ) -> List[Dict]:
        sollwerte: List[Dict] = self.getSollmietenMonat( jahr, monat )
        # <sollwerte> enthält je Mietverhältnis genau 1 Satz mit den Werten netto, nkv und brutto.
        # Diese müssen je MV in <mieten> in die Spalte <soll> eingearbeitet werden.
        # Beide Listen müssen nach mv_id sortiert sein.
        for m in mieten:
            solldict = next( ( d for d in sollwerte if d["mv_id"] == m["mv_id"] ), None )
            #solldict = next( filter( lambda x: x["mv_id"] == m["mv_id"], sollwerte ), None )
            if not solldict:
                m["soll"] = 0
            else:
                if solldict["brutto"] != m["soll"]:
                    m["soll"] = solldict["brutto"]
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

    def getExistingNkAbrechnungsjahre( self ) -> List[int]:
        return self._db.getExistingNkAbrechnungsjahre()

    def getExistingHgAbrechnungsjahre( self ) -> List[int]:
        return self._db.getExistingHgAbrechnungsjahre()

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
        if len( x.master_name ) > 0 : # kann auch leer sein, wenn Objekt der Auszahlung unbekannt
            if x.master_id == 0 or x.master_id is None:
                x.master_id = self._db.getMasterId( x.master_name )
            if x.master_id < 0:
                raise Exception( "couldn't get master_id for master_name '%s' " % (x.master_name))
        self._db.insertSonstAus( x, False )
        x.saus_id = self._db.getMaxId( "sonstaus", "saus_id" )
        self._writeZahlungFromXSonstAus( x, insert=True )
        self._db.commit()
        if x.master_id is not None:
            self._checkKreditorleistung( x.master_id, x.mobj_id, x.kreditor, x.buchungstext )

    def insertNkAbrechnung( self, x:XNkAbrechnung ) -> None:
        self._db.insertNkAbrechnung( x, commit=False )
        x.nka_id = self._db.getMaxId( "nk_abrechnung", "nka_id" )
        if x.buchungsdatum > "":
            self._writeZahlungFromXAbrechnung( x, Zahlart.NKA, insert=True )
        self._db.commit()

    def updateNkAbrechnung( self, x:XNkAbrechnung ) -> None:
        self._db.updateNkAbrechnung( x, commit=False )
        z:XZahlung = self._db.getZahlung( x.nka_id, "nka_id" )
        if z.z_id == 0:
            # abrechnung not yet payed (booked) so not inserted yet.
            # Insert into zahlung if buchungsdatum is set
            if x.buchungsdatum > "":
                self._writeZahlungFromXAbrechnung( x, Zahlart.NKA, insert=True )
        else:
            # got an abrechnung record. Delete it if buchungsdatum is "". Else update.
            if x.buchungsdatum is None or x.buchungsdatum == "":
                self._deleteZahlung( x.nka_id, Zahlart.NKA )
            else:
                self._writeZahlungFromXAbrechnung( x, Zahlart.NKA, insert=False )
        self._db.commit()

    def deleteNkAbrechnung( self, x:XNkAbrechnung ) -> None:
        self._db.deleteNkAbrechnung( x.nka_id, commit=False )
        self._db.deleteZahlung( x.nka_id, "nka_id", commit=False )
        self._db.commit()
        x.nka_id = 0

    def insertHgAbrechnung( self, x: XHgAbrechnung ) -> None:
        self._db.insertHgAbrechnung( x, commit=False )
        x.hga_id = self._db.getMaxId( "hg_abrechnung", "hga_id" )
        if x.buchungsdatum > "":
            self._writeZahlungFromXAbrechnung( x, Zahlart.HGA, insert=True )
        self._db.commit()

    def updateHgAbrechnung( self, x: XHgAbrechnung ) -> None:
        self._db.updateHgAbrechnung( x, commit=False )
        z: XZahlung = self._db.getZahlung( x.hga_id, "hga_id" )
        if z.z_id == 0:
            # abrechnung not yet payed (booked) so not inserted yet.
            # Insert into zahlung if buchungsdatum is set
            if x.buchungsdatum > "":
                self._writeZahlungFromXAbrechnung( x, Zahlart.HGA, insert=True )
        else:
            # got an abrechnung record. Delete it if buchungsdatum is "". Else update.
            if x.buchungsdatum is None or x.buchungsdatum == "":
                self._deleteZahlung( x.hga_id, Zahlart.HGA )
            else:
                self._writeZahlungFromXAbrechnung( x, Zahlart.HGA, insert=False )
        self._db.commit()

    def deleteHgAbrechnung( self, x:XHgAbrechnung ) -> None:
        self._db.deleteHgAbrechnung( x.hga_id, commit=False )
        self._db.deleteZahlung( x.hga_id, "hga_id", commit=False )
        self._db.commit()
        x.hga_id = 0

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
        z.betrag = x.betrag #if x.betrag < 0 else x.betrag*(-1)
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

    def _writeZahlungFromXAbrechnung( self, x:XAbrechnung, zahlart:Zahlart, insert:bool ):
        z = XZahlung()
        z.betrag = x.betrag
        z.jahr = int( x.buchungsdatum[0:4] )
        z.mobj_id = x.mobj_id
        z.master_id = self._db.getMasterIdFromMietobjekt( x.mobj_id )
        z.write_time = datetime.now().strftime( "%Y-%m-%d:%H.%M.%S" )
        z.zahl_art = zahlartstrings[zahlart.value]
        id = x.getId()
        if zahlart == Zahlart.NKA:
            id_name = "nka_id"
            z.nka_id = id
        else:
            id_name = "hga_id"
            z.hga_id = id
        if insert:
            self._db.insertZahlung( z, False )
        else:
            self._db.updateZahlung(id, id_name, z, False )

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

    def kuendigeMietverhaeltnis( self, mv_id:str, kuenddatum:str ) -> None:
        """
        - Kündigung in Tabelle mietverhaeltnis eintragen
        - Kündigung in Tabelle sollmiete eintragen
        """
        # aktives Mietverhältnis lesen
        mv:XMietverhaeltnis = self._db.getAktivesMietverhaeltnisZuMvId( mv_id )
        if kuenddatum and mv.von > kuenddatum:
            raise Exception( "BusinessLogic.kuendigeMietverhaeltnis( '%s', '%s' ): "
                             "Mietverhältnis-von ('%s') > Mietverhältnis-bis nicht erlaubt" %
                             (mv_id, mv.von, kuenddatum ) )

        # aktive Sollmiete lesen
        sm:XSollMiete = self._db.getAktiveSollmiete( mv_id )
        if kuenddatum and sm.von > kuenddatum:
            raise Exception( "BusinessLogic.kuendigeMietverhaeltnis( '%s', '%s' ): "
                             "Sollmiete-von ('%s') > Sollmiete-bis nicht erlaubt" %
                             (mv_id, sm.von, kuenddatum ) )

        # Mietverhältnis beenden
        self._db.updateMietverhaeltnis2( mv.id, "bis", kuenddatum, commit=False )
        # Sollmiete beenden
        sm.bis = kuenddatum
        self._db.updateSollmiete( sm, commit=True )

    def getSollmietenMonat( self, jahr:int, monat:int ) -> List[Dict]:
        return self._db.getSollmietenMonat( jahr, monat )

    def getSollmieten(self ) -> List[XSollMiete]:
        """liefert alle im jahr aktiven Mietverhältnisse mit den in diesem Jahr gültigen Sollmieten.
           Je Mietverhältnis werden soviele Sollmieten geliefert, wie in diesem Jahr gültig waren.
        """
        y = getCurrentYear()
        return self._db.getSollmieten2( y - 1 )

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

    def getSollHausgelder( self ) -> List[XSollHausgeld]:
        # wir holen die Soll-Hausgelder, die im letzten und aktuellen Jahr gültig waren/sind
        y = getCurrentYear()
        return self._db.getSollHausgelder2( y-1 )

    # def getSollHausgelder( self, mobj_id:str ) -> List[XSollHausgeld]:
    #     return

    def canCreateFolgeIntervallHausgeld( self, x:XSollHausgeld ) -> bool:
        # prüfen, ob x das zeitlich neueste Intervall für x.mobj_id ist.
        # Nur für dieses kann ein Folge-Intervall angelegt werden, und auch  nur dann, wenn es nicht terminiert ist.
        if x.bis > " ":
            return False
        shglist:List[XSollHausgeld] = self._db.getSollHausgelder( mobj_id=x.mobj_id )
        for shg in shglist:
            if shg.von > x.von:
                return False
        return True

    def getStartOfNextSollzahlungInterval( self, oldIsoDate:str ) -> str:
        if oldIsoDate > getTodayAsIsoString():
            return getFirstOfFollowingMonth( oldIsoDate )
        else:
            return getFirstOfNextMonth()

    def canCreateFolgeIntervallMiete( self, x:XSollMiete ) -> bool:
        # prüfen, ob x das zeitlich neueste Intervall für x.mv_id ist.
        # Nur für dieses kann ein Folge-Intervall angelegt werden, und auch  nur dann, wenn es nicht terminiert ist.
        if x.bis > " ":
            return False
        smlist:List[XSollMiete] = self._db.getSollmieten( mv_id=x.mv_id )
        for sm in smlist:
            if sm.von > x.von:
                return False
        return True

    def getLetztenMonat( self ) -> Tuple[int, str]:
        return getLastMonth()

    def getMonatsletzter( self, monatidx:int ) -> int:
        smonat = monthList[monatidx-1]
        return monatsletzter[smonat]

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
        return mietobjekte

    def getMasteridFromMastername( self, master_name:str ) -> int:
        if self._masterundmietobjekte:
            for d in self._masterundmietobjekte:
                if d["master_name"] == master_name:
                    return d["master_id"]

    def getKreditoren( self, master_name:str ) -> List[str]:
        return self._db.getKreditoren( master_name )

    def getKuendigungsdatum( self, mv_id:str ) -> str:
        x:XMietverhaeltnis = self._db.getAktivesMietverhaeltnisZuMvId( mv_id )
        return x.bis

    def getKuendigungsdatum2( self, mv_id:str ) -> (int, int, int) or None:
        bis = self.getKuendigungsdatum( mv_id )
        if not bis: return None
        return getDateParts( bis )


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

    def getSummen( self ) -> Tuple[int, int, int]:
        sumMiete:float = self._db.getSummeZahlungen( "bruttomiete" )
        sumSonstAus:float = self._db.getSummeZahlungen( "sonstaus" )
        sumNka:float = self._db.getSummeZahlungen( "nka" )
        sumHga:float = self._db.getSummeZahlungen( "hga" )
        sumAusgaben: float = sumSonstAus + sumNka + sumHga
        sumHGV:float = self._db.getSummeZahlungen( "hgv" )
        return ( int(sumMiete), int(sumAusgaben), int(sumHGV) )

    def getNkAbrechnungenTableModel( self, ab_jahr:int ) -> NkAbrechnungenTableModel:
        """
        Gets ALL Mietverhältnisse.
        Creates a XNkAbrechnung object for each mietverhaeltnis.
        Merges NKA informations with mietverhaeltnis where exists.
        :param ab_jahr:
        :return:
        """
        def _provideAbrechnungInfo( x:XNkAbrechnung, realabrechlist:List[XNkAbrechnung] ):
            for abr in realabrechlist:
                if x.mv_id == abr.mv_id and abr.ab_jahr == x.ab_jahr:
                    x.ab_jahr = ab_jahr
                    x.nka_id = abr.nka_id
                    x.betrag = abr.betrag
                    x.ab_datum = abr.ab_datum
                    x.buchungsdatum = abr.buchungsdatum
                    x.bemerkung = abr.bemerkung
                    # we don't have to deal with von and bis as we have selected conveniant mietverhaeltnisse only.
                    # print( x.mv_id, "---", x.betrag, "---", x.ab_datum, "---", x.buchungsdatum )
                    break

        # the list we will create the model with:
        abrechlist: List[XNkAbrechnung] = list()
        # all mietverhaeltnisse:
        mvlist:List[Dict] = self._db.getMietverhaeltnisseEssentials( jahr=ab_jahr, orderby="mobj_id" )
        # [
        #     {
        #         "mv_id": "lander_anke",
        #         "mobj_id": "volkerstal",
        #         "von": "2019-01-01"
        #         "bis": ""
        #      },
        # ...
        # ]
        # get existing nk_abrechnung objects
        realabrechlist: List[XNkAbrechnung] = self._db.getNkAbrechnungen( ab_jahr )
        # create a XNkAbrechnung object from each mietverhaeltnis and provide it with
        # real abrechnung information if a corresponding XNkAbrechnung object is found in realabrechlist
        for mv in mvlist:
            x = XNkAbrechnung()
            x.mv_id = mv["mv_id"]
            x.mobj_id = mv["mobj_id"]
            x.von = mv["von"]
            x.bis = mv["bis"]
            x.ab_jahr = ab_jahr
            _provideAbrechnungInfo( x, realabrechlist )
            abrechlist.append( x )

        model = NkAbrechnungenTableModel( abrechlist )
        return model

    def getHgAbrechnungenTableModel( self, ab_jahr:int ) -> HgAbrechnungenTableModel:
        """
        Gets ALL Verwaltungen (WEG).
        Creates a XHgAbrechnung object for each verwaltung.
        Merges HGA informations with verwaltung where exists.
        :param ab_jahr:
        :return:
        """
        def _provideAbrechnungInfo( x:XHgAbrechnung, realabrechlist:List[XHgAbrechnung] ):
            for abr in realabrechlist:
                if x.vwg_id == abr.vwg_id and abr.ab_jahr == x.ab_jahr:
                    x.ab_jahr = ab_jahr
                    x.hga_id = abr.hga_id
                    x.betrag = abr.betrag
                    x.ab_datum = abr.ab_datum
                    x.buchungsdatum = abr.buchungsdatum
                    x.bemerkung = abr.bemerkung
                    # we don't have to deal with von and bis as we have selected conveniant verwaltungen only.
                    break

        # the list we will create the model with:
        abrechlist: List[XHgAbrechnung] = list()
        # all verwaltungen:
        vwglist:List[Dict] = self._db.getVerwaltungen( jahr=ab_jahr, orderby="mobj_id" )
        # [
        #     {
        #         "vwg_id": 19,
        #         "mobj_id": "volkerstal",
        #         "vw_id": "Palm"
        #         "weg_name": "WEG Thomas-Mann-Str. 2"
        #         "von": "2019-01-01"
        #         "bis": ""
        #      },
        # ...
        # ]
        # get existing hg_abrechnung objects
        realabrechlist: List[XHgAbrechnung] = self._db.getHgAbrechnungen( ab_jahr )
        # create a XHgAbrechnung object from each verwaltung and provide it with
        # real abrechnung information if a corresponding XHgAbrechnung object is found in realabrechlist
        for vwg in vwglist:
            x = XHgAbrechnung()
            x.vwg_id = vwg["vwg_id"]
            x.weg_name_vw_id = vwg["weg_name"] + " / " + vwg["vw_id"]
            x.mobj_id = vwg["mobj_id"]
            x.von = vwg["von"]
            x.bis = vwg["bis"]
            x.ab_jahr = ab_jahr
            _provideAbrechnungInfo( x, realabrechlist )
            abrechlist.append( x )

        model = HgAbrechnungenTableModel( abrechlist )
        return model

    def insertSollmieten( self, xlist:List[XSollMiete] ):
        for x in xlist:
            self._db.insertSollmiete( x, False )
        self._db.commit()

    def updateSollmieten( self, xlist:List[XSollMiete] ):
        for x in xlist:
            self._db.updateSollmiete( x, False )
        self._db.commit()

    def insertSollHausgelder( self, xlist:List[XSollHausgeld] ):
        for x in xlist:
            self._db.insertSollHausgeld( x, False )
        self._db.commit()

    def updateSollHausgelder( self, xlist:List[XSollHausgeld] ):
        for x in xlist:
            self._db.updateSollHausgeld( x, False )
        self._db.commit()

    def exportToCsv( self, model:QAbstractItemModel, tablename:str="" ):
        now = str( datetime.now() )
        csv = "./csv/" + tablename + "_" + now + ".csv"
        csv = csv.replace( " ", "-" )
        f = open( csv, "w" )
        rows = model.rowCount()
        cols = model.columnCount()
        #  Export headers
        for c in range( 0, cols ):
            header = model.headerData( c, Qt.Horizontal, Qt.DisplayRole )
            f.write( header )
            if not c == cols - 1:
                f.write( "\t" )

        for r in range( 0, rows ):
            f.write( "\n" )
            for c in range( 0, cols ):
                idx = model.index( r, c )
                val = model.data( idx, Qt.DisplayRole )
                if val is None: val = ""
                #print( "val=", val, " - r/c=", r, "/", c )
                if isinstance( val, int ) or isinstance( val, float):
                    val = str( val )
                    val = val.replace( ".", "," )
                else:
                    if self._isIntOrFloatFormat( val ):
                        val = val.replace( ".", "," )
                    else:
                        val = val.replace( "\t", "   " )
                        val = val.replace( "\n", " " )

                f.write( val )
                if not c == cols - 1:
                    f.write( "\t" )
        f.close()

        if sys.platform.startswith( "linux" ):
            os.system( "xdg-open " +  csv )

    def getOposModel( self ) -> OffenePostenTableModel:
        xlist:List[XOffenerPosten] = self._db.getOffenePosten()
        model = OffenePostenTableModel( xlist )
        return model

    def _isIntOrFloatFormat( self, val:str ) -> bool:
        points = 0
        minus = 0
        for c in val:
            if not c.isdigit():
                if c == ".":
                    points = points + 1
                    if points > 1: return False
                elif c == "-":
                    minus = minus + 1
                    if minus > 1: return False
                else:
                    return False
        return True

    def getAlleVerwalter( self ) -> List[str]:
        return self._db.getVerwalter()

    def getAlleFirmen( self ) -> List[str]:
        return self._db.getAlleKreditoren()

    def getAlleMieter( self ) -> List[str]:
        return self._db.getAlleMieter()

    def validateOffenerPosten( self, x:XOffenerPosten ) -> str:
        if not x.erfasst_am:
            return "Datum 'erfasst am' fehlt."
        if not x.debi_kredi:
            return "Debitor/Kreditor fehlt."
        if x.betrag == 0:
            return "Betrag fehlt."
        return ""

    def validateNotiz( self, x:XNotiz ) -> str:
        if not x.ueberschrift:
            return "Überschrift fehlt"
        if not x.bezug:
            return "Bezug fehlt"
        return ""

    def saveOffenePosten( self, model:OffenePostenTableModel ) -> None:
        changes: Dict[str, List[XOffenerPosten]] = model.getChanges()
        for key in changes.keys():
            oposlist = changes[key]
            if key == "INSERT":
                for opos in oposlist:
                    self._db.insertOpos( opos, False )
            elif key == "UPDATE":
                for opos in oposlist:
                    self._db.updateOpos( opos, False )
            elif key == "DELETE":
                for opos in oposlist:
                    self._db.deleteOpos( opos.opos_id, False )
            else:
                raise Exception( "OffenePostenController.save(): Unknown key: %s" % (key) )
        self._db.commit()
        model.resetChanges()

    def saveNotizen( self, model: NotizenTableModel ) -> None:
        changes: Dict[str, List[XNotiz]] = model.getChanges()
        for key in changes.keys():
            notizlist = changes[key]
            if key == "INSERT":
                for notiz in notizlist:
                    self._db.insertNotiz( notiz, False )
            elif key == "UPDATE":
                for notiz in notizlist:
                    self._db.updateNotiz( notiz, False )
            elif key == "DELETE":
                for notiz in notizlist:
                    self._db.deleteNotiz( notiz.notiz_id, False )
            else:
                raise Exception( "NotizenController.save(): Unknown key: %s" % (key) )
        self._db.commit()
        model.resetChanges()


    def getNotizenModel( self, auch_erledigte:bool=False ) -> NotizenTableModel:
        notizenlist:List[XNotiz] = self._db.getNotizen( auch_erledigte )
        model = NotizenTableModel( notizenlist )
        return model

    def getRenditeTableModel( self, jahr:int ) -> RenditeTableModel:
        renditeList:List[XRendite] = list()

        def getXRenditeFromZahlungslist( master_name:str, zlist:List[XZahlung2] ) -> XRendite:
            """
            macht für ein Master-Objekt aus einer Liste von Zahlungen ein Rendite-Objekt
            :param master_name:
            :param zlist: Liste aller Zahlungen, die für das Master-Objekt <master_name> angefallen sind (Ein- und Ausz.)
            :return:
            """
            x = XRendite()
            x.master_name = master_name
            x.wert = 0 # todo
            ## in der Liste der Zahlungen sind Sammelabgaben, wie sie die Stadt NK erhebt, NICHT enthalten;
            ## deshalb selektieren wir sie hier extra
            x.ausgaben = self._getSummeAbgabenAusSammelAbgabe( master_name, jahr )
            master_id = self._db.getMasterId( master_name )
            x.davon_reparaturen = self._db.getSummeSonstigeAusgaben( jahr, master_id, "r" )
            if len( zlist ) > 0:
                x.jahr = zlist[0].jahr
                x.afa = zlist[0].afa
                x.qm = zlist[0].gesamt_wfl
            for z in zlist:
                if z.betrag > 0:
                    x.einnahmen += z.betrag
                else:
                    x.ausgaben += z.betrag
            x.ueberschuss_o_afa = x.einnahmen + x.ausgaben # "+", weil der ausgaben-Wert negativ ist
            if x.qm > 0:
                x.ertrag_pro_qm = round( float( x.ueberschuss_o_afa / x.qm ), 2 )
            x.ueberschuss_m_afa = x.ueberschuss_o_afa + x.afa # "+", weil afa negativ ist
            return x
        # alle Ein- und Auszahlungen des betreffenden Jahres holen:
        zahlungenList:List[XZahlung2] = self._db.getZahlungen( jahr )
        key_fnc = lambda x: x.master_name
        for key, group in itertools.groupby( zahlungenList, key_fnc ):
            xrendite = getXRenditeFromZahlungslist( key, list( group ) )
            renditeList.append( xrendite )
        tm = RenditeTableModel( renditeList )
        return tm

    def _getSummeAbgabenAusSammelAbgabe( self, master_name, jahr ) -> float:
        xsammeldetail: XSammelAbgabeDetail = self._db.getDetailFromSammelabgabe( master_name, jahr )
        if xsammeldetail:
            ausgaben = xsammeldetail.grundsteuer + xsammeldetail.abwasser + xsammeldetail.strassenreinigung
            return round( ausgaben, 2 )
        return 0.0

    def getDetaillierteAusgaben( self, model:RenditeTableModel, row:int, jahr:int ) -> AusgabenTableModel:
        master_name:str = model.getObjekt( row )
        master_id:int = self._db.getMasterId( master_name )
        ausgabenlist:List[XSonstAus] = self._db.getSonstigeAusgaben( jahr, master_id )
        # mobj_id_list:List[str] = self._db.getMietobjekteZuMasterId( master_id )
        # nkabrechnglist:List[XNkAbrechnung] = self._db.getNkAbrechnungen( jahr - 1 )
        # hgabrechnglist:List[XHgAbrechnung] = self._db.getHgAbrechnungen( jahr - 1 )
        li:List[XAusgabe] = list()
        for aus in ausgabenlist:
            x = XAusgabe()
            x.master_name = master_name
            x.mobj_id = aus.mobj_id
            x.kreditor = aus.kreditor
            x.betrag = aus.betrag
            x.kostenart = aus.kostenart
            x.buchungsdatum = aus.buchungsdatum
            x.buchungstext = aus.buchungstext
            li.append( x )
        # for nka in nkabrechnglist:
        #     if nka.mobj_id in mobj_id_list:
        #         x = XAusgabe()
        #         x.master_name = master_name
        #         x.mobj_id = nka.mobj_id
        #         x.betrag = nka.betrag
        #         x.buchungsdatum = nka.buchungsdatum
        #         x.kostenart = "nka"
        #         li.append( x )
        # for hga in hgabrechnglist:
        #     if hga.mobj_id in mobj_id_list:
        #         x = XAusgabe()
        #         x.master_name = master_name
        #         x.mobj_id = hga.mobj_id
        #         x.betrag = hga.betrag
        #         x.buchungsdatum = hga.buchungsdatum
        #         x.kostenart = "hga"
        #         li.append( x )
        sammelabgabe:float = self._getSummeAbgabenAusSammelAbgabe( master_name, jahr )
        if sammelabgabe > 0:
            x = XAusgabe()
            x.master_name = master_name
            x.betrag = sammelabgabe
            x.buchungstext = "Grundsteuer/Abwasser/Str.reinigg aus Sammelabgabe"
            x.kostenart = "a"
            li.append( x )
        li.sort( key=lambda y: y.kostenart )
        kostart = ""
        li2 = list()
        summe = total_sum = 0.0
        for aus in li:
            if kostart == "":
                kostart = aus.kostenart
            if aus.kostenart != kostart:
                # process group break
                x = XAusgabe()
                x.betrag = summe
                x.buchungstext = "Summe '%s' " % ( kostart )
                kostart = aus.kostenart
                total_sum += summe
                summe = 0.0
                li2.append( x )
            li2.append( aus )
            summe += aus.betrag
        x = XAusgabe()
        x.betrag = summe
        x.buchungstext = "Summe '%s' " % (kostart)
        li2.append( x )
        total_sum += summe
        x = XAusgabe()
        x.betrag = total_sum
        x.buchungstext = "Summe über alles"
        li2.append( x )
        model = AusgabenTableModel( li2 )
        return model

def test():
    busi = BusinessLogic.inst()

    #model = busi.getNkAbrechnungenTableModel( 2019 )
    model = busi.getRenditeTableModel( 2021 )
    print( model )

    # model = busi.getBuchungstextMatches( "2019" )
    #
    # li = busi.getAlleSollHausgelder()
    #
    # li = busi.getMasterobjekte()
    # print( li )
    # idx, monat = busi.getLetztenMonat()
    # letzter = busi.getMonatsletzter( 2 )

    # li = busi.getServiceLeistungen()
    # for x in li:
    #     print( x.kreditor )
    #busi.initSollhausgeld( "2019-01-01" )
    #mz = busi.getMietzahlungenMitSummen( 2020, 7 )
    #busi.createMtlEinAusJahresSet( 2021 )
    busi.terminate()

if __name__ == "__main__":
    test()

