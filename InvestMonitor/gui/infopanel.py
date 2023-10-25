from enum import Enum
from typing import List, Tuple

import matplotlib
from PySide2.QtCore import QSize, Signal
from pandas import DataFrame

from base.baseqtderivates import BaseGridLayout, BaseLabel, BaseEdit, SignedNumEdit, IntEdit, FloatEdit, HLine, \
    BaseButton, BaseComboBox
from base.enumhelper import getEnumFromValue
from data.finance.tickerhistory import TickerHistory, Period, Interval
from interface.interfaces import XDepotPosition

matplotlib.use('Qt5Agg')
from PySide2.QtWidgets import QWidget, QApplication, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT #as NavigationToolbar
from matplotlib.figure import Figure
import pandas as pd

class NavigationToolbar(NavigationToolbar2QT):
    # only display the buttons we need
    toolitems = [t for t in NavigationToolbar2QT.toolitems if
                 t[0] in ('Home', 'Pan', 'Zoom', None)]

##############################################################
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

        self.toolbar = NavigationToolbar( self, self )

#############################################################
class InfoPanel( QWidget ):
    """
    Ein InfoPanel enthält alle Informationen zu einem Wertpapier (Aktie, Fonds- oder ETF-Anteil)
    und einen Graph, der die Kursentwicklung eines Zeitraums anzeigt.
    """
    # def makeToolButton( self, txt:str ) -> BaseButton:
    #     btn = BaseButton( text=txt, callback=None )
    #     btn.setFixedSize( QSize(23, 23) )
    #     return btn

    period_changed = Signal( Period )   # arg: neues Periodenkürzel
    interval_changed = Signal( Interval ) # arg: neues Intervall-Kürzel

    @staticmethod
    def createCombo( items: List[str], signal_to_emit: Signal, enu:Enum ) -> BaseComboBox:
        cbo = BaseComboBox()
        cbo.addItems( items )
        cbo.currentIndexChanged.connect( lambda x: signal_to_emit.emit( getEnumFromValue( enu, cbo.currentText() ) ) )
        return cbo

    def __init__(self):
        QWidget.__init__( self )
        maxw = 70
        self._layout = BaseGridLayout()
        self.setLayout( self._layout )
        self._mplCanvas = MplCanvas()
        self._x:XDepotPosition = None
        self._lblName = BaseEdit( isReadOnly=True)

        self._layCombos = QHBoxLayout()
        self._cboPeriod = self.createCombo( Period.getPeriods(), self.period_changed, Period )
        self._cboInterval = self.createCombo( Interval.getIntervals(), self.interval_changed, Interval )

        self._lblWkn = BaseEdit( isReadOnly=True)
        self._lblIsin = BaseEdit( isReadOnly=True)
        self._lblWaehrung = BaseEdit( isReadOnly=True )
        self._lblAcc = BaseEdit( isReadOnly=True )
        self._lblStueck = IntEdit( isReadOnly=True )
        self._lblStueck.setMaximumWidth( maxw )
        self._lblGesamtPreis = IntEdit( isReadOnly=True )
        self._lblGesamtPreis.setMaximumWidth( maxw )
        self._lblPreisProStueck = FloatEdit( isReadOnly=True )
        self._lblPreisProStueck.setMaximumWidth( maxw )
        self._lblMaxKaufpreis = FloatEdit( isReadOnly=True )
        self._lblMaxKaufpreis.setMaximumWidth( maxw )
        self._lblMinKaufpreis = FloatEdit( isReadOnly=True )
        self._lblMinKaufpreis.setMaximumWidth( maxw )
        self._lblGesamtWertAktuell = IntEdit( isReadOnly=True )
        self._lblGesamtWertAktuell.setMaximumWidth( maxw )
        self._lblKursAktuell = FloatEdit( isReadOnly=True )
        self._lblKursAktuell.setMaximumWidth( maxw )
        self._lblDeltaProz = FloatEdit( isReadOnly=True )
        self._lblDeltaProz.setMaximumWidth( maxw )
        self._createGui()

    def _createGui( self ):
        l = self._layout
        cols = 5
        r, c = 0, 0
        l.addWidget( self._lblName, r, c, 1, 4 )

        r += 1
        self._layCombos.addWidget( BaseLabel( "Period" ) )
        self._layCombos.addWidget( self._cboPeriod )
        self._layCombos.addWidget( BaseLabel( " Interval" ) )
        self._layCombos.addWidget( self._cboInterval )
        c = 3
        l.addLayout( self._layCombos, r, c )
        r += 1
        c = 0
        l.addWidget( self._lblWkn, r, c, 1, 3 )
        r = 2
        l.addWidget( self._lblIsin, r, c, 1, 3 )
        r += 1
        l.addWidget( self._lblWaehrung, r, c, 1, 3 )
        r += 1
        l.addWidget( self._lblAcc, r, c, 1, 3 )
        r += 1
        c = 0
        l.addWidget( BaseLabel( "Bestand" ), r, c )
        c = 1
        l.addWidget( self._lblStueck, r, c )
        c = 2
        l.addWidget( BaseLabel("Stck"), r, c )
        r += 1
        c = 0
        l.addWidget( BaseLabel( "Kauf" ), r, c )
        c = 1
        self._lblGesamtPreis.setToolTip( "Summe aller Einzelkäufe" )
        l.addWidget( self._lblGesamtPreis, r, c )
        c = 2
        l.addWidget( BaseLabel( "€" ), r, c )
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
        self._lblKursAktuell.setToolTip( "aktueller Kurs" )
        l.addWidget( self._lblKursAktuell, r, c )
        c = 2
        l.addWidget( BaseLabel( "€" ), r, c )

        r += 1
        c = 0
        l.addWidget( HLine(), r, c, 1, 3 )

        r += 1
        c = 0
        l.addWidget( BaseLabel( "Δ Kurs" ), r, c )
        c = 1
        self._lblDeltaProz.setToolTip( "Verh. durchschn. Kaufpreis zu akt. Kurs" )
        l.addWidget( self._lblDeltaProz, r, c )
        c = 2
        l.addWidget( BaseLabel( "%" ), r, c )

        r, c = 2, 3
        l.addWidget( self._mplCanvas, r, c, l.rowCount()-1, 2 )

    def setModel( self, x:XDepotPosition ):
        self._x = x
        self._lblName.setValue(x.name)
        self._lblWkn.setValue( x.wkn )
        self._lblIsin.setValue( x.isin )
        self._lblWaehrung.setValue( x.waehrung )
        self._lblAcc.setValue( "Thesaurierend" if x.flag_acc else "Ausschüttend" )
        self._lblStueck.setValue( x.stueck )
        self._lblGesamtPreis.setValue( x.gesamtkaufpreis )
        self._lblPreisProStueck.setValue( x.preisprostueck )
        self._lblMaxKaufpreis.setValue( x.maxKaufpreis )
        self._lblMinKaufpreis.setValue( x.minKaufpreis )

        self._lblGesamtWertAktuell.setValue( x.gesamtwert_aktuell )
        self._lblKursAktuell.setValue( x.kurs_aktuell )
        self._lblDeltaProz.setValue( x.delta_proz )

        self._plot()

    def _plot( self ):
        self._x.history.plot( ax=self._mplCanvas.axes, grid=True )


##########  TEST ###  TEST  ###################################################
def test():
    app = QApplication()
    ip = InfoPanel()
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
    ip.show()
    app.exec_()