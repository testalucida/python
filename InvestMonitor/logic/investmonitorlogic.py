from typing import List

from pandas import DataFrame, Series
import pandas as pd
from yfinance.scrapers.quote import FastInfo

from base.basetablemodel import BaseTableModel, SumTableModel
from data.db.investmonitordata import InvestMonitorData
from data.finance.tickerhistory import Period, Interval, TickerHistory, SeriesName
from interface.interfaces import XDepotPosition, XDelta, XDetail
from imon.definitions import DATABASE_DIR


class InvestMonitorLogic:
    def __init__( self ):
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
        self._provideOrderData( deppos )
        tickerHistory:DataFrame = self._tickerHist.getTickerHistoryByPeriod( ticker, period, interval )
        closeHist:Series = tickerHistory[SeriesName.Close.value]
        dividends:Series = tickerHistory[SeriesName.Dividends.value]
        self._provideWertpapierData( deppos, closeHist, dividends )
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
        tickerHistories:DataFrame = self._tickerHist.getTickerHistoriesByPeriod( tickerlist,
                                                                                 period=self._defaultPeriod,
                                                                                 interval=self._defaultInterval )
        closeDf:DataFrame = tickerHistories[SeriesName.Close.value]
        dividendsDf:DataFrame = tickerHistories[SeriesName.Dividends.value]
        for deppos in poslist:
            self._provideOrderData( deppos )
            try:
                closeHist:Series = closeDf[deppos.ticker]
                dividends:Series = dividendsDf[deppos.ticker]
                self._provideWertpapierData( deppos, closeHist, dividends )
            except Exception as ex:
                print( deppos.ticker, " not found in DataFrame closeDf" )
        return poslist

    def _provideWertpapierData( self, deppos:XDepotPosition, closeHist:Series, dividends:Series ) -> None:
        deppos.history = closeHist
        deppos.history_period = self._defaultPeriod
        deppos.history_interval = self._defaultInterval
        try:
            deppos.kurs_aktuell, orig_currency = self.getKursAktuellInEuro( deppos.ticker )
            deppos.dividend_period = self._getSumDividends( dividends )
            if orig_currency != "EUR":
                deppos.history = self._convertSeries( deppos.history, orig_currency )
                deppos.dividend_period = round( TickerHistory.convertToEuro( deppos.dividend_period, orig_currency ), 3 )
            deppos.dividend_yield = self._computeDividendYield( deppos.kurs_aktuell, deppos.dividend_period )
            deppos.gesamtwert_aktuell = int( round( deppos.stueck * deppos.kurs_aktuell, 2 ) )
            if deppos.gesamtkaufpreis > 0:
                deppos.delta_proz = round( (deppos.gesamtwert_aktuell / deppos.gesamtkaufpreis - 1) * 100, 2 )
        except Exception as ex:
            print( deppos.wkn, "/", deppos.ticker, ": no fast info available " )

    @staticmethod
    def _getSumDividends( dividends: Series ) -> float:
        div: float = sum( [v for v in dividends.values] )
        return round( div, 3 )

    def updateWertpapierData( self, x:XDepotPosition, period:Period, interval:Interval ) -> None:
        """
        Ermittelt für das übergebene Wertpapier (repräsentiert durch <x>) die Historie gem. <period> und <interval>
        und schreibt diese Werte in <x> (x.history, x.history_period, x.history_interval.
        :param x: die zu aktualisierende Depot-Position
        :param period:
        :param interval:
        :return:
        """
        df:DataFrame = self._tickerHist.getTickerHistoryByPeriod( x.ticker, period, interval )
        self._provideWertpapierData( x, df[SeriesName.Close.value], df[SeriesName.Dividends.value] )
        x.history_period = period
        x.history_interval = interval

    def updateKursAndDivYield( self, deppos:XDepotPosition ):
        deppos.kurs_aktuell, dummy = self.getKursAktuellInEuro( deppos.ticker )
        deppos.dividend_yield = self._computeDividendYield( deppos.kurs_aktuell, deppos.dividend_period )

    @staticmethod
    def _computeDividendYield( kurs_aktuell:float, dividend:float ) -> float:
        divYield = dividend / kurs_aktuell
        return round( divYield*100, 3 )

    def getKursAktuellInEuro( self, ticker:str ) -> (float, str):
        """
        Ermittelt den letzten Kurs des Wertpapiers.
        Transformiert ihn in EUR, wenn erforderlich.
        umgewandelt in eine Serie mit EUR-Werten.
        :param ticker:
        :return: den letzten Kurs in Euro, gerundet auf 3 Stellen hinter dem Komma
                 UND die ursprüngliche Währung (EUR oder Fremdwährung, die konvertiert wurde)
        """
        fastInfo: FastInfo = self._tickerHist.getFastInfo( ticker )
        last_price = fastInfo.last_price
        currency = str( fastInfo.currency )
        if currency != "EUR":
            last_price = TickerHistory.convertToEuro( last_price, currency )
        return round( last_price, 3 ), currency

    @staticmethod
    def _convertSeries( series:Series, currency:str ):
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
        for value in values:
            value = TickerHistory.convertToEuro( value, currency )
            vlist.append( value )
        index = series.index
        serNew = Series(vlist, index)
        return serNew

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

    def getOrders( self, wkn:str ) -> SumTableModel:
        deltalist = self._db.getDeltas( wkn )
        tm = SumTableModel( deltalist, 0, ("delta_stck", "order_summe") )
        tm.setKeyHeaderMappings2( ("delta_datum", "delta_stck", "preis_stck",    "order_summe",   "bemerkung"),
                                  ("Datum",        "Stück",     "Stück-\npreis (€)", "Order-\nsumme (€)", "Bemerkung") )
        return tm

    def getDetails( self, deppos:XDepotPosition ) -> XDetail:
        """
        Liefert die Daten für die Detailanzeige.
        Diese befinden sich bereits in <deppos>, sie müssen nur in ein XDetail-Objekt überführt werden.
        :param deppos:
        :return:
        """
        x = XDetail()
        x.basic_index = deppos.basic_index
        x.beschreibung = deppos.beschreibung
        x.bank = deppos.bank
        x.depot_nr = deppos.depot_nr
        x.depot_vrrkto = deppos.depot_vrrkto
        return x

def test():
    logic = InvestMonitorLogic()
    lastPrice = logic.getKursAktuellInEuro( "PRIJ.L" )
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