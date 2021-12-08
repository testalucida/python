
import json
from typing import List

import jsonhelper
from generictable_stuff.xbasetablemodel import XBaseTableModel
from geplant.geplantucc import GeplantUcc
from interfaces import XGeplant
from returnvalue import ReturnValue


class GeplantServices:
    @staticmethod
    def getPlanungenModel( jahr:int=None) -> XBaseTableModel:
        gucc = GeplantUcc()
        #### json_ = gucc.getPlanungen( jahr ) todo: aktivieren, wenn der UCC in der Lage ist, einen JSON-String zurückzugeben
        #### model = jsonhelper.xbaseTableModelToJson( )
        model = gucc.getPlanungen( jahr )
        return model

def test():
    res = GeplantServices.getPlanungenModel( 2021 )