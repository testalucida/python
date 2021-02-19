import numbers
from copy import copy

from PySide2.QtCore import QModelIndex, Qt, QItemSelectionModel
from PySide2.QtWidgets import QTableView

# class Match:
#     index: QModelIndex = None
#

class SearchHandler:
    def __init__( self, tv: QTableView ):
        self._searchstring = ""
        self._tv = tv
        self._model = tv.model()
        self._row = 0
        self._col = 0

    def onSearch( self, searchstring:str ) -> None:
        """
        Callback function for button "Search" or F3 key.
        Searches tv.model for searchstring.
        If searchstring has changed, initialize search engine, search next match
        If searchstring hasn't changed, search next match
        :param searchstring:
        :return:
        """
        if searchstring.lower() != self._searchstring:
            self._searchstring = searchstring.lower()
            self._row = 0
            self._col = 0
        self.searchNextMatch()

    def searchNextMatch( self ) -> None:
        row = self._row
        col = self._col
        maxrow = self._model.rowCount()
        maxcol = self._model.columnCount()
        for r in range( row, maxrow ):
            for c in range( col, maxcol ):
                idx = self._getIndex( r, c )
                val = self._model.data( idx, Qt.DisplayRole )
                tmp = copy( val )
                if isinstance( tmp, numbers.Number ):
                   tmp = str( tmp )
                if self._searchstring in tmp.lower(): # Match
                    self._row = r
                    self._col = c+1
                    if self._col >= self._model.columnCount():
                        self._row += 1
                        self._col = 0
                        if self._row >= self._model.rowCount():
                            self._row = 0
                    self.showMatch( idx )
                    return
            col = 0
        self._row = 0
        self._col = 0

    def showMatch( self, index:QModelIndex ):
        self._tv.selectionModel().select( index, QItemSelectionModel.ClearAndSelect )
        self._tv.scrollTo( index )

    def _getIndex( self, row:int, col:int ) -> QModelIndex:
        return self._model.index( row, col )




