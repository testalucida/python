import copy
import numbers
from functools import cmp_to_key

from PySide2.QtGui import QFont, QBrush, QColor
from PySide2.QtCore import *
from typing import List, Dict, Any

from icctablemodel import IccTableModel
from interfaces import XSonstAus
from enum import Enum
import constants

class SonstAusTableModel( IccTableModel ):
    def __init__( self, sonstausList:List[XSonstAus] ):
        IccTableModel.__init__( self )
        self._sonstauslist:List[XSonstAus] = sonstausList
        """
        Gewünschte Spaltenfolge: 
        werterhaltend | umlegbar | master_name | mobj_id | kreditor | buchungstext | rgdatum | buchungsdatum | betrag | rgtext
        """
        self._keylist = ("werterhaltend", "umlegbar", "master_name", "mobj_id", "kreditor", "buchungstext", "rgdatum", "buchungsdatum", "betrag", "rgtext")
        self._headers = ("w", "u", "Haus", "Whg", "Kreditor", "Buchungstext", "Rg.datum", "Buch.datum", "Betrag", "Rg.text")
        # Änderungslog vorbereiten:
        self._changes:Dict[str, List[XSonstAus]] = {}
        for s in constants.actionList:
            self._changes[s] = list()
        """
        Aufbau von _changes:
        {
            "INSERT": List[XSonstAus],
            "UPDATE": List[XSonstAus],
            "DELETE": List[XSonstAus]
        }
        """
        self._greyBrush = QBrush( Qt.gray )
        self._redBrush = QBrush( Qt.red )
        self._yellowBrush = QBrush( Qt.yellow )
        self._blueBrush = QBrush( Qt.darkBlue )
        self._boldFont = QFont( "Arial", 11, QFont.Bold )
        self._columnWerterhaltend = 0
        self._columnUmlegbar = 1
        self._columnBuchungsdatum = 7
        self._columnBetrag = 8
        self._sortable = False

    def getBetragColumnIndex( self ) -> int:
        return self._keylist.index( "betrag" )

    def setSortable( self, sortable:bool=True ):
        self._sortable = sortable

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
            val = format( val, ".2f" )
        #     val = "%.2f" % (val)
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

    def getBackground( self, indexrow:int, indexcolumn:int ) -> Any:
        x = self.getXSonstAus( indexrow )
        if self.isXSonstAusInsertedOrUpdated( x ):
            return self._yellowBrush
        return None

    def isXSonstAusInsertedOrUpdated( self, x:XSonstAus ) -> bool:
        dictChanges = self.getChanges()
        if x in dictChanges["INSERT"]: return True
        if x in dictChanges["UPDATE"]: return True
        return False

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
        elif role == Qt.BackgroundRole:
            return self.getBackground( index.row(), index.column() )
        return None

    def headerData(self, col, orientation, role=None):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self._headers[col]
            # if role == Qt.BackgroundRole:
            #     pass
        return None

    def resetChanges( self ):
        for k in self._changes.keys():
            self._changes[k] = list()
        self.layoutChanged.emit()

    def getChanges( self ) -> Dict[str, List[XSonstAus]]:
        return self._changes

    def isChanged( self ) -> bool:
        for k, v in self._changes.items():
            if len( v ) > 0: return True
        return False

    def updateOrInsert( self, x:XSonstAus ):
        l = self._sonstauslist
        cols = len( self._headers )
        if x.saus_id or x in self._sonstauslist: # update of existing auszahlung
            row = self.getRow( x )
            idxfrom = self.index( row, 0 )
            idxbis = self.index( row, cols-1 )
            self._writeChangeLog( constants.tableAction.UPDATE, x )
            self.dataChanged.emit( idxfrom, idxbis )
        else:   # insert new auszahlung
            l.append( x )
            self._writeChangeLog( constants.tableAction.INSERT, x )
            self.layoutChanged.emit()

    def delete( self, x:XSonstAus ) -> None:
        self._sonstauslist.remove( x )
        self._writeChangeLog( constants.tableAction.DELETE, x )
        self.layoutChanged.emit()

    def duplicate( self, x:XSonstAus ) -> XSonstAus:
        """
        duplicates x and returns the duplicate copy
        Raises an exception if x cannot be found in the list of XSonstAus
        :param x:
        :return:
        """
        x2:XSonstAus = copy.copy( x )
        x2.saus_id = 0
        l = self._sonstauslist
        for i in range( len( l ) ):
            tmp:XSonstAus = l[i]
            if tmp.saus_id == x.saus_id:
                l.insert( i, x2 )
                self._writeChangeLog( constants.tableAction.INSERT, x2 )
                self.layoutChanged.emit()
                return x2
        raise Exception( "Auszahlung mit ID = %d nicht in der Auszahlungsliste gefunden." % (x.saus_id) )

    def getRow( self, x:XSonstAus ) -> int:
        for r in range( len( self._sonstauslist ) ):
            e:XSonstAus = self._sonstauslist[r]
            if e.saus_id == x.saus_id:
                return r
        raise Exception( "SonstAusTableModel.getRow(): can't find saus_id %d" % (x.saus_id) )

    def _writeChangeLog( self, actionId:constants.tableAction, x:XSonstAus ) -> None:
        """
        Schreibt ein in-memory-Log der eingefügten, geänderten, gelöschten Zahlungen.
        Dieses kann über getChanges() abgerufen werden.
        """
        actionstring = constants.actionList[actionId]
        xlist:List[XSonstAus] = self._changes[actionstring]
        if not x in xlist:
            xlist.append( x )

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
        self._sonstauslist = sorted( self._sonstauslist, key=cmp_to_key( self.cmpXSonstAus ) )
        self.emit(SIGNAL("layoutChanged()"))

    def cmpXSonstAus( self, x1:XSonstAus, x2:XSonstAus ) -> int:
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
