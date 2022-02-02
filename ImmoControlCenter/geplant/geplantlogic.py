from typing import List
import datehelper
from geplant.geplantdata import GeplantData
from interfaces import XGeplant


class GeplantLogic:
    def __init__(self):
        self._db:GeplantData = GeplantData()

    def getDistinctYears( self ) -> List[int]:
        years = self._db.getDistinctYears()
        return years

    def getPlanungen( self, jahr:int=None ) -> List[XGeplant]:
        """
        Liefert die Planungen des angegebenen Jahres.
        Wird kein Jahr angegeben, werden die Planungen des laufenden Jahres ermittelt.
        :param jahr:
        :return:
        """
        if not jahr:
            jahr = datehelper.getCurrentYear()
        try:
            planungslist:List[XGeplant] = self._db.getPlanungen( jahr )
            return planungslist
        except Exception as ex:
            raise Exception( "Fehler beim Lesen der Planungen für das Jahr %d:\n'%s' " % (jahr, str( ex )) )
        # model = XBaseTableModel( planungslist, jahr )
        # model.setSortable( True )

    def save( self, x:XGeplant ):
        if x.id <= 0:
            self._db.insertPlanung( x )
        else:
            self._db.updatePlanung( x )

def test():
    logic = GeplantLogic()
    model = logic.getPlanungen( 2022 )