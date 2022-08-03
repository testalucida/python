from typing import List, Dict, Tuple

from anlage_v.anlagev_interfaces import XObjektStammdaten, XZeilendefinition, XAfA, XErhaltungsaufwand, \
    XAllgemeineKosten, XSammelAbgabeDetail, XAusgabeKurz, XVerteilterAufwand, XEinnahmeKurz, XNebenkostenabrechnung, \
    XSollMiete2, XBruttomiete
from constants import Zahlart, zahlartstrings, Sonstaus_Kostenart
from dbaccess import DbAccess
from interfaces import XSollMiete, XGeschaeftsreise, XPauschale, XSollHausgeld


class AnlageV_DataAccess( DbAccess ):
    def __init__( self, dbname:str ):
        DbAccess.__init__( self, dbname )

    def getAnlageV_Zeilendefinitionen( self ) -> List[XZeilendefinition]:
        sql = "select feld_nr, feld_id, zeile, printX, printY, new_page_after, rtl " \
              "from anlagev_layout order by feld_nr "
        dictlist = self._doReadAllGetDict( sql )
        li:List[XZeilendefinition] = list()
        for dic in dictlist:
            x = XZeilendefinition( dic )
            x.new_page_after = False if x.new_page_after is None or x.new_page_after == 0 else True
            x.rtl = True if x.rtl == 1 else False
            li.append( x )
        return li

    def getSteuerpflichtige( self ) -> List[Dict]:
        """
        liefert alle Steuerpflichtigen aus Tabelle steuerpflichtiger
        in einem Dictionary mit den Keys name, vorname, steuernummer
        :return: List[Dict]
        """
        sql = "select name, vorname, steuernummer from steuerpflichtiger order by name "
        ld = self._doReadAllGetDict( sql )
        return ld

    def getSteuerpflichtiger( self, master_name:str ) -> Dict:
        """
        liefert den Steuerpflichtigen zu einem Masterobjekt.
        :param master_name:
        :return: Dict mit keys name, vorname, steuernummer
        """
        sql = "select name, vorname, steuernummer " \
              "from steuerpflichtiger s " \
              "inner join masterobjekt mo on mo.stpfl_id = s.stpfl_id " \
              "where mo.master_name = '%s' " % ( master_name )
        return self._doReadOneGetDict( sql )

    # def getObjektNamen( self ) -> List[str]:
    #     sql = "select master_name from masterobjekt " \
    #           "where master_name not like '*%' " \
    #           "order by master_name "
    #     tuplelist = self._doRead( sql )
    #     names = [e[0] for e in tuplelist]
    #     return names

    def getObjektStammdaten( self, vjahr:int ) -> List[XObjektStammdaten]:
        """
        Ermittelt alle für das Veranlagungsjahr <vjahr> relevanten Masterobjekte
        :param vjahr: Veranlagungsjahr. Ermittelt werden die Objekte, die vor oder im Vj angeschafft und frühestens
                        im Vj verkauft wurden.
        :return:
        """
        jahranfang, jahrende = "%d-01-01" % vjahr, "%d-12-31" % vjahr
        sql = "select lfdnr, master_id, master_name, strasse_hnr, plz, ort, angeschafft_am, veraeussert_am, gesamt_wfl, einhwert_az " \
              "from masterobjekt " \
              "where master_name not like '%s' " \
              "and angeschafft_am <= '%s' " \
              "and (veraeussert_am is NULL or veraeussert_am = '' or veraeussert_am > '%s' ) " \
              "order by master_name" % ("*%", jahrende, jahranfang)
        diclist = self._doReadAllGetDict( sql )
        li:List[XObjektStammdaten] = list()
        for dic in diclist:
            x = XObjektStammdaten( dic )
            li.append( x )
        return li

    def getMasterobjektJahresBruttomieteSumme( self, master_id:int, jahr:int ) -> float:
        # liefert die Jahresbruttomieeinnahmen eines Masterobjekts in *einer* Summe
        sql = "select sum( coalesce(jan,0) +  coalesce(feb, 0) + coalesce(mrz, 0) + coalesce(apr, 0) + coalesce(mai, 0) + coalesce(jun, 0) + " \
              "coalesce(jul, 0) + coalesce(aug, 0) + coalesce(sep, 0) + coalesce(okt, 0) + coalesce(nov, 0) + coalesce(dez, 0) ) as masterobjekt_jahressumme " \
              "from mietobjekt mobj " \
              "inner join mietverhaeltnis mv on mv.mobj_id = mobj.mobj_id " \
              "inner join mtleinaus mea on mea.mv_id = mv.mv_id " \
              "where mobj.master_id = %d " \
              "and mea.jahr = %d " % (master_id, jahr)
        listoftuples = self._doRead( sql )
        return listoftuples[0][0]

    def getMasterobjektBruttomieten( self, master_id:int, jahr:int ) -> List[Dict]:
        # liefert die Jahresbruttomieteinnahmen je Mieter als Liste von Dictionaries.
        # Jeder Dictionary hat den Aufbau
        # {
        #    'mv_id': 'bucher_lothar'
        #    'brutto_me:': 780.0
        # }
        sql = "select mv.mv_id, coalesce(jan,0) +  coalesce(feb, 0) + coalesce(mrz, 0) + coalesce(apr, 0) + coalesce(mai, 0) + coalesce(jun, 0) + " \
              "coalesce(jul, 0) + coalesce(aug, 0) + coalesce(sep, 0) + coalesce(okt, 0) + coalesce(nov, 0) + coalesce(dez, 0) as brutto_me " \
              "from mietobjekt mobj " \
              "inner join mietverhaeltnis mv on mv.mobj_id = mobj.mobj_id " \
              "inner join mtleinaus mea on mea.mv_id = mv.mv_id " \
              "where mobj.master_id = %d " \
              "and mea.jahr = %d " % (master_id, jahr)
        dictlist = self._doReadAllGetDict( sql )
        return dictlist

    def getSollmieten3( self, mv_id:str, jahr:int ) -> List[XSollMiete]:
        # liefert die Sollmieten für Mieter mv_id im Jahr jahr
        minbis = "%d-%02d-%02d" % (jahr, 1, 1)
        maxvon = "%d-%02d-%02d" % (jahr+1, 1, 1)
        sql = "select sm.sm_id, sm.mv_id, sm.von, coalesce(sm.bis, '') as bis, sm.netto, sm.nkv, (sm.netto + sm.nkv) as brutto, " \
              "coalesce(sm.bemerkung, '') as bemerkung, mv.mobj_id " \
              "from sollmiete sm " \
              "inner join mietverhaeltnis mv on mv.mv_id = sm.mv_id " \
              "where sm.von < '%s' " \
              "and (sm.bis is NULL or sm.bis = '' or sm.bis >= '%s') " \
              "and sm.mv_id = '%s' " \
              "order by sm.mv_id, sm.von desc" % ( maxvon, minbis, mv_id )
        l: List[Dict] = self._doReadAllGetDict( sql )
        sollList: List[XSollMiete] = list()
        for d in l:
            x = XSollMiete( d )
            sollList.append( x )
        return sollList

    def getSollmietenFuerMasterobjekt( self, master_name: str, jahr: int ) -> List[XSollMiete]:
        # liefert die Sollmieten für Mieter mv_id im Jahr jahr
        minbis = "%d-%02d-%02d" % (jahr, 1, 1)
        maxvon = "%d-%02d-%02d" % (jahr + 1, 1, 1)
        sql = "select sm.sm_id, sm.mv_id, sm.von, coalesce(sm.bis, '') as bis, sm.netto, sm.nkv, (sm.netto + sm.nkv) as brutto, " \
              "coalesce(sm.bemerkung, '') as bemerkung, mv.mobj_id " \
              "from masterobjekt master " \
              "inner join mietobjekt mobj on mobj.master_id = master.master_id " \
              "inner join mietverhaeltnis mv on mv.mobj_id = mobj.mobj_id " \
              "inner join sollmiete sm on sm.mv_id = mv.mv_id " \
              "where master.master_name = '%s' " \
              "and sm.von < '%s' " \
              "and (sm.bis is NULL or sm.bis = '' or sm.bis >= '%s') " \
              "order by sm.von " % (master_name, maxvon, minbis)
        l: List[Dict] = self._doReadAllGetDict( sql )
        sollList: List[XSollMiete] = list()
        for d in l:
            x = XSollMiete( d )
            sollList.append( x )
        return sollList

    def getZahlungssumme( self, master_name:str, jahr:int, art:Zahlart ) -> float:
        artstr = zahlartstrings[art]
        sql = "select sum(betrag) " \
              "from zahlung z " \
              "inner join masterobjekt master on master.master_id = z.master_id " \
              "where master.master_name = '%s' " \
              "and zahl_art = '%s' " \
              "and jahr = %d " % ( master_name, artstr, jahr )
        l = self._doRead( sql )
        sum = l[0][0]
        return 0.0 if sum is None else sum

    def getOffeneNKErstattungen( self, master_name:str, jahr:int ) -> float:
        sql = "select sum( betrag ) " \
              "from masterobjekt master " \
              "inner join mietobjekt mobj on mobj.master_id = master.master_id " \
              "inner join mietverhaeltnis mv on mv.mobj_id = mobj.mobj_id " \
              "inner join nk_abrechnung nka on nka.mv_id = mv.mv_id " \
              "where master.master_name = '%s' " \
              "and ab_jahr = %d " \
              "and betrag < 0 " \
              "and (buchungsdatum is NULL or buchungsdatum = '') " % ( master_name, jahr )
        l = self._doRead( sql )
        sum = l[0][0]
        return 0.0 if sum is None else sum

    def getSollmietenMasterEinzeln( self, master_name:str, jahr:int ) -> List[XSollMiete2]:
        von, bis = str(jahr) + "-12-31", str(jahr) + "-01-01" # sic!
        sql = "select soll.mv_id, soll.von, coalesce(soll.bis, '') as bis, " \
              "soll.netto, soll.nkv, mobj.mobj_id, master.master_id, master.master_name " \
            "from sollmiete soll " \
            "inner join mietverhaeltnis mv on mv.mv_id = soll.mv_id " \
            "inner join mietobjekt mobj on mobj.mobj_id = mv.mobj_id " \
            "inner join masterobjekt master on master.master_id = mobj.master_id " \
            "where master.master_name = '%s' " \
            "and soll.von < '%s' " \
            "and (soll.bis is NULL or soll.bis = '' or soll.bis > '%s') " \
            "order by soll.von asc " % (master_name, von, bis)
        dictlist = self._doReadAllGetDict( sql )
        l:List[XSollMiete2] = list()
        for dic in dictlist:
            x = XSollMiete2()
            x.master_name = dic["master_name"]
            x.master_id = dic["master_id"]
            x.mobj_id = dic["mobj_id"]
            x.mv_id = dic["mv_id"]
            x.von = dic["von"]
            x.bis = dic["bis"]
            x.netto = dic["netto"]
            x.nkv = dic["nkv"]
            l.append( x )
        return l


    def getNKA2( self, master_name:str, jahr:int ) -> List[XNebenkostenabrechnung]:
        sql = "select z.master_id, z.mobj_id, z.nka_id, z.jahr, z.betrag, nka.mv_id, nka.buchungsdatum " \
              "from zahlung z " \
              "inner join masterobjekt master on master.master_id = z.master_id " \
              "inner join nk_abrechnung nka on nka.nka_id = z.nka_id " \
              "where z.jahr = %d " \
              "and z.zahl_art = 'nka' " \
              "and master.master_name = '%s' " % (jahr, master_name)
        dictlist = self._doReadAllGetDict( sql )
        l:List[XNebenkostenabrechnung] = list()
        for dic in dictlist:
            x = XNebenkostenabrechnung()
            x.master_id = dic["master_id"]
            x.master_name = master_name
            x.kennung = "NKA"
            x.nka_id = dic["nka_id"]
            x.mobj_id_mv_id = dic["mobj_id"] + " / " + dic["mv_id"]
            x.betrag = dic["betrag"]
            x.buchungsdatum = dic["buchungsdatum"]
            l.append( x )
        return l

    def getNKA( self, master_name:str, jahr:int ) -> float:
        sql = "select sum( betrag ) " \
              "from masterobjekt master " \
              "inner join mietobjekt mobj on mobj.master_id = master.master_id " \
              "inner join mietverhaeltnis mv on mv.mobj_id = mobj.mobj_id " \
              "inner join nk_abrechnung nka on nka.mv_id = mv.mv_id " \
              "where master.master_name = '%s' " \
              "and ab_jahr = %d " \
              "and buchungsdatum is not NULL and buchungsdatum > '' " % (master_name, jahr)
        l = self._doRead( sql )
        sum = l[0][0]
        return 0.0 if sum is None else sum

    def getAfA( self, master_name:str ) -> XAfA or None:
        sql = "select coalesce(afa, 0) as afa, afa_wie_vj, afa_lin_deg, coalesce(afa_proz, 0) as afa_proz " \
              "from masterobjekt " \
              "where master_name = '%s' " % ( master_name )
        d = self._doReadOneGetDict( sql )
        if d["afa"] != 0:
            x = XAfA( master_name )
            x.afa = d["afa"]
            if d["afa_lin_deg"] == "linear":
                x.afa_linear = True
            elif d["afa_lin_deg"] == "degressiv":
                x.afa_degressiv = True
            x.afa_prozent = d["afa_proz"]
            if d["afa_wie_vj"] > " ":
                x.afa_wie_vorjahr = True
            return x
        return None

    def getNichtVerteiltenErhaltungsaufwandSumme( self, master_name:str, jahr:int ) -> int:
        sql = "select sum( betrag ) as summe_betrag " \
              "from sonstaus sa " \
              "inner join masterobjekt master on master.master_id = sa.master_id " \
              "where master.master_name = '%s' " \
              "and buchungsjahr = %d " \
              "and kostenart = 'r' " \
              "and sa.verteilen_auf_jahre = 1" % (master_name, jahr)
        l = self._doRead( sql )
        sum = l[0][0]
        return 0 if sum is None else round( sum )

    def getNichtVerteilteErhaltungsaufwendungen( self, master_name:str, jahr:int ) -> List[XErhaltungsaufwand]:
        sql = "select master.master_name, " \
                "sa.master_id, mobj_id, kreditor, betrag, rgdatum, rgtext, verteilen_auf_jahre, buchungsjahr," \
                "buchungsdatum, buchungstext " \
                "from sonstaus sa " \
                "inner join masterobjekt master on master.master_id = sa.master_id " \
                "where master.master_name = '%s' " \
                "and kostenart = 'r' " \
                "and verteilen_auf_jahre = 1 " \
                "and buchungsjahr = %d " % (master_name, jahr)
        dictlist = self._doReadAllGetDict( sql )
        l:List[XErhaltungsaufwand] = list()
        for d in dictlist:
            x = XErhaltungsaufwand( d )
            l.append( d )
        return l

    def getVerteilteErhaltungsaufwendungen( self, master_name:str, jahr:int ) -> List[XErhaltungsaufwand]:
        """
        Liefert alle Aufwände, wo buchungsjahr + verteilen_auf_jahre > <jahr>.
        Am Beispiel jahr = 2021: Es werden Aufwände aus den Jahren 2021 bis 2017 geliefert. (Aufwände können auf
        max. 5 Jahre verteilt werden.)
        Betrifft nur Kostenart 'r'
        :param master_name:
        :param jahr:
        :return:
        """
        sql = "select master.master_name, " \
                "sa.master_id, mobj_id, kreditor, betrag, rgdatum, rgtext, verteilen_auf_jahre, buchungsjahr," \
                "buchungsdatum, buchungstext " \
                "from sonstaus sa " \
                "inner join masterobjekt master on master.master_id = sa.master_id " \
                "where master.master_name = '%s' " \
                "and kostenart = 'r' " \
                "and verteilen_auf_jahre > 1 " \
                "and buchungsjahr + verteilen_auf_jahre  > %d " \
                "order by buchungsjahr " % (master_name, jahr)
        dictlist = self._doReadAllGetDict( sql )
        l: List[XErhaltungsaufwand] = list()
        for d in dictlist:
            x = XErhaltungsaufwand( d )
            l.append( x )
        return l

    def getZuVerteilendeAufwaendeVJ( self, master_name:str, jahr:int ) -> List[XErhaltungsaufwand]:
        """
        Liefert die Aufwände aus <jahr>, die zu verteilen sind (verteilen_auf_jahre > 1)
        Betrifft nur Kostenart 'r'.
        :param master_name:
        :param jahr:
        :return:
        """
        sql = "select master.master_name, " \
              "sa.master_id, mobj_id, kreditor, betrag, rgdatum, rgtext, verteilen_auf_jahre, buchungsjahr," \
              "buchungsdatum, buchungstext " \
              "from sonstaus sa " \
              "inner join masterobjekt master on master.master_id = sa.master_id " \
              "where master.master_name = '%s' " \
              "and kostenart = 'r' " \
              "and verteilen_auf_jahre > 1 " \
              "and buchungsjahr = %d " % (master_name, jahr)
        dictlist = self._doReadAllGetDict( sql )
        l: List[XErhaltungsaufwand] = list()
        for d in dictlist:
            x = XErhaltungsaufwand( d )
            l.append( x )
        return l

    def getAllgemeineKosten( self, master_name:str, jahr:int ) -> List[XAllgemeineKosten]:
        """
        Ermittelt allgemeine Kosten (Kostenart a)
        :param master_name:
        :param jahr:
        :return:
        """
        sql = "select master.master_name, " \
              "sa.master_id, mobj_id, kreditor, betrag, rgdatum, rgtext, verteilen_auf_jahre, buchungsjahr," \
              "buchungsdatum, buchungstext " \
              "from sonstaus sa " \
              "inner join masterobjekt master on master.master_id = sa.master_id " \
              "where master.master_name = '%s' " \
              "and kostenart = 'a' " \
              "and buchungsjahr = %d " % ( master_name, jahr )
        dictlist = self._doReadAllGetDict( sql )
        l: List[XAllgemeineKosten] = list()
        for d in dictlist:
            x = XAllgemeineKosten( d )
            l.append( x )
        return l

    def getSonstigeKosten( self, master_name: str, jahr: int ) -> List[XAllgemeineKosten]:
        sql = "select master.master_name, " \
              "sa.master_id, mobj_id, kreditor, betrag, rgdatum, rgtext, verteilen_auf_jahre, buchungsjahr," \
              "buchungsdatum, buchungstext " \
              "from sonstaus sa " \
              "inner join masterobjekt master on master.master_id = sa.master_id " \
              "where master.master_name = '%s' " \
              "and kostenart = 's' " \
              "and buchungsjahr = %d " % (master_name, jahr)
        dictlist = self._doReadAllGetDict( sql )
        l: List[XAllgemeineKosten] = list()
        for d in dictlist:
            x = XAllgemeineKosten( d )
            l.append( x )
        return l

    def getAusgabenSumme( self, master_name:str, jahr:int, kostenart:Sonstaus_Kostenart ) -> int:
        """
        Ermittelt die Summe der Ausgaben einer Kostenart
        :param master_name:
        :param jahr:
        :param kostenart: Kostenart, deren Ausgaben in einer Summe ermittelt werden sollen
        :return: Summe der Ausgaben
        """
        sql = "select sum(betrag) as summe_betrag " \
              "from sonstaus sa " \
              "inner join masterobjekt master on master.master_id = sa.master_id " \
              "where master.master_name = '%s' " \
              "and kostenart = '%s' " \
              "and buchungsjahr = %d " % ( master_name, kostenart.value[0], jahr )
        l = self._doRead( sql )
        sum = l[0][0]
        return 0 if sum is None else round( sum )

    def getMietenEinzeln( self, master_name:str, jahr:int ) -> List[XEinnahmeKurz]:
        """
        Liefert alle Brutto-Mieten für <master_name> im Jahr <jahr> als Liste von XEinnahmeKurz
        Wird von AnlageV_Preview_Logic.get

        :param master_name:
        :param jahr:
        :return:
        """
        sql = "select z.master_id, z.mobj_id, monat, betrag " \
              "from zahlung z " \
              "inner join masterobjekt master on master.master_id = z.master_id " \
              "where zahl_art = 'bruttomiete' " \
              "and master.master_name = '%s' " \
              "and z.jahr = %d " % (master_name, jahr)
        dictList = self._doReadAllGetDict( sql )
        l: List[XEinnahmeKurz] = list()
        for dic in dictList:
            x = XEinnahmeKurz()
            x.kennung = "bruttomiete"
            x.master_id = dic["master_id"]
            x.master_name = master_name
            x.mobj_id = dic["mobj_id"]
            x.mobj_id_mv_id = x.mobj_id
            x.betrag = dic["betrag"]
            x.jahr = jahr
            x.monat = dic["monat"]
            x.buchungsdatum = x.monat + "/" + str( x.jahr )
            l.append( x )
        return l

    def getHGVEinzeln( self, master_name:str, jahr:int ) -> List[XAusgabeKurz]:
        """
        Liefert alle Brutto-Hausgeldvorauszahlungen (inkl. RüZuFü)
        für <master_name> im Jahr <jahr> als Liste von XAusgabeKurz.
        Wird von AnlageV_Preview_Logic.getHausgeldModel(..) benötigt.
        :param master_name:
        :param jahr:
        :return:
        """
        def createXAusgabeKurzList( dic:Dict, jahr:int ) -> List[XAusgabeKurz]:
            """
            Das hier übergebene <dic> enthält einen Satz aus <mtleinaus>. Dieser enthält 0 bis 12
            HG-Vorauszahlungen (Spalten <jan> bis <dez>).
            Für jeden Wert ungleich 0 und ungleich None wird ein XAusgabeKurz-Objekt erstellt, welcher
            der Rückgabeliste hinzugefügt wird.
            :param dic:
            :return: eine Liste mit XAusgabeKurz-Objekten oder eine leere Liste, wenn kein XAusgabeKurz-Objekt
                    erstellt wurde. Niemals None.
            """
            l:List[XAusgabeKurz] = list()
            columns = ("jan", "feb", "mrz", "apr", "mai", "jun", "jul", "aug", "sep", "okt", "nov", "dez")
            for m in range(0, 12):
                col = columns[m]
                if dic[col] and dic[col] != 0:
                    x = XAusgabeKurz()
                    x.master_name = dic["master_name"]
                    x.master_id = dic["master_id"]
                    x.mobj_id = "alle"
                    x.kostenart = "HG-Voraus"
                    x.kreditor = dic["weg_name"] + " / " + dic["vw_id"]
                    x.betrag = dic[col]
                    x.buchungsdatum = col + " / " + str( jahr )
                    l.append( x )
            return l

        sql = "select master.master_name, master.master_id, vwg.vw_id, vwg.weg_name, mea.vwg_id, " \
              "jan, feb, mrz, apr, mai, jun, jul, aug, sep, okt, nov, dez " \
              "from mtleinaus mea " \
              "inner join verwaltung vwg on vwg.vwg_id = mea.vwg_id " \
              "inner join masterobjekt master on master.master_id = vwg.master_id " \
              "where mea.jahr = %d " \
              "and master.master_name = '%s' " % (jahr, master_name )
        dictList = self._doReadAllGetDict( sql )
        l:List[XAusgabeKurz] = list()
        for dic in dictList:
            # wir haben dann mehrere dic's, wenn es einen unterjährigen Verwalterwechsel gegeben hat
            ltmp = createXAusgabeKurzList( dic, jahr ) # aus jeder Monatszahlung wird ein XAusgabeKurz-Objekt
            l.extend( ltmp )
        return l

    def getHGAbrechnungszahlungen( self, master_name:str, jahr:int ) -> List[XAusgabeKurz]:
        """
        Liefert aus <zahlung> die Zahlungen <zahl_art> == 'hga'
        für <master_name> und <jahr> in einer Liste von XAusgabeKurz-OBjekten.
        Beachte: <jahr> bezieht sich auf das Jahr der Zahlung, nicht auf das mit der HGA abgerechnete Jahr.
        :param master_name:
        :param jahr:
        :return: Eine Liste mit 0 bis n XAusgabeKurz-Objekten. Niemals None
        """
        def createXAusgabeKurz( dic:Dict ) -> XAusgabeKurz:
            """
            Das hier übergebene <dic> enthält einen Satz aus Spalten von <zahlung> und von <hg_abrechnung>.
            Aus ihm wird ein XAusgabeKurz-Objekt erzeugt und zurückgeliefert.
            :param dic:
            :return:
            """
            x = XAusgabeKurz()
            x.master_name = dic["master_name"]
            x.master_id = dic["master_id"]
            x.mobj_id = "alle"
            x.kostenart = "HG-Abrechnung"
            x.betrag = dic["betrag"]
            x.kreditor = "Vermieter" if x.betrag >= 0 else dic["weg_name"] + " / " + dic["vw_id"]
            x.buchungstext = "Abrechng.jahr: " + str( dic["ab_jahr"] )
            #x.buchungsdatum = "Zahljahr: " + str( dic["jahr"] )
            x.buchungsdatum = dic["buchungsdatum"]
            return x

        sql = "select master.master_name, master.master_id, vwg.vw_id, vwg.weg_name, " \
              "hga.ab_jahr, hga.buchungsdatum, z.jahr, z.betrag " \
              "from zahlung z " \
              "inner join hg_abrechnung hga on hga.hga_id = z.hga_id " \
              "inner join verwaltung vwg on vwg.vwg_id = hga.vwg_id " \
              "inner join masterobjekt master on master.master_id = vwg.master_id " \
              "where z.jahr = %d " \
              "and z.zahl_art = 'hga' " \
              "and master.master_name = '%s' " % ( jahr, master_name )
        dictList = self._doReadAllGetDict( sql )
        l: List[XAusgabeKurz] = list()
        for dic in dictList:
            # wir haben dann mehrere dic's, wenn es Zahlungen zu mehreren Abrechnungen gegeben hat (Corona!)
            x = createXAusgabeKurz( dic )  # aus jeder Monatszahlung wird ein XAusgabeKurz-Objekt
            l.append( x )
        return l

    def getAusgaben( self, master_name:str, jahr:int, kostenarten:List[Sonstaus_Kostenart] ) -> List[XAusgabeKurz]:
        """
        Liefert die Ausgaben der gewünschten Kostenarten.
        ACHTUNG: Es werden nur solche Sätze geliefert, wo verteilen_auf_jahre == 1.
        Auf mehrere Jahre verteilte Aufwendungen müssen mit Methode getVerteilteRepAufwendungen() selektiert werden.
        Das betrifft nur Kostenart 'r'. Bei allen anderen steht verteilen_auf_jahre immer auf 1.
        :param master_name:
        :param jahr:
        :param kostenarten:
        :return: Eine Liste mit XAusgabeKurz-Objekten. Wurde keine Ausgabe gefunden, wird eine leere Liste
                zurückgegeben.
        """
        k_arten = ""
        for art in kostenarten:
            k_arten += "'"
            k_arten += art.value[0]
            k_arten += "'"
            k_arten += ","
        k_arten = k_arten[:-1]
        sql = "select  master.master_name, master.master_id, " \
              "mobj_id, kostenart, kreditor, buchungstext, buchungsdatum, betrag " \
              "from sonstaus sa " \
              "inner join masterobjekt master on master.master_id = sa.master_id " \
              "where master.master_name = '%s' " \
              "and buchungsjahr = %d " \
              "and kostenart in (%s) " \
              "and verteilen_auf_jahre = 1 " \
              "order by kostenart, kreditor, betrag " % ( master_name, jahr, k_arten )
        dictlist = self._doReadAllGetDict( sql )
        l: List[XAusgabeKurz] = list()
        for d in dictlist:
            x = XAusgabeKurz( d )
            l.append( x )
        return l

    def getMietobjekteZuMasterName( self, master_name:str, jahr:int ) -> List[str]:
        """
        Liefert alle Mietobjekte zu einem Masterobjekt, unabhängig vom Aktiv-Kennzeichen.
        ACHTUNG: Das ist nur richtig, solange das Masterobjekt kein Haus ist, das mir gehört UND dem mehr als *ein*
                Mietobjekt zugeordnet ist. (Beispiel Kuchenberg: Hätten die Spielhalle und die Wohnung einen
                gemeinsamen Master, würde auch für die Veranlagung 2022 die Wohnung geliefert werden, obwohl sie schon
                2021 verkauft wurde. Da die Wohnung aber ihren eigenen Master hat, erhält dieser ein entsprechendes
                veraeussert_am - Datum, was bewirkt, das mit diesem Master überhaupt kein Aufruf mehr erfolgt.)
        :param master_name:
        :param jahr:
        :return:
        """
        sql = "select mobj_id " \
              "from mietobjekt mo " \
              "inner join masterobjekt ma on ma.master_id = mo.master_id " \
              "where ma.master_name = '%s' " \
              "order by mobj_id " % master_name
        tuplelist = self._doRead( sql )
        return [t[0] for t in tuplelist]

    # def getHGVmitRueZuFue( self, mobj_id:str, jahr:int ) -> float:
    #     """
    #     Liefert die Summe aller Brutto-HG-Vorauszahlungen für Mietobjekt <mobj_id> im Zeitraum <jahr>.
    #     Achtung: es wird eine negative Zahl geliefert. (Auszahlungen)
    #     :param mobj_id:
    #     :param jahr:
    #     :return:
    #     """
    #     sql = "select sum(betrag) as hgv " \
    #         "from zahlung " \
    #         "where zahl_art = 'hgv' " \
    #         "and jahr = %d " \
    #         "and mobj_id = '%s'" % (jahr, mobj_id)
    #     tuplelist = self._doRead( sql )
    #     li = [t[0] for t in tuplelist]
    #     return li[0]

    # def getSollHGV( self, mobj_id:str, jahr:int ) -> List[XSollHausgeld]:
    #     """
    #     Liefert für <mobj_id> die im betreffenden <jahr> relevanten Soll-Hausgelder.
    #     Es ist eine Liste, weil sich das Hausgeld mitten im Jahr ändern kann.
    #     :param mobj_id:
    #     :param jahr:
    #     :return: Eine Liste von XSollHausgeld-OBjekten
    #     """
    #     jahranf, jahrend = "%d-01-01" % jahr, "%d-12-31" % jahr
    #     sql = "select s.shg_id, v.vw_id, s.vwg_id, s.von, coalesce(s.bis, '') as bis, s.netto, s.ruezufue, " \
    #           "v.mobj_id, v.weg_name,  coalesce(s.bemerkung, '') as bemerkung " \
    #           "from sollhausgeld s " \
    #           "inner join verwaltung v on v.vwg_id = s.vwg_id " \
    #           "where v.mobj_id = '%s' " \
    #           "and (s.von <= '%s') " \
    #           "and (s.bis is NULL or s.bis = '' or s.bis >= '%s') " \
    #           "order by v.weg_name, s.von desc" % (mobj_id, jahrend, jahranf)
    #     l: List[Dict] = self._doReadAllGetDict( sql )
    #     return [XSollHausgeld( d ) for d in l]

    # def getSollHGV( self, master_name:str, jahr:int ) -> List[XSollHausgeld]:
    #     """
    #     Liefert für <master_name> die im betreffenden <jahr> relevanten Soll-Hausgelder.
    #     Es ist eine Liste, weil sich das Hausgeld mitten im Jahr ändern kann.
    #     :param master_name:
    #     :param jahr:
    #     :return: Eine Liste von XSollHausgeld-OBjekten
    #     """
    #     jahranf, jahrend = "%d-01-01" % jahr, "%d-12-31" % jahr
    #     sql = "select s.shg_id, s.vwg_id, s.von, coalesce(s.bis, '') as bis, s.netto, s.ruezufue, " \
    #           "mao.master_name, " \
    #           "v.vw_id, v.weg_name,  coalesce(s.bemerkung, '') as bemerkung " \
    #           "from sollhausgeld s " \
    #           "inner join verwaltung v on v.vwg_id = s.vwg_id " \
    #           "inner join masterobjekt mao on mao.master_id = v.master_id " \
    #           "where mao.master_name = '%s' " \
    #           "and (s.von <= '%s') " \
    #           "and (s.bis is NULL or s.bis = '' or s.bis >= '%s') " \
    #           "order by v.weg_name, s.von desc" % (master_name, jahrend, jahranf)
    #     l: List[Dict] = self._doReadAllGetDict( sql )
    #     return [XSollHausgeld( d ) for d in l]

    # def getHGA( self, mobj_id:str, jahr:int ) -> float:
    #     """
    #     Liefert die SUmmen der HG-Abrechnungszahlungen für ein Mietobjekt <mobj_id> für einen Zeitraum <jahr>.
    #     Annahme: in der Tabelle <zahlung> kann es mehr als einen Eintrag je mobj_id und jahr geben.
    #     Es wird eine positive (Gutschrift) oder negative Zahl (Nachzahlung) geliefert.
    #     :param mobj_id:
    #     :param jahr:
    #     :return:
    #     """
    #     sql = "select coalesce(sum(betrag), 0) as hga " \
    #           "from zahlung " \
    #           "where zahl_art = 'hga' " \
    #           "and jahr = %d " \
    #           "and mobj_id = '%s'" % (jahr, mobj_id)
    #     tuplelist = self._doRead( sql )
    #     li = [x[0] for x in tuplelist]
    #     return li[0]

    def getGeschaeftsreisen( self, jahr:int ) -> List[XGeschaeftsreise]:
        sql = "select id, mobj_id, von, bis, jahr, ziel,  zweck, km, personen, uebernachtung, uebernacht_kosten " \
              "from geschaeftsreise " \
              "where jahr = %d " \
              "order by von " % jahr
        dictlist = self._doReadAllGetDict( sql )
        return [XGeschaeftsreise( d ) for d in dictlist]

    def getPauschalen( self, jahr:int ) -> XPauschale:
        """
        Liefert den einen Satz in der Tabelle <pauschale>, der sich auf das übergebene <jahr> bezieht.
        Er enthält mehrere Pauschalen, deshalb heißt die Methode getPauschalen()
        :param jahr:
        :return:
        """
        sql = "select id, coalesce(jahr_bis, 9999) as jahr_bis, km, vpfl " \
              "from pauschale "
        dictlist =  self._doReadAllGetDict( sql )
        # dictlist sortieren nach jahr_bis und den für <jahr> passenden Satz zurückliefern.
        sortedlist = sorted( dictlist, key=lambda d: d["jahr_bis"] )
        for d in sortedlist:
            if jahr <= d["jahr_bis"]:
                if d["jahr_bis"] == 9999:
                    d["jahr_bis"] = None
                return XPauschale( d )
        raise Exception( "Anlagev_DataAccess.getPauschalen(): "
                         "Keinen zum Jahr %d passenden Pauschalensatz gefunden" % jahr )


    # def getVerteilteRepAufwendungen( self, master_name:str, vonjahr:int, bisjahr:int ) -> List[XVerteilterAufwand]:
    #     sql = "select  master.master_name, master.master_id, " \
    #           "mobj_id, kostenart, kreditor, buchungstext, buchungsdatum, buchungsjahr, verteilen_auf_jahre, betrag " \
    #           "from sonstaus sa " \
    #           "inner join masterobjekt master on master.master_id = sa.master_id " \
    #           "where master.master_name = '%s' " \
    #           "and buchungsjahr >= %d " \
    #           "and buchungsjahr <= %d " \
    #           "and verteilen_auf_jahre > 1 " \
    #           "and kostenart = 'r' " \
    #           "order by buchungsjahr, kreditor, betrag " % (master_name, vonjahr, bisjahr)
    #     dictlist = self._doReadAllGetDict( sql )
    #     l: List[XAusgabeKurz] = list()
    #     for d in dictlist:
    #         x = XAusgabeKurz( d )
    #         l.append( x )
    #     return l

    def getJahre( self ) -> List[int]:
        """
        Liefert die Jahre, für die Daten erfasst wurden.
        :return:
        """
        sql = "select distinct jahr from zahlung order by jahr asc;"
        tuplelist = self._doRead( sql )
        li = [ x[0] for x in tuplelist ]
        return li


    # def getDetailFromSammelabgabe( self, master_name:str, jahr:int ) -> XSammelAbgabeDetail or None:
    #     sql = "select master.master_name, " \
    #           "sd.master_id, sd.grundsteuer, sd.abwasser, sd.strassenreinigung " \
    #           "from sammelabgabe_detail sd " \
    #           "inner join masterobjekt master on master.master_id = sd.master_id " \
    #           "where master.master_name = '%s' " \
    #           "and jahr = %d " % (master_name, jahr)
    #     d = self._doReadOneGetDict( sql )
    #     if d:
    #         x = XSammelAbgabeDetail( d )
    #         return x
    #     return None


def test10():
    av = AnlageV_DataAccess( "../immo.db" )
    av.open()
    l = av.getVerteilteErhaltungsaufwendungen( "SB_Kaiser", 2024 )
    print( l )

def test9():
    data = AnlageV_DataAccess( "../immo.db" )
    data.open()
    l = data.getMietenEinzeln( "ER_Heuschlag", 2021 )
    print( l )


def test8():
    data = AnlageV_DataAccess( "../immo.db" )
    data.open()
    #l = data.getHGVEinzeln( "SB_Kaiser", 2022 )
    l = data.getHGAbrechnungszahlungen( "ER_Heuschlag", 2021 )
    print( l )

def test7():
    av = AnlageV_DataAccess( "../immo.db" )
    av.open()
    b = av.getObjektStammdaten( 2021 )
    print( b )

def test6():
    av = AnlageV_DataAccess( "../immo.db" )
    av.open()
    b = av.getMietobjekteZuMasterName( "NK_Kleist" )
    print( b )

# def test5():
#     av = AnlageV_DataAccess( "../immo.db" )
#     av.open()
#     b = av.getSollHGV( "linx", 2020 )
#     print( b )


def test4():
    av = AnlageV_DataAccess( "../immo.db" )
    av.open()
    b = av.getPauschalen( 2019 )
    print( b )

def test3():
    av = AnlageV_DataAccess( "../immo.db" )
    av.open()
    b = av.getGeschaeftsreisen( 2021 )
    print( b )

# def test2():
#     av = AnlageV_DataAccess( "../immo.db" )
#     av.open()
#     b = av.getHGVmitRueZuFue( "linx", 2021 )
#     print( b )
#     b = av.getHGA( "zweibrueck", 2021 )
#     print( b )

def test():
    av = AnlageV_DataAccess( "../immo.db")
    av.open()
    #l = av.getVerteilteRepAufwendungen( "ILL_Eich", 2017, 2021 )
    l = av.getAusgaben( "SB_Kaiser", 2021, [Sonstaus_Kostenart.ALLGEMEIN,
                                            Sonstaus_Kostenart.VERSICHERUNG, Sonstaus_Kostenart.GRUNDSTEUER] )
    d = av.getSteuerpflichtiger( "ER_Heuschlag" )
    l = av.getNichtVerteilteErhaltungsaufwendungen( "SB_Kaiser", 2021 )
    l = av.getVerteilteErhaltungsaufwendungen( "SB_Kaiser", 2021 )
    s = av.getNichtVerteiltenErhaltungsaufwandSumme( "SB_Kaiser", 2021 )
    x = av.getAfA( "Rülzheim")
    b = av.getOffeneNKErstattungen( "NK_Zweibrueck", 2020 )
    b = av.getNKA( "NK_Kleist", 2020 )
    # names = av.getObjektNamen()
    # print( names )

    #li = db.getSollmieten2( 2020 )

    li = av.getSollmieten3( "bucher_lothar", 2020 )

    dictlist = av.getMasterobjektBruttomieten( 17, 2021 )
    print( dictlist )

    av.close()

if __name__ == '__main__':
    test()