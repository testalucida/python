import jsonhelper
from generictable_stuff.xbasetablemodel import XBaseTableModel
from geplant.geplantlogic import GeplantLogic


class GeplantUcc:
    """
    Sammelbecken für die UCC rund um Planungen (neue Planung, Planung ändern, Planung löschen, Planungen lesen)
    """
    def __init__( self ):
        self._logic = GeplantLogic()

    # def getPlanungen( self, jahr:int=None ) -> str:
    #     """
    #     erhält von der Geschäftslogik ein Tablemodel, das in einen json-String umgewandelt und an GeplantServices
    #     übergeben wird.
    #     :param jahr:
    #     :return:
    #     """
    #     model:XBaseTableModel = self._logic.getPlanungen( jahr )
    #     jsonhelper.  todo: wie wandelt man ein model in einen JSON-String um??

    def getPlanungen( self, jahr:int=None ) -> XBaseTableModel:
        """
        :param jahr:
        :return: todo: es darf hier kein Objekt zurückgegeben werden, sondern ein JSON-String
        """
        model: XBaseTableModel = self._logic.getPlanungen( jahr )
        return model
