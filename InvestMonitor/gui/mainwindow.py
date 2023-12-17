from PySide2.QtCore import Signal, QSize, QPoint
from PySide2.QtGui import Qt, QScreen
from PySide2.QtWidgets import QMainWindow, QScrollArea, QWidget, QApplication, QDesktopWidget, QHBoxLayout

from base.baseqtderivates import BaseGridLayout, BaseToolBar, SearchField, BaseComboBox, BaseLabel, Separator, \
    BaseButton, BaseWidget
from base.enumhelper import getEnumValues, getEnumFromValue
from gui.infopanel import InfoPanel
from imon.definitions import DEFAULT_PERIOD, DEFAULT_INTERVAL
from imon.enums import InfoPanelOrder, Period, Interval


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

    def removeInfoPanel( self, ip:InfoPanel ):
        self._layout.removeWidget( ip )

    def clear( self ) -> None:
        self.children().clear()
        self._row = 0
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
    period_interval_changed = Signal( Period, Interval )
    def __init__(self):
        BaseToolBar.__init__( self )
        self._searchField = SearchField()
        self._searchField.setPlaceholderText( "Suche nach WKN oder ISIN oder Ticker" )
        self._searchField.setFixedWidth( 300 )
        self.addWidget( self._searchField )
        self._cboOrder = BaseComboBox()
        self._cboOrder.addItems( getEnumValues( InfoPanelOrder ) )
        self.addSeparator()
        self.addWidget( BaseLabel( "   InfoPanels anordnen:  " ) )
        self.addWidget( self._cboOrder )
        self.addSeparator()
        self._periodAndIntervalWidget = BaseWidget()
        self._cboPeriod = BaseComboBox()
        self._cboInterval = BaseComboBox()
        self._btnUpdateAllInfoPanels = BaseButton( "⟳", callback=self.onUpdateAllInfoPanels )
        self._addPeriodAndIntervalWidget()
        self.addSeparator()
        self._btnUndock = BaseButton( "⏏" )
        self._btnUndock.setToolTip( "Markierte Depotpositionen in separatem Fenster zeigen" )
        self.addWidget( self._btnUndock)

    def _addPeriodAndIntervalWidget( self ):
        self._cboPeriod.addItems( Period.getPeriods() )
        self._cboPeriod.setCurrentText( DEFAULT_PERIOD.value )
        self._cboInterval.addItems( Interval.getIntervals() )
        self._cboInterval.setCurrentText( DEFAULT_INTERVAL.value )
        self._cboPeriod.currentIndexChanged.connect( self.onPeriodIntervalChanged )
        self._cboInterval.currentIndexChanged.connect( self.onPeriodIntervalChanged )
        lay = QHBoxLayout()
        lay.addWidget( BaseLabel( "Period" ) )
        lay.addWidget( self._cboPeriod )
        lay.addWidget( BaseLabel( "Interval" ) )
        lay.addWidget( self._cboInterval )
        self._btnUpdateAllInfoPanels.setFixedSize( QSize(25, 25) )
        self._btnUpdateAllInfoPanels.setEnabled( False )
        lay.addWidget( self._btnUpdateAllInfoPanels )
        self._periodAndIntervalWidget.setLayout( lay )
        self.addWidget( self._periodAndIntervalWidget )

    def getSearchField( self ) -> SearchField:
        return self._searchField

    def getOrderComboBox( self ) -> BaseComboBox:
        return self._cboOrder

    def getUndockButton( self ) -> BaseButton:
        return self._btnUndock

    def onPeriodIntervalChanged( self, arg ):
        self._btnUpdateAllInfoPanels.setEnabled( True )

    def onUpdateAllInfoPanels( self ):
        period = getEnumFromValue( Period, self._cboPeriod.currentText() )
        interval = getEnumFromValue( Interval, self._cboInterval.currentText() )
        self._btnUpdateAllInfoPanels.setEnabled( False )
        self.period_interval_changed.emit( period, interval )


############################################################
class MainWindow( QMainWindow ):
    change_infopanel_order = Signal( InfoPanelOrder )
    undock_infopanel = Signal()
    period_interval_changed = Signal( Period, Interval )
    def __init__( self ):
        QMainWindow.__init__( self )
        self._toolBar = IMonToolBar()
        self.addToolBar( self._toolBar )
        self._toolBar.period_interval_changed.connect( self.period_interval_changed.emit )
        self._allInfoPanel = AllInfoPanel()
        self._panelsScroll = AllInfoPanelsScrollArea()
        self._panelsScroll.setWidget( self._allInfoPanel )
        self.setCentralWidget( self._panelsScroll )
        cbo = self._toolBar.getOrderComboBox()
        cbo.currentTextChanged.connect(
            lambda txt: self.change_infopanel_order.emit( getEnumFromValue( InfoPanelOrder, txt ) ) )
        btn = self._toolBar.getUndockButton()
        btn.clicked.connect( self.undock_infopanel.emit )

    def addInfoPanel( self, infopanel:InfoPanel ):
        self._allInfoPanel.addInfoPanel( infopanel )

    def getToolBar( self ) -> IMonToolBar:
        return self._toolBar

    def getSearchField( self ) -> SearchField:
        return self._toolBar.getSearchField()

    def clear( self ) -> None:
        self._allInfoPanel.clear()

    def ensureVisible( self, infopanel:InfoPanel ):
        if infopanel.visibleRegion().isEmpty():
            self._panelsScroll.ensureWidgetVisible( infopanel )

    def removeInfoPanel( self, ip:InfoPanel ):
        self._allInfoPanel.removeInfoPanel( ip )

#####################################################################################################
def test():
    def changeOrder( newOrder:InfoPanelOrder ):
        print( "new Order: ", newOrder.value )
    app = QApplication()
    win = MainWindow()
    win.show()
    win.change_infopanel_order.connect( changeOrder )
    rect = QDesktopWidget().screenGeometry()
    #r:QPoint = rect.topRight()
    w = rect.right() - rect.left()
    #w = rect.topRight().x() - rect.topLeft().x() - 100
    h = rect.bottom() - rect.top()
    win.resize( QSize( w, h ) )
    app.exec_()
