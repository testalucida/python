from typing import List

from pandas import DataFrame, Series
import pandas as pd
from yfinance.scrapers.quote import FastInfo

from data.db.investmonitordata import InvestMonitorData
from data.finance.tickerhistory import Period, Interval, TickerHistory, SeriesName
from interface.interfaces import XDepotPosition, XDelta
from imon.definitions import DATABASE_DIR


class InvestMonitorLogic:
    def __init__( self, isTest=False ):
        self.TEST = isTest
        print( "running in '%s' environment" % ("TEST" if isTest else "RELEASE") )
        self._db = InvestMonitorData()
        self._tickerHist = TickerHistory()
        self._defaultPeriod = Period.oneYear
        self._defaultInterval = Interval.oneWeek
        self._minPeriod = Period.oneDay
        self._minInterval = Interval.oneMin

    def saveMyHistories( self ):
        histDf:DataFrame = self.getMyTickerHistories( self._defaultPeriod, self._defaultInterval )
        histDf.to_pickle( DATABASE_DIR + "/histories.df" ) # + datehelper.getCurrentDateIso() )
        actDf:DataFrame = self.getMyTickerHistories( Period.oneDay, Interval.oneMin )
        actDf.to_pickle( DATABASE_DIR + "/todayhistories.df" )

    @staticmethod
    def loadMyHistories( todayHistory:bool = False) -> DataFrame:
        if todayHistory:
            df = pd.read_pickle( DATABASE_DIR + "/todayhistories.df" )
        else:
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

    def getMyTickerHistories( self, period=Period.oneYear, interval=Interval.oneWeek ):
        # Alle Ticker aus dem Depot holen:
        tickerlist = self._db.getAllMyTickers()
        # Mit der TickerList die Historien holen:
        tickerHistories: DataFrame = self._tickerHist.getTickerHistoriesByPeriod( tickerlist,
                                                                                  period=period,
                                                                                  interval=interval )
        return tickerHistories

    def getDepotPosition( self, ticker:str, period=Period.oneYear, interval=Interval.oneWeek ) -> XDepotPosition:
        """
        Liefert alle Daten für die Depotposition <ticker>.

        :param ticker:
        :param period:
        :param interval:
        :return:
        """
        deppos:XDepotPosition = self._db.getDepotPosition( ticker )
        tickerHistory:DataFrame = self._tickerHist.getTickerHistoryByPeriod( ticker, period, interval )
        closeHist:Series = tickerHistory[SeriesName.Close.value]
        self._provideOrderData( deppos )
        self._provideDepotPositionData( deppos, closeHist )
        return deppos

    def getDepotPositions( self ) -> List[XDepotPosition]: #(List[XDepotPosition], Period, Interval):
        """
        Liefert die Depot-Positionen inkl. der Bestände und der Kursentwicklung in der Default-Periode und
        im Default-Zeitintervall
        :return:
        """
        # Depotpositonen holen:
        poslist:List[XDepotPosition] = self._db.getDepotPositions()
        tickerlist = [pos.ticker for pos in poslist]

        if self.TEST:
            tickerHistories: DataFrame = self.loadMyHistories( todayHistory=False )
            # tickerTodayHistories: DataFrame = self.loadMyHistories( todayHistory=True )
        else:
            tickerHistories:DataFrame = self._tickerHist.getTickerHistoriesByPeriod( tickerlist,
                                                                                     period=self._defaultPeriod,
                                                                                     interval=self._defaultInterval )
            # tickerTodayHistories:DataFrame = self._tickerHist.getTickerHistoriesByPeriod( tickerlist,
            #                                                                               period = Period.oneDay,
            #                                                                               interval = Interval.twoMins )

        closeDf:DataFrame = tickerHistories[SeriesName.Close.value]
        for deppos in poslist:
            self._provideOrderData( deppos )
            try:
                closeHist:Series = closeDf[deppos.ticker]
                self._provideDepotPositionData( deppos, closeHist )
            except Exception as ex:
                print( deppos.ticker, " not found in DataFrame closeDf" )
        return poslist

    def _provideDepotPositionData( self, deppos:XDepotPosition, closeHist:Series ) -> None:
        deppos.history = closeHist
        deppos.history_period = self._defaultPeriod
        deppos.history_interval = self._defaultInterval
        try:
            self._ensureEuro( deppos )
            deppos.gesamtwert_aktuell = int( round( deppos.stueck * deppos.kurs_aktuell, 2 ) )
            if deppos.gesamtkaufpreis > 0:
                deppos.delta_proz = round( (deppos.gesamtwert_aktuell / deppos.gesamtkaufpreis - 1) * 100, 2 )
        except Exception as ex:
            print( deppos.wkn, "/", deppos.ticker, ": no fast info available " )

    def updateDepotPositionData( self, x:XDepotPosition, period:Period, interval:Interval ) -> None:
        """
        Ermittelt für das übergebene Wertpapier die Historie gem. <period> und <interval>
        und schreibt diese Werte in <x> (x.history, x.history_period, x.history_interval.
        :param x: die zu aktualisierende Depot-Position
        :param period:
        :param interval:
        :return:
        """
        df:DataFrame = self._tickerHist.getTickerHistoryByPeriod( x.ticker, period, interval )
        self._provideDepotPositionData( x, df[SeriesName.Close.value] )
        x.history_period = period
        x.history_interval = interval

    def _ensureEuro( self, deppos:XDepotPosition ):
        """
        Ermittelt den letzten Kurs des Wertpapiers.
        Transformiert ihn in EUR, wenn erforderlich.
        Wenn die Währung des Wertpapiers USD oder GBP ist, wird deppos.history (Series)
        umgewandelt in eine Serie mit EUR-Werten.
        :param deppos: XDepotPosition
        """
        ticker = deppos.ticker
        #wkn = deppos.wkn
        fastInfo: FastInfo = self._tickerHist.getFastInfo( ticker )
        last_price = fastInfo.last_price
        currency = str(fastInfo.currency)
        if currency != "EUR":
            #print( ticker, " / ", wkn, ": ", currency, ": ", fastInfo.last_price )
            if currency == "GBp":
                last_price = last_price / 100
            last_price = TickerHistory.convertToEuro( last_price, fromCurr=currency.upper() )
            deppos.history = self._translateSeries( deppos.history, currency )
            #print( ticker, " / ", wkn, " nach Korrektur: ", currency.upper(), ": ", deppos.kurs_aktuell )
        deppos.kurs_aktuell = round( last_price, 3 )

    @staticmethod
    def _translateSeries( series:Series, currency:str ):
        """
        Übersetzt alle Werte in series.values in Euro und schreibt sie in eine Liste.
        Macht daraus und aus series.index eine neue Series und gibt diese zurück.
        Das muss sein, damit die Beschriftung der y-Achse im Graphen stimmt.
        :param series:
        :param currency: Währung wie in FastInfo eingetragen. (GBp also noch nicht in GBP umgewandelt.)
        :return:
        """
        values = series.values
        vlist = list()
        curr_upper = currency.upper()
        for value in values:
            if currency == "GBp": # pence
                value = value / 100 # pound
            value = TickerHistory.convertToEuro( value, curr_upper )
            vlist.append( value )
        index = series.index
        serNew = Series(vlist, index)
        return serNew

    # def getLastEuroPrice( self, ticker:str, wkn:str ) -> float:
    #     fastInfo: FastInfo = self._tickerHist.getFastInfo( ticker )
    #     if fastInfo.currency != "EUR":
    #         print( ticker, " / ", wkn, ": ", fastInfo.currency, ": ", fastInfo.last_price )
    #         last_price = fastInfo.last_price
    #         if fastInfo.currency == "GBp":
    #             last_price = last_price / 100
    #         currency = str(fastInfo.currency).upper()
    #         last_price = TickerHistory.convertCurrency( last_price, fromCurr=currency )
    #         print( ticker, " / ", wkn, " nach Korrektur: ", currency, ": ", last_price )
    #     else:
    #         last_price = fastInfo.last_price
    #     return round( last_price, 3 )

    def _provideOrderData( self, deppos:XDepotPosition ):
        """
        Holt zur übergebenen Depotposition die delta-Daten aus der DB und trägt sie ein
        :param deppos:
        :return:
        """
        deltalist:List[XDelta] = self._db.getDeltas( deppos.wkn )
        for delta in deltalist:
            deppos.stueck += delta.delta_stck
            orderpreis = delta.delta_stck * delta.preis_stck
            deppos.gesamtkaufpreis += orderpreis
            deppos.maxKaufpreis = delta.preis_stck if delta.preis_stck > deppos.maxKaufpreis else deppos.maxKaufpreis
            deppos.minKaufpreis = delta.preis_stck \
                                  if delta.preis_stck < deppos.minKaufpreis or deppos.minKaufpreis == 0 \
                                  else deppos.minKaufpreis
        deppos.gesamtkaufpreis = int( round( deppos.gesamtkaufpreis, 2 ) )
        if deppos.stueck > 0:
            deppos.preisprostueck = round( deppos.gesamtkaufpreis / deppos.stueck, 2 )

    def getHistoryByPeriod( self, ticker:str, period:Period, interval:Interval ):
        df:DataFrame = self._tickerHist.getTickerHistoryByPeriod( ticker, period, interval )
        return df

    def getSeriesHistoryByPeriod( self, ticker, seriesName:SeriesName, period:Period, interval:Interval ) -> Series:
        df:DataFrame = self.getHistoryByPeriod( ticker, period, interval )
        return df[seriesName.value]


def test():
    logic = InvestMonitorLogic()
    lastPrice = logic.getLastEuroPrice( "PRIJ.L" )
    #poslist = logic.getDepotPositions()
    #print( poslist )

    # logic.saveMyHistories()

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