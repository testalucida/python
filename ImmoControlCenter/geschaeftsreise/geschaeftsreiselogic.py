from typing import List

import datehelper
from geschaeftsreise.geschaeftsreisedata import GeschaeftsreiseData
from geschaeftsreise.geschaeftsreisentablemodel import GeschaeftsreisenTableModel
from interfaces import XGeschaeftsreise
from transaction import BEGIN_TRANSACTION, COMMIT_TRANSACTION, ROLLBACK_TRANSACTION


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

    def getGeschaeftsreisen( self, master_name: str, jahr: int ) -> List[XGeschaeftsreise]:
        xlist = self._data.getGeschaeftsreisen( master_name, jahr )
        return xlist

    def getAllGeschaeftsreisen( self, jahr:int ) -> List[XGeschaeftsreise]:
        return self._data.getAllGeschaeftsreisen( jahr )

    def insertGeschaeftsreise( self, x:XGeschaeftsreise ):
        self._data.insertGeschaeftsreise( x )
        x.id = self._data.getMaxId( "geschaeftsreise", "id" )

    def updateGeschaeftsreise( self, x:XGeschaeftsreise ):
        self._data.updateGeschaeftsreise( x )

    def deleteGeschaeftsreise( self, id:int ):
        self._data.deleteGeschaeftsreise( id )