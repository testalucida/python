import math
from typing import List

from pandas import DataFrame, Series
import pandas as pd
from yfinance.scrapers.quote import FastInfo

from base.basetablemodel import BaseTableModel, SumTableModel
from data.db.investmonitordata import InvestMonitorData
from data.finance.tickerhistory import Period, Interval, TickerHistory, SeriesName
from imon.enums import InfoPanelOrder
from interface.interfaces import XDepotPosition, XDelta, XDetail
from imon.definitions import DATABASE_DIR, DEFAULT_PERIOD, DEFAULT_INTERVAL


class InvestMonitorLogic:
    def __init__( self ):
        self._db = InvestMonitorData()
        self._tickerHist = TickerHistory()
        self._defaultPeriod = DEFAULT_PERIOD #Period.oneYear
        self._defaultInterval = DEFAULT_INTERVAL #Interval.oneWeek
        self._minPeriod = Period.oneDay
        self._minInterval = Interval.oneMin

    # def saveMyHistories( self ):
    #     histDf:DataFrame = self.getMyTickerHistories( self._defaultPeriod, self._defaultInterval )
    #     histDf.to_pickle( DATABASE_DIR + "/histories.df" ) # + datehelper.getCurrentDateIso() )
    #     actDf:DataFrame = self.getMyTickerHistories( Period.oneDay, Interval.oneMin )
    #     actDf.to_pickle( DATABASE_DIR + "/todayhistories.df" )
    #
    # @staticmethod
    # def loadMyHistories( todayHistory:bool = False) -> DataFrame:
    #     if todayHistory:
    #         df = pd.read_pickle( DATABASE_DIR + "/todayhistories.df" )
    #     else:
    #         df = pd.read_pickle( DATABASE_DIR + "/histories.df" )
    #     return df
    #
    # @staticmethod
    # def getHistory( ticker:str, series:SeriesName, dfAllHistories:DataFrame=None ) -> Series:
    #     """
    #     Ermittelt aus dem DataFrame, der alle Historien aller Ticker enthält, die gewünschte Serie.
    #     !!! Ist dfAllHistories nicht angegeben, wird der DataFrame ***DER AUF PLATTE GESPEICHERT IST*** geladen. !!!
    #     :param ticker:
    #     :param series:
    #     :param dfAllHistories:
    #     :return:
    #     """
    #     if not dfAllHistories:
    #         dfAllHistories = InvestMonitorLogic.loadMyHistories()
    #     allSeries:DataFrame = dfAllHistories[series.value]
    #     tickerhist:Series = allSeries[ticker]
    #     return tickerhist

    # def getMyTickerHistories( self, period=Period.oneYear, interval=Interval.oneWeek ):
    #     # Alle Ticker aus dem Depot holen:
    #     tickerlist = self._db.getAllMyTickers()
    #     # Mit der TickerList die Historien holen:
    #     tickerHistories: DataFrame = self._tickerHist.getTickerHistoriesByPeriod( tickerlist,
    #                                                                               period=period,
    #                                                                               interval=interval )
    #     return tickerHistories

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

    def getDepotPositions____( self, period:Period, interval:Interval ) -> List[XDepotPosition]:
        """
        Liefert die Depot-Positionen inkl. der Bestände und der Kursentwicklung in der Default-Periode und
        im Default-Zeitintervall
        :return:
        """
        # Depotpositonen holen:
        poslist:List[XDepotPosition] = self._db.getDepotPositions()
        tickerlist = [pos.ticker for pos in poslist]
        tickerHistories:DataFrame = self._tickerHist.getTickerHistoriesByPeriod( tickerlist,
                                                                                 period=period,
                                                                                 interval=interval )
        tickerHistories = self._checkForNaN( tickerHistories )
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

    def getDepotPositions( self, period:Period, interval:Interval ) -> List[XDepotPosition]:
        """
        Liefert die Depot-Positionen inkl. der Bestände und der Kursentwicklung in der Default-Periode und
        im Default-Zeitintervall
        :return:
        """
        # Depotpositonen holen:
        poslist:List[XDepotPosition] = self._db.getDepotPositions()
        for deppos in poslist:
            self._provideOrderData( deppos )
        return self.getTickerHistories( poslist, period, interval )

    def getTickerHistories( self, poslist:List[XDepotPosition], period:Period, interval:Interval ) -> List[XDepotPosition]:
        tickerlist = [pos.ticker for pos in poslist]
        tickerHistories: DataFrame = self._tickerHist.getTickerHistoriesByPeriod( tickerlist,
                                                                                  period=period,
                                                                                  interval=interval )
        tickerHistories = self._checkForNaN( tickerHistories )
        closeDf: DataFrame = tickerHistories[SeriesName.Close.value]
        dividendsDf: DataFrame = tickerHistories[SeriesName.Dividends.value]
        for deppos in poslist:
            self._provideOrderData( deppos )
            try:
                closeHist: Series = closeDf[deppos.ticker]
                dividends: Series = dividendsDf[deppos.ticker]
                self._provideWertpapierData( deppos, closeHist, dividends )
            except Exception as ex:
                print( deppos.ticker, " not found in DataFrame closeDf" )
        return poslist

    @staticmethod
    def _checkForNaN( df:DataFrame ) -> DataFrame:
        row = df.tail(1) # damit haben wir die letzte Zeile des DataFrame, also die letzten Values aller Series (columns)
        for name, cellValues in row.items():
            # name: Spaltenkopf, z.B. EZTQ.F
            # cellValues: die Values von row
            if math.isnan( cellValues[0] ):
                df = df[:-1]
                break
        return df

    def _provideWertpapierData( self, deppos:XDepotPosition, closeHist:Series, dividends:Series ) -> None:
        deppos.history = closeHist
        deppos.history_period = self._defaultPeriod
        deppos.history_interval = self._defaultInterval

        deppos.kurs_aktuell, orig_currency = self.getKursAktuellInEuro( deppos.ticker )
        if deppos.kurs_aktuell == 0:
            print( deppos.wkn, "/", deppos.ticker,
                   ": _provideWertpapierData(): call to getKursAktuellInEuro() failed.\nNo last_price availabel.")

        deppos.dividend_period = self._getSumDividends( dividends )
        if orig_currency != "EUR":
            deppos.history = self._convertSeries( deppos.history, orig_currency )
            if deppos.dividend_period > 0:
                deppos.dividend_period = \
                    round( TickerHistory.convertToEuro( deppos.dividend_period, orig_currency ), 3 )
        if deppos.dividend_period > 0:
            deppos.dividend_yield = self._computeDividendYield( deppos.kurs_aktuell, deppos.dividend_period )
        self._provideGesamtwertAndDelta( deppos )

    @staticmethod
    def _provideGesamtwertAndDelta( deppos:XDepotPosition ):
        deppos.gesamtwert_aktuell = int( round( deppos.stueck * deppos.kurs_aktuell, 2 ) )
        if deppos.gesamtkaufpreis > 0:
            deppos.delta_proz = round( (deppos.gesamtwert_aktuell / deppos.gesamtkaufpreis - 1) * 100, 2 )

    @staticmethod
    def _getSumDividends( dividends: Series ) -> float:
        div: float = sum( [v for v in dividends.values if not math.isnan( v )] )
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
        if deppos.kurs_aktuell > 0 and deppos.dividend_period > 0:
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
        if fastInfo:
            last_price = fastInfo.last_price
            currency = str( fastInfo.currency )
            if currency != "EUR":
                last_price = TickerHistory.convertToEuro( last_price, currency )
            return round( last_price, 3 ), currency
        else:
            print( "Ticker '%s':\nNo FastInfo available" % ticker )
            return 0, ""

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
            if not math.isnan( value ):
                value = TickerHistory.convertToEuro( value, currency )
            else:
                value = 0
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
        deppos.stueck = 0
        deppos.gesamtkaufpreis = deppos.maxKaufpreis = deppos.minKaufpreis = 0
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

    @staticmethod
    def getDetails( deppos:XDepotPosition ) -> XDetail:
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

    def insertOrderAndUpdateDepotData( self, delta:XDelta, deppos:XDepotPosition ):
        """
        Fügt eine Order (Kauf oder Verkauf) in Tabelle delta ein.
        Danach werden die deppos-Attribute stueck, gesamtkaufpreis, preisprostueck und ggf. maxKaufpreis oder minKaufpreis
        geändert. Außerdem werden gesamtwert_aktuell und elta_prod neu berechnet.
        :param delta: die Daten der neuen Order
        :param deppos: die Depotposition, die sich durch die Order verändert
        :return:
        """
        delta.preis_stck = round( delta.order_summe / delta.delta_stck, 3 )
        self._db.insertDelta( delta )
        self._db.commit()
        self._provideOrderData( deppos )
        self._provideGesamtwertAndDelta( deppos )

def test():
    logic = InvestMonitorLogic()
    lastPrice = logic.getKursAktuellInEuro( "PRIJ.L" )
    #poslist = logic.getDepotPositions()
    #print( poslist )

    # logic.saveMyHistories()

    poslist, dummy = logic.getDepotPositions()
    print( poslist )

    # df = logic.loadMyHistories()
    # close:DataFrame = df["Close"]
    # cols:Index = close.columns # <-- ticker-collection
    # print( cols[0] ) # <-- ticker
    # eusri:DataFrame = close["EUSRI.PA"]
    # print( eusri )

    #series = logic.getSeriesHistoryByPeriod( "WTEM.DE", SeriesName.Close, Period.fiveDays, Interval.oneDay )
    #print( series )