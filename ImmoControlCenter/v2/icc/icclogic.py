from typing import List, Iterable

from base.basetablemodel import BaseTableModel, SumTableModel
from base.interfaces import XBase
from v2.icc.iccdata import IccData

######################   IccTableModel   ########################
class IccTableModel( BaseTableModel ):
    def __init__( self, rowList:List[XBase]=None, jahr:int=None ):
        BaseTableModel.__init__( self, rowList, jahr )

######################   IccSumTableModel   #####################
class IccSumTableModel( SumTableModel ):
    def __init__( self, objectList:List[XBase], jahr:int, colsToSum:Iterable[str] ):
        SumTableModel.__init__( self, objectList, jahr, colsToSum )

########################   IccLogic   ###########################
class IccLogic:
    def __init__(self):
        self._iccdata = IccData()

    def getJahre( self ) -> List[int]:
        """
        Liefert eine Liste der Jahre, für die Daten in der Datenbank vorhanden sind.
        :return:
        """
        return self._iccdata.getJahre()