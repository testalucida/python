from typing import List, Dict

from anlage_v.anlagev_interfaces import XObjektStammdaten, XZeilendefinition, XAfA, XErhaltungsaufwand, \
    XAllgemeineKosten
from constants import Zahlart, zahlartstrings
from dbaccess import DbAccess
from interfaces import XSollMiete


class AnlageV_DataAccess( DbAccess ):
    def __init__( self, dbname:str ):
        DbAccess.__init__( self, dbname )

    def getAnlageV_Zeilendefinitionen( self ) -> List[XZeilendefinition]:
        sql = "select feld_nr, feld_id, zeile, printX, printY, new_page_after from anlagev_layout order by feld_nr "
        dictlist = self._doReadAllGetDict( sql )
        li:List[XZeilendefinition] = list()
        for dic in dictlist:
            x = XZeilendefinition( dic )
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

    def getObjektNamen( self ) -> List[str]:
        sql = "select master_name from masterobjekt " \
              "where master_name not like '*%' " \
              "order by master_name "
        tuplelist = self._doRead( sql )
        names = [e[0] for e in tuplelist]
        return names

    def getObjektStammdaten( self ) -> List[XObjektStammdaten]:
        sql = "select lfdnr, master_id, master_name, strasse_hnr, plz, ort, angeschafft_am, veraeussert_am, gesamt_wfl, einhwert_az " \
              "from masterobjekt " \
              "where master_name not like '*%'"
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
        if d["afa"] > 0:
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
        sql = "select master.master_name, " \
                "sa.master_id, mobj_id, kreditor, betrag, rgdatum, rgtext, verteilen_auf_jahre, buchungsjahr," \
                "buchungsdatum, buchungstext " \
                "from sonstaus sa " \
                "inner join masterobjekt master on master.master_id = sa.master_id " \
                "where master.master_name = '%s' " \
                "and kostenart = 'r' " \
                "and verteilen_auf_jahre > 1 " \
                "and buchungsjahr + verteilen_auf_jahre  > %d " % (master_name, jahr)
        dictlist = self._doReadAllGetDict( sql )
        l: List[XErhaltungsaufwand] = list()
        for d in dictlist:
            x = XErhaltungsaufwand( d )
            l.append( x )
        return l

    def getAllgemeineKosten( self, master_name:str, jahr:int ) -> List[XAllgemeineKosten]:
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

    def getAllgemeineKostenSumme( self, master_name:str, jahr:int ) -> int:
        sql = "select sum(betrag) as summe_betrag " \
              "from sonstaus sa " \
              "inner join masterobjekt master on master.master_id = sa.master_id " \
              "where master.master_name = '%s' " \
              "and kostenart = 'a' " \
              "and buchungsjahr = %d " % ( master_name, jahr )
        l = self._doRead( sql )
        sum = l[0][0]
        return 0 if sum is None else round( sum )

    def getSonstigeKosten( self, master_name:str, jahr:int ) -> List[XAllgemeineKosten]:
        sql = "select master.master_name, " \
              "sa.master_id, mobj_id, kreditor, betrag, rgdatum, rgtext, verteilen_auf_jahre, buchungsjahr," \
              "buchungsdatum, buchungstext " \
              "from sonstaus sa " \
              "inner join masterobjekt master on master.master_id = sa.master_id " \
              "where master.master_name = '%s' " \
              "and kostenart = 's' " \
              "and buchungsjahr = %d " % ( master_name, jahr )
        dictlist = self._doReadAllGetDict( sql )
        l: List[XAllgemeineKosten] = list()
        for d in dictlist:
            x = XAllgemeineKosten( d )
            l.append( x )
        return l

    def getSonstigeKostenSumme( self, master_name:str, jahr:int ) -> int:
        sql = "select sum(betrag) as summe_betrag " \
              "from sonstaus sa " \
              "inner join masterobjekt master on master.master_id = sa.master_id " \
              "where master.master_name = '%s' " \
              "and kostenart = 's' " \
              "and buchungsjahr = %d " % ( master_name, jahr )
        l = self._doRead( sql )
        sum = l[0][0]
        return 0 if sum is None else round( sum )

def test():
    av = AnlageV_DataAccess( "../immo.db")
    av.open()
    l = av.getNichtVerteilteErhaltungsaufwendungen( "SB_Kaiser", 2021 )
    l = av.getVerteilteErhaltungsaufwendungen( "SB_Kaiser", 2021 )
    s = av.getNichtVerteiltenErhaltungsaufwandSumme( "SB_Kaiser", 2021 )
    x = av.getAfA( "Rülzheim")
    b = av.getOffeneNKErstattungen( "NK_Zweibrueck", 2020 )
    b = av.getNKA( "NK_Kleist", 2020 )
    names = av.getObjektNamen()
    print( names )

    #li = db.getSollmieten2( 2020 )

    li = av.getSollmieten3( "bucher_lothar", 2020 )

    dictlist = av.getMasterobjektBruttomieten( 17, 2021 )
    print( dictlist )

    av.close()

if __name__ == '__main__':
    test()