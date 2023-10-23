import sys

#import matplotlib.pyplot as plt  !!!ERST NACH QtWidgets IMPORTIEREN!!!
import yfinance, json
import matplotlib as mpl
#matplotlib.use( 'Agg' )
from matplotlib.axis import Axis
from pandas import Series, DataFrame


def getOneYearHistory( ticker:str ) -> Series:
    goog = yfinance.Ticker( 'goog' )
    df = goog.history( period="1y", interval="1d", start="2022-09-07" )
    series:Series = df["Close"]
    #series.plot()
    return series

def test6():
    import matplotlib.pyplot as plt
    ticker = yfinance.Ticker( 'GGRG.L' )
    df = ticker.history( period="1y", interval="1d", start="2022-09-07" )
    """
    def history( self, period="1mo", interval="1d",
                 start=None, end=None, prepost=False, actions=True,
                 auto_adjust=True, back_adjust=False,
                 proxy=None, rounding=False, tz=None, timeout=None, **kwargs ):
        :Parameters:
            period : str
                Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
                Either Use period parameter or use start and end
            interval : str
                Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                Intraday data cannot extend last 60 days
            start: str
                Download start date string (YYYY-MM-DD) or _datetime.
                Default is 1900-01-01
            end: str
                Download end date string (YYYY-MM-DD) or _datetime.
                Default is now
            prepost : bool
                Include Pre and Post market data in results?
                Default is False
            auto_adjust: bool
                Adjust all OHLC automatically? Default is True
            back_adjust: bool
                Back-adjusted data to mimic true historical prices
            proxy: str
                Optional. Proxy server URL scheme. Default is None
            rounding: bool
                Round values to 2 decimal places?
                Optional. Default is False = precision suggested by Yahoo!
            tz: str
                Optional timezone locale for dates.
                (default data is returned as non-localized dates)
            timeout: None or float
                If not None stops waiting for a response after given number of
                seconds. (Can also be a fraction of a second e.g. 0.01)
                Default is None.
            **kwargs: dict
                debug: bool
                    Optional. If passed as False, will suppress
                    error message printing to console.
    """
    series:Series = df["Close"]
    series.plot()
    #import matplotlib.pyplot as plt
    plt.grid()
    plt.gcf().autofmt_xdate()
    plt.tick_params( axis='x', which='major', labelsize=8 )
    plt.show()

def test5():
    import matplotlib.pyplot as plt
    goog = yfinance.Ticker( 'goog' )
    df = goog.history()
    series = df["High"]
    print( series )
    headdf = df.head()
    headdf.plot()
    plt.show()

def test3():
    #ticker = yfinance.Ticker( "SPYY.DE" )
    ticker = yfinance.Ticker( "SEDM.L" )
    daten = ticker.info
    for key, value in daten.items():
        print( key, ":\t", value )

def test2():
    microsoft = yfinance.Ticker( 'MSF.F' )
    print( microsoft.info )


def test1():
    # siehe https://ingo-janssen.de/aktienkurse-abfragen-mit-python-schritt-fuer-schritt/
    # Ticker zu Firma, Ticker zu ISIN finden: https://finance.yahoo.com
    #t = yfinance.Ticker( "MSF.DE" )
    #t = yfinance.Ticker( "EUSRI.PA" )
    #t = yfinance.Ticker( "LU0831568729.SG" )
    t = yfinance.Ticker( "VAPX.L" )
    print( t.info["regularMarketPrice"], " ", t.info["currency"] )
    print( "------------------------------" )
    print( t.history( period='1d', interval='1d' ) )
    print( "-------------------------------" )
    hist = t.history( period='1d', interval='1d' )
    print( "Close: ", hist["Close"] )
    print( hist )
    #print( json.dumps( t.history, indent=4 ) )
    #print( json.dumps( t.info, indent=4 ) )


def test8():
    # so geht's mit Qt
    import sys
    from PySide2 import QtWidgets
    #from PySide2.QtWidgets import QMainWindow, QApplication
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure

    # class MplCanvas( FigureCanvas ):
    #     def __init__( self, parent=None, width=5, height=4, dpi=100 ):
    #         fig = Figure( figsize=(width, height), dpi=dpi )
    #         self.axes = fig.add_subplot( 111 )
    #         super( MplCanvas, self ).__init__( fig )

    class MainWindow( QtWidgets.QMainWindow ):
        def __init__( self, *args, **kwargs ):
            super( MainWindow, self ).__init__( *args, **kwargs )

            # Create the maptlotlib FigureCanvas object,
            # which defines a single set of axes as self.axes.
            #sc = MplCanvas( self, width=5, height=4, dpi=100 )
            fig = Figure( figsize=(7, 5), dpi=65 )
            canvas = FigureCanvas( fig )
            canvas.axes = fig.add_subplot( 111 )
            canvas.axes.plot( [0, 1, 2, 3, 4], [10, 1, 20, 3, 40] )
            #print( type( sc ) )
            self.setCentralWidget( canvas )

    app = QtWidgets.QApplication( sys.argv )
    w = MainWindow()
    w.show()
    app.exec_()

def test9():
    import sys
    import matplotlib

    matplotlib.use( 'Qt5Agg' )

    from PySide2.QtWidgets import QMainWindow, QApplication

    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
    from matplotlib.figure import Figure

    class MplCanvas( FigureCanvasQTAgg ):

        def __init__( self, parent=None, width=5, height=4, dpi=100 ):
            fig = Figure( figsize=(width, height), dpi=dpi )
            self.axes = fig.add_subplot( 111 )
            super( MplCanvas, self ).__init__( fig )

    class MainWindow( QMainWindow ):

        def __init__( self, *args, **kwargs ):
            super( MainWindow, self ).__init__( *args, **kwargs )

            # Create the maptlotlib FigureCanvas object,
            # which defines a single set of axes as self.axes.
            sc = MplCanvas( self, width=5, height=4, dpi=100 )
            sc.axes.plot( [0, 1, 2, 3, 4], [10, 1, 20, 3, 40] )
            self.setCentralWidget( sc )

            self.show()

    app = QApplication( sys.argv )
    w = MainWindow()
    app.exec_()

