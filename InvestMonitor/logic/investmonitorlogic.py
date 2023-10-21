from typing import List

from pandas import DataFrame

from data.db.investmonitordata import InvestMonitorData
from data.finance.tickerhistory import Period, Interval, TickerHistory
from interface.interfaces import XDepotPosition


class InvestMonitorLogic:
    def __init__( self ):
        self._db = InvestMonitorData()
        self._tickerHist = TickerHistory()
        self._defaultPeriod = Period.oneYear
        self._defaultInterval = Interval.oneWeek

    def getDepotPositions( self ) -> List[XDepotPosition]:
        """
        Liefert die Depot-Positionen inkl. der Bestände und der Kursentwicklung in der Default-Periode und
        im Default-Zeitintervall
        :return:
        """
        # Depotpositonen holen:
        poslist:List[XDepotPosition] = self._db.getDepotPositions()
        tickerlist = [pos.ticker for pos in poslist]
        tickerHistories:DataFrame = self._tickerHist.getTickerHistories( tickerlist,
                                                                         period=self._defaultPeriod,
                                                                         interval=self._defaultInterval )
        print( tickerHistories )
        for pos in poslist:
            # todo: Bestände ergänzen
            # Kursentwicklungen ergänzen:
            pos.history = self._tickerHist.getTickerHistory( pos.ticker,
                                                             period=self._defaultPeriod, interval=self._defaultInterval )

        return poslist

def test():
    logic = InvestMonitorLogic()
    poslist = logic.getDepotPositions()
    print( poslist )