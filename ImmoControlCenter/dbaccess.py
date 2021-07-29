import sqlite3
from typing import List, Tuple, Dict
from anlage_v.anlagev_interfaces import XSammelAbgabeDetail
from constants import einausart
from datehelper import getNumberOfDays, getCurrentTimestampIso
from interfaces import XSonstAus, XZahlung, XSollHausgeld, XSollMiete, XNkAbrechnung, XHgAbrechnung, \
    XMietverhaeltnis, XOffenerPosten, XNotiz, XZahlung2, XZahlung3

mon_dbnames = ("jan", "feb", "mrz", "apr", "mai", "jun", "jul", "aug", "sep", "okt", "nov", "dez")


class DbAccess:
    def __init__( self, dbname: str ):
        self._con = None
        self._cursor = None
        self._dbname = dbname

    def getDbName( self ) -> str:
        return self._dbname

    def open( self ) -> None:
        self._con = sqlite3.connect( self._dbname )
        # self._con = ConnectionProvider.inst().getConnection() #  sqlite3.connect( self._dbname )
        self._cursor = self._con.cursor()

    def close( self ) -> None:
        self._cursor.close()
        self._con.close()

    def getMaxId( self, table: str, id_name: str ) -> int:
        sql = "select max(%s) from %s" % (id_name, table)
        records = self._doRead( sql )
        return records[0][0]

    def commit( self ):
        self._con.commit()

    def getLetzteBuchung( self ):
        """
        liefert den einzigen Eintrag der Tabelle letztebuchung
        :return:
        """
        sql = "select datum, text from letztebuchung"
        row = self._doRead( sql )
        try:
            return row[0][0], row[0][1]
        except:
            return "", ""

    def deleteLetzteBuchung( self, commit: bool = True ) -> int:
        sql = "delete from letztebuchung"
        return self._doWrite( sql, commit )

    def insertLetzteBuchung( self, datum: str, text: str, commit: bool = True ) -> int:
        sql = "insert into letztebuchung (datum, text) values ('%s', '%s')" % (datum, text)
        return self._doWrite( sql, commit )

    def getMietobjekteKurz( self ) -> List[Dict]:
        """
        Liefert folgende Informationen für alle aktiven Mietobjekte:
        - mobj_id
        - master_id
        - whg_bez
        :return:
        """
        sql = "select mobj_id, master_id, whg_bez " \
              "from mietobjekt " \
              "where aktiv = 1 " \
              "and mobj_id > ' ' and mobj_id not like '%*%' " \
              "order by mobj_id "
        return self._doReadAllGetDict( sql )

    def getMietobjekteZuMasterId( self, master_id: int ) -> List[str]:
        """
        Liefert alle Mietobjekte (mobj_id) zu einem Master-Objekt (master_id)
        """
        sql = "select mobj_id " \
              "from mietobjekt " \
              "where master_id = %d " \
              "order by mobj_id " % (master_id)
        return self._doReadAllGetDict( sql )

    def getMasterUndMietobjekte( self ) -> List[Dict]:
        """
        Liefert Informationen aus einem Join von masterobjekt und mietobjekt
        :return:
        """
        sql = "select ma.master_id, ma.master_name, mi.mobj_id, mi.whg_bez " \
              "from masterobjekt ma " \
              "inner join mietobjekt mi on mi.master_id = ma.master_id " \
              "where mi.aktiv = 1 " \
              "order by ma.master_name, mi.mobj_id "
        return self._doReadAllGetDict( sql )

    def getAktuellesMietverhaeltnis( self, mv_id: str ) -> XMietverhaeltnis:
        """
        Liefert das aktuelle Mietverhältnis zur gegebenen mv_id (aktiv oder gekündigt).
        NICHT abgedeckt ist der Fall, dass ein Mieter 2 Wohnungen bewohnt.
        Dann wird eine Exception geworfen.
        :param mv_id: Selektionsparameter
        :return: XMietverhaeltnis
        """
        sql = "select mv.id, mv.mv_id, mv.mobj_id, mv.von, coalesce(mv.bis, '') as bis, mv.name, mv.vorname, " \
              "coalesce(mv.name2, '') as name2, coalesce(mv.vorname2, '') as vorname2, " \
              "coalesce(mv.telefon, '') as telefon, coalesce(mv.mobil, '') as mobil, coalesce(mv.mailto, '') as mailto," \
              "mv.anzahl_pers, mv.IBAN, " \
              "mv.bemerkung1, mv.bemerkung2, mv.kaution, coalesce(mv.kaution_bezahlt_am, '') as kaution_bezahlt_am, " \
              "sm.netto as nettomiete, sm.nkv " \
              "from mietverhaeltnis mv " \
              "inner join sollmiete sm on sm.mv_id = mv.mv_id " \
              "where mv.mv_id = '%s' " \
              "order by mv.von desc, sm.von desc " % mv_id
        listofdicts = self._doReadAllGetDict( sql )
        x = XMietverhaeltnis( listofdicts[0] )
        return x

    def getAktuellesMietverhaeltnisZuMietobjekt( self, mobj_id:str ) -> str:
        sql = "select mv_id " \
              "from mietverhaeltnis where mobj_id = '%s' " \
              "order by von desc " % mobj_id
        tuplelist:List[tuple] = self._doRead( sql )
        if len( tuplelist ) == 0:
            return ""
        return tuplelist[0][0]

    def getAktuellesMietverhaeltnisVonBis( self, mv_id:str ) -> Dict:
        """
        Liefert für eine Mietverhältnis-ID das letzte (aktuelle) von/bis.
        Das Mietverhältnis kann noch aktiv oder bereits gekündigt sein.
        :param mv_id:
        :return: ein Dict mit den Keys id, mv_id, mobj_id, von, bis
        """
        sql = "select id, mv_id, mobj_id, von, bis from mietverhaeltnis " \
              "where mv_id = '%s' " \
              "order by von desc " % mv_id
        dictlist = self._doReadAllGetDict( sql )
        return dictlist[0]

    def getMietverhaeltnisseEssentials( self, jahr: int, orderby: str = None ) -> List[Dict]:
        """
        Liefert zu allen Mietverhältnissen, die in <jahr> aktiv sind, die Werte der Spalten mv_id, von, bis
        :param jahr:
        :param orderby:
        :return: List[Dict]:
                [
                    {
                        "id":   23,
                        "mv_id":  "lander_anke",
                        "mobj_id": "volkerstal",
                        "von":    "2019-01-01"
                        "bis":    ""
                    },
                    ...
                ]
        """
        sql = "select id, mv_id, mobj_id, von, bis from mietverhaeltnis " \
              "where substr(von, 0, 5) <= '%s' " \
              "and (bis is NULL or bis = '' or substr(bis, 0, 5) >= '%s') " % (jahr, jahr)
        if orderby:
            sql += "order by %s " % (orderby)
        return self._doReadAllGetDict( sql )

    def getMieteBestandteile( self, mv_id: str, jahr: int, monat: int ) -> (float, float):
        von = "%d-%02d-01" % (jahr, monat)
        letzter = getNumberOfDays( monat )
        bis = "%d-%02d-%d" % (jahr, monat, letzter)
        sql = "select netto, nkv " \
              "from sollmiete " \
              "where mv_id = '%s' " \
              "and von < '%s' " \
              "and (bis is NULL or bis = '' or bis > '%s' ) " % (mv_id, bis, von)
        li = self._doRead( sql )
        return li[0]

    def getMietzahlungenMitSummen( self, jahr: int ) -> List[Dict]:
        # Achtung: das TableModel verlässt sich auf die Reihenfolge der Spalten.
        # Wenn sie geändert wird, muss man das im CheckTableModel.__init()__ anpassen.
        sql = "select ea.meinaus_id, mv.mv_id, " \
              "mv.von, coalesce( mv.bis, '') as bis, mv.mobj_id as objekt, mv.name || ', ' || mv.vorname as name, " \
              "0 as soll, " \
              "'ok' as ok, 'nok' as nok, " \
              "jan, feb, mrz, apr, mai, jun, jul, aug, sep, okt, nov, dez, " \
              "(coalesce(jan,0)+coalesce(feb,0)+coalesce(mrz,0)+coalesce(apr,0)+coalesce(mai,0)+coalesce(jun,0)+" \
              "coalesce(jul,0)+coalesce(aug,0)+coalesce(sep,0)+coalesce(okt,0)+coalesce(nov, 0) + coalesce(dez, 0)) as summe " \
              "from mietverhaeltnis mv " \
              "inner join mtleinaus ea on ea.mv_id = mv.mv_id " \
              "where ea.jahr = %s " \
              "and ea.mv_id > '' " \
              "and (mv.bis = '' or mv.bis is NULL or substr(mv.bis, 0, 5) >= '%s') " \
              "order by mv.mv_id" % (jahr, jahr)
        diclist: List[Dict] = self._doReadAllGetDict( sql )
        return diclist

    def getJahrFromMtlEinAus( self, meinaus_id: int ) -> int:
        sql = "select jahr from mtleinaus where meinaus_id = " + str( meinaus_id )
        l = self._doRead( sql )
        return l[0][0]

    def getMasterUndMietobjekt( self, meinaus_id: int ) -> Dict or None:
        """
        Liest den Satz mit der Id meinaus_id aus der Tabelle mtleinaus.
        Ist die mv_id belegt, werden master_id, master_name und mobj_id aus den Tabellen mietverhaeltnis und mietobjekt ermittelt.
        Ist die vwg_id belegt, werden master_id, master_name und mobj_id aus den Tabellen verwaltung und mietobjekt ermittelt.
        :param meinaus_id:
        :return: einen Dict mit den Keys meinaus_id, mobj_id, master_id, master_name.
                 Zusätzlich: mv_id, wenn die meinaus_id sich auf einen Mietzahlungssatz bezieht bzw.
                             vwg_id, wenn die meinaus_id sich auf einen HGV-Satz bezieht.
        """
        sql = "select meinaus_id, mv_id, vwg_id from mtleinaus where meinaus_id = " + str( meinaus_id )
        d = self._doReadOneGetDict( sql )
        ret: Dict = None
        if d["mv_id"]:
            ret = self.getMasterUndMietobjektFromMietverhaeltnis( d["mv_id"] )
        else:
            ret = self.getMasterUndMietobjektFromVerwaltung( d["vwg_id"] )
        return ret

    def getMasterUndMietobjektFromMietverhaeltnis( self, mv_id: str ) -> Dict:
        sql = "select mv.mv_id, mi.mobj_id, mo.master_id, mo.master_name " \
              "from mietverhaeltnis mv " \
              "inner join mietobjekt mi on mi.mobj_id = mv.mobj_id " \
              "inner join masterobjekt mo on mo.master_id = mi.master_id " \
              "where mv.mv_id = '%s'" % (mv_id)
        return self._doReadOneGetDict( sql )

    def getMasterUndMietobjektFromVerwaltung( self, vwg_id: int ) -> Dict:
        sql = "select vwg.vwg_id, mi.mobj_id, mo.master_id, mo.master_name " \
              "from verwaltung vwg " \
              "inner join mietobjekt mi on mi.mobj_id = vwg.mobj_id " \
              "inner join masterobjekt mo on mo.master_id = mi.master_id " \
              "where vwg.vwg_id = " + str( vwg_id )
        return self._doReadOneGetDict( sql )

    def getVerwalter( self ) -> List[str]:
        sql = "select name from verwalter order by vw_id  "
        tupellist = self._doRead( sql )
        stringlist = [x[0] for x in tupellist]
        return stringlist

    def getVerwaltungen( self, jahr: int, orderby: str = None ) -> List[Dict]:
        vgldat = str( jahr ) + "-01-01"
        sql = "select vwg_id, mobj_id, vw_id, weg_name, von, coalesce( bis, '' ) as bis " \
              "from verwaltung " \
              "where von <= '%s' and (bis is NULL or bis = '' or bis > '%s') " % (vgldat, vgldat)
        if orderby:
            sql += "order by %s" % (orderby)
        diclist: List[Dict] = self._doReadAllGetDict( sql )
        return diclist

    def getHausgeldvorauszahlungenMitSummen( self, jahr: int ) -> List[Dict]:
        # Achtung: das TableModel verlässt sich auf die Reihenfolge der Spalten.
        # Wenn sie geändert wird, muss man das im CheckTableModel.__init()__ anpassen.
        sql = "select ea.meinaus_id, vwg.vwg_id, " \
              "vwg.von, coalesce( vwg.bis, '') as bis, vwg.mobj_id as objekt, vwg.weg_name || ' / ' || vwg.vw_id as name, " \
              "0 as soll, " \
              "'ok' as ok, 'nok' as nok, " \
              "jan, feb, mrz, apr, mai, jun, jul, aug, sep, okt, nov, dez, " \
              "(coalesce(jan,0)+coalesce(feb,0)+coalesce(mrz,0)+coalesce(apr,0)+coalesce(mai,0)+coalesce(jun,0)+" \
              "coalesce(jul,0)+coalesce(aug,0)+coalesce(sep,0)+coalesce(okt,0)+coalesce(nov, 0) + coalesce(dez, 0)) as summe " \
              "from verwaltung vwg " \
              "inner join mtleinaus ea on ea.vwg_id = vwg.vwg_id " \
              "where ea.jahr = %s " \
              "and ea.vwg_id > 0 " \
              "and (vwg.bis = '' or vwg.bis is NULL or substr(vwg.bis, 0, 5) >= '%s') " \
              "order by vwg.weg_name" % (jahr, jahr)
        diclist: List[Dict] = self._doReadAllGetDict( sql )
        return diclist

    def getAktiveSollmiete( self, mv_id: str ) -> XSollMiete:
        """
        Liefert die aktuelle Sollmiete des Mieters mv_id.
        Achtung: das funktioniert nicht, wenn mv_id mehr als 1 Wohnung gemietet hat.
        :param mv_id:
        :return:
        """
        sql = "select sm_id, mv_id, von, coalesce(bis, '') as bis, netto, nkv, coalesce(bemerkung, '') as bemerkung " \
              "from sollmiete " \
              "where mv_id = '%s' " \
              "and ( von <= CURRENT_DATE and bis is NULL or bis = '' or bis > CURRENT_DATE ) " % (mv_id)
        listofdicts = self._doReadAllGetDict( sql )
        if len( listofdicts ) > 1:
            raise Exception( "DbAccess.getAktiveSollmiete( mv_id ):\n more than 1 row for mv_id = '%s' " % (mv_id) )
        elif len( listofdicts ) < 1:
            raise Exception( "DbAccess.getAktiveSollmiete( mv_id ):\n found 0 rows for mv_id = '%s' " % (mv_id) )
        x: XSollMiete = XSollMiete( listofdicts[0] )
        return x

    def getSollmietenMonat( self, jahr: int, monat: int ) -> List[Dict]:
        datum = str( jahr ) + "-" + "%02d" % monat + "-01"
        sql = "select mv_id, von, coalesce(bis, ''), netto, nkv, netto+nkv as brutto " \
              "from sollmiete " \
              "where von <= '%s' " \
              "and (bis is NULL or bis = '' or bis > '%s') " \
              "order by mv_id" % (datum, datum)
        return self._doReadAllGetDict( sql )

    def getSollHausgelderMonat( self, jahr: int, monat: int ) -> List[Dict]:
        datum = str( jahr ) + "-" + "%02d" % monat + "-01"
        sql = "select vwg_id, von, coalesce(bis, '') as bis, netto, ruezufue " \
              "from sollhausgeld " \
              "where von <= '%s' " \
              "and (bis is NULL or bis = '' or bis > '%s') " \
              "order by vwg_id" % (datum, datum)
        return self._doReadAllGetDict( sql )

    def getSollHausgelder( self, mobj_id: str = None, nurAktive: bool = True ) -> List[XSollHausgeld]:
        """
        Liefert Soll-Hausgelder.
        Wenn mobj_id gesetzt ist, werden nur die Hausgelder für mobj_id geliefert.
        Wenn ohneInaktive == True, dann werden nur aktive und zukünftige Hausgeld-Sätze geliefert.
        :return: eine Liste von XHausgeld-Objekten
        """
        sql = "select s.shg_id, v.vw_id, s.vwg_id, s.von, coalesce(s.bis, '') as bis, s.netto, s.ruezufue, " \
              "(s.netto + s.ruezufue) as brutto, " \
              "v.mobj_id, v.weg_name,  coalesce(s.bemerkung, '') as bemerkung " \
              "from sollhausgeld s " \
              "inner join verwaltung v on v.vwg_id = s.vwg_id "
        nextKeyword = "where "
        if mobj_id:
            sql += ("where v.mobj_id = '%s' " % (mobj_id))
            nextKeyword = "and "
        if nurAktive:
            sql += nextKeyword
            sql += "(s.bis is NULL or s.bis = '' or s.bis >= CURRENT_DATE) "
        sql += "order by v.weg_name, s.von desc"
        l: List[Dict] = self._doReadAllGetDict( sql )
        sollList: List[XSollHausgeld] = list()
        for d in l:
            x = XSollHausgeld( d )
            sollList.append( x )
        return sollList

    def getSollHausgelder2( self, startjahr: int ) -> List[XSollHausgeld]:
        """
        Liefert Soll-Hausgelder, die ab startjahr gültig waren/sind.
        :return: eine Liste von XHausgeld-Objekten
        """
        minbis = "%d-%02d-%02d" % (startjahr, 1, 1)
        sql = "select s.shg_id, v.vw_id, s.vwg_id, s.von, coalesce(s.bis, '') as bis, s.netto, s.ruezufue, " \
              "(s.netto + s.ruezufue) as brutto, " \
              "v.mobj_id, v.weg_name,  coalesce(s.bemerkung, '') as bemerkung " \
              "from sollhausgeld s " \
              "inner join verwaltung v on v.vwg_id = s.vwg_id " \
              "where (s.bis is NULL or s.bis = '' or s.bis >= '%s') " \
              "order by v.weg_name, s.von desc" % (minbis)
        l: List[Dict] = self._doReadAllGetDict( sql )
        sollList: List[XSollHausgeld] = list()
        for d in l:
            x = XSollHausgeld( d )
            sollList.append( x )
        return sollList

    def getSollmieten( self, mv_id: str = None, nurAktive: bool = True ) -> List[XSollMiete]:
        sql = "select sm.sm_id, sm.mv_id, sm.von, coalesce(sm.bis, '') as bis, sm.netto, sm.nkv, (sm.netto + sm.nkv) as brutto, " \
              "coalesce(sm.bemerkung, '') as bemerkung, mv.mobj_id " \
              "from sollmiete sm " \
              "inner join mietverhaeltnis mv on mv.mv_id = sm.mv_id "
        nextKeyword = "where "
        if mv_id:
            sql += ("where sm.mv_id = '%s' " % (mv_id))
            nextKeyword = "and "
        if nurAktive:
            sql += nextKeyword
            sql += "(sm.bis is NULL or sm.bis = '' or sm.bis >= CURRENT_DATE) "
        sql += "order by sm.mv_id, sm.von desc"
        l: List[Dict] = self._doReadAllGetDict( sql )
        sollList: List[XSollMiete] = list()
        for d in l:
            x = XSollMiete( d )
            sollList.append( x )
        return sollList

    def getSollmieten2( self, startjahr: int ) -> List[XSollMiete]:
        minbis = "%d-%02d-%02d" % (startjahr, 1, 1)
        sql = "select sm.sm_id, sm.mv_id, sm.von, coalesce(sm.bis, '') as bis, sm.netto, sm.nkv, (sm.netto + sm.nkv) as brutto, " \
              "coalesce(sm.bemerkung, '') as bemerkung, mv.mobj_id " \
              "from sollmiete sm " \
              "inner join mietverhaeltnis mv on mv.mv_id = sm.mv_id " \
              "where (sm.bis is NULL or sm.bis = '' or sm.bis >= '%s') " \
              "order by sm.mv_id, sm.von desc" % (minbis)
        l: List[Dict] = self._doReadAllGetDict( sql )
        sollList: List[XSollMiete] = list()
        for d in l:
            x = XSollMiete( d )
            sollList.append( x )
        return sollList

    def getZahlungen2( self, jahr: int, master_id: int, pos_or_neg:str="<" ) -> List[XZahlung3]:
        """
        Liefert Ein- oder Auszahlungen aus Tabelle zahlung für ein bestimmtes Jahr und ein bestimmtes Masterobjekt.
        :param jahr:
        :param master_id:
        :param pos_or_neg:  "<" für Auszahlungen, ">" für Einzahlungen
        :return:
        """
        sql = "select z.mobj_id, z.betrag, z.zahl_art, s.kostenart, s.kreditor, s.buchungsdatum, s.buchungstext " \
            "from zahlung z " \
            "left outer join sonstaus s on s.saus_id = z.saus_id " \
            "where z.betrag %s 0 " \
            "and z.jahr = %d " \
            "and z.master_id = %d " \
            "order by z.zahl_art, s.kostenart, z.mobj_id " % (pos_or_neg, jahr, master_id)
        l: List[Dict] = self._doReadAllGetDict( sql )
        zList: List[XZahlung3] = list()
        for d in l:
            x = XZahlung3( d )
            zList.append( x )
        return zList

    def getSonstigeAusgaben( self, jahr: int, master_id: int = None, kostenart: str = None ) -> List[XSonstAus]:
        """
        Liest alle Einträge der Tabelle sonstaus für buchungsjahr <jahr>
        :param jahr: gewünschtes Buchungsjahr
        :return:
        """
        sql = "select saus_id, m.master_id, m.master_name, mobj_id, kostenart, " \
              "kreditor, rgnr, betrag, rgdatum, rgtext, buchungsdatum, buchungsjahr, umlegbar, werterhaltend, buchungstext " \
              "from sonstaus s " \
              "inner join masterobjekt m on m.master_id = s.master_id " \
              "where buchungsjahr = %d " % (jahr)
        if master_id:
            sql += "and s.master_id = %d " % (master_id)
        if kostenart:
            sql += "and s.kostenart = '%s' " % (kostenart)
        dictlist = self._doReadAllGetDict( sql )
        sonstalist = []
        for d in dictlist:
            x = XSonstAus( d )
            sonstalist.append( x )

        return sonstalist

    def getSummeSonstigeAusgaben( self, jahr: int, master_id: int, kostenart: str ):
        sql = "select sum(betrag) as summe " \
              "from sonstaus s " \
              "inner join masterobjekt m on m.master_id = s.master_id " \
              "where buchungsjahr = %d " \
              "and s.master_id = %d " \
              "and s.kostenart = '%s' " % (jahr, master_id, kostenart)
        lst = self._doRead( sql )
        summe = lst[0][0]
        return 0.0 if summe is None else summe

    def getSummeZahlungen( self, zahl_art: str ) -> float:
        sql = "select sum( betrag ) from zahlung where zahl_art = '%s'" % (zahl_art)
        lst = self._doRead( sql )
        sum = lst[0][0]
        return 0.0 if sum is None else sum

    def getZahlung( self, id: int, id_name: str ) -> XZahlung:
        sql = "select z_id, master_id, mobj_id, meinaus_id, saus_id, nka_id, hga_id, write_time, jahr, monat, betrag, zahl_art " \
              "from zahlung " \
              "where %s = %d " % (id_name, id)
        d = self._doReadOneGetDict( sql )
        x = XZahlung()
        if d:
            x.z_id = d["z_id"]
            x.master_id = d["master_id"]
            x.mobj_id = d["mobj_id"]
            x.meinaus_id = d["meinaus_id"]
            x.saus_id = d["saus_id"]
            x.nka_id = d["nka_id"]
            x.hga_id = d["hga_id"]
            x.write_time = d["write_time"]
            x.jahr = d["jahr"]
            x.monat = d["monat"]
            x.betrag = d["betrag"]
            x.zahl_art = d["zahl_art"]
        return x

    def getZahlungen( self, jahr: int, master_name: str = None ) -> List[XZahlung2]:
        sql = "select master.master_name, mobj.mobj_id, z.z_id, z.meinaus_id, z.saus_id, z.nka_id, z.hga_id, z.betrag, " \
              "z.zahl_art, z.jahr, coalesce( mobj.qm, 0 ) as qm, coalesce( master.gesamt_wfl, 0 ) as gesamt_wfl, " \
              "coalesce( master.afa, 0 ) as afa " \
              "from zahlung z  inner join mietobjekt mobj on mobj.mobj_id = z.mobj_id " \
              "inner join masterobjekt master on master.master_id = mobj.master_id " \
              "where jahr = %d " % (jahr)
        if master_name:
            sql += ("and master.master_name = '%s' order by master.master_name, mobj.mobj_id, z.zahl_art " % (
                master_name))
        else:
            sql += "and master.master_name not like '%*%' "
            sql += "order by master.master_name, z.zahl_art "
        dictlist = self._doReadAllGetDict( sql )
        zlist = []
        for d in dictlist:
            x = XZahlung2( d )
            zlist.append( x )
        return zlist

    def getJahre( self, eaart: einausart ) -> List[int]:
        id = "mv_id" if eaart == einausart.MIETE else "vwg_art"
        sql = "select distinct jahr from mtleinaus where %s > 0 order by jahr desc " % (id)
        rowlist = self._doRead( sql )
        list = [x[0] for x in rowlist]
        return list

    def getAlleMieter( self ) -> List[str]:
        sql = "select distinct mv_id " \
              "from mietverhaeltnis "
        rowlist = self._doRead( sql )
        li = [x[0] for x in rowlist]
        li = sorted( li, key=str.casefold )
        return li

    def getKreditoren( self, master_name: str ) -> List[str]:
        sql = "select distinct kreditor " \
              "from kreditorleistung k " \
              "inner join masterobjekt m on m.master_id = k.master_id " \
              "where m.master_name = '%s' " % (master_name)
        rowlist = self._doRead( sql )
        li = [x[0] for x in rowlist]
        li = sorted( li, key=str.casefold )
        return li

    def getAlleKreditoren( self ) -> List[str]:
        sql = "select distinct kreditor from kreditorleistung "
        rowlist = self._doRead( sql )
        li = [x[0] for x in rowlist]
        li = sorted( li, key=str.casefold )
        return li

    def getKreditorleistungen( self ) -> List[Dict]:
        sql = "select distinct k.kreditor, k.master_id, m.master_name, k.mobj_id, buchungstext, umlegbar " \
              "from kreditorleistung k " \
              "inner join masterobjekt m on m.master_id = k.master_id "
        dictlist = self._doReadAllGetDict( sql )
        dictlist = sorted( dictlist, key=lambda x: (
        x["master_name"].lower(), x["kreditor"].lower(), x["mobj_id"].lower(), x["buchungstext"]) )
        return dictlist

    def existsKreditorleistung( self, master_id: int, mobj_id: str, kreditor: str, buchungstext: str ) -> bool:
        sql = "select count(*) from kreditorleistung " \
              "where master_id = %d " % (master_id)
        if mobj_id:
            sql += " and mobj_id = '" + mobj_id + "' "
        sql += " and kreditor = '%s' " \
               "and buchungstext = '%s' " % (kreditor, buchungstext)
        tuplelist = self._doRead( sql )
        n = tuplelist[0][0]
        return n

    def getBuchungstexte( self, kreditor: str ) -> List[str]:
        sql = "select buchungstext from kreditorleistung where kreditor = '%s' " % (kreditor)
        rowlist = self._doRead( sql )
        list = [x[0] for x in rowlist]
        list = sorted( list, key=str.casefold )
        return list

    def getBuchungstexteFuerMasterobjekt( self, master_name: str, kreditor: str ) -> List[str]:
        sql = "select buchungstext " \
              "from kreditorleistung k " \
              "inner join masterobjekt m on m.master_id = k.master_id " \
              "where k.kreditor = '%s' " \
              "and m.master_name = '%s' " % (kreditor, master_name)
        rowlist = self._doRead( sql )
        list = [x[0] for x in rowlist]
        list = sorted( list, key=str.casefold )
        return list

    def getBuchungstexteFuerMietobjekt( self, mobj_id: str, kreditor: str ) -> List[str]:
        sql = "select buchungstext " \
              "from kreditorleistung k " \
              "where k.kreditor = '%s' " \
              "and k.mobj_id = '%s' " % (kreditor, mobj_id)
        rowlist = self._doRead( sql )
        list = [x[0] for x in rowlist]
        list = sorted( list, key=str.casefold )
        return list

    def getMasterobjekte( self ) -> List[Dict]:
        sql = "select master_id, master_name " \
              "from masterobjekt " \
              "order by master_name "
        dictlist = self._doReadAllGetDict( sql )
        return dictlist

    def getMasterId( self, master_name: str ) -> int:
        sql = "select master_id from masterobjekt where master_name = '%s' " % (master_name)
        r: List[Tuple] = self._doRead( sql )
        try:
            return r[0][0]
        except:
            return -1

    def getMasterIdFromMietobjekt( self, mobj_id: str ) -> int:
        sql = "select master_id from mietobjekt where mobj_id = '%s' " % (mobj_id)
        res = self._doRead( sql )
        return int( res[0][0] )

    def getExistingNkAbrechnungsjahre( self ) -> List[int]:
        sql = "select distinct ab_jahr from nk_abrechnung order by ab_jahr desc;"
        tuplelist = self._doRead( sql )
        li = [x[0] for x in tuplelist]
        return li

    def getNkAbrechnungen( self, ab_jahr: int ) -> List[XNkAbrechnung]:
        """
        get all records of table nk_abrechnung concerning the given year
        :param ab_jahr: e.g. 2020
        :return:
        """
        sql = "select nka_id, nka.mv_id, mobj_id, mv.von, coalesce(mv.bis, '') as bis, ab_jahr, " \
              "betrag, ab_datum, coalesce(buchungsdatum, '') as buchungsdatum, coalesce(nka.bemerkung, '') as bemerkung " \
              "from nk_abrechnung nka " \
              "inner join mietverhaeltnis mv on mv.mv_id = nka.mv_id " \
              "where ab_jahr = %d " \
              "order by mobj_id" % (ab_jahr)
        dictlist = self._doReadAllGetDict( sql )
        xlist: List[XNkAbrechnung] = list()
        for d in dictlist:
            x = XNkAbrechnung()
            x.nka_id = d["nka_id"]
            x.mv_id = d["mv_id"]
            x.mobj_id = d["mobj_id"]
            x.von = d["von"]
            x.bis = d["bis"]
            x.ab_jahr = d["ab_jahr"]
            x.betrag = d["betrag"]
            x.ab_datum = d["ab_datum"]
            x.buchungsdatum = d["buchungsdatum"]
            x.bemerkung = d["bemerkung"]
            xlist.append( x )
        return xlist

    def getExistingHgAbrechnungsjahre( self ) -> List[int]:
        sql = "select distinct ab_jahr from hg_abrechnung order by ab_jahr desc;"
        tuplelist = self._doRead( sql )
        li = [x[0] for x in tuplelist]
        return li

    def getHgAbrechnungen( self, ab_jahr: int ) -> List[XHgAbrechnung]:
        """
        get all records of table hg_abrechnung concerning the given year
        :param ab_jahr: e.g. 2020
        :return:
        """
        sql = "select hga_id, hga.vwg_id, vw.vw_id, vwg.mobj_id, vwg.weg_name, vwg.von, coalesce(vwg.bis, '') as bis, ab_jahr, " \
              "betrag, ab_datum, coalesce(buchungsdatum, '') as buchungsdatum, coalesce(hga.bemerkung, '') as bemerkung " \
              "from hg_abrechnung hga " \
              "inner join verwaltung vwg on vwg.vwg_id = hga.vwg_id " \
              "inner join verwalter vw on vw.vw_id = vwg.vw_id " \
              "where ab_jahr = %d " \
              "order by mobj_id" % (ab_jahr)
        dictlist = self._doReadAllGetDict( sql )
        xlist: List[XHgAbrechnung] = list()
        for d in dictlist:
            x = XHgAbrechnung()
            x.hga_id = d["hga_id"]
            x.vwg_id = d["vwg_id"]
            x.weg_name_vw_id = d["weg_name"] + " / " + d["vw_id"]
            x.mobj_id = d["mobj_id"]
            x.von = d["von"]
            x.bis = d["bis"]
            x.ab_jahr = d["ab_jahr"]
            x.betrag = d["betrag"]
            x.ab_datum = d["ab_datum"]
            x.buchungsdatum = d["buchungsdatum"]
            x.bemerkung = d["bemerkung"]
            xlist.append( x )
        return xlist

    def getOffenePosten( self ) -> List[XOffenerPosten]:
        sql = "select opos_id, debi_kredi, erfasst_am, betrag, " \
              "betrag_beglichen, letzte_buchung_am, bemerkung " \
              "from opos "
        dictlist = self._doReadAllGetDict( sql )
        xlist: List[XOffenerPosten] = list()
        for d in dictlist:
            x = XOffenerPosten( d )
            xlist.append( x )
        return xlist

    def getNotizen( self, auch_erledigte: bool = False ) -> List[XNotiz]:
        sql = "select notiz_id, bezug, ueberschrift, text, erfasst_am, erledigt, lwa " \
              "from notiz "
        if auch_erledigte:  # nur aktive
            sql += "where erledigt in (0, 1)"
        else:
            sql += "where erledigt = 0"
        dictlist = self._doReadAllGetDict( sql )
        xlist: List[XNotiz] = list()
        for d in dictlist:
            x = XNotiz( d )
            xlist.append( x )
        return xlist

    def getDetailFromSammelabgabe( self, master_name: str, jahr: int ) -> XSammelAbgabeDetail or None:
        sql = "select master.master_name, " \
              "sd.master_id, sd.grundsteuer, sd.abwasser, sd.strassenreinigung " \
              "from sammelabgabe_detail sd " \
              "inner join masterobjekt master on master.master_id = sd.master_id " \
              "where master.master_name = '%s' " \
              "and jahr = %d " % (master_name, jahr)
        d = self._doReadOneGetDict( sql )
        if d:
            x = XSammelAbgabeDetail( d )
            return x
        return None

    def insertMietobjekt( self, d: Dict, commit: bool = True ) -> int:
        sql = "insert into mietobjekt " \
              "(mobj_id, master_id, whg_bez, qm, container_nr, bemerkung, aktiv) " \
              "values " \
              "('%s', %d, '%s', %d, '%s', '%s', %d) " % \
              (d["mobj_id"], d["master_id"], d["whg_bez"], d["qm"], d["container_nr"], d["bemerkung"], d["aktiv"])
        return self._doWrite( sql, commit )

    # def insertMietverhaeltnis( self, d: Dict, commit: bool = True ) -> int:
    #     sql = "insert into mietverhaeltnis " \
    #           "(mv_id, mobj_id, von, bis, name, vorname, telefon, mobil, mailto, anzahl_pers, IBAN, bemerkung1, bemerkung2) " \
    #           "values " \
    #           "('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %d, '%s', '%s', '%s') " % \
    #           (d["mv_id"], d["mobj_id"], d["von"], d["bis"], d["name"], d["vorname"], "", d["mobil"], d["mailto"],
    #            d["anzahl_pers"],
    #            d["IBAN"], d["bemerkung1"], d["bemerkung2"])
    #     return self._doWrite( sql, commit )

    def insertMietverhaeltnis( self, x:XMietverhaeltnis, commit:bool=True ) -> int:
        sql = "insert into mietverhaeltnis " \
              "(mv_id, mobj_id, von, bis, name, vorname, name2, vorname2, telefon, mobil, mailto, anzahl_pers, " \
              "IBAN, kaution, kaution_bezahlt_am, bemerkung1, bemerkung2) " \
              "values " \
              "('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %d, " \
              "'%s', %d, '%s', '%s', '%s') " % \
              ( x.mv_id, x.mobj_id, x.von, x.bis, x.name, x.vorname, x.name2, x.vorname2, x.telefon, x.mobil, x.mailto,
               x.anzahl_pers, x.IBAN, x.kaution, x.kaution_bezahlt_am, x.bemerkung1, x.bemerkung2 )
        return self._doWrite( sql, commit )

    def insertSollmiete( self, x: XSollMiete, commit: bool = True ) -> int:
        bis = "NULL" if not x.bis else "'" + x.bis + "'"
        sql = "insert into sollmiete " \
              "(mv_id, von, bis, netto, nkv, bemerkung ) " \
              "values( '%s', '%s', %s, %.2f, %.2f, '%s' ) " % (x.mv_id, x.von, bis, x.netto, x.nkv, x.bemerkung)
        return self._doWrite( sql, commit )

    def insertSollHausgeld( self, x: XSollHausgeld, commit: bool = True ) -> int:
        bis = "NULL" if not x.bis else "'" + x.bis + "'"
        sql = "insert into sollhausgeld " \
              "(vwg_id, von, bis, netto, ruezufue, bemerkung) " \
              "values( '%s', '%s', %s, %.2f, %.2f, '%s' ) " % (x.vwg_id, x.von, bis, x.netto, x.ruezufue, x.bemerkung)
        return self._doWrite( sql, commit )

    def updateSollHausgeld( self, x: XSollHausgeld, commit: bool = True ) -> int:
        bis = "NULL" if not x.bis else "'" + x.bis + "'"
        sql = "update sollhausgeld " \
              "set " \
              "von = '%s', " \
              "bis = %s, " \
              "netto = %.2f, " \
              "ruezufue = %.2f, " \
              "bemerkung = '%s' " \
              "where shg_id = %d " % (x.von, bis, x.netto, x.ruezufue, x.bemerkung, x.shg_id)
        return self._doWrite( sql, commit )

    def updateSollmiete( self, x: XSollMiete, commit: bool = True ):
        bis = "NULL" if not x.bis else "'" + x.bis + "'"
        sql = "update sollmiete set " \
              "mv_id = '%s', " \
              "von = '%s', " \
              "bis = %s, " \
              "netto = %.2f, " \
              "nkv = %.2f, " \
              "bemerkung = '%s' " \
              "where sm_id = %d" % (x.mv_id, x.von, bis, x.netto, x.nkv, x.bemerkung, x.sm_id)
        return self._doWrite( sql, commit )

    def insertKreditorleistung( self, master_id: int, mobj_id: str, kreditor: str, buchungstext: str, umlegbar: int = 0,
                                commit: bool = True ):
        if buchungstext is None: buchungstext = ""
        if mobj_id is None: mobj_id = ""
        sql = "insert into kreditorleistung " \
              "(kreditor, master_id, mobj_id, buchungstext, umlegbar) " \
              "values" \
              "('%s', %d, '%s', '%s', %d) " % (kreditor, master_id, mobj_id, buchungstext, umlegbar)
        return self._doWrite( sql, commit )

    def existsEinAusArt( self, eaart: einausart, jahr: int ) -> bool:
        id = "mv_id" if eaart == einausart.MIETE else "vwg_id"
        sql = "select count(*) as anz from mtleinaus where jahr = %d and %s is not null" % (jahr, id)
        d = self._doReadOneGetDict( sql )
        return d["anz"] > 0

    def insertMtlEinAus( self, mv_or_vwg_id: str, eaart: einausart, jahr: int, commit: bool = True ) -> int:
        """
        legt einen Satz in der Tabelle mtleinaus an, wobei alle Monatswerte auf 0 gesetzt werden
        :param mv_or_vwg_id: je nach einausart ist das die mv_id oder die vwg_id
        :param eaart: "miete" oder "hgv"
        :param jahr:
        :param commit:
        :return:
        """
        id = "mv_id" if eaart == einausart.MIETE else "vwg_id"
        sql = "insert into mtleinaus (%s, jahr) values ('%s', %d) " % (id, mv_or_vwg_id, jahr)
        return self._doWrite( sql, commit )

    def insertSonstAus( self, x: XSonstAus, commit: bool = True ) -> int:
        master_id = "NULL" if x.master_id is None else str( x.master_id )
        sql = "insert into sonstaus " \
              "(master_id, mobj_id, buchungsjahr, buchungsdatum, kreditor, rgnr, betrag, rgdatum, rgtext, umlegbar, werterhaltend, buchungstext) " \
              "values " \
              "(%s, '%s', %d, '%s', '%s', '%s', %.2f, '%s', '%s', %d, %d, '%s') " \
              % (
              master_id, x.mobj_id, x.buchungsjahr, x.buchungsdatum, x.kreditor, x.rgnr, x.betrag, x.rgdatum, x.rgtext,
              x.umlegbar, x.werterhaltend, x.buchungstext)
        return self._doWrite( sql, commit )

    def updateSonstAus( self, x: XSonstAus, commit: bool = True ):
        sql = "update sonstaus set " \
              "master_id = %d, " \
              "mobj_id = '%s', " \
              "kreditor = '%s', " \
              "rgnr = '%s', " \
              "rgdatum = '%s', " \
              "rgtext = '%s', " \
              "betrag = %.2f, " \
              "umlegbar = %d, " \
              "werterhaltend = %d, " \
              "buchungsdatum = '%s', " \
              "buchungsjahr = %d, " \
              "buchungstext = '%s' " \
              "where saus_id = %d " % (x.master_id,
                                       x.mobj_id,
                                       x.kreditor,
                                       x.rgnr,
                                       x.rgdatum,
                                       x.rgtext,
                                       x.betrag,
                                       x.umlegbar,
                                       x.werterhaltend,
                                       x.buchungsdatum,
                                       x.buchungsjahr,
                                       x.buchungstext,
                                       x.saus_id)
        return self._doWrite( sql, commit )

    def deleteSonstAus( self, saus_id: int, commit: bool = True ) -> int:
        sql = "delete from sonstaus where saus_id = %d; " % (saus_id)
        return self._doWrite( sql, commit )

    def insertVerwalter( self, d: Dict, commit: bool = True ) -> int:
        sql = "insert into verwalter " \
              "(vw_id, name, strasse, plz_ort, telefon_1, telefon_2, mailto, ansprechpartner_1, ansprechpartner_2, bemerkung)" \
              "values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s' )" \
              % (d["vw_id"], d["name"], d["strasse"], d["plz_ort"], d["telefon_1"], d["telefon_2"], d["mailto"],
                 d["ansprechpartner_1"], d["ansprechpartner_2"], d["bemerkung"])
        return self._doWrite( sql, commit )

    def insertVerwaltung( self, d: Dict, commit: bool = True ) -> int:
        sql = "insert into verwaltung " \
              "(mobj_id, vw_id, weg_name, von, bis) " \
              "values " \
              "('%s', '%s', '%s', '%s', '%s')" % \
              (d["mobj_id"], d["vw_id"], d["weg_name"], d["von"], d["bis"])
        return self._doWrite( sql, commit )

    def insertZahlung( self, z: XZahlung, commit: bool = True ) -> int:
        master_id = "NULL" if z.master_id is None else str( z.master_id )
        sql = "insert into zahlung " \
              "(master_id, mobj_id, meinaus_id, saus_id, nka_id, hga_id, write_time, jahr, monat, betrag, zahl_art) " \
              "values " \
              "(%s, '%s', %d, %d, %d, %d, '%s', %d, '%s', %.2f, '%s') " % \
              (master_id, z.mobj_id, z.meinaus_id, z.saus_id, z.nka_id, z.hga_id, z.write_time, z.jahr, z.monat,
               z.betrag, z.zahl_art)
        return self._doWrite( sql, commit )

    def deleteZahlung( self, id: int, id_name: str, monat: str = None, zahl_art: str = None,
                       commit: bool = True ) -> int:
        sql = "delete from zahlung " \
              "where %s = %d " % (id_name, id)
        if monat:
            sql += " and monat = '%s' " % (monat)
        if zahl_art:
            sql += " and zahl_art = '%s' " % (zahl_art)
        return self._doWrite( sql, commit )

    def updateZahlung( self, id: int, id_name: str, z: XZahlung, commit: bool = True ):
        sql = "update zahlung " \
              "set master_id = %d, " \
              "mobj_id = '%s', " \
              "write_time = '%s', " \
              "jahr = %d, " \
              "monat = '%s', " \
              "betrag = %.2f " \
              "where %s = %d " % (z.master_id, z.mobj_id, z.write_time, z.jahr, z.monat, z.betrag, id_name, id)
        return self._doWrite( sql, commit )

    def updateMtlEinAus( self, meinaus_id: int, monat: int or str, value: float, commit: bool = True ) -> int:
        """
        Ändert einen Monatswert in der Tabelle mtleinaus
        :param meinaus_id: identifz. den mtleinaus-Satz, damit auch das Jahr, egal ob Miete oder HGV
        :param monat: identifiziert den Monat: 1 -> Januar, ..., 12 -> Dezember oder als string "jan",..."dez"
        :param value: der Wert, der im betreffenden Monat eingetragen werden soll
        :return:
        """
        dbval = "%.2f" % (value) if value != 0 else "NULL"  # value ist bei Mieten > 0, bei HGV < 0
        sMonat = mon_dbnames[monat - 1] if isinstance( monat, int ) else monat
        sql = "update mtleinaus set '%s' = %s where meinaus_id = %d  " % (sMonat, dbval, meinaus_id)
        return self._doWrite( sql, commit )

    def updateMietverhaeltnis( self, x: XMietverhaeltnis, commit: bool = True ) -> int:
        """
        macht einen Update mit den in x enthaltenen Daten
        auf einen durch x.id spezifizierten Satz in der Tabelle mietverhaeltnis.
        ******* ACHTUNG **********
        Wenn ein Update auf mv_id gemacht wird, müssen auch die entsprechenden Werte
        in den Tabellen mtleinaus, nk_abrechnung, sollmiete geändert werden!
        ******** ACHTUNG ENDE ****
        :param x:
        :param commit:
        :return:
        """
        sql = "update mietverhaeltnis set " \
              "mv_id = '%s', " \
              "von = '%s', " \
              "bis = '%s', " \
              "name = '%s', " \
              "vorname = '%s', " \
              "name2 = '%s', " \
              "vorname2 = '%s', " \
              "telefon = '%s', " \
              "mobil = '%s', " \
              "mailto = '%s', " \
              "anzahl_pers = %d, " \
              "bemerkung1 = '%s', " \
              "bemerkung2 = '%s', " \
              "kaution = %d, " \
              "kaution_bezahlt_am = '%s' " \
              "where id = %d " % (x.mv_id, x.von, x.bis, x.name, x.vorname, x.name2, x.vorname2, x.telefon, x.mobil, x.mailto,
                                  x.anzahl_pers, x.bemerkung1, x.bemerkung2, x.kaution, x.kaution_bezahlt_am, x.id)
        return self._doWrite( sql, commit )

    def updateMietverhaeltnis2( self, id: int, column: str, newVal: str, commit: bool = True ):
        sql = "update mietverhaeltnis set %s = '%s' where id = %d " % (column, newVal, id)
        return self._doWrite( sql, commit )

    def insertNkAbrechnung( self, x: XNkAbrechnung, commit: bool = True ) -> int:
        sql = "insert into nk_abrechnung " \
              "(ab_jahr, mv_id, betrag, ab_datum, buchungsdatum, bemerkung) " \
              "values" \
              "(%d,      '%s',   %.2f,     '%s',   '%s',          '%s')" % \
              (x.ab_jahr, x.mv_id, x.betrag, x.ab_datum, x.buchungsdatum, x.bemerkung)
        return self._doWrite( sql, commit )

    def updateNkAbrechnung( self, x: XNkAbrechnung, commit: bool = True ) -> int:
        sql = "update nk_abrechnung " \
              "set ab_jahr = %d, " \
              "mv_id = '%s', " \
              "betrag = %.2f, " \
              "ab_datum = '%s', " \
              "buchungsdatum = '%s', " \
              "bemerkung = '%s' " \
              "where nka_id = %d" % \
              (x.ab_jahr, x.mv_id, x.betrag, x.ab_datum, x.buchungsdatum, x.bemerkung, x.nka_id)
        return self._doWrite( sql, commit )

    def deleteNkAbrechnung( self, nka_id: int, commit: bool = True ) -> int:
        sql = "delete from nk_abrechnung " \
              "where nka_id = %d" % (nka_id)
        return self._doWrite( sql, commit )

    def insertHgAbrechnung( self, x: XHgAbrechnung, commit: bool = True ) -> int:
        sql = "insert into hg_abrechnung " \
              "(ab_jahr, vwg_id, betrag, ab_datum, buchungsdatum, bemerkung) " \
              "values" \
              "(%d,      %d,   %.2f,     '%s',   '%s',          '%s')" % \
              (x.ab_jahr, x.vwg_id, x.betrag, x.ab_datum, x.buchungsdatum, x.bemerkung)
        return self._doWrite( sql, commit )

    def updateHgAbrechnung( self, x: XHgAbrechnung, commit: bool = True ) -> int:
        sql = "update hg_abrechnung " \
              "set ab_jahr = %d, " \
              "vwg_id = %d, " \
              "betrag = %.2f, " \
              "ab_datum = '%s', " \
              "buchungsdatum = '%s', " \
              "bemerkung = '%s' " \
              "where hga_id = %d" % \
              (x.ab_jahr, x.vwg_id, x.betrag, x.ab_datum, x.buchungsdatum, x.bemerkung, x.hga_id)
        return self._doWrite( sql, commit )

    def deleteHgAbrechnung( self, hga_id: int, commit: bool = True ) -> int:
        sql = "delete from hg_abrechnung " \
              "where hga_id = %d" % (hga_id)
        return self._doWrite( sql, commit )

    def insertOpos( self, x: XOffenerPosten, commit: bool = True ) -> int:
        letzte_buchung = "NULL" if (x.letzte_buchung_am is None or x.letzte_buchung_am == "") else \
            "'" + x.letzte_buchung_am + "'"
        bemerkung = "NULL" if x.bemerkung in (None, "") else "'" + x.bemerkung + "'"
        sql = "insert into opos " \
              "(debi_kredi, erfasst_am, betrag, betrag_beglichen, letzte_buchung_am, bemerkung) " \
              "values " \
              "('%s', '%s', %.2f, %.2f, %s, %s) " % \
              (x.debi_kredi, x.erfasst_am, x.betrag, x.betrag_beglichen, letzte_buchung, bemerkung)
        return self._doWrite( sql, commit )

    def updateOpos( self, x: XOffenerPosten, commit: bool = True ) -> int:
        letzte_buchung = "NULL" if (x.letzte_buchung_am is None or x.letzte_buchung_am == "") else \
            "'" + x.letzte_buchung_am + "'"
        bemerkung = "NULL" if x.bemerkung in (None, "") else "'" + x.bemerkung + "'"
        sql = "update opos set " \
              "debi_kredi = '%s', " \
              "erfasst_am = '%s', " \
              "betrag = %.2f, " \
              "betrag_beglichen = %.2f, " \
              "letzte_buchung_am = %s, " \
              "bemerkung = %s " \
              "where opos_id = %d " % \
              (x.debi_kredi, x.erfasst_am, x.betrag, x.betrag_beglichen, letzte_buchung, bemerkung, x.opos_id)
        return self._doWrite( sql, commit )

    def deleteOpos( self, opos_id: int, commit: bool = True ) -> int:
        sql = "delete from opos " \
              "where opos_id = %d" % (opos_id)
        return self._doWrite( sql, commit )

    def insertNotiz( self, x: XNotiz, commit: bool = True ) -> int:
        erledigt = 0 if x.erledigt == False else 1
        lwa = getCurrentTimestampIso()
        sql = "insert into notiz " \
              "(bezug, ueberschrift, text, erfasst_am, erledigt, lwa) " \
              "values" \
              "('%s', '%s', '%s', '%s', %d, '%s')" % (x.bezug, x.ueberschrift, x.text, x.erfasst_am, erledigt, lwa)
        return self._doWrite( sql, commit )

    def updateNotiz( self, x: XNotiz, commit: bool = True ) -> int:
        erledigt = 0 if x.erledigt == False else 1
        lwa = getCurrentTimestampIso()
        sql = "update notiz " \
              "set bezug = '%s', " \
              "ueberschrift = '%s', " \
              "text = '%s', " \
              "erledigt = %d, " \
              "lwa = '%s' " \
              "where notiz_id = %d " % (x.bezug, x.ueberschrift, x.text, erledigt, lwa, x.notiz_id)
        return self._doWrite( sql, commit )

    def deleteNotiz( self, notiz_id: int, commit: bool = True ) -> int:
        sql = "delete from notiz " \
              "where notiz_id = %d" % (notiz_id)
        return self._doWrite( sql, commit )

    #########################################################################################

    def createObjektKonto( self, konto_name: str, commit: bool = True ) -> None:
        ddl = """CREATE TABLE %s (
            "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            "z_id"	INTEGER NOT NULL,
            "lwa"	TEXT NOT NULL,
            "forderungsdatum" TEXT,
            "buchungsdatum"	TEXT,
            "monat"	INTEGER NOT NULL,
            "jahr"	INTEGER NOT NULL,
            "betrag"	REAL NOT NULL,
            "art"	TEXT NOT NULL,
            "beschreibung"	TEXT
        )""" % (konto_name)
        self._doWrite( ddl, commit )

    def _doRead( self, sql: str ) -> List[Tuple]:
        self._cursor.execute( sql )
        records = self._cursor.fetchall()
        return records

    def dict_factory( self, cursor, row ):
        d = { }
        for idx, col in enumerate( cursor.description ):
            d[col[0]] = row[idx]
        return d

    def _doReadOneGetDict( self, sql: str ) -> Dict or None:
        self._con.row_factory = self.dict_factory
        cur = self._con.cursor()
        cur.execute( sql )
        return cur.fetchone()

    def _doReadAllGetDict( self, sql: str ) -> Dict or None:
        self._con.row_factory = self.dict_factory
        cur = self._con.cursor()
        cur.execute( sql )
        return cur.fetchall()

    def _doWrite( self, sql: str, commit: bool ) -> int:
        c = self._cursor.execute( sql )
        if commit:
            self._con.commit()
        return c.rowcount


# =============================================================================
# crsr.execute("CREATE TABLE employees( \
#                  id integer PRIMARY KEY, \
#                  name text, \
#                  salary real, \
#                  department text, \
#                  position text, \
#                  hireDate text)")
#
# con.commit()
# =============================================================================

def test():
    db = DbAccess( "immo.db" )
    db.open()
    mobj_id = db.getMietobjektZuMietverhaeltnis( "lander_ank" )
    d = db.getAktuellesMietverhaeltnisVonBis( "lander_anke" )
    x = db.getAktuellesMietverhaeltnis( "lander_anke" )
    #zlist = db.getZahlungen( 2021, "SB_Charlotte" )

    print( "" )
    db.close()


if __name__ == '__main__':
    test()
