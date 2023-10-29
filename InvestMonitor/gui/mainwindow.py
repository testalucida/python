from PySide2.QtCore import Signal, QSize, QPoint
from PySide2.QtGui import Qt, QScreen
from PySide2.QtWidgets import QMainWindow, QScrollArea, QWidget, QApplication, QDesktopWidget

from base.baseqtderivates import BaseGridLayout, BaseToolBar, SearchField
from gui.infopanel import InfoPanel


class AllInfoPanel( QWidget ):
    def __init__( self ):
        QWidget.__init__( self )
        self._layout = BaseGridLayout()
        self.setLayout( self._layout )
        self._row = 0
        self._col = 0
        self._maxCols = 3

    def addInfoPanel( self, infopanel: InfoPanel ):
        self._layout.addWidget( infopanel, self._row, self._col )
        self._col += 1
        if self._col == self._maxCols:
            self._row += 1
            self._col = 0


##############################################################
class AllInfoPanelsScrollArea( QScrollArea ):
    def __init__(self):
        QScrollArea.__init__( self )
        self._layout = BaseGridLayout()
        self.setLayout( self._layout )
        self.setVerticalScrollBarPolicy( Qt.ScrollBarAlwaysOn )
        self.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOn )
        self.setWidgetResizable( True )

##############################################################
class IMonToolBar( BaseToolBar ):
    def __init__(self):
        BaseToolBar.__init__( self )
        self._searchField = SearchField()
        self._searchField.setPlaceholderText( "Suche nach WKN oder ISIN oder Ticker" )
        self._searchField.setFixedWidth( 300 )
        self.addWidget( self._searchField )

    def getSearchField( self ) -> SearchField:
        return self._searchField

############################################################
class MainWindow( QMainWindow ):
    def __init__( self ):
        QMainWindow.__init__( self )
        self._toolBar = IMonToolBar()
        self.addToolBar( self._toolBar )
        self._allInfoPanel = AllInfoPanel()
        self._panelsScroll = AllInfoPanelsScrollArea()
        self._panelsScroll.setWidget( self._allInfoPanel )
        self.setCentralWidget( self._panelsScroll )

    def addInfoPanel( self, infopanel:InfoPanel ):
        self._allInfoPanel.addInfoPanel( infopanel )

    def getToolBar( self ) -> IMonToolBar:
        return self._toolBar

    def getSearchField( self ) -> IMonToolBar:
        return self._toolBar.getSearchField()

    def ensureVisible( self, infopanel:InfoPanel ):
        if infopanel.visibleRegion().isEmpty():
            self._panelsScroll.ensureWidgetVisible( infopanel )

#####################################################################################################
def test():
    app = QApplication()
    win = MainWindow()
    win.show()
    rect = QDesktopWidget().screenGeometry()
    #r:QPoint = rect.topRight()
    w = rect.right() - rect.left()
    #w = rect.topRight().x() - rect.topLeft().x() - 100
    h = rect.bottom() - rect.top()
    win.resize( QSize( w, h ) )
    app.exec_()
