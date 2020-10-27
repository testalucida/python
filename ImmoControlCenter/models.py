from typing import Dict, List
from PySide2.QtCore import *
from PySide2.QtGui import QFont, QStandardItemModel, QStandardItem, QBrush, QColor
import operator

class KontrollModel( QAbstractTableModel ):
    def __init__( self, parent, dictList:List[Dict], checkmonat:int ):
        QAbstractTableModel.__init__(self, parent)
        self._rowlist:List[Dict] = dictList
        if len( self._rowlist ) > 0:
            self._headers:List = list( self._rowlist[0].keys() )
        else:
            self._headers:List = ["Keine Daten vorhanden"]
        self._headerColor = QColor("#FDBC6A")
        self._headerBrush = QBrush( self._headerColor )
        self._greyColor = QColor( "#A19696")
        self._greyBrush = QBrush( self._greyColor )
        self._boldFont = QFont( "Arial", 11, QFont.Bold )
        self._yellow = QColor( "yellow" )
        self._yellowBrush = QBrush( self._yellow )
        self._leadingColumns = 6 # es gibt 6 leading columns, die nichts mit den Monatswerten zu tun haben
        self._checkMonatColumnIdx = 0
        self._checkMonat = 0
        self._nameColumnIdx = 3
        self._sollColumnIdx = 4 # die Spalte mit den Soll-Werten
        self._okColumnIdx = 5 # Spalte des OK-Buttons
        self._nokColumnIdx = 6 # Spalte des NOK-Buttons
        self._summeColumnIdx = 19 #Summe aller Monatszahlungen - Spalte
        self.setCheckmonat( checkmonat )
        self.okstatecallback = None

    def rowCount( self, parent ):
        return len(self._rowlist)

    def columnCount(self, parent):
        if len( self._rowlist ) == 0: return 0
        return len(self._rowlist[0])

    def getOkColumnIdx( self ):
        return self._okColumnIdx

    def getNokColumnIdx( self ):
        return self._nokColumnIdx

    def setCheckmonat(self, monatIdx:int ):
        self._checkMonat = monatIdx
        self._checkMonatColumnIdx = self._checkMonat + self._leadingColumns

    def setOkStateCallback(self, cbfnc ):
        self.okstatecallback = cbfnc

    def setOkState(self, index, isChecked ):
        ist = self.getCheckMonatIst( index )
        soll = self.getSoll( index )
        if ist != soll:
            self.setCheckMonatIst( index, soll )

    def setCheckMonatIst(self, index, val ):
        istidx = self.index(index.row(), self._checkMonatColumnIdx)
        print( "going to set %d to cell %d/%d" % ( val, istidx.row(), istidx.column() ) )
        self.setData( istidx, val )

    def getCheckMonatIst(self, index ):
        istidx = self.index(index.row(), self._checkMonatColumnIdx)
        ist = self.data(istidx, Qt.DisplayRole)
        return ist

    def getSoll( self, index ):
        sollidx = self.index(index.row(), self._sollColumnIdx)
        soll = self.data(sollidx, Qt.DisplayRole)
        return soll

    def setCheckMonatValue(self, index, value ):
        idx = self.createIndex( index.row(), self._checkMonatColumnIdx )
        self.setData( idx, value )

    def setData( self, index, value ):
        rowdict = self._rowlist[index.row()]
        key = self._headers[index.column()]
        rowdict[key] = value
        self.dataChanged.emit( index, index )
        return True

    def data( self, index:QModelIndex, role:int=None ):
        #print( "data: ", index, ", ", role)
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            key = self._headers[index.column()]
            d:Dict = self._rowlist[index.row()]
            v = d[key]
            if v == 0: v = ""
            return v
        elif role == Qt.TextAlignmentRole:
            if index.column() > self._nokColumnIdx: return Qt.AlignRight
        elif role == Qt.BackgroundRole:
            if index.column() == self._nameColumnIdx:
                #return QBrush( Qt.lightGray )
                return QBrush(self._headerColor)
            elif index.column() == self._checkMonatColumnIdx:
                return self._yellowBrush
            elif index.column() == self._summeColumnIdx:
                return QBrush( Qt.lightGray )
        elif role == Qt.ForegroundRole:
            if index.column() < self._nameColumnIdx:
                return self._greyBrush
        elif role == Qt.FontRole:
            if index.column() in ( self._nameColumnIdx, self._summeColumnIdx):
                return self._boldFont

    def headerData(self, col, orientation, role=None):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self._headers[col]
            if role == Qt.BackgroundRole:
                return self._headerBrush #QBrush(self._headerColor)
        return None

    def sort(self, col, order):
        """sort table by given column number col"""
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.mylist = sorted(self.mylist,
                             key=operator.itemgetter(col))
        if order == Qt.DescendingOrder:
            self.mylist.reverse()
        self.emit(SIGNAL("layoutChanged()"))
