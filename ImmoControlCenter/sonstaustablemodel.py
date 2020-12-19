import numbers

from PySide2.QtGui import QFont, QBrush, QColor
from PySide2.QtCore import *
from typing import List, Dict, Any
from interfaces import XSonstAus
from enum import Enum

class SonstAusTableModel( QAbstractTableModel ):
    def __init__( self, sonstausList:List[XSonstAus] ):
        QAbstractTableModel.__init__( self )
        self._sonstauslist:List[XSonstAus] = sonstausList
        """
        Gewünschte Spaltenfolge: 
        werterhaltend | umlegbar | master_name | mobj_id | kreditor | buchungstext | rgdatum | buchungsdatum | betrag | rgtext
        """
        self._keylist = ("werterhaltend", "umlegbar", "master_name", "mobj_id", "kreditor", "buchungstext", "rgdatum", "buchungsdatum", "betrag", "rgtext")
        self._headers = ("w", "u", "Haus", "Whg", "Kreditor", "Buchungstext", "Rg.datum", "Buch.datum", "Betrag", "Rg.text")
        self._changes:Dict[int, Dict] = {}
        """
        Aufbau von _changes:
        #todo
        """
        self._greyBrush = QBrush( Qt.gray )
        self._redBrush = QBrush( Qt.red )
        self._blueBrush = QBrush( Qt.darkBlue )
        self._boldFont = QFont( "Arial", 11, QFont.Bold )
        self._columnWerterhaltend = 0
        self._columnUmlegbar = 1
        self._columnBuchungsdatum = 7
        self._columnBetrag = 8
        self._sortable = False

    def rowCount( self, parent:QModelIndex=None ) -> int:
        return len( self._sonstauslist )

    def columnCount( self, parent:QModelIndex=None ) -> int:
        return len( self._headers )

    def getXSonstAus( self, row:int ) -> XSonstAus:
        return self._sonstauslist[row]

    def getValue( self, indexrow: int, indexcolumn: int ) -> Any:
        x = self._sonstauslist[indexrow]
        key = self._keylist[indexcolumn]
        val = x.__dict__[key]
        if indexcolumn == self._columnBetrag:
            val = "%.2f" % (val)
        if indexcolumn == self._columnWerterhaltend:
            val = 'w' if val else ''
        if indexcolumn == self._columnUmlegbar:
            val = 'u' if val else ''
        return val

    def getForeground( self, indexrow:int, indexcolumn:int ) -> Any:
        if indexcolumn < 4: return self._greyBrush
        if indexcolumn == self._columnBetrag:
            val = self.getValue( indexrow, indexcolumn )
            try:
                val = float( val )
                return self._redBrush if val < 0 else self._blueBrush
            except:
                return None

    def getFont( self, indexrow: int, indexcolumn: int ) -> Any:
        if indexcolumn in ( self._columnBuchungsdatum, self._columnBetrag ):
            return self._boldFont

    def getAlignment( self, indexrow: int, indexcolumn: int ):
        if indexcolumn == self._columnBetrag:
            return int( Qt.AlignRight | Qt.AlignVCenter )

    def data(self, index: QModelIndex, role: int = None):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self.getValue( index.row(), index.column() )
        elif role == Qt.TextAlignmentRole:
            return self.getAlignment( index.row(), index.column() )
        elif role == Qt.ForegroundRole:
            return self.getForeground( index.row(), index.column() )
        elif role == Qt.FontRole:
            return self.getFont( index.row(), index.column() )
        return None

    def headerData(self, col, orientation, role=None):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self._headers[col]
            # if role == Qt.BackgroundRole:
            #     pass
        return None

    def resetChanges( self ):
        self._changes.clear()

    def getChanges( self ) -> Dict[int, Dict]:
        return self._changes

    def isChanged( self ) -> bool:
        return any( self._changes )

    def updateOrInsert( self, x:XSonstAus ):
        l = self._sonstauslist
        cols = len( self._headers )
        if x.saus_id: # update of existing auszahlung
            row = self.getRow( x )
            idxfrom = self.index( row, 0 )
            idxbis = self.index( row, cols-1 )
            self.dataChanged.emit( idxfrom, idxbis )
        else:   # insert new auszahlung
            l.append( x )
            rows = self.rowCount()
            idxfrom = self.index( rows-1, 0 )
            idxbis = self.index( rows-1, cols-1 )
            self.layoutChanged.emit()

    def getRow( self, x:XSonstAus ) -> int:
        for r in range( len( self._sonstauslist ) ):
            e:XSonstAus = self._sonstauslist[r]
            if e.saus_id == x.saus_id:
                return r
        raise Exception( "SonstAusTableModel.getRow(): can't find saus_id %d" % (x.saus_id) )

    def _writeChangeLog( self, index, value:float ) -> None:
        """
        Schreibt ein Änderungslog für den durch <index> spezifizierten Monat
        :param index: spezifiert Zeile (meinaus_id) und Spalte (Monat)
        :param value: neuer Monatswert
        :return: None
        """
        # get meinaus_id
        ididx = self.index( index.row(), self._meinausidIdx )
        meinaus_id = self.data( ididx, Qt.DisplayRole )
        # get column name
        header = self.headerData( index.column(), Qt.Horizontal, Qt.DisplayRole )
        if not meinaus_id in self._changes:
            self._changes[meinaus_id] = {}
        self._changes[meinaus_id][header] = value

    def sort( self, col:int, order: Qt.SortOrder ) -> None:
        if not self._sortable: return
        """sort table by given column number col"""
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        sort_reverse = True if order == Qt.SortOrder.AscendingOrder else False
        self.rowlist = sorted( self.rowlist, key=lambda x: x[self._headers[col]], reverse=sort_reverse )
        self.emit(SIGNAL("layoutChanged()"))