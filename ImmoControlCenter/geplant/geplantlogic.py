from typing import List

import datehelper
from generictable_stuff.xbasetablemodel import XBaseTableModel
from geplant.geplantdata import GeplantData
from interfaces import XGeplant


class GeplantLogic:
    def __init__(self):
        self._db:GeplantData = GeplantData()

    def getPlanungen( self, jahr:int=None ) -> XBaseTableModel:
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
        except Exception as ex:
            raise Exception( "Fehler beim Lesen der Planungen für das Jahr %d:\n'%s' " % (jahr, str( ex )) )
        model = XBaseTableModel( planungslist )
        model.setSortable( True )
        return model

def test():
    logic = GeplantLogic()
    model = logic.getPlanungen( 2022 )