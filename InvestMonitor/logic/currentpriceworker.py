import sys
import traceback

from PySide6.QtCore import QObject, Signal, QRunnable, Slot


class CurrentPriceWorkerSignals( QObject ):
    got_price_and_currency = Signal(float, str)
    finished = Signal()
    error = Signal( tuple )
    result = Signal( object )

##############################################################
class CurrentPriceWorker( QRunnable ):
    # def __init__( self, fn, wkn_ticker_list:List[Dict], allOrders:List[XDelta] ):
    def __init__( self, fn, tickers:list):
        super( CurrentPriceWorker, self ).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        #self._wkn_ticker_list = wkn_ticker_list
        self._tickers = tickers
        self.signals = CurrentPriceWorkerSignals()

    @Slot()
    def run( self ):
        try:
            #result = self.fn( self._wkn_ticker_list, self._allOrders )
            result = self.fn( self._tickers )
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit( (exctype, value, traceback.format_exc()) )
        else:
            self.signals.result.emit( result )  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done
