from enum import Enum
from typing import List, Tuple

import matplotlib
from PySide2.QtCore import QSize, Signal, Qt, Slot, QRect
#from pandas import DataFrame
from PySide2.QtGui import QPalette, QColor

from base.baseqtderivates import BaseGridLayout, BaseLabel, BaseEdit, SignedNumEdit, IntEdit, FloatEdit, HLine, \
    BaseButton, BaseComboBox, BaseLink, HistoryButton
from base.enumhelper import getEnumFromValue
from data.finance.tickerhistory import TickerHistory, Period, Interval
from interface.interfaces import XDepotPosition

matplotlib.use('Qt5Agg')
from PySide2.QtWidgets import QWidget, QApplication, QHBoxLayout, QFrame
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT #as NavigationToolbar
from matplotlib.figure import Figure
#import pandas as pd

class NavigationToolbar(NavigationToolbar2QT):
    # only display the buttons we need
    toolitems = [t for t in NavigationToolbar2QT.toolitems if
                 t[0] in ('Home', 'Pan', 'Zoom', None)]

##############################################################
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, width=5, height=4, dpi=100):
        self._width = width
        self._height = height
        self._dpi = dpi
        self._figure = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self._figure.add_subplot(111)
        super(MplCanvas, self).__init__( self._figure )

        self.toolbar = NavigationToolbar( self, self )

    def clear( self ):
        self._figure.clear()
        self._figure = Figure( figsize=(self._width, self._height), dpi=self._dpi )
        self.figure = self._figure
        self.axes = self._figure.add_subplot( 111 )

    def draw( self ):
        super().draw()
        rend = self.get_renderer()
        self._figure.draw( rend )


#############################################################
class InfoPanel( QFrame ):
    """
    Ein InfoPanel enthält alle Informationen zu einem Wertpapier (Aktie, Fonds- oder ETF-Anteil)
    und einen Graph, der die Kursentwicklung eines Zeitraums anzeigt.
    """
    # period_changed = Signal( Period )   # arg: neues Periodenkürzel
    # interval_changed = Signal( Interval ) # arg: neues Intervall-Kürzel
    update_graph = Signal( Period, Interval )
    enter_bestand_delta = Signal()
    show_kauf_historie = Signal()
    update_kurs = Signal()
    show_details = Signal()

    @staticmethod
    def createCombo( items: List[str], slot:Slot ) -> BaseComboBox:
        cbo = BaseComboBox()
        cbo.addItems( items )
        cbo.currentIndexChanged.connect( slot )
        return cbo

    def __init__(self):
        QFrame.__init__( self )
        self._row = -1 # row im MainWindow
        self._col = -1 # col im MainWindow
        maxwnumlabels = 70
        self._layout = BaseGridLayout()
        self.setLayout( self._layout )
        self._mplCanvas = MplCanvas()
        self._x:XDepotPosition = None
        self._lblName = BaseEdit( isReadOnly=True)
        self._btnDetails = BaseButton( "ⓘ" )
        self._btnDetails.clicked.connect( self.show_details.emit )
        self._btnDetails.setMaximumSize( QSize(23, 23) )
        self._btnSelect = BaseButton( "☐" )
        self._btnSelect.clicked.connect( lambda x: self.setSelected( not self._isSelected ) )
        self._isSelected = False
        self._btnSelect.setMaximumSize( QSize( 23, 23 ) )
        self._laySort = QHBoxLayout()
        #self._lblSortItems = BaseEdit( isReadOnly=True )
        self._lblSortValues = BaseEdit( isReadOnly=True )
        self._lblSortValues.setObjectName( "sortvalues" )
        self._lblSortValues.setStyleSheet( "#sortvalues {background: #e7e3e4}")

        self._layCombos = QHBoxLayout()
        self._cboPeriod = self.createCombo( Period.getPeriods(), self.onPeriodIntervalChanged )
        self._cboInterval = self.createCombo( Interval.getIntervals(), self.onPeriodIntervalChanged )

        self._btnUpdateGraph = BaseButton( "⟳", callback=self.onUpdateGraphClicked )
        self._btnUpdateGraph.setFixedSize( QSize( 23, 23 ) )
        self._lblWkn = BaseEdit( isReadOnly=True )
        #self._lblWkn.setMaximumWidth( maxwtextlabels )
        self._lblTicker = BaseEdit( isReadOnly=True )
        self._lblTicker.setFixedWidth( 90 )
        self._lblIsin = BaseEdit( isReadOnly=True )
        #self._lblIsin.setMaximumWidth( maxwtextlabels )
        self._lblWaehrung = BaseEdit( isReadOnly=True )
        self._lblWaehrung.setFixedWidth( 90 )
        self._lblAcc = BaseEdit( isReadOnly=True )
        #self._lblAcc.setMaximumWidth( maxwtextlabels )
        self._lblStueck = IntEdit( isReadOnly=True )
        self._lblStueck.setMaximumWidth( maxwnumlabels )
        self._btnStueckDelta = BaseButton( "Δ" )
        self._btnStueckDelta.clicked.connect( self.enter_bestand_delta.emit )
        self._btnStueckDelta.setFixedSize( QSize(23, 23) )
        self._lblGesamtPreis = IntEdit( isReadOnly=True )
        self._lblGesamtPreis.setMaximumWidth( maxwnumlabels )
        self._btnKaufHistorie = HistoryButton( "Zeigt die Historie der Käufe an" )
        self._btnKaufHistorie.clicked.connect( self.show_kauf_historie.emit )
        self._btnKaufHistorie.setFixedSize( QSize(23, 23) )
        self._lblPreisProStueck = FloatEdit( isReadOnly=True )
        self._lblPreisProStueck.setMaximumWidth( maxwnumlabels )
        self._lblMaxKaufpreis = FloatEdit( isReadOnly=True )
        self._lblMaxKaufpreis.setMaximumWidth( maxwnumlabels )
        self._lblMinKaufpreis = FloatEdit( isReadOnly=True )
        self._lblMinKaufpreis.setMaximumWidth( maxwnumlabels )
        self._lblGesamtWertAktuell = IntEdit( isReadOnly=True )
        self._lblGesamtWertAktuell.setMaximumWidth( maxwnumlabels )
        self._lblKursAktuell = FloatEdit( isReadOnly=True )
        self._lblKursAktuell.setMaximumWidth( maxwnumlabels )
        self._btnKursAktualisieren = BaseButton( "⟳" )
        self._btnKursAktualisieren.clicked.connect( self.update_kurs.emit )
        self._btnKursAktualisieren.setFixedSize( QSize(23, 23) )
        self._lblDivJeStck = FloatEdit( isReadOnly=True )
        self._lblDivJeStck.setMaximumWidth( maxwnumlabels )
        self._lblDivYield = FloatEdit( isReadOnly=True )
        self._lblDivYield.setMaximumWidth( maxwnumlabels )
        self._lblDeltaProz = FloatEdit( isReadOnly=True )
        self._lblDeltaProz.setMaximumWidth( maxwnumlabels )
        self._createGui()

    def _createGui( self ):
        l = self._layout
        cols = 6
        r, c = 0, 0
        l.addWidget( self._lblName, r, c, 1, 6 )
        c = 6
        layBtnDetAndMark = QHBoxLayout()
        layBtnDetAndMark.addWidget( self._btnDetails )
        layBtnDetAndMark.addWidget( self._btnSelect )
        self._layout.addLayout( layBtnDetAndMark, r, c )
        self._btnDetails.setToolTip( "Details anzeigen" )
        self._btnSelect.setToolTip( "Diese Depotposition markieren" )
        ######l.addWidget( self._btnDetails, r, c )

        r += 1
        c = 0
        self._laySort.addWidget( BaseLabel( "Sort" ) )
        #self._laySort.addWidget( self._lblSortItems )
        self._laySort.addWidget( self._lblSortValues )
        l.addLayout( self._laySort, r, c, 1, 5 )

        self._layCombos.addWidget( BaseLabel( "Period" ) )
        self._layCombos.addWidget( self._cboPeriod )
        self._layCombos.addWidget( BaseLabel( " Interval" ) )
        self._layCombos.addWidget( self._cboInterval )
        self._layCombos.addWidget( self._btnUpdateGraph )
        self._layCombos.addStretch()
        c = 5
        l.addLayout( self._layCombos, r, c )

        r += 1
        c = 0
        l.addWidget( self._lblWkn, r, c, 1, 2 )
        r += 1
        c = 0
        l.addWidget( self._lblIsin, r, c, 1, 2 )
        r += 1
        l.addWidget( self._lblTicker, r, c, 1, 2 )
        r += 1
        l.addWidget( self._lblWaehrung, r, c, 1, 2 )
        r += 1
        l.addWidget( self._lblAcc, r, c, 1, 2 )
        r += 1
        c = 0
        l.addWidget( BaseLabel( "Bestand" ), r, c )
        c = 1
        l.addWidget( self._lblStueck, r, c )
        c = 2
        l.addWidget( BaseLabel("St"), r, c )
        c = 3
        self._btnStueckDelta.setToolTip( "Bestandsveränderung eintragen (Kauf/Verkauf)" )
        l.addWidget( self._btnStueckDelta, r, c, 1, 1, Qt.AlignLeft )
        r += 1
        c = 0
        l.addWidget( BaseLabel( "Kauf" ), r, c )
        c = 1
        self._lblGesamtPreis.setToolTip( "Summe aller Einzelkäufe" )
        l.addWidget( self._lblGesamtPreis, r, c )
        c = 2
        l.addWidget( BaseLabel( "€" ), r, c )
        c = 3
        l.addWidget( self._btnKaufHistorie, r, c, 1, 1, Qt.AlignLeft )
        r += 1
        c = 0
        l.addWidget( BaseLabel( "Ø je Stck" ), r, c )
        c = 1
        self._lblPreisProStueck.setToolTip( "Summe aller Einzelkäufe / Stück" )
        l.addWidget( self._lblPreisProStueck, r, c )
        c = 2
        l.addWidget( BaseLabel( "€"), r, c )
        r += 1
        c = 0
        l.addWidget( BaseLabel( "max je Stck" ), r, c )
        c = 1
        l.addWidget( self._lblMaxKaufpreis, r, c )
        c = 2
        l.addWidget( BaseLabel( "€" ), r, c )
        r += 1
        c = 0
        l.addWidget( BaseLabel( "min je Stck" ), r, c )
        c = 1
        l.addWidget( self._lblMinKaufpreis, r, c )
        c = 2
        l.addWidget( BaseLabel( "€" ), r, c )

        r += 1
        c = 0
        l.addWidget( HLine(), r, c, 1, 3 )

        r += 1
        l.addWidget( BaseLabel( "Wert" ), r, c )
        c = 1
        self._lblGesamtWertAktuell.setToolTip( "Wert der Depotposition: Stück * akt. Kurs" )
        l.addWidget( self._lblGesamtWertAktuell, r, c )
        c = 2
        l.addWidget( BaseLabel( "€" ), r, c )
        r += 1
        c = 0
        l.addWidget( BaseLabel( "Kurs" ), r, c )
        c = 1
        self._lblKursAktuell.setToolTip( "aktueller Kurs in Euro" )
        l.addWidget( self._lblKursAktuell, r, c )
        c = 2
        l.addWidget( BaseLabel( "€" ), r, c )
        c = 3
        self._btnKursAktualisieren.setToolTip( "Kurs aktualisieren")
        l.addWidget( self._btnKursAktualisieren, r, c, 1, 1, Qt.AlignLeft )
        r += 1
        c = 0
        l.addWidget( BaseLabel( "Div./Stck" ), r, c )
        c = 1
        self._lblDivJeStck.setToolTip( "Dividende in Euro im gewählten Zeitraum pro Stück" )
        l.addWidget( self._lblDivJeStck, r, c )
        c = 2
        l.addWidget( BaseLabel( "€" ) )

        r += 1
        c = 0
        l.addWidget( BaseLabel( "Div.Rend." ), r, c )
        c = 1
        self._lblDivYield.setToolTip( "Dividendenrendite: Dividende/akt.Kurs" )
        l.addWidget( self._lblDivYield, r, c )
        c = 2
        l.addWidget( BaseLabel( "%" ) )

        r += 1
        c = 0
        l.addWidget( HLine(), r, c, 1, 3 )

        r += 1
        c = 0
        l.addWidget( BaseLabel( "Δ Wert" ), r, c )
        #l.addWidget( BaseLabel( "Entwicklg." ), r, c )
        c = 1
        self._lblDeltaProz.setToolTip( "Verh. durchschn. Kaufpreis zu akt. Kurs" )
        l.addWidget( self._lblDeltaProz, r, c )
        c = 2
        l.addWidget( BaseLabel( "%" ), r, c )

        # der Graph:
        r, c = 2, 4
        l.addWidget( self._mplCanvas, r, c, l.rowCount()-1, 3 )

        l.setColumnStretch( 0, 0 )
        l.setColumnStretch( 1, 0 )
        l.setColumnStretch( 2, 0 )
        l.setColumnStretch( 3, 0 )
        l.setColumnStretch( 4, 1 )

    def setModel( self, x:XDepotPosition ):
        self._x = x
        self.setObjectName( x.wkn )
        self._dataToGui()
        self._btnUpdateGraph.setEnabled( False )
        self._plot()

    def changeModel( self, x:XDepotPosition ):
        """
        Versieht dieses InfoPanel mit einer geänderten Depot-Position, was zur Änderung es Graphen führt.
        (x- und ggf. y-Achse - nach Änderung von Period oder Interval)
        :return:
        """
        self._x = x
        self._dataToGui()
        self._btnUpdateGraph.setEnabled( False )
        self._mplCanvas.clear()
        self._plot()
        self._mplCanvas.draw()

    def _dataToGui( self ):
        x = self._x
        self._cboPeriod.setCurrentText( x.history_period.value )
        self._cboInterval.setCurrentText( x.history_interval.value )
        self._lblName.setValue( x.name )
        # self._lblWkn.setValue( x.wkn )
        self._lblIsin.setValue( x.isin )
        self._lblWkn.setValue( x.wkn )
        self._lblTicker.setValue( x.ticker )
        self._lblWaehrung.setValue( x.waehrung )
        self._lblAcc.setValue( "Thesaurierend" if x.flag_acc else "Ausschüttend" )
        self._lblStueck.setValue( x.stueck )
        self._lblGesamtPreis.setValue( x.gesamtkaufpreis )
        self._lblPreisProStueck.setValue( x.preisprostueck )
        self._lblMaxKaufpreis.setValue( x.maxKaufpreis )
        self._lblMinKaufpreis.setValue( x.minKaufpreis )
        self._lblGesamtWertAktuell.setValue( x.gesamtwert_aktuell )
        self._lblKursAktuell.setValue( x.kurs_aktuell )
        self._lblDivJeStck.setValue( x.dividend_period )
        self._lblDivYield.setValue( x.dividend_yield )
        self._lblDeltaProz.setValue( x.delta_proz )

    def updateKursAktuell( self, kurs:float, divYield:float ):
        self._lblKursAktuell.setValue( kurs )
        self._lblDivYield.setValue( divYield )

    def updateOrderRelatedData( self ):
        x = self._x
        self._lblGesamtPreis.setValue( x.gesamtkaufpreis )
        self._lblPreisProStueck.setValue( x.preisprostueck )
        self._lblMaxKaufpreis.setValue( x.maxKaufpreis )
        self._lblMinKaufpreis.setValue( x.minKaufpreis )
        self._lblGesamtWertAktuell.setValue( x.gesamtwert_aktuell )
        self._lblDeltaProz.setValue( x.delta_proz )

    def getModel( self ) -> XDepotPosition:
        return self._x

    def setSelected2( self, selected:bool=True ):
        self._lblName.setBold( selected )
        color = "red" if selected else "black"
        self._lblName.setTextColor( color )

    def setSelected( self, selected:bool=True ):
        if selected:
            borderstyle = "#" + self._x.wkn + " {border: 5px solid darkblue; }"
        else:
            borderstyle = "#" + self._x.wkn + " {border: 0px solid black; }"
        self.setStyleSheet(  borderstyle )
        self._isSelected = selected

    def isSelected( self ) -> bool:
        return self._isSelected

    def setSortInfo( self, values:str ):
        #self._lblSortItems.setValue( items )
        self._lblSortValues.setValue( values )

    def _plot( self ):
        self._x.history.plot( ax=self._mplCanvas.axes, grid=True )

    def onPeriodIntervalChanged( self ):
        self._btnUpdateGraph.setEnabled( True )

    def onUpdateGraphClicked( self ):
        period = getEnumFromValue( Period, self._cboPeriod.currentText() )
        interval = getEnumFromValue( Interval, self._cboInterval.currentText() )
        self._btnUpdateGraph.setEnabled( False )
        self.update_graph.emit( period, interval )

    def setPosition( self, row:int, col:int ):
        self._row = row
        self._col = col

    def getPosition( self ) -> (int, int):
        return self._row, self._col


##########  TEST ###  TEST  ###################################################
def test():
    app = QApplication()
    ip = InfoPanel()
    #ip.setFrameRect()
    #ip.setContentsMargins( 5, 5, 5, 5 )
    # pal = ip.palette()
    # pal.setColor( QPalette.WindowText, QColor( "red" ) )
    # ip.setPalette( pal )
    # ip.setObjectName( "ip" )
    # ip.setStyleSheet( "#ip {border: 5px solid black; }")
    # ip.setStyleSheet( "#ip {border: 0px solid black; }" )
    # ip.setFrameStyle( QFrame.Box | QFrame.Raised )
    # ip.setLineWidth( 3 )
    #ip.setFrameStyle( QFrame.NoFrame )
    x = XDepotPosition()
    x.name = "WisdomTree Global Quality Dividend Growth"
    x.wkn = "A2AG1E"
    x.isin = "IE00BZ56SW52"
    x.ticker = "WTEM.DE"
    x.basic_index = "WisdomTree Global Developed Quality Dividend Growth index"
    x.gattung = "ETF"
    x.waehrung = "USD"
    x.flag_acc = True
    x.beschreibung = "The WisdomTree Global Quality Dividend Growth UCITS ETF USD Acc seeks to track the WisdomTree Global Developed Quality Dividend Growth index. The WisdomTree Global Developed Quality Dividend Growth index tracks dividend-paying developed markets stocks with growth characteristics. The index is a fundamentally weighted index."
    x.history = TickerHistory.getTickerHistoryByPeriod( x.ticker )
    x.stueck = 445
    x.gesamtkaufpreis = 13461
    x.preisprostueck = round( 13461/445, 2 )
    x.minKaufpreis = 30.00
    x.maxKaufpreis = 31.21
    x.kurs_aktuell = 30.02
    x.gesamtwert_aktuell = round( x.stueck * x.kurs_aktuell, 2 )
    #x.delta_proz = round( (x.gesamtwert_aktuell - x.gesamtkaufpreis) * 100 / x.gesamtkaufpreis, 2 )
    x.delta_proz = round( (x.kurs_aktuell - x.preisprostueck) * 100 / x.preisprostueck, 2 )
    x.depot_id = "ING_023"
    x.bank = "Ing DiBa"
    x.depot_nr = 4242424256
    x.depot_vrrkto = "FR55 0098 9907 6676 9912 12"
    # df = pd.DataFrame( [
    #     [0, 10], [5, 15], [2, 20], [15, 25], [4, 10],
    # ], columns=['A', 'B'] )
    ip.setModel( x )
    ip.setSelected2()
    ip.show()
    app.exec_()