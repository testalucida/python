from typing import List

from pandas import DataFrame, Series, Index
import pandas as pd
import datehelper
from data.db.investmonitordata import InvestMonitorData
from data.finance.tickerhistory import Period, Interval, TickerHistory, SeriesName
from interface.interfaces import XDepotPosition
from main.definitions import DATABASE_DIR


class InvestMonitorLogic:
    def __init__( self ):
        self._db = InvestMonitorData()
        self._tickerHist = TickerHistory()
        self._defaultPeriod = Period.oneYear
        self._defaultInterval = Interval.oneWeek

    def saveMyHistories( self ):
        histDf:DataFrame = self.getMyTickerHistories()
        histDf.to_pickle( DATABASE_DIR + "/histories.df" ) # + datehelper.getCurrentDateIso() )

    @staticmethod
    def loadMyHistories() -> DataFrame:
        df = pd.read_pickle( DATABASE_DIR + "/histories.df" )
        return df

    @staticmethod
    def getHistory( ticker:str, series:SeriesName, dfAllHistories:DataFrame=None ) -> Series:
        """
        Ermittelt aus dem DataFrame, der alle Historien aller Ticker enthält, die gewünschte Serie.
        !!! Ist dfAllHistories nicht angegeben, wird der DataFrame ***DER AUF PLATTE GESPEICHERT IST*** geladen. !!!
        :param ticker:
        :param series:
        :param dfAllHistories:
        :return:
        """
        if not dfAllHistories:
            dfAllHistories = InvestMonitorLogic.loadMyHistories()
        allSeries:DataFrame = dfAllHistories[series.value]
        tickerhist:Series = allSeries[ticker]
        return tickerhist

    def getMyTickerHistories( self ):
        # Alle Ticker aus dem Depot holen:
        tickerlist = self._db.getAllMyTickers()
        # Mit der TickerList die Historien holen:
        tickerHistories: DataFrame = self._tickerHist.getTickerHistoriesByPeriod( tickerlist,
                                                                                  period=self._defaultPeriod,
                                                                                  interval=self._defaultInterval )
        return tickerHistories

    def getDepotPositions( self ) -> (List[XDepotPosition], Period, Interval):
        """Scanned Document
        Liefert die Depot-Positionen inkl. der Bestände und der Kursentwicklung in der Default-Periode und
        im Default-Zeitintervall
        :return:
        """
        # Depotpositonen holen:
        poslist:List[XDepotPosition] = self._db.getDepotPositions()
        tickerlist = [pos.ticker for pos in poslist]

        ###### TEST TEST TEST TEST TEST
        # !!! die nachfolgenden 3 Zeilen scharf schalten, wenn TEST-Ende !!!
        # tickerHistories:DataFrame = self._tickerHist.getTickerHistoriesByPeriod( tickerlist,
        #                                                                          period=self._defaultPeriod,
        #                                                                          interval=self._defaultInterval )

        # !!!nachfolgende Zeile deaktivieren bei TEST-ENDE!!!
        tickerHistories:DataFrame = self.loadMyHistories()

        closeDf:DataFrame = tickerHistories[SeriesName.Close.value]
        tickers:Index = closeDf.columns # tickers ist eine Liste mit allen Tickers
        for ticker in tickers:
            closeHist:Series = closeDf[ticker]
            # jetzt anhand von ticker die richtige XDepotPosition finden:
            for deppos in poslist:
                if deppos.ticker == ticker:
                    # XDepotPosition gefunden; History eintragen
                    deppos.history = closeHist
                    deppos.history_period = self._defaultPeriod
                    deppos.history_interval = self._defaultInterval
                    break

        return poslist

    def getHistoryByPeriod( self, ticker:str, period:Period, interval:Interval ):
        df:DataFrame = self._tickerHist.getTickerHistoryByPeriod( ticker, period, interval )
        return df

    def getSeriesHistoryByPeriod( self, ticker, seriesName:SeriesName, period:Period, interval:Interval ) -> Series:
        df:DataFrame = self.getHistoryByPeriod( ticker, period, interval )
        return df[seriesName.value]


def test():
    logic = InvestMonitorLogic()
    #poslist = logic.getDepotPositions()
    #print( poslist )
    #logic.saveMyHistories()

    poslist = logic.getDepotPositions()
    print( poslist )

    # df = logic.loadMyHistories()
    # close:DataFrame = df["Close"]
    # cols:Index = close.columns # <-- ticker-collection
    # print( cols[0] ) # <-- ticker
    # eusri:DataFrame = close["EUSRI.PA"]
    # print( eusri )

    #series = logic.getSeriesHistoryByPeriod( "WTEM.DE", SeriesName.Close, Period.fiveDays, Interval.oneDay )
    #print( series )