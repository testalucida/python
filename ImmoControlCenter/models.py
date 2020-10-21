from typing import Dict, List
from PySide2.QtCore import *
from PySide2.QtGui import QFont, QStandardItemModel, QStandardItem, QBrush, QColor
import operator


class KontrollModel( QAbstractTableModel ):
    def __init__( self, parent, dictList:List[Dict], checkmonat:int ):
        QAbstractTableModel.__init__(self, parent)
        self._rowlist:List[Dict] = dictList
        self._headers:List = list( self._rowlist[0].keys() )
        self._headerColor = QColor("#FDBC6A")
        self._headerBrush = QBrush( self._headerColor )
        self._greyColor = QColor( "#A19696")
        self._greyBrush = QBrush( self._greyColor )
        self._boldFont = QFont( "Arial", 11, QFont.Bold )
        self._yellow = QColor( "yellow" )
        self._yellowBrush = QBrush( self._yellow )
        self._checkMonat = checkmonat

    def rowCount( self, parent ):
        return len(self._rowlist)

    def columnCount(self, parent):
        return len(self._rowlist[0])

    def setCheckmonat(self, monatIdx:int ):
        self._checkMonat = monatIdx

    def data(self, index, role):
        #print( "data: ", index, ", ", role)
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            key = self._headers[index.column()]
            d:Dict = self._rowlist[index.row()]
            v = d[key]
            return v
        elif role == Qt.BackgroundRole:
            if index.column() == 3:
                #return QBrush( Qt.lightGray )
                return QBrush(self._headerColor)
            elif index.column() == self._checkMonat + 6:
                return self._yellowBrush
        elif role == Qt.ForegroundRole:
            if index.column() < 3:
                return self._greyBrush
        elif role == Qt.FontRole:
            if index.column() == 3:
                return self._boldFont

    def headerData(self, col, orientation, role):
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
