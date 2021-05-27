from typing import List

from PySide2 import QtWidgets
from PySide2.QtCore import Qt, QSize, QModelIndex, Signal
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QPushButton, QWidget, QHBoxLayout, QApplication, QTableView, QTabWidget

from anlage_v.anlagev_tablemodel import AnlageVTableModel

###################################################################

class AnlageVTabs( QTabWidget ):
    def __init__( self, parent=None ):
        QTabWidget.__init__( self, parent )

###################################################################

class AnlageVTableView( QTableView ):
    cell_clicked = Signal( str, int, int, int )
    def __init__( self, parent=None ):
        QTableView.__init__( self, parent )
        self.clicked.connect( self._onLeftClick )

    def _onLeftClick( self, item:QModelIndex ):
        tm:AnlageVTableModel = self.model()
        self.cell_clicked.emit( tm.getMasterName(), tm.getJahr(), item.row(), item.column() )

###################################################################

class ToolbarButton( QPushButton ):
    def __init__( self, parent, size:QSize, pathToIcon:str, tooltip:str ):
        QPushButton.__init__( self, parent )
        self.setFlat( True )
        self.setFixedSize( size )
        icon = QIcon( pathToIcon )
        self.setIcon( icon )
        self.setIconSize( size )
        self.setToolTip( tooltip )

###################################################################

class AnlageVView( QWidget ):
    def __init__( self, parent=None ):
        QWidget.__init__( self, parent )
        self.setWindowTitle( "Anlage V" )
        self._mainLayout = QtWidgets.QGridLayout( self )
        self._toolbarLayout = QHBoxLayout()
        #self._btnSave = ToolbarButton( self, QSize(30,30), "../images/save_30.png", "Änderungen speichern" )
        self._btnPrint = ToolbarButton( self, QSize(30,30), "../images/print_30.png", "Anlagen V drucken" )
        self._tabs:QTabWidget() = QTabWidget()
        self._tvList:List[AnlageVTableView] = list()
        self._createGui()

    def _createGui( self ):
        self._createToolbar()
        self._mainLayout.addLayout( self._toolbarLayout, 0, 0, alignment=Qt.AlignLeft )
        self._mainLayout.addWidget( self._tabs, 1, 0 )
        self.setLayout( self._mainLayout )

    def _createToolbar( self ):
        #self._btnSave.clicked.connect( self._onSave )
        #self._toolbarLayout.addWidget( self._btnSave, alignment=Qt.AlignLeft )
        self._btnPrint.clicked.connect( self._onPrint )
        self._toolbarLayout.addWidget( self._btnPrint, alignment=Qt.AlignLeft )

    def addAnlageV( self, tm:AnlageVTableModel ) -> AnlageVTableView:
        tv = AnlageVTableView()
        tv.setModel( tm )
        tv.resizeColumnsToContents()
        self._tabs.addTab( tv, tm.getMasterName() )
        self._tvList.append( tv )
        return tv

    def _onSave( self ):
        print( "AnlageVView._onSave")

    def _onPrint( self ):
        print( "AnlageVView._onPrint" )


def test():
    app = QApplication()
    v = AnlageVView()
    v.show()
    app.exec_()

if __name__ == "__main__":
    test()