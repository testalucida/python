from PySide2.QtCore import *
from PySide2.QtWidgets import QTableView, QAbstractScrollArea
from dictlisttablemodel import DictListTableModel

class TableView( QTableView ):
    def __init__(self):
        QTableView.__init__(self)
        self.setAlternatingRowColors( True )
        self.setStyleSheet( "alternate-background-color: lightgrey" )
        self.setContextMenuPolicy( Qt.CustomContextMenu )
        self.customContextMenuRequested.connect( self.onRightClick )
        self.clicked.connect( self.onLeftClick )
        self.verticalHeader().setVisible( False )
        self.horizontalHeader().setStretchLastSection( True )
        self.setSortingEnabled( True )

    def onLeftClick(self, index:QModelIndex):
        print( "cell %d/%d clicked." % ( index.row(), index.column() ) )

    def onRightClick(self, qPoint:QPoint):
        for index in self.selectedIndexes():
            print( "cell %d/%d RIGHT clicked." % ( index.row(), index.column() ) )

    def setModel(self, model: DictListTableModel) -> None:
        super().setModel( model )
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.resizeColumnsToContents()

    def getModel( self ) -> DictListTableModel:
        return self.model()