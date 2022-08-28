from typing import List, Dict

import datehelper
from geschaeftsreise.geschaeftsreisedata import GeschaeftsreiseData
from geschaeftsreise.geschaeftsreisentablemodel import GeschaeftsreisenTableModel
from interfaces import XGeschaeftsreise, XPauschale
from base.transaction import BEGIN_TRANSACTION, COMMIT_TRANSACTION, ROLLBACK_TRANSACTION


class GeschaeftsreiseUcc:
    __instance = None

    def __init__( self ):
        self._logic:GeschaeftsreiseLogic = None
        if GeschaeftsreiseUcc.__instance:
            raise Exception( "You can't instantiate GeschaeftsreiseUcc more than once." )
        else:
            GeschaeftsreiseUcc.__instance = self
            try:
                self._logic = GeschaeftsreiseLogic()
            except Exception as ex:
                print( str( ex ) )

    @staticmethod
    def inst() -> __instance:
        if GeschaeftsreiseUcc.__instance is None:
            GeschaeftsreiseUcc()
        return GeschaeftsreiseUcc.__instance

    #-------------------------------------------

    # def getDefaultJahr( self ) -> int:
    #     try:
    #         return self._logic.getDefaultJahr()
    #     except Exception as ex:
    #         raise Exception( "GeschaeftsreiseUcc.getDefaultJahr():\n"
    #                          "Fehler beim Datenbankzugriff:\n" + str( ex ) )

    def getDistinctJahre( self ) -> List[int]:
        """
        Ermittelt, zu welchen Jahren Geschäftsreisen in der DB erfasst sind
        :return:  eine Liste der existierenden Jahre in der Tabelle <geschaeftsreise>
        """
        try:
            return self._logic.getDistinctJahre()
        except Exception as ex:
            raise Exception( "GeschaeftsreiseUcc.getJahre():\nFehler beim Datenbankzugriff:\n" + str( ex ) )

    def getGeschaeftsreisen( self, master_name: str, jahr: int ) -> List[XGeschaeftsreise]:
        try:
            return self._logic.getGeschaeftsreisen( master_name, jahr )
        except Exception as ex:
            raise Exception( "GeschaeftsreiseUcc.getGeschaeftsreisen():\n"
                             "Fehler beim Datenbankzugriff:\n" + str( ex ) )

    def getGeschaeftsreisenTableModel( self, jahr:int ) -> GeschaeftsreisenTableModel:
        try:
            xlist = self._logic.getAllGeschaeftsreisen( jahr )
            model = GeschaeftsreisenTableModel( xlist )
            return model
        except Exception as ex:
            raise Exception( "GeschaeftsreiseUcc.getGeschaeftsreisenTableModel():\n"
                             "Fehler beim Datenbankzugriff:\n" + str( ex ) )

    def insertGeschaeftsreise( self, x: XGeschaeftsreise ):
        BEGIN_TRANSACTION()
        try:
            self._logic.insertGeschaeftsreise( x )
            COMMIT_TRANSACTION()
        except Exception as ex:
            ROLLBACK_TRANSACTION()
            raise Exception( "GeschaeftsreiseUcc.insertGeschaeftsreise():\n"
                             "Fehler beim Datenbankzugriff:\n" + str( ex ) )

    def updateGeschaeftsreise( self, x: XGeschaeftsreise ):
        BEGIN_TRANSACTION()
        try:
            self._logic.updateGeschaeftsreise( x )
            COMMIT_TRANSACTION()
        except Exception as ex:
            ROLLBACK_TRANSACTION()
            raise Exception( "GeschaeftsreiseUcc.updateGeschaeftsreise():\n"
                             "Fehler beim Datenbankzugriff:\n" + str( ex ) )

    def deleteGeschaeftsreise( self, id:int ):
        BEGIN_TRANSACTION()
        try:
            self._logic.deleteGeschaeftsreise( id )
            COMMIT_TRANSACTION()
        except Exception as ex:
            ROLLBACK_TRANSACTION()
            raise Exception( "GeschaeftsreiseUcc.deleteGeschaeftsreise():\n"
                             "Fehler beim Datenbankzugriff:\n" + str( ex ) )


####################   GeschaeftsreiseLogic   ################################
class GeschaeftsreiseLogic:
    """
    Methoden rund ums Thema Geschäftsreisen.
    ACHTUNG: Einige Methoden dazu sind noch in der alten BusinessLogic!! #todo
    """
    def __init__( self ):
        self._data = GeschaeftsreiseData()
        self._pauschalen:Dict = dict() # key: Jahr; value: XPauschale

    def getDistinctJahre( self ) -> List[int]:
        """
        Liefert die Jahre, zu denen in der DB Reisen erfasst sind.
        Wenn zum lfd. Jahr noch keine Reise erfasst ist, wird das lfd. Jahr
        trotzdem zur Rückgabe-Liste hinzugefügt.
        :return: Liste der Jahre
        """
        jahre = self._data.getDistinctJahre()
        current = datehelper.getCurrentYear()
        if not current in jahre:
            jahre.insert( 0, current )
        return jahre

    def getPauschale( self, jahr:int ) -> XPauschale:
        try:
            return self._pauschalen[jahr]
        except:
            pausch = self._data.getPauschalen( jahr )
            self._pauschalen[jahr] = pausch
            return pausch

    def getGeschaeftsreisen( self, master_name: str, jahr: int ) -> List[XGeschaeftsreise]:
        xlist = self._data.getGeschaeftsreisen( master_name, jahr )
        return xlist

    def getAllGeschaeftsreisen( self, jahr:int ) -> List[XGeschaeftsreise]:
        return self._data.getAllGeschaeftsreisen( jahr )

    def getSummeGeschaeftsreisekosten( self, jahr:int ) -> float:
        """
        Ermittelt anhand der Tabellen geschaeftsreise und pauschale die Gesamtkosten für das Jahr <jahr>.
        Wir gehen davon aus, dass nur Kosten für mich, nicht für Gudi ansetzbar sind. Die Spalte <personen> in Tabelle
        geschaeftsreise wird also ignoriert.
        :param jahr: das Jahr, das beauskunftet werden soll
        :return: Die Gesamtkosten aller Dienstreisen im Jahr <jahr>
        """
        geschaeftsreisen = self.getAllGeschaeftsreisen( jahr )
        return self._getGeschaeftsreisekosten( geschaeftsreisen )

    def getGeschaeftsreisekosten( self, master_name:str, jahr:int ) -> float:
        """
        Ermittelt die Geschäftsreisekosten für <master_name> im Jahr <jahr>.
        :param master_name:
        :param jahr:
        :return:
        """
        geschaeftsreisen = self.getGeschaeftsreisen( master_name, jahr )
        return self._getGeschaeftsreisekosten( geschaeftsreisen )

    def getGeschaeftsreisekosten2( self, reise:XGeschaeftsreise ) -> float:
        """
        Ermittelt die Kosten für eine Geschäftsreise.
        ACHTUNG: Unterkunftskosten (Hotel) finden sich NICHT in den Tabellen <sonstaus> und <zahlung>,
                 sondern NUR in Tabelle <geschaeftsreise>.
                 Grund: Zwar sind Hotelkosten echte Abflüsse (im Ggs zum km-Geld und der Vpfl.-Pauschale),
                 es scheint aber plausibler, dass alle 3 Kostenarten einer Geschäftsreise zusammen in einer Tabelle
                 stehen.
                 Natürlich könnten auch die echten Km-Kosten und Vpfl.-aufwendungen in sonstaus u. zahlung eingetragen
                 werden, das würde aber einen hohen bürokratischen Aufwand fordern (Tankbelege (aber davon meistens
                 nur Teile), Essensrechnungen).
                 Deshalb nehmen wir sowohl für den Abfluss- wie auch den steuerlichen Aspekt die
                 Steuerwerte von derzeit 0.3 Euro pro km und 14 bzw. 28 Euro Vpfl.-pauschale.
        Methode wird auch von der AnlageV_Base_Logic und der AnlageV_Preview_Logic verwendet.
        :param reise:
        :return:
        """
        jahr = datehelper.getDateParts( reise.von )[0]
        pausch: XPauschale = self.getPauschale( jahr )
        dauer = datehelper.getNumberOfDays2( reise.von, reise.bis, jahr )
        if dauer == 1:
            f = 1
        else:
            f = 2
        vpflkosten = pausch.vpfl_8 * f  # Hin- u. Rückfahrt
        if dauer > 2:
            ganzetage = dauer - 2
            vpflkosten += (ganzetage * pausch.vpfl_24)
        vpflkosten = vpflkosten * -1
        uekosten = reise.uebernacht_kosten
        kmkosten = reise.km * pausch.km * -1
        summe = vpflkosten + uekosten + kmkosten
        return summe

    def _getGeschaeftsreisekosten( self, geschaeftsreisen: List[XGeschaeftsreise] ) -> float:
        """
        Berechnet die Summe der Geschäftsreisekosten für die in <geschaeftsreisen> übergebenen Geschäftsreisen.
        Reisekosten setzen sich zusammen aus km-Geld, Übernachtungskosten, Verpfl.pauschale
        :param geschaeftsreisen:
        :return:
        """
        summe = 0.0
        for g in geschaeftsreisen:
            summe += self.getGeschaeftsreisekosten2( g )
        return summe

    def insertGeschaeftsreise( self, x:XGeschaeftsreise ):
        self._data.insertGeschaeftsreise( x )
        x.id = self._data.getMaxId( "geschaeftsreise", "id" )

    def updateGeschaeftsreise( self, x:XGeschaeftsreise ):
        self._data.updateGeschaeftsreise( x )

    def deleteGeschaeftsreise( self, id:int ):
        self._data.deleteGeschaeftsreise( id )

########################################################################################

def test():
    logic = GeschaeftsreiseLogic()
    reisekosten = logic.getSummeGeschaeftsreisekosten( 2021 )
    print( reisekosten )