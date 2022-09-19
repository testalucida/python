from typing import List, Iterable

from base.basetablemodel import BaseTableModel, SumTableModel
from base.interfaces import XBase


class IccTableModel( BaseTableModel ):
    def __init__( self, rowList:List[XBase]=None, jahr:int=None ):
        BaseTableModel.__init__( self, rowList, jahr )


class IccSumTableModel( SumTableModel ):
    def __init__( self, objectList:List[XBase], jahr:int, colsToSum:Iterable[str] ):
        SumTableModel.__init__( self, objectList, jahr, colsToSum )