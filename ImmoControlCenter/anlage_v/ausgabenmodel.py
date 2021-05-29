import numbers
from typing import List, Any
from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt

from anlage_v.anlagev_interfaces import XAusgabeKurz
from interfaces import XSonstAus


class AusgabenModel( QAbstractTableModel ):
    def __init__( self, master_name:str, jahr:int, sonstausList: List[XAusgabeKurz] ):
        QAbstractTableModel.__init__( self )
        self._master_name = master_name
        self._jahr = jahr
        self._sonstausList = sonstausList
        self._headers:List[str] = ["Kreditor", "Wohng", "Buchungstext", "Buch.datum", "Kostenart", "Betrag", "Summe"]

    def getMasterName( self ) -> str:
        return self._master_name

    def rowCount( self, parent: QModelIndex = None ) -> int:
        return len( self._sonstausList )

    def columnCount( self, parent: QModelIndex = None ) -> int:
        return len( self._headers )

    def getValue( self, indexrow: int, indexcolumn: int ) -> Any:
        x:XAusgabeKurz = self._sonstausList[indexrow]
        columns = {
            0: x.kreditor,
            1: x.mobj_id,
            2: x.buchungstext,
            3: x.buchungsdatum,
            4: x.kostenart,
            5: x.betrag,
            6: None
        }
        val = columns.get( indexcolumn )
        if val is None:
            return self._getSumme( indexrow )
        return val

    def _getSumme( self, indexrow:int ) -> float:
        pass

    def data( self, index: QModelIndex, role: int = None ):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self.getValue( index.row(), index.column() )
        elif role == Qt.TextAlignmentRole:
            v = self.getValue( index.row(), index.column() )
            if isinstance( v, numbers.Number ): return int( Qt.AlignRight | Qt.AlignVCenter )
        return None

    def headerData( self, col, orientation, role=None ):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self._headers[col]
            if role == Qt.BackgroundRole:
                pass
                # if self.headerBrush:
                #     return self.headerBrush
        return None