#import json
import jsonpickle

from geplant.geplantlogic import GeplantLogic
from returnvalue import ReturnValue
from base.transaction import BEGIN_TRANSACTION, ROLLBACK_TRANSACTION, COMMIT_TRANSACTION


class GeplantUcc:
    """
    Serverseitig.
    Sammelbecken für die UCC rund um Planungen (neue Planung, Planung ändern, Planung löschen, Planungen lesen)
    Die lesenden Methoden (GET) erhalten Objekte von GeplantLogic, wanden diese in JSON-Strings um und
    geben sie zurück.
    Die schreibenden Methoden (PUT) erhalten JSON-Strings, wandeln diese in Objekte um und geben sie an
    GeplantLogic weiter.
    """
    def __init__( self ):
        self._logic = GeplantLogic()

    def getDistinctYears( self ) -> str:
        """
        Ermittelt alle Jahre, zu denen in der Tabelle <geplant> Planungen angelegt wurden.
        :return:  einen json-String, die ermittelten Jahreszahlen enthält.
        """
        years = self._logic.getDistinctYears()
        jsn = jsonpickle.encode( years )
        return jsn

    def getPlanungen( self, jahr:int=None ) -> str:
        """
        :param jahr:
        :return:
        """
        planungslist = self._logic.getPlanungen( jahr )
        jsn = jsonpickle.encode( planungslist )
        return jsn

    def save( self, xgeplant_jsn:str ) -> str:
        xgeplant = jsonpickle.decode( xgeplant_jsn )
        BEGIN_TRANSACTION()
        try:
            self._logic.save( xgeplant )
            COMMIT_TRANSACTION()
            rv = ReturnValue.fromValue( xgeplant )
        except Exception as ex:
            ROLLBACK_TRANSACTION()
            rv = ReturnValue.fromException( ex )
        jsn = jsonpickle.encode( rv )
        return jsn