from PySide2 import QtWidgets
from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QPushButton, QWidget, QHBoxLayout, QApplication, QTableView

from anlage_v.anlagev_tablemodel import AnlageVTableModel


class AnlageVTableView( QTableView ):
    def __init__( self, parent=None ):
        QTableView.__init__( self, parent )

class ToolbarButton( QPushButton ):
    def __init__( self, parent, size:QSize, pathToIcon:str, tooltip:str ):
        QPushButton.__init__( self, parent )
        self.setFlat( True )
        self.setFixedSize( size )
        icon = QIcon( pathToIcon )
        self.setIcon( icon )
        self.setIconSize( size )
        self.setToolTip( tooltip )

class AnlageVView( QWidget ):
    def __init__( self, parent=None ):
        QWidget.__init__( self, parent )
        self.setWindowTitle( "Anlagen V" )
        self._mainLayout = QtWidgets.QGridLayout( self )
        self._toolbarLayout = QHBoxLayout()
        self._btnSave = ToolbarButton( self, QSize(30,30), "../images/save_30.png", "Änderungen speichern" )
        self._btnPrint = ToolbarButton( self, QSize(30,30), "../images/print_30.png", "Anlagen V drucken" )
        self._tv = AnlageVTableView( self )
        self._createGui()

    def _createGui( self ):
        self._createToolbar()
        self._mainLayout.addLayout( self._toolbarLayout, 0, 0, alignment=Qt.AlignLeft )
        self._mainLayout.addWidget( self._tv, 1, 0 )
        self.setLayout( self._mainLayout )

    def _createToolbar( self ):
        self._btnSave.clicked.connect( self._onSave )
        self._toolbarLayout.addWidget( self._btnSave, alignment=Qt.AlignLeft )
        self._btnPrint.clicked.connect( self._onPrint )
        self._toolbarLayout.addWidget( self._btnPrint, alignment=Qt.AlignLeft )

    def _onSave( self ):
        print( "AnlageVView._onSave")

    def _onPrint( self ):
        print( "AnlageVView._onPrint" )

    def setAnlageVTableModel( self, model:AnlageVTableModel ) -> None:
        self._tv.setModel( model )

def test():
    app = QApplication()
    v = AnlageVView()
    v.show()
    app.exec_()

if __name__ == "__main__":
    test()