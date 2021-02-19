from functools import cmp_to_key

from PySide2.QtGui import QFont, QBrush
from PySide2.QtCore import *
from typing import List, Any

from icctablemodel import IccTableModel
from interfaces import XBuchungstextMatch

class BuchungstextMatchModel( IccTableModel ):
    def __init__( self, matchList:List[XBuchungstextMatch] ):
        IccTableModel.__init__( self )
        self._matchlist:List[XBuchungstextMatch] = matchList
        self._keylist = ("umlegbar", "master_name", "mobj_id", "kreditor", "buchungstext")
        self._headers = ("u", "Haus", "Whg", "Kreditor", "Buchungstext")

        self._greyBrush = QBrush( Qt.gray )
        self._columnUmlegbar = 0
        self._sortable = False

    def setSortable( self, sortable:bool=True ):
        self._sortable = sortable

    def rowCount( self, parent:QModelIndex=None ) -> int:
        return len( self._matchlist )

    def columnCount( self, parent:QModelIndex=None ) -> int:
        return len( self._headers )

    def getXBuchungstextMatch( self, row:int ) -> XBuchungstextMatch:
        return self._matchlist[row]

    def getValue( self, indexrow: int, indexcolumn: int ) -> Any:
        x = self._matchlist[indexrow]
        key = self._keylist[indexcolumn]
        val = x.__dict__[key]
        if indexcolumn == self._columnUmlegbar:
            val = 'u' if val else ''
        return val

    def getForeground( self, indexrow:int, indexcolumn:int ) -> Any:
        if indexcolumn < 3: return self._greyBrush
        return None

    def data(self, index: QModelIndex, role: int = None):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self.getValue( index.row(), index.column() )
        elif role == Qt.ForegroundRole:
            return self.getForeground( index.row(), index.column() )
        return None

    def headerData(self, col, orientation, role=None):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self._headers[col]
        return None

    # def getRow( self, x:XBuchungstextMatch ) -> int:
    #     for r in range( len( self._matchlist ) ):
    #         e:XBuchungstextMatch = self._matchlist[r]
    #         if e.saus_id == x.saus_id:
    #             return r
    #     raise Exception( "SonstAusTableModel.getRow(): can't find saus_id %d" % (x.saus_id) )


    sort_col = -1
    sort_reverse = False
    def sort( self, col:int, order: Qt.SortOrder ) -> None:
        if not self._sortable: return
        """sort table by given column number col"""
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        global sort_col
        sort_col = col
        global sort_reverse
        sort_reverse = True if order == Qt.SortOrder.AscendingOrder else False
        self._matchlist = sorted( self._matchlist, key=cmp_to_key( self.cmpXBuchungstextMatch ) )
        self.emit(SIGNAL("layoutChanged()"))

    def cmpXBuchungstextMatch( self, x1:XBuchungstextMatch, x2:XBuchungstextMatch ) -> int:
        global sort_col, sort_reverse
        key = self._keylist[sort_col]
        v1 = x1.__dict__[key]
        v2 = x2.__dict__[key]
        if isinstance( v1, str ):
            v1 = v1.lower()
            v2 = v2.lower()
        if v1 < v2: return -1 if sort_reverse else 1
        if v1 > v2: return 1 if sort_reverse else -1
        if v1 == v2: return 0
