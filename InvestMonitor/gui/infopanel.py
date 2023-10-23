import matplotlib
from pandas import DataFrame

from base.baseqtderivates import BaseGridLayout, BaseLabel, BaseEdit, SignedNumEdit, IntEdit, FloatEdit
from data.finance.tickerhistory import TickerHistory
from interface.interfaces import XDepotPosition

matplotlib.use('Qt5Agg')
from PySide2.QtWidgets import QWidget, QApplication, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import pandas as pd

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

#############################################################
class InfoPanel( QWidget ):
    """
    Ein InfoPanel enthält alle Informationen zu einem Wertpapier (Aktie, Fonds- oder ETF-Anteil)
    und einen Graph, der die Kursentwicklung eines Zeitraums anzeigt.
    """
    class CombiInfo( QWidget ):
        def __init__(self, txt1:str, lbl:BaseEdit, txt2:str ):
            QWidget.__init__( self )
            self._lblTxt1 = BaseLabel( text=txt1 )
            self._lblLabel = lbl
            self._lblTxt2 = BaseLabel( text=txt2 )
            self._layout = QHBoxLayout()
            self.setLayout( self._layout )
            self._layout.addWidget( self._lblTxt1 )
            self._layout.addWidget( self._lblLabel )
            self._layout.addWidget( self._lblTxt2 )

        def setLabelValue( self, value ):
            #self._lblLabel.setValue( value )
            self._lblLabel.setTextAndAdjustWidth( value )

    def __init__(self):
        QWidget.__init__( self )
        self._layout = BaseGridLayout()
        self.setLayout( self._layout )
        self._mplCanvas = MplCanvas()
        self._x:XDepotPosition = None
        self._lblName = BaseEdit( isReadOnly=True)
        self._lblWkn = BaseEdit( isReadOnly=True)
        self._lblIsin = BaseEdit( isReadOnly=True)
        self._lblWaehrung = BaseEdit( isReadOnly=True )
        self._lblAcc = BaseEdit( isReadOnly=True )
        self._lblStueck = IntEdit( isReadOnly=True )
        self._combiStueck = InfoPanel.CombiInfo( "Bestand ", self._lblStueck, " Stck" )
        self._lblGesamtPreis = IntEdit( isReadOnly=True )
        self._combiGesamtPreis = InfoPanel.CombiInfo( "Kaufpreis ", self._lblGesamtPreis, " €" )
        self._lblPreisProStueck = FloatEdit( isReadOnly=True )
        self._combiPreisProStueck = InfoPanel.CombiInfo( "Preis je Stck ", self._lblPreisProStueck, " €" )
        self._createGui()

    def _createGui( self ):
        l = self._layout
        r, c = 0, 0
        l.addWidget( self._lblName, r, c, 1, 2 )
        r = 1
        l.addWidget( self._lblWkn, r, c )
        r = 2
        l.addWidget( self._lblIsin, r, c )
        r += 1
        l.addWidget( self._lblWaehrung, r, c )
        r += 1
        l.addWidget( self._lblAcc, r, c )
        r += 1
        l.addWidget( self._combiStueck, r, c )
        r += 1
        l.addWidget( self._combiGesamtPreis, r, c )
        r += 1
        l.addWidget( self._combiPreisProStueck, r, c )
        r, c = 1, 1
        l.addWidget( self._mplCanvas, r, c, l.rowCount(), 1 )


    def setModel( self, x:XDepotPosition ):
        self._x = x
        self._lblName.setValue(x.name)
        self._lblWkn.setValue( x.wkn )
        self._lblIsin.setValue( x.isin )
        self._lblWaehrung.setValue( x.waehrung )
        self._lblAcc.setValue( "Thesaurierend" if x.flag_acc else "Ausschüttend" )
        self._combiStueck.setLabelValue( str(x.stueck) )
        self._combiGesamtPreis.setLabelValue( str(x.gesamtkaufpreis) )
        self._combiPreisProStueck.setLabelValue( str(x.preisprostueck) )
        self._plot()

    def _plot( self ):
        self._x.history["Close"].plot( ax=self._mplCanvas.axes, grid=True )

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