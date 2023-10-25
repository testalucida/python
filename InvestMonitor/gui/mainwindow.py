from PySide2.QtWidgets import QMainWindow, QScrollArea

from base.baseqtderivates import BaseGridLayout
from gui.infopanel import InfoPanel


class AllInfoPanelsScrollArea( QScrollArea ):
    def __init__(self):
        QScrollArea.__init__( self )
        self._layout = BaseGridLayout()
        self.setLayout( self._layout )
        self._row = 0
        self._col = 0
        self._maxCols = 3

    def addInfoPanel( self, infopanel:InfoPanel ):
        self._layout.addWidget( infopanel, self._row, self._col )
        self._col += 1
        if self._col == self._maxCols:
            self._row += 1
            self._col = 0

class MainWindow( QMainWindow ):
    def __init__( self ):
        QMainWindow.__init__( self )
        self._panelsScroll = AllInfoPanelsScrollArea()
        self.setCentralWidget( self._panelsScroll )

    def addInfoPanel( self, infopanel:InfoPanel ):
        self._panelsScroll.addInfoPanel( infopanel )