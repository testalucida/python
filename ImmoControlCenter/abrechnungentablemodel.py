import copy
import numbers
from functools import cmp_to_key

from PySide2.QtGui import QFont, QBrush, QColor
from PySide2.QtCore import *
from typing import List, Dict, Any

from icctablemodel import IccTableModel
from interfaces import XAbrechnung, XNkAbrechnung, XHgAbrechnung
from enum import Enum
import constants

class AbrechnungenTableModel( IccTableModel ):
    def __init__( self, abrechList:List[XAbrechnung] ):
        IccTableModel.__init__( self )
        self._abrechlist:List[XAbrechnung] = abrechList
        """
        Gewünschte Spaltenfolge: 
        mobj_id | mv_id oder weg_name_vw_id | von | bis | ab_jahr | betrag | ab_datum | buchungsdatum | bemerkung
        """
        self._headers = ("Wohnung", "Name", "MV von", "MV bis", "Jahr", "Betrag", "Abr.-Datum", "Buchungsdatum", "Bemerkung")
        self._keylist = ("mobj_id", "", "von", "bis", "ab_jahr", "betrag", "ab_datum", "buchungsdatum", "bemerkung")
        # Änderungslog vorbereiten:
        self._changes:Dict[str, List[XAbrechnung]] = {}
        for s in constants.actionList:
            self._changes[s] = list()
        """
        Aufbau von _changes:
        {
            "UPDATE": List[XAbrechnung]
        }
        Wir haben hier nur Updates, keine Inserts, weil in _abrechlist jeder Mieter bzw. jede WEG bereits
        in einem XAbrechnung-Objekt geliefert wird. Es kommen keine XAbrechnung-Objekte dazu und es werden 
        keine gelöscht.
        """
        self._greyBrush = QBrush( Qt.gray )
        self._redBrush = QBrush( Qt.red )
        self._yellowBrush = QBrush( Qt.yellow )
        self._blueBrush = QBrush( Qt.darkBlue )
        self._boldFont = QFont( "Arial", 11, QFont.Bold )
        self._columnMobjId = 0
        self._columnName = 1
        self._columnVon = 2
        self._columnBis = 3
        self._columnBuchungsdatum = 7
        self._columnBetrag = 5
        self._sortable = False

    def getHeader( self, col:int ) -> str:
        if col == self._columnName:
            return self.getNameColumnHeader()
        else:
            return self._headers[col]

    def getKey( self, col:int ) -> str:
        if col == self._columnName:
            return self.getNameColumnKey()
        else:
            return self._keylist[col]

    def getNameColumnHeader( self ) -> str:
        pass

    def getNameColumnKey( self ) -> str:
        pass

    def getId( self, x:XAbrechnung ) -> str:
        """
        :param x:
        :return: the id of the derived abrechnung table (nk or hg)
        """
        pass

    def getName( self, x:XAbrechnung ) -> str:
        pass

    def getBetragColumnIndex( self ) -> int:
        return self._keylist.index( "betrag" )

    def setSortable( self, sortable:bool=True ):
        self._sortable = sortable

    def rowCount( self, parent:QModelIndex=None ) -> int:
        return len( self._abrechlist )

    def columnCount( self, parent:QModelIndex=None ) -> int:
        return len( self._headers )

    def getXAbrechnung( self, row:int ) -> XAbrechnung:
        #x = self._abrechlist[row]
        #print( "getXAbrechnung: row= ", row, "name= ", x.getName() )
        return self._abrechlist[row]

    def getValue( self, indexrow: int, indexcolumn: int ) -> Any:
        x:XAbrechnung = self._abrechlist[indexrow]
        key = self.getKey( indexcolumn )
        val = x.__dict__[key]
        if indexcolumn == self._columnBetrag:
            val = format( val, ".2f" )
        return val

    def getForeground( self, indexrow:int, indexcolumn:int ) -> Any:
        if indexcolumn in  (self._columnMobjId, self._columnVon, self._columnBis): return self._greyBrush
        if indexcolumn == self._columnBetrag:
            val = self.getValue( indexrow, indexcolumn )
            try:
                val = float( val )
                return self._redBrush if val < 0 else self._blueBrush
            except:
                return None

    def getBackground( self, indexrow:int, indexcolumn:int ) -> Any:
        x = self.getXAbrechnung( indexrow )
        if self.isXAbrechnungUpdated( x ):
            return self._yellowBrush
        return None

    def isXAbrechnungUpdated( self, x:XAbrechnung ) -> bool:
        dictChanges = self.getChanges()
        if x in dictChanges["UPDATE"]: return True

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
                return self.getHeader( col )
        return None

    def resetChanges( self ):
        for k in self._changes.keys():
            self._changes[k] = list()
        self.layoutChanged.emit()

    def getChanges( self ) -> Dict[str, List[XAbrechnung]]:
        return self._changes

    def isChanged( self ) -> bool:
        for k, v in self._changes.items():
            if len( v ) > 0: return True
        return False

    def delete( self, x:XAbrechnung ):
        x.betrag = 0.0
        x.ab_datum = x.buchungsdatum = x.bemerkung = ""
        self.update( x, deleteFlag=True )

    def update( self, x:XAbrechnung, deleteFlag:bool=False ):
        x.deleteFlag = deleteFlag
        l = self._abrechlist
        cols = len( self._headers )
        row = self.getRow( x )
        idxfrom = self.index( row, 0 )
        idxbis = self.index( row, cols-1 )
        self._writeChangeLog( constants.tableAction.UPDATE, x )
        self.dataChanged.emit( idxfrom, idxbis )

    def getRow( self, x:XAbrechnung ) -> int:
        for r in range( len( self._abrechlist ) ):
            e:XAbrechnung = self._abrechlist[r]
            if self.getId( e ) == self.getId( x ):
                return r
        raise Exception( "AbrechnungenTableModel.getRow(): can't find id '%s'" % ( self.getId( x ) ) )

    def _writeChangeLog( self, actionId:constants.tableAction, x:XAbrechnung ) -> None:
        """
        Schreibt ein in-memory-Log der eingefügten, geänderten, gelöschten Zahlungen.
        Dieses kann über getChanges() abgerufen werden.
        """
        actionstring = constants.actionList[actionId]
        xlist:List[XAbrechnung] = self._changes[actionstring]
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
        self._abrechlist = sorted( self._abrechlist, key=cmp_to_key( self.cmpXSonstAus ) )
        self.emit(SIGNAL("layoutChanged()"))

    def cmpXAbrechnung( self, x1:XAbrechnung, x2:XAbrechnung ) -> int:
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

########################################################################################
class NkAbrechnungenTableModel( AbrechnungenTableModel ):
    def __init__( self, abrechList: List[XNkAbrechnung] ):
        AbrechnungenTableModel.__init__( self, abrechList )

    def getNameColumnHeader( self ) -> str:
        return "Mieter"

    def getNameColumnKey( self ) -> str:
        return "mv_id"

    def getId( self, x:XNkAbrechnung ) -> str:
        return x.nka_id

    def getName( self, x:XNkAbrechnung ) -> str:
        return x.mv_id

#########################################################################################
class HgAbrechnungenTableModel( AbrechnungenTableModel ):
    def __init__( self, abrechList: List[XNkAbrechnung] ):
        AbrechnungenTableModel.__init__( self, abrechList )

    def getNameColumnHeader( self ) -> str:
        return "WEG"

    def getNameColumnKey( self ) -> str:
        return "weg_name_vw_id"

    def getId( self, x:XHgAbrechnung ) -> str:
        return x.hga_id

    def getName( self, x:XHgAbrechnung ) -> str:
        return x.vwg_id