from typing import List, Dict

from databasecommon import DatabaseCommon
from interfaces import XVerwaltung, XSollHausgeld


class VerwaltungData( DatabaseCommon ):
    def __init__( self ):
        DatabaseCommon.__init__( self )

    def getAktiveVerwaltungen( self, jahr: int, orderby: str = None ) -> List[XVerwaltung]:
        """
        Liefert alle Verwaltungen, die im Jahr <jahr> aktiv waren/sind.
        Das beinhaltet auch die, die in <jahr> enden bzw. anfangen.
        :param jahr:
        :param orderby:
        :return:
        """
        vgldat_von = str( jahr ) + "-01-01"
        vgldat_bis = str( jahr ) + "-12-31"
        sql = "select vwg_id, mobj_id, vw_id, weg_name, von, coalesce( bis, '' ) as bis " \
              "from verwaltung " \
              "where von < '%s' and (bis is NULL or bis = '' or bis > '%s') " % ( vgldat_bis, vgldat_von )
        if orderby:
            sql += "order by %s" % orderby
        return self.readAllGetObjectList( sql, XVerwaltung )

    def getSollHausgeld( self, master_name:str, jahr:int ) -> List[XSollHausgeld]:
        von, bis = "%d-01-01" % jahr, "%d-12-31" % jahr
        sql = "select master.master_name, " \
              "soll.shg_id, soll.vwg_id, soll.von, soll.bis, " \
              "soll.netto, soll.ruezufue, soll.netto+soll.ruezufue as brutto, " \
              "soll.bemerkung, " \
              "vwg.weg_name " \
              "from sollhausgeld soll " \
              "inner join verwaltung vwg on vwg.vwg_id = soll.vwg_id " \
              "inner join masterobjekt master on master.master_id = vwg.master_id " \
              "where master.master_name = '%s' " \
              "and soll.von < '%s' " \
              "and (soll.bis is NULL or soll.bis = '' or soll.bis > '%s') " \
              "and vwg.von < '%s' " \
              "and (vwg.bis is NULL or vwg.bis = '' or vwg.bis > '%s')" % (master_name, bis, von, bis, von)
        return self.readAllGetObjectList( sql, XSollHausgeld)

    def getHGVSumme( self, master_name: str, jahr: int ) -> float:
        """
        Liefert die Summe aller Brutto-HG-Vorauszahlungen für Masterobjekt <master_name> im Zeitraum <jahr>.
        Brutto heißt Hausgeld inklusive RüZuFü.
        Achtung: es wird eine negative Zahl geliefert. (Auszahlungen)
        :param master_name:
        :param jahr:
        :return:
        """
        sql = "select coalesce(sum(betrag), 0) as hgv " \
              "from zahlung z " \
              "inner join masterobjekt master on master.master_id = z.master_id " \
              "where zahl_art = 'hgv' " \
              "and jahr = %d " \
              "and master.master_name = '%s'" % (jahr, master_name)
        tuplelist = self.read( sql )
        li = [t[0] for t in tuplelist]
        return li[0]

    def getHGASumme( self, master_name: str, jahr: int ) -> float:
        """
        Liefert die SUmmen der HG-Abrechnungszahlungen für ein Masterobjekt <master_name> für einen Zeitraum <jahr>.
        Annahme: in der Tabelle <zahlung> kann es mehr als einen Eintrag je <master_name> und jahr geben.
        Es wird eine positive (Gutschrift) oder negative Zahl (Nachzahlung) geliefert.
        :param master_name:
        :param jahr:
        :return: die Summe aller Gutschriften bzw. Nachzahlungen für Masterobjekt <master_name> im Jahr <jahr>
        """
        sql = "select coalesce(sum(betrag), 0) as hga " \
              "from zahlung z " \
              "inner join masterobjekt master on master.master_id = z.master_id " \
              "where zahl_art = 'hga' " \
              "and jahr = %d " \
              "and master.master_name = '%s'" % (jahr, master_name )
        tuplelist = self.read( sql )
        li = [x[0] for x in tuplelist]
        return li[0]

def test4():
    data = VerwaltungData()
    s = data.getSollHausgeld( "NK_Volkerstal", 2021 )
    print( s )


def test3():
    data = VerwaltungData()
    s = data.getHGASumme( "ER_Heuschlag", 2021 )
    print( s )

def test1():
    data = VerwaltungData()
    s = data.getHGVSumme( "HOM_Remigius", 2021 )
    print( s )

def test2():
    data = VerwaltungData()
    s = data.getHGASumme( "NK_Volkerstal", 2021 )
    print( s )