from numbers import Number
from typing import List

from PySide2.QtCore import QPoint, Qt
from PySide2.QtGui import QGuiApplication
from PySide2.QtWidgets import QAction, QMenu

from qtderivates import SumDialog
from tableviewext import TableViewExt


class TableCellActionHandler:
    def __init__( self, tv: TableViewExt ):
        tv.setMouseTracking( True )
        tv.setContextMenuPolicy( Qt.CustomContextMenu )
        tv.customContextMenuRequested.connect( self.onRightClick )
        tv.setCopyCallback( self._onCopy )  # wenn der User Ctrl+c drückt
        self._tv = tv
        self._actionList:List[List] = list() #Liste die eine Liste mit Paaren action / callback enthält.
        # self._actionList.append( ( QAction( "Berechne Summe" ), self._onComputeSum ) )
        self._actionList.append( ( QAction( "Kopiere" ), self._onCopy) ) # für Kontextmenü

    def activateComputeSumAction( self, activate:bool=True ):
        self._actionList.append( (QAction( "Berechne Summe" ), self._onComputeSum) )

    def addAction( self, action:QAction, callback ):
        self._actionList.append( ( action, callback ) )

    def onRightClick( self, point: QPoint ):
        index = self._tv.indexAt( point )
        row = index.row()
        if row < 0 or index.column() < 0: return  # nicht auf eine  Zeile geklickt
        selectedIndexes = self._tv.selectedIndexes()
        if selectedIndexes is None or len( selectedIndexes ) < 1: return
        menu = QMenu( self._tv )
        for pair in self._actionList:
            menu.addAction( pair[0] )
        action = menu.exec_( self._tv.viewport().mapToGlobal( point ) )
        if action:
            sel = [pair[1] for pair in self._actionList if pair[0] == action]
            sel[0]()

    def _onComputeSum( self ):
        valuelist = list()
        model = self._tv.model()
        if not model: return
        for idx in self._tv.selectedIndexes():
            val = self._tv.model().data( idx, Qt.DisplayRole )
            if not val: val = 0
            if isinstance( val, int ) or isinstance( val, float ):
                valuelist.append( val )
            else:
                return
        sumval = sum( valuelist )
        self.showSumDialog( sumval )

    def showSumDialog( self, sumval ):
        dlg = SumDialog( self._tv )
        dlg.setSum( sumval )
        dlg.show()

    def _onCopy( self ):
        values:str = ""
        indexes = self._tv.selectedIndexes()
        row = -1
        for idx in indexes:
            if row == -1: row = idx.row()
            if row != idx.row():
                values += "\n"
                row = idx.row()
            elif len( values ) > 0:
                values += "\t"
            val = self._tv.model().data( idx, Qt.DisplayRole )
            val = "" if not val else val
            if isinstance( val, Number ):
                values += str( val )
            else:
                values += val
            #print( idx.row(), "/", idx.column(), ": ", val )
        #print( "valuestring: ",  values )
        clipboard = QGuiApplication.clipboard()
        clipboard.setText( values )



